"""Independent search stores preserve local rows and actual WAL states."""
import pathlib
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.Twitter import get_Twitter, open_sqlite_db_readonly

SQL = 'CREATE TABLE search_queries(time,name,query,query_id,user_search_suggestion,topic_search_suggestion,latitude,longitude,radius,location,priority,score)'


def make_database(path, label='first', empty=False, bad=False):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE unrelated(value)' if bad else SQL)
    if not empty and not bad:
        con.executemany('INSERT INTO search_queries VALUES(1700000000123,?,?,1,NULL,0,1.5,2.5,0,NULL,1,0.25)', [(label, 'same query')] * 2)
    con.commit()
    con.close()
    return path


class TwitterSourcesTest(unittest.TestCase):
    def test_sources_aliases_users_prefixes_and_schema_diagnostics(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            first = make_database(root / 'data/data/com.twitter.android/databases/1-search.db')
            alias = root / 'data/user/0/com.twitter.android/databases/1-search.db'
            alias.parent.mkdir(parents=True)
            shutil.copy2(first, alias)
            second = make_database(root / 'data/user/10/com.twitter.android/databases/1-search.db', 'user10')
            third = make_database(root / 'OtherRoot/data/data/com.twitter.android/databases/1-search.db', 'prefix')
            bad = make_database(root / 'bad/2-search.db', bad=True)
            with patch('scripts.artifacts.Twitter.logfunc') as log:
                headers, rows, sources = get_Twitter.__wrapped__(context(folder, [first, alias, second, third, bad]))
            self.assertEqual(len(rows), 6)
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual(len(sources.splitlines()), 3)
            for row in rows:
                label = 'user10' if '/10/' in row[-1] else 'prefix' if row[-1].startswith('OtherRoot') else 'first'
                self.assertEqual(row[1], label)
                self.assertEqual(row[2:6], ('same query', 1, None, 0))
            self.assertTrue(any('unsupported search schema' in call.args[0] for call in log.call_args_list))

    def test_actual_conflicting_wal_states(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            live = make_database(root / 'live', empty=True)
            con = sqlite3.connect(live)
            con.execute('PRAGMA journal_mode=WAL')
            con.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            paths = []
            for user, label in [('data/data', 'one'), ('data/user/0', 'two')]:
                con.execute('INSERT INTO search_queries VALUES(0,?,NULL,1,0,0,NULL,NULL,NULL,NULL,0,0)', (label,))
                con.commit()
                target = root / user / 'com.twitter.android/databases/1-search.db'
                target.parent.mkdir(parents=True, exist_ok=True)
                for suffix in ['', '-wal', '-shm']:
                    shutil.copy2(str(live) + suffix, str(target) + suffix)
                paths.append(target)
            con.close()
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())
            headers, rows, sources = get_Twitter.__wrapped__(context(folder, paths))
            self.assertEqual(len(rows), 3)
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual(len(sources.splitlines()), 2)
            self.assertEqual([row[1] for row in rows], ['one', 'one', 'two'])

    def test_single_yielded_source_empty_and_unavailable_continue(self):
        with tempfile.TemporaryDirectory() as folder:
            empty = make_database(pathlib.Path(folder) / 'empty/1-search.db', empty=True)
            good = make_database(pathlib.Path(folder) / 'good/1-search.db')
            def opener(path):
                return None if path == str(empty) else open_sqlite_db_readonly(path)
            with patch('scripts.artifacts.Twitter.open_sqlite_db_readonly', side_effect=opener), patch('scripts.artifacts.Twitter.logfunc'):
                headers, rows, sources = get_Twitter.__wrapped__(context(folder, [empty, good]))
            self.assertEqual(len(rows), 2)
            self.assertNotIn('Source File', headers)
            self.assertEqual(sources, str(good))
            headers, rows, sources = get_Twitter.__wrapped__(context(folder, [empty]))
            self.assertEqual((rows, sources), ([], ''))
            self.assertNotIn('Source File', headers)
