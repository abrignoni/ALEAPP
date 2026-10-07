"""Actual SQLite scalar, affinity, join and WAL observations for Nova."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from scripts.artifacts import novaLauncher as parser

VALUES = [None, 0, 1, -1, 5, 0.0, 0.5, '', '0', '1', 'unknown', b'', b'\x00\xff']


def populate(db, affinity=''):
    """Produce typed stores, repeated assignments and ambiguous join NULLs."""
    db.executescript('''
        CREATE TABLE appgroups (modified, groupId, component, _id);
        CREATE TABLE favorites (modified,title,container,screen,cellX,cellY,
                                spanX,spanY,itemType,intent,_id);
    ''')
    db.execute('CREATE TABLE drawer_groups (_id,title,groupType,hideApps '
               + affinity + ',tabOrder)')
    for index, value in enumerate(VALUES):
        db.execute('INSERT INTO drawer_groups VALUES (?,?,?,?,?)',
                   (index, 'group', 0, value, 0 if index % 2 else None))
        db.execute('INSERT INTO appgroups VALUES (?,?,?,?)',
                   (1700000000123, index, 'pkg/activity', index))
    db.execute('INSERT INTO appgroups SELECT * FROM appgroups WHERE _id=1')
    db.execute('INSERT INTO drawer_groups SELECT * FROM drawer_groups WHERE _id=1')
    db.executemany('INSERT INTO appgroups VALUES (?,?,?,?)',
                   [(0, 999, None, 90), (None, None, '', 91)])
    db.executemany('INSERT INTO favorites VALUES (?,?,?,?,?,?,?,?,?,?,?)', [
        (1700000000123, 'home', -100, 0, 0, 0, 1, 1, 0, 'component=pkg/Main;', 1),
        (0, None, -101, 0, 0, 0, 1, 1, 0, None, 2),
        (0, 'not selected', None, 0, 0, 0, 1, 1, 0, None, 3)])
    db.commit()


def context(root, paths):
    """Actual evidence-relative paths, not mocked database rows."""
    return SimpleNamespace(get_files_found=lambda: list(map(str, paths)),
                           get_relative_path=lambda p: str(Path(p).relative_to(root)))


class NovaRawHideAppsTest(unittest.TestCase):
    """All SQLite classes survive projection after actual affinity and LEFT JOIN."""

    def test_affinity_raw_null_repeats_and_other_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for affinity in ['', 'INTEGER', 'TEXT']:
                with self.subTest(affinity=affinity):
                    main = root / (affinity or 'NONE') / 'databases/nova.db'
                    main.parent.mkdir(parents=True)
                    with sqlite3.connect(main) as db:
                        populate(db, affinity)
                        expected = db.execute('SELECT a._id,g.hideApps FROM appgroups a '
                                              'LEFT JOIN drawer_groups g ON g._id=a.groupId '
                                              'ORDER BY a.groupId,a._id').fetchall()
                    heads, rows, source = parser.nova_drawer_groups.__wrapped__(
                        context(root, [main]))
                    self.assertEqual(len(heads), 9)
                    self.assertEqual([(r[7], r[5]) for r in rows], expected)
                    self.assertEqual([type(r[5]) for r in rows], [type(v) for _, v in expected])
                    self.assertEqual(source, str(main))
                    self.assertEqual(len(rows), 18)
                    self.assertTrue(all(r[8] == str(main.relative_to(root)) for r in rows))
                    self.assertEqual(len(parser.nova_layout.__wrapped__(context(root, [main]))[1]), 2)

    def test_wal_alias_preference_and_empty_cursor_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            main = root / 'data/data/com.teslacoilsw.launcher/databases/nova.db'
            main.parent.mkdir(parents=True)
            writer = sqlite3.connect(main)
            try:
                writer.execute('PRAGMA journal_mode=WAL')
                writer.execute('PRAGMA wal_autocheckpoint=0')
                populate(writer)
                writer.execute('PRAGMA wal_checkpoint(TRUNCATE)')
                writer.execute('UPDATE drawer_groups SET hideApps=? WHERE _id=2', (b'wal',))
                writer.commit()
                working = root / 'working'
                working.mkdir()
                for suffix in ['', '-wal', '-shm']:
                    shutil.copyfile(str(main) + suffix, working / ('nova.db' + suffix))
                with sqlite3.connect(working / 'nova.db') as db:
                    self.assertEqual(db.execute('SELECT hideApps FROM drawer_groups WHERE _id=2').fetchone(), (b'wal',))
                with sqlite3.connect('file:' + str(main) + '?immutable=1', uri=True) as db:
                    self.assertEqual(db.execute('SELECT hideApps FROM drawer_groups WHERE _id=2').fetchone(), (1,))
                alias = root / 'data/user/0/com.teslacoilsw.launcher/databases/nova.db'
                alias.parent.mkdir(parents=True)
                with sqlite3.connect(alias) as db:
                    populate(db)
                    db.execute('DELETE FROM appgroups')
                ctx = context(root, [alias, main])
                self.assertEqual(parser._db_files(ctx), [str(main)])  # pylint: disable=protected-access
                self.assertEqual(parser.nova_drawer_groups.__wrapped__(context(root, [alias]))[1:],
                                 ([], str(alias)))
            finally:
                writer.close()


if __name__ == '__main__':
    unittest.main()
