"""Contacts remain database-local while admitted main occurrences are retained."""
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from scripts.artifacts import telegramAndroid


class TestTelegramContactsSources(unittest.TestCase):
    def make(self, root, relative, name='A', empty=False, wal=False, missing=None):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        if wal:
            connection.execute('pragma journal_mode=wal')
            connection.execute('pragma wal_autocheckpoint=0')
        if missing != 'phones':
            connection.execute('create table user_phones_v7(key,phone,deleted)')
        if missing != 'contacts':
            connection.execute('create table user_contacts_v7(key,uid,fname,sname,imported)')
        connection.commit()
        if wal:
            connection.execute('pragma wal_checkpoint(truncate)')
        if not empty:
            if missing != 'phones':
                connection.executemany('insert into user_phones_v7 values(?,?,?)',
                                       [('key', name, 0), ('key', name, None), ('key', 'hidden', '0')])
            if missing != 'contacts':
                connection.executemany('insert into user_contacts_v7 values(?,?,?,?,?)',
                                       [('key', b'\xff', name, 0, None)] * 2)
            connection.commit()
        return path, connection

    def parse(self, root, paths, same_origin=False):
        context = SimpleNamespace(
            get_files_found=lambda: [str(p) for p in paths],
            get_relative_path=lambda p: ('data/user/0/org.telegram.messenger/files/cache4.db'
                                         if same_origin else str(Path(p).relative_to(root))),
        )
        return telegramAndroid.get_telegramContacts.__wrapped__(context)

    def test_local_lookup_repeats_and_contributor_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first, c1 = self.make(root, 'data/user/0/org.telegram.messenger/files/cache4.db', 'one')
            second, c2 = self.make(root, 'data/user/0/org.telegram.messenger/files/account1/cache4.db', 'two')
            c1.close()
            c2.close()
            headers, rows, sources = self.parse(root, [second, first, second])
            self.assertEqual(len(headers), 7)
            self.assertEqual([r[3] for r in rows], ['two, two'] * 2 + ['one, one'] * 2 + ['two, two'] * 2)
            self.assertEqual([r[0] for r in rows], [b'\xff'] * 6)
            self.assertEqual(sources, str(second) + '\n' + str(first))
            self.assertEqual([r[-1] for r in rows], [str(second.relative_to(root))] * 2 +
                             [str(first.relative_to(root))] * 2 + [str(second.relative_to(root))] * 2)
            headers, rows, _ = self.parse(root, [first, first])
            self.assertEqual((len(headers), len(rows)), (6, 4))
            headers, rows, _ = self.parse(root, [first, second], same_origin=True)
            self.assertEqual((len(headers), len(rows)), (6, 4))

    def test_exact_bounded_paths_and_empty_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = []
            for account in ['account0', 'account4', 'account01', 'deep']:
                path, c = self.make(root, f'data/user/0/org.telegram.messenger/files/{account}/cache4.db')
                c.close()
                paths.append(path)
            path, c = self.make(root, 'data/user/0/org.telegram.messenger/deeper/files/cache4.db')
            c.close()
            paths.append(path)
            self.assertEqual(self.parse(root, paths)[1:], ([], ''))
            for account in ['account1', 'account2', 'account3']:
                path, c = self.make(root, f'data/user/10/org.telegram.messenger.beta/files/{account}/cache4.db')
                c.close()
                self.assertEqual(len(self.parse(root, [path])[1]), 2)
            path, c = self.make(root, 'data/user/0/org.telegram.messenger/files/cache4.db', empty=True)
            c.close()
            headers, rows, source = self.parse(root, [path])
            self.assertEqual((len(headers), rows, source), (6, [], ''))

    def test_committed_wal_and_missing_table_continue(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path, writer = self.make(root, 'data/user/0/org.telegram.messenger/files/cache4.db', wal=True)
            self.assertTrue(Path(str(path) + '-wal').stat().st_size)
            immutable = sqlite3.connect(path.as_uri() + '?immutable=1', uri=True)
            self.assertEqual(immutable.execute('select count(*) from user_contacts_v7').fetchone()[0], 0)
            immutable.close()
            self.assertEqual(len(self.parse(root, [Path(str(path) + '-wal'), path])[1]), 2)
            no_contacts, c = self.make(root, 'data/user/0/org.telegram.messenger/files/account1/cache4.db', missing='contacts')
            c.close()
            no_phones, c = self.make(root, 'data/user/0/org.telegram.messenger/files/account2/cache4.db', missing='phones')
            c.close()
            headers, rows, sources = self.parse(root, [no_contacts, no_phones, path])
            self.assertEqual((len(headers), len(rows)), (7, 4))
            self.assertEqual([r[3] for r in rows], ['', '', 'A, A', 'A, A'])
            self.assertNotIn(str(no_contacts), sources)
            writer.close()


if __name__ == '__main__':
    unittest.main()
