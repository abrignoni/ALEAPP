"""Distinct Proton Drive databases retain rows, mappings and source identity."""
import pathlib
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.ProtonDrive import protondrive_useraccount, protondrive_fileinfo

PARSERS = [protondrive_useraccount, protondrive_fileinfo]

def make_database(path, user='fixture-user', empty=False):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE UserEntity(userId,email,name,createdAtUTC,usedspace,Maxspace)')
    con.execute('CREATE TABLE LinkEntity(id,share_id,user_id,parent_id,type,name,state,creation_time,last_modified,trashed_time,size,mime_type,is_shared,number_of_accesses)')
    if not empty:
        con.executemany('INSERT INTO UserEntity VALUES(?,?,?,?,?,?)', [(user, 'fixture@example.invalid', 'User', 1700000000000, 2097152, 4194304)] * 2)
        for record in [(1, 'share', user, 'parent', 2, 'File', 1, 1700000000, 1700000001, None, 10, 'type', 0, 1)] * 2 + [(2, 'share', user, None, 77, 'Unknown', 88, 0, None, -1, 0, None, 9, None)]:
            con.execute('INSERT INTO LinkEntity VALUES(' + ','.join('?' * 14) + ')', record)
    con.commit()
    con.close()
    return path

def make_multisource(root):
    root = pathlib.Path(root)
    first = make_database(root / 'data/data/me.proton.android.drive/databases/db-drive')
    mirror = root / 'data/user/0/me.proton.android.drive/databases/db-drive'
    mirror.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(first, mirror)
    second = make_database(root / 'data/user/10/me.proton.android.drive/databases/db-drive', 'user10')
    third = make_database(root / 'OtherRoot/data/data/me.proton.android.drive/databases/db-drive', 'prefix-user')
    return [first, mirror, second, third]

class ProtonDriveSourcesTest(unittest.TestCase):
    def test_all_sources_aliases_types_duplicates_and_origin(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = make_multisource(folder)
            for parser, count, user_header in zip(PARSERS, [6, 9], ['User ID', 'Stored User ID']):
                headers, rows, sources = parser.__wrapped__(context(folder, paths))
                self.assertEqual(len(rows), count)
                self.assertEqual(headers[-1], 'Source File')
                self.assertEqual(len(sources.splitlines()), 3)
                for row in rows:
                    expected = 'user10' if '/10/' in row[-1] else 'prefix-user' if row[-1].startswith('OtherRoot') else 'fixture-user'
                    self.assertEqual(row[headers.index(user_header)], expected)
                self.assertEqual(rows[0], rows[1])
                if parser is protondrive_fileinfo:
                    self.assertEqual(rows[2][headers.index('Type')], 77)
                    self.assertEqual(rows[2][headers.index('State')], 88)
                    self.assertEqual(rows[2][headers.index('Is Shared')], 9)
                    self.assertEqual(headers[:3], (('Creation Time', 'datetime'), ('Last Modified', 'datetime'), ('Trashed Time', 'datetime')))

    def test_actual_wal_conflicts_and_complete_alias(self):
        with tempfile.TemporaryDirectory() as folder:
            live = make_database(pathlib.Path(folder) / 'live', empty=True)
            con = sqlite3.connect(live)
            con.execute('PRAGMA journal_mode=WAL')
            con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            paths = []
            for userpath, user in [('data/data', 'one'), ('data/user/0', 'two')]:
                con.execute('INSERT INTO UserEntity VALUES(?,?,?,?,?,?)', (user, 'email', 'User', 1700000000000, 0, 0))
                con.execute('INSERT INTO LinkEntity(id,user_id,type,state) VALUES(1,?,2,1)', (user,))
                con.commit()
                target = pathlib.Path(folder) / userpath / 'me.proton.android.drive/databases/db-drive'
                target.parent.mkdir(parents=True, exist_ok=True)
                for suffix in ['', '-wal', '-shm']:
                    shutil.copy2(str(live) + suffix, str(target) + suffix)
                paths.append(target)
            con.close()
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())
            for parser in PARSERS:
                _, rows, sources = parser.__wrapped__(context(folder, paths))
                self.assertEqual(len(rows), 3)
                self.assertEqual(len(sources.splitlines()), 2)
                self.assertEqual(len({row[-1] for row in rows}), 2)

    def test_invalid_header_sidecar_and_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            bad = root / 'bad/db-drive'
            bad.parent.mkdir()
            bad.write_bytes(b'not SQLite')
            main = make_database(root / 'good/db-drive')
            for parser in PARSERS:
                with patch('scripts.artifacts.ProtonDrive.logfunc') as log:
                    _, rows, _ = parser.__wrapped__(context(folder, [bad, main]))
                self.assertTrue(rows)
                self.assertTrue(any('invalid SQLite header' in call.args[0] for call in log.call_args_list))
                headers, rows, source = parser.__wrapped__(context(folder, [str(main) + '-wal']))
                self.assertNotIn('Source File', headers)
                self.assertEqual(rows, [])
                self.assertEqual(source, '')
