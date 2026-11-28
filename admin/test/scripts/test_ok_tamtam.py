"""OK tamtam_messages: messages, chats and contacts.

The fixture holds a subset of the app's columns, with chat, contact and attachment blobs built
here in the protobuf wire format the app's generated classes write. Values are made up.
"""
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import okTamTam as ok  # pylint: disable=wrong-import-position

MS = 1767225600000  # 2026-01-01 00:00:00 UTC


def varint(value):
    out = b''
    while True:
        byte = value & 0x7f
        value >>= 7
        if value:
            out += bytes([byte | 0x80])
        else:
            return out + bytes([byte])


def field(number, value):
    if isinstance(value, int):
        return varint(number << 3) + varint(value)
    data = value.encode() if isinstance(value, str) else value
    return varint(number << 3 | 2) + varint(len(data)) + data


def database(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE chats (_id INTEGER PRIMARY KEY, cht_server_id INTEGER, cht_data BLOB)')
    db.execute('CREATE TABLE contacts (_id INTEGER PRIMARY KEY, ctt_data BLOB, ctt_presence INTEGER, '
               'ctt_server_id INTEGER)')
    db.execute('''CREATE TABLE messages (_id INTEGER PRIMARY KEY, msg_server_id INTEGER, msg_time INTEGER,
        msg_update_time INTEGER, msg_sender INTEGER, msg_text TEXT, msg_delivered_status INTEGER,
        msg_status INTEGER, msg_attaches BLOB, msg_type INTEGER, msg_chat_id INTEGER)''')
    dialog = field(1, 900) + field(4, 7) + field(5, field(1, 7) + field(2, 0)) + \
        field(5, field(1, 8) + field(2, 0)) + field(11, MS)
    group = field(1, 901) + field(2, 3) + field(3, 1) + field(7, 'Group') + field(11, MS)
    db.execute('INSERT INTO chats VALUES (1, 900, ?)', (dialog,))
    db.execute('INSERT INTO chats VALUES (2, 901, ?)', (group,))
    contact = field(1, 8) + field(8, MS) + field(14, field(1, 'Other') + field(2, 1)) + \
        field(14, field(1, 'Nick') + field(2, 3))
    db.execute('INSERT INTO contacts VALUES (1, ?, 0, 8)', (contact,))
    attaches = field(1, field(1, 2) + field(14, '/storage/emulated/0/x.jpg')) + field(1, field(1, 8))
    db.execute('INSERT INTO messages VALUES (1, 55, ?, 0, 8, ?, 30, 10, ?, 10, 1)', (MS, 'hello', attaches))
    db.execute('INSERT INTO messages VALUES (2, 56, ?, 0, 7, ?, 20, 0, NULL, 10, 2)', (MS + 1000, 'hi'))
    db.commit()
    db.close()


class OkTamTamTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'data' / 'data' / 'ru.ok.android' / 'databases' / 'tamtam_messages'
        database(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def run_artifact(self, function):
        context = SimpleNamespace(get_files_found=lambda: [str(self.path)],
                                  get_relative_path=lambda p: str(Path(p).relative_to(self.temp.name)))
        headers, rows, _source = function.__wrapped__(context)
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        self.assertTrue(all(len(row) == len(names) for row in rows))
        return [dict(zip(names, row)) for row in rows]

    def test_messages(self):
        rows = self.run_artifact(ok.ok_tamtam_messages)
        first = rows[0]
        self.assertEqual(first['Time'], datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual((first['Chat Type'], first['Sender'], first['Text']), ('DIALOG', 'Other (OK)\nNick (CUSTOM)', 'hello'))
        self.assertEqual(first['Attachments'], 'PHOTO /storage/emulated/0/x.jpg\nCALL')
        self.assertEqual((first['Delivery Status'], first['Status'], first['Message Type']), ('READ', 'DELETED', 'USER'))
        self.assertEqual((rows[1]['Chat Title'], rows[1]['Chat Type'], rows[1]['Sender']), ('Group', 'GROUP_CHAT', ''))

    def test_chats(self):
        rows = {row['Server ID']: row for row in self.run_artifact(ok.ok_tamtam_chats)}
        self.assertEqual(rows[900]['Participants'], '7\nOther (OK) [8]')
        self.assertEqual((rows[900]['Type'], rows[900]['Status']), ('DIALOG', 'ACTIVE'))
        self.assertEqual((rows[901]['Type'], rows[901]['Status'], rows[901]['Title']), ('GROUP_CHAT', 'LEFT', 'Group'))

    def test_contacts_and_bad_blob(self):
        db = sqlite3.connect(self.path)
        db.execute("INSERT INTO contacts VALUES (2, X'FF', 0, 9)")
        db.commit()
        db.close()
        rows = {row['Server ID']: row for row in self.run_artifact(ok.ok_tamtam_contacts)}
        self.assertEqual(rows[8]['Names'], 'Other (OK)\nNick (CUSTOM)')
        self.assertEqual(rows[8]['Last Update Time'], datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(rows[9]['Names'], '')


if __name__ == '__main__':
    unittest.main()
