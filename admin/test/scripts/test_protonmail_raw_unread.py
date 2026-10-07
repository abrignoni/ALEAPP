"""Actual SQLite unread values survive the MailX message projection."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest

from scripts.artifacts import protonmailDbMail as parser


FIELDS = ('time', 'subject', 'sender_address', 'sender_name', 'toList', 'ccList',
          'bccList', 'unread', 'isReplied', 'isForwarded', 'numAttachments', 'size',
          'conversationId', 'messageId')


def create(db, affinity=''):
    """Declare the actual fields queried by the artifact."""
    db.execute('CREATE TABLE MessageEntity (' + ', '.join(
        field + (' ' + affinity if field == 'unread' else '') for field in FIELDS) + ')')


def insert(db, flag):
    """Use a repeated message id and safe populated recipient fields."""
    db.execute('INSERT INTO MessageEntity VALUES (' + ','.join('?' for _ in FIELDS) + ')',
               (1700000000, 'subject', 'from@example.org', 'From', '[]', '[]', '[]',
                flag, 0, 1, 0, 10, 'conversation', 'repeated'))


def context(paths, root):
    """Give the artifact real files and evidence-relative paths."""
    return SimpleNamespace(get_files_found=lambda: paths,
                           get_relative_path=lambda p: str(Path(p).relative_to(root)))


class RawUnreadTest(unittest.TestCase):
    """Do not infer Read from NULL, zero or unknown stored values."""

    def test_sqlite_affinity_and_repeated_occurrences(self):
        values = [None, 0, 1, -1, 5, 0.0, 0.5, '', '0', '1', 'unknown', b'', b'\x00\xff']
        for affinity in ['', 'INTEGER', 'TEXT']:
            with self.subTest(affinity=affinity), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                path = root / 'db-mail'
                with sqlite3.connect(path) as db:
                    create(db, affinity)
                    for flag in values:
                        insert(db, flag)
                    insert(db, values[1])
                    expected = db.execute('SELECT unread, typeof(unread) FROM MessageEntity').fetchall()
                headers, rows, source = parser.protonmailDbMailMessages.__wrapped__(
                    context([str(path), str(path)], root))
                self.assertEqual(len(headers), 14)
                self.assertEqual(headers[6], 'unread (as stored)')
                self.assertEqual([(type(r[6]), r[6]) for r in rows],
                                 [(type(v), v) for v, _ in expected] * 2)
                self.assertEqual([r[12] for r in rows], ['repeated'] * len(rows))
                self.assertEqual([r[13] for r in rows], ['db-mail'] * len(rows))
                self.assertEqual(source, 'db-mail')

    def test_schema_in_live_wal(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'writer'
            live = sqlite3.connect(path)
            try:
                live.execute('CREATE TABLE unrelated(x)')
                live.commit()
                live.execute('PRAGMA journal_mode=WAL')
                live.execute('PRAGMA wal_autocheckpoint=0')
                create(live)
                insert(live, None)
                insert(live, '0')
                live.commit()
                copy = root / 'copy'
                copy.mkdir()
                for suffix in ['', '-wal', '-shm']:
                    shutil.copyfile(str(path) + suffix, str(copy / 'db-mail') + suffix)
                _, rows, source = parser.protonmailDbMailMessages.__wrapped__(
                    context([str(copy / 'db-mail')], copy))
                self.assertEqual([r[6] for r in rows], [None, '0'])
                self.assertEqual(source, 'db-mail')
                with sqlite3.connect(path.as_uri() + '?immutable=1', uri=True) as main:
                    self.assertEqual(main.execute(
                        "SELECT name FROM sqlite_master WHERE name='MessageEntity'").fetchall(), [])
            finally:
                live.close()

    def test_user_and_alias_files_are_not_deduplicated(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = []
            for user, value in [('data/data', None), ('data/user/0', 0), ('data/user/10', 5)]:
                path = root / user / 'ch.protonmail.android/databases/db-mail'
                path.parent.mkdir(parents=True)
                with sqlite3.connect(path) as db:
                    create(db)
                    insert(db, value)
                paths.append(str(path))
            _, rows, source = parser.protonmailDbMailMessages.__wrapped__(context(paths, root))
            self.assertEqual([r[6] for r in rows], [None, 0, 5])
            self.assertEqual([r[13] for r in rows], [str(Path(p).relative_to(root)) for p in paths])
            self.assertEqual(source, ', '.join(r[13] for r in rows))


if __name__ == '__main__':
    unittest.main()
