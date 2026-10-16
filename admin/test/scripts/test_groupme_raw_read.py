"""Stored SQLite read values, joins and optional columns in GroupMe chats."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import groupMe


VALUES = [None, 0, 1, 2, -1, 5, 0.0, 1.0, -0.0, 1.5, '', '0', '1',
          '01', 'unknown', 'line\nΩ', b'', b'1', b'\x00\xff', 1, 0,
          -(2**63), 2**63 - 1]


def create_store(path, affinity='', missing=(), fanout=False):
    """Build actual tables used by both wrappers with controlled flag storage."""
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE groups(group_id,created_at,name,group_type,creator_user_id,'
               'message_count,attachment_count,last_message_created_at,updated_at)')
    db.execute('CREATE TABLE members(user_id,group_id,user_real_name,role)')
    db.execute('INSERT INTO groups VALUES(1,1700000000,"group","private",7,23,0,1700000100,1700000200)')
    db.execute('INSERT INTO members VALUES(7,1,"creator","member")')
    if fanout:
        db.execute('INSERT INTO groups SELECT * FROM groups')
    columns = ['created_at', 'deleted_at', 'conversation_id', 'name', 'sender_type',
               'is_system', 'hidden', 'read', 'deletion_actor', 'message_text',
               'photo_url', 'photo_uri', 'photo_width', 'photo_height', 'photo_is_gif',
               'video_url', 'location_lat', 'location_lng', 'location_name']
    selected = [c for c in columns if c not in missing]
    db.execute('CREATE TABLE messages(' + ','.join(c + (' ' + affinity if c == 'read' else '')
                                                 for c in selected) + ')')
    for n, value in enumerate(VALUES):
        row = [1700000300 + n, 1700000400 if n % 3 == 0 else 0, 1 if n % 2 else 99,
               'sender', 'user', n % 3, n % 3, value, 'sender', 'message', '', '', 0, 0,
               n % 3, '', 0.0, 0.0, '']
        db.execute('INSERT INTO messages VALUES(' + ','.join('?' for _ in selected) + ')',
                   [v for c, v in zip(columns, row) if c in selected])
    db.execute('INSERT INTO messages SELECT * FROM messages WHERE created_at=1700000301')
    db.commit()
    return db


class TestGroupMeRawRead(unittest.TestCase):
    def parse(self, path):
        return groupMe.get_groupMe_chat.__wrapped__(
            SimpleNamespace(get_files_found=lambda: [str(path)]))

    def test_storage_classes_and_join_occurrences(self):
        with tempfile.TemporaryDirectory() as folder:
            for affinity in ['', 'TEXT', 'INTEGER']:
                with self.subTest(affinity=affinity):
                    path = Path(folder) / ((affinity or 'NONE') + '.db')
                    with create_store(path, affinity, fanout=True) as db:
                        expected = db.execute('SELECT messages.read FROM messages LEFT JOIN groups '
                                              'ON groups.group_id=messages.conversation_id '
                                              'ORDER BY messages.created_at ASC').fetchall()
                    headers, rows, source = self.parse(path)
                    self.assertEqual(headers[7], 'read (as stored)')
                    self.assertEqual(len(headers), 19)
                    self.assertTrue(all(len(r) == 19 for r in rows))
                    self.assertEqual([(r[7],) for r in rows], expected)
                    self.assertEqual([type(r[7]) for r in rows], [type(r[0]) for r in expected])
                    self.assertEqual(source, str(path))
                    self.assertGreater(len(rows), len(VALUES) + 1)
                    self.assertTrue(any(r[2] is None for r in rows))
                    self.assertIn(b'\x00\xff', [r[7] for r in rows])

    def test_missing_columns_remain_positional_null(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'groupme.db'
            create_store(path, missing=('read', 'deleted_at', 'deletion_actor')).close()
            _, rows, _ = self.parse(path)
            self.assertEqual(len(rows), len(VALUES) + 1)
            self.assertTrue(all(r[7] is None and r[8] is None and r[1] == '' for r in rows))
            self.assertTrue(all(r[9] == 'message' for r in rows))

    def test_committed_wal_update_and_duplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'groupme.db'
            db = create_store(path)
            try:
                db.execute('PRAGMA journal_mode=WAL')
                db.execute('PRAGMA wal_autocheckpoint=0')
                db.execute('UPDATE messages SET read="wal-only" WHERE created_at=1700000300')
                db.execute('INSERT INTO messages SELECT * FROM messages WHERE created_at=1700000300')
                db.commit()
                self.assertTrue(Path(str(path) + '-wal').is_file())
                _, rows, _ = self.parse(path)
                self.assertEqual(len(rows), len(VALUES) + 2)
                self.assertEqual([r[7] for r in rows].count('wal-only'), 2)
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
