"""Actual SQLite/zlib/protobuf rows retain emails without optional header mappings."""
from pathlib import Path
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts.gmailEmails import gmailEmails  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import decode_protobuf  # pylint: disable=wrong-import-position

MESSAGE_SCHEMA = '''CREATE TABLE item_messages(row_id INTEGER PRIMARY KEY AUTOINCREMENT,
server_perm_id TEXT,items_row_id INTEGER,message_proto BLOB,zipped_message_proto BLOB,
is_missing_details INTEGER,write_sequence_id INTEGER,message_details_external_storage_id TEXT,
is_invalidated INTEGER,legacy_storage_id INTEGER)'''
ATTACHMENT_SCHEMA = '''CREATE TABLE item_message_attachments(row_id INTEGER PRIMARY KEY AUTOINCREMENT,
item_messages_row_id INTEGER,is_synced INTEGER,attachment_url TEXT,attachment_cache_key TEXT,
attachment_file_name TEXT,attachment_hash TEXT,message_synced_time_ms INTEGER)'''


def varint(value):
    output = bytearray()
    while value > 127:
        output.append((value & 127) | 128)
        value >>= 7
    return bytes(output) + bytes([value])


def integer(field, value):
    return varint(field << 3) + varint(value)


def binary(field, value):
    return varint((field << 3) | 2) + varint(len(value)) + value


def wire(header='valid'):
    data = integer(17, 1700000000123)
    data += binary(1, binary(2, b'recipient@example.org') + binary(3, b'Recipient'))
    data += binary(5, b'Subject')
    data += binary(6, binary(2, binary(3, binary(2, b'<p>body <a href="https://example.org">link</a></p>'))))
    if header == 'valid':
        data += binary(11, binary(8, b'mailer') + binary(9, b'signer') +
                       binary(15, b'Reply Name') + binary(17, b'reply@example.org'))
    elif header == 'integer':
        data += integer(11, 7)
    elif header == 'bytes':
        data += binary(11, b'opaque header')
    elif header == 'list':
        data += integer(11, 7) + integer(11, 8)
    elif header == 'empty':
        data += binary(11, b'')
    return b'\0' + zlib.compress(data)


def make_database(root, edge=True, suffix='123'):
    path = Path(root) / ('data/data/com.google.android.gm/databases/bigTopDataDB.' + suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute(MESSAGE_SCHEMA)
    con.execute(ATTACHMENT_SCHEMA)
    variants = ['valid', 'absent', 'integer', 'bytes', 'list', 'empty', 'valid'] if edge else ['valid', 'valid']
    for i, header in enumerate(variants, 1):
        identifier = 'duplicate' if i in [2, 3] else ('long\n' + 'x' * 200 if i == 4 else str(i))
        con.execute('INSERT INTO item_messages VALUES(?,?,?,?,?,?,?,?,?,?)',
                    (i, identifier, None, None, wire(header), 0, 0, None, 0, None))
    con.execute('INSERT INTO item_messages VALUES(?,?,?,?,?,?,?,?,?,?)',
                (99, 'NULL-proto', None, None, None, 0, 0, None, 0, None))
    con.executemany('INSERT INTO item_message_attachments VALUES(?,?,?,?,?,?,?,?)', [
        (1, 1, 0, None, None, 'noname', None, 0),
        (2, 1, 0, None, None, 'missing.txt', None, 0)])
    con.commit()
    assert con.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
    con.close()
    return path, variants


def parse(paths, root):
    return gmailEmails.__wrapped__(SimpleNamespace(
        get_files_found=lambda: list(map(str, paths)),
        get_relative_path=lambda p: str(Path(p).relative_to(root))))


class GmailOptionalHeaderTest(unittest.TestCase):
    def setUp(self):
        self.original_data_folder = Context.get_data_folder()

    def tearDown(self):
        Context.set_data_folder(self.original_data_folder)

    def test_actual_wire_missing_and_unsupported_headers_keep_join_occurrences(self):
        with tempfile.TemporaryDirectory() as root:
            Context.set_data_folder(root)
            path, variants = make_database(root)
            with patch('scripts.artifacts.gmailEmails.logfunc') as log:
                headers, rows, source = parse([path], root)
            self.assertEqual(len(headers), 16)
            self.assertEqual(headers[0], ('Timestamp', 'datetime'))
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual(source, str(path))
            self.assertEqual(len(rows), 8)
            self.assertEqual([r[3] for r in rows[:4]], ['1', '1', 'duplicate', 'duplicate'])
            self.assertCountEqual([r[7] for r in rows[:2]], ['', 'missing.txt'])
            self.assertTrue(all(r[4] == 'body link [1]' for r in rows))
            self.assertTrue(all(r[5] == '[1] https://example.org' for r in rows))
            self.assertTrue(all(r[8:10] == ('recipient@example.org', 'Recipient') for r in rows))
            self.assertTrue(all(r[12] == 'Subject' for r in rows))
            self.assertTrue(all(r[-1] == str(path.relative_to(root)) for r in rows))
            for row in [rows[0], rows[1], rows[-1]]:
                self.assertEqual(row[10:12] + row[13:15],
                                 ('reply@example.org', 'Reply Name', 'mailer', 'signer'))
            for row in rows[2:-1]:
                self.assertEqual(row[10:12] + row[13:15], ('', '', '', ''))
            decoded = [decode_protobuf(zlib.decompress(wire(v)[1:]))[0] for v in variants]
            unsupported = [m['11'] for m in decoded if '11' in m and not isinstance(m['11'], dict)]
            self.assertEqual(log.call_count, len(unsupported))
            for call in log.call_args_list:
                diagnostic = call.args[0]
                self.assertNotIn(root, diagnostic)
                self.assertNotIn('\n', diagnostic)
                self.assertLess(len(diagnostic), 500)
                self.assertIn('header columns omitted', diagnostic)
            self.assertNotIn('NULL-proto', str(rows))

    def test_valid_later_store_and_unchanged_no_attachment_cells(self):
        with tempfile.TemporaryDirectory() as root:
            Context.set_data_folder(root)
            first, _ = make_database(root)
            second, _ = make_database(root, edge=False, suffix='456')
            with patch('scripts.artifacts.gmailEmails.logfunc'):
                _, rows, sources = parse([second, first], root)
            self.assertEqual(len(rows), 11)
            self.assertEqual(sources.splitlines(), [str(first), str(second)])
            self.assertEqual([r[2] for r in rows[-3:]], ['456'] * 3)
            self.assertEqual(rows[-1][6:8], ('', ''))
            self.assertEqual(rows[-1][10:12], ('reply@example.org', 'Reply Name'))
