"""Real msg/contact SQLite states retain typed read_status and every message row."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import tikTok as artifact  # pylint: disable=wrong-import-position


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def copy_state(target, schema, records, wal):
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / target.name
        connection = sqlite3.connect(source)
        if wal:
            connection.execute('pragma journal_mode=wal')
            connection.execute('pragma wal_autocheckpoint=0')
        connection.executescript(schema)
        if wal:
            connection.execute('pragma wal_checkpoint(truncate)')
        for query, values in records:
            connection.executemany(query, values)
        connection.commit()
        for item in Path(work).glob(target.name + '*'):
            shutil.copyfile(item, target.parent / item.name)
        connection.close()
    for item in target.parent.glob(target.name + '*'):
        item.chmod(0o444)
    return target


def create_stores(root, wal=False, multi=False):
    folder = Path(root) / 'data/data/com.zhiliaoapp.musically/databases'
    flags = [None, 0, 1, 2, -1, 0.0, 1.0, 1.25, '0', '1', 'Read', '', b'\x00\xff']
    paths = []
    for uid, filename in [(101, '101_im.db')] + ([(202, 'biz_2_202_im.db')] if multi else []):
        rows = []
        for index, flag in enumerate(flags):
            content = json.dumps({'text': 'message-' + str(index), 'display_name': 'GIF', 'url': {'url_list': ['first', 'second']}})
            if index == 1:
                content = 'not JSON'
            elif index == 2:
                content = None
            elif index == 3:
                content = b'not JSON'
            rows.append((1700000000000 + index, uid if index % 2 else 999, content, index, index % 2, flag, 'thread-' + str(index % 2)))
        rows.append(rows[2])
        paths.append(copy_state(folder / filename,
                                'CREATE TABLE msg(created_time,sender,content,type,deleted,read_status,conversation_id);',
                                [('INSERT INTO msg VALUES(?,?,?,?,?,?,?)', rows)], wal))
    schema = 'CREATE TABLE IM_USER_BASE_INFO(UID,NICK_NAME,UNIQUE_ID,INITIAL_LETTER,AVATAR_THUMB,FOLLOW_STATUS,UPDATE_TIME,BLOCK,DELETED);'
    values = [(999, 'contact-name', 'contact-id', 'C', '{}', 1, 1700000000000, 0, 0)]
    paths.append(copy_state(folder / 'db_im_contact', schema, [('INSERT INTO IM_USER_BASE_INFO VALUES(?,?,?,?,?,?,?,?,?)', values)], wal))
    schema = 'CREATE TABLE SIMPLE_USER(UID,NICK_NAME,UNIQUE_ID,INITIAL_LETTER,AVATAR_THUMB,FOLLOW_STATUS);'
    values = [(999, 'ignored-name', 'ignored-id', 'I', '{}', 1), (101, 'self-name', 'self-id', 'S', '{}', 0)]
    paths.append(copy_state(folder / 'db_im_xx', schema, [('INSERT INTO SIMPLE_USER VALUES(?,?,?,?,?,?)', values)], wal))
    return paths


def direct_status(path):
    connection = sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True)
    rows = connection.execute('SELECT created_time,sender,content,type,deleted,read_status,conversation_id FROM msg ORDER BY created_time').fetchall()
    classes = connection.execute('SELECT typeof(read_status) FROM msg ORDER BY created_time').fetchall()
    connection.close()
    return rows, classes


class TestRawReadStatus(unittest.TestCase):
    def test_native_typed_status_and_duplicate_rows(self):
        with tempfile.TemporaryDirectory() as root:
            files = create_stores(root)
            headers, rows, _ = artifact.get_tikTok.__wrapped__(Context(root, files))
            raw, classes = direct_status(files[0])
            self.assertEqual(len(headers), 14)
            self.assertEqual(len(rows), 14)
            self.assertEqual([r[10] for r in rows], [r[5] for r in raw])
            self.assertEqual([type(r[10]) for r in rows], [type(r[5]) for r in raw])
            self.assertEqual([r[0] for r in rows], [datetime.fromtimestamp(r[0] / 1000, timezone.utc) for r in raw])
            self.assertEqual(rows[2], rows[3])
            self.assertEqual(classes[-1], ('blob',))
            self.assertTrue(all(len(r) == 14 for r in rows))

    def test_actual_wal_rows_and_all_accounts(self):
        with tempfile.TemporaryDirectory() as root:
            files = create_stores(root, wal=True, multi=True)
            self.assertGreater(Path(str(files[0]) + '-wal').stat().st_size, 0)
            _, rows, source = artifact.get_tikTok.__wrapped__(Context(root, list(reversed(files))))
            self.assertEqual(len(rows), 28)
            self.assertEqual([r[12] for r in rows], ['101'] * 14 + ['202'] * 14)
            self.assertEqual([r[10] for r in rows], [r[5] for path in files[:2] for r in direct_status(path)[0]])
            self.assertEqual(source.split('\n'), [str(p) for p in files])
            self.assertEqual([r[13] for r in rows[:14]], [str(files[0].relative_to(root))] * 14)

    def test_json_fallback_name_precedence_and_source(self):
        with tempfile.TemporaryDirectory() as root:
            files = create_stores(root)
            _, rows, source = artifact.get_tikTok.__wrapped__(Context(root, files))
            self.assertEqual(rows[0][2], 'contact-name')
            self.assertEqual(rows[0][5], 'contact-id')
            self.assertEqual(rows[0][7], 'first')
            self.assertIsNone(rows[1][3])
            self.assertIsNone(rows[2][3])
            self.assertIsNone(rows[4][3])
            self.assertEqual(source.split('\n'), [str(p) for p in files])
            _, contacts, _ = artifact.get_tikTok_contacts.__wrapped__(Context(root, files))
            self.assertEqual(len(contacts), 2)
            self.assertEqual(contacts[0][2], 'contact-name')

    def test_existing_storage_alias_preference(self):
        with tempfile.TemporaryDirectory() as root:
            files = create_stores(root)
            alias = Path(root) / 'data/user/0/com.zhiliaoapp.musically/databases/101_im.db'
            alias.parent.mkdir(parents=True)
            shutil.copyfile(files[0], alias)
            alias.chmod(0o444)
            _, rows, _ = artifact.get_tikTok.__wrapped__(Context(root, [alias] + files))
            self.assertEqual(len(rows), 14)
            self.assertTrue(all(r[13] == str(files[0].relative_to(root)) for r in rows))


if __name__ == '__main__':
    unittest.main()
