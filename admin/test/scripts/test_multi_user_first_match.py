"""Artifacts that read one database per Android user, built on a synthetic two-user tree.

The Secure Folder user's copy (user 150) sorts before the owner's, and holds fewer rows, which is
the shape that made first-match artifacts return the wrong user's data.
"""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import frosting, googleCalendar, settingsSearch, smyfilesRecents  # pylint: disable=wrong-import-position
from scripts.artifacts.storagePathViews import android_user, user_files  # pylint: disable=wrong-import-position


def make_db(path, statements):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    for statement in statements:
        db.execute(statement)
    db.commit()
    db.close()
    return path


def frosting_db(path, packages):
    make_db(path, ['create table frosting (pk text, apk_path text, last_updated integer)'] +
            [f"insert into frosting values ('{p}', '/data/app/{p}/base.apk', 1700000000000)" for p in packages])


def calendar_db(path, titles):
    make_db(path, [
        'create table Calendars (_id integer, cal_sync8 text, name text, calendar_displayName text, '
        'account_name text, account_type text, visible integer, calendar_location text, '
        'calendar_timezone text, ownerAccount text, isPrimary integer, calendar_color integer, '
        'calendar_color_index text)',
        "insert into Calendars values (1, '1700000000000', 'n', 'Display', 'a@example.test', 'com.google', "
        "1, '', 'UTC', 'a@example.test', 1, 0, '')",
        'create table Events (dtstart integer, dtend integer, eventTimezone text, title text, '
        'description text, eventLocation text, _sync_id text, organizer text, calendar_id integer, '
        'allDay integer, hasAlarm integer)'] +
        [f"insert into Events values (1700000000000, 1700003600000, 'UTC', '{t}', '', '', '', '', 1, 0, 0)"
         for t in titles])


def search_db(path, queries):
    make_db(path, ['create table saved_queries (timestamp integer, query text)'] +
            [f"insert into saved_queries values (1700000000000, '{q}')" for q in queries])


def myfiles_db(path, names):
    make_db(path, ['create table recent_files (date_modified integer, name text, size integer, _data text, '
                   'ext text, _source text, _description text, recent_date integer)'] +
            [f"insert into recent_files values (1700000000000, '{n}', 1, '/x/{n}', 'txt', '', '', "
             "1700000000000)" for n in names])


def context(root, paths):
    root = pathlib.Path(root)
    return SimpleNamespace(
        get_files_found=lambda: [str(path) for path in paths],
        get_relative_path=lambda path: str(pathlib.Path(path).relative_to(root)))


class MultiUserFirstMatchTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = pathlib.Path(self.folder.name)

    def tree(self, relative, build, owner, secure):
        """Owner (user 0, with its data/user/0 mirror) and a user 150 copy listed first."""
        paths = [self.root / 'data/user/150' / relative, self.root / 'data/data' / relative,
                 self.root / 'data/user/0' / relative]
        build(paths[0], secure)
        build(paths[1], owner)
        build(paths[2], owner)
        return paths

    def run_artifact(self, module, function, paths):
        with patch.object(module, 'logfunc', create=True):
            return getattr(module, function).__wrapped__(context(self.root, paths))

    def test_android_user(self):
        self.assertEqual(android_user('data/data/p/databases/a.db'), '0')
        self.assertEqual(android_user('data/user/150/p/databases/a.db'), '150')
        self.assertEqual(android_user('data/user_de/10/p/databases/a.db'), '10')
        self.assertEqual(android_user('userdata/user/7/p/databases/a.db'), '7')
        self.assertEqual(android_user('data_mirror/data_ce/null/11/p/databases/a.db'), '11')
        self.assertEqual(android_user('sdcard/DCIM/a.db'), '')

    def test_user_files_keeps_each_user_once_and_skips_sidecars(self):
        paths = self.tree('p/databases/a.db', lambda path, _: make_db(path, ['create table t (a)']), 0, 0)
        paths.append(self.root / 'data/data/p/databases/a.db-wal')
        paths.append(self.root / 'data/data/p/databases/b.db')
        found = user_files(context(self.root, paths), 'a.db')
        self.assertEqual([user for _, user in found], ['150', '0'])
        self.assertTrue(all(path.endswith('a.db') for path, _ in found))

    def test_frosting(self):
        paths = self.tree('com.android.vending/databases/frosting.db', frosting_db,
                          ['own.one', 'own.two', 'own.three'], ['secure.one'])
        headers, rows, source = self.run_artifact(frosting, 'frosting', paths)
        self.assertEqual(headers[-1], 'Android User')
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        self.assertEqual(sorted((row[1], row[3]) for row in rows),
                         [('own.one', '0'), ('own.three', '0'), ('own.two', '0'), ('secure.one', '150')])
        self.assertEqual(len(source.splitlines()), 2)

    def test_calendar_events_and_calendars(self):
        paths = self.tree('com.android.providers.calendar/databases/calendar.db', calendar_db,
                          ['own a', 'own b', 'own c'], [])
        headers, rows, _ = self.run_artifact(googleCalendar, 'get_calendar', paths)
        self.assertEqual(headers[-1], 'Android User')
        self.assertEqual(sorted((row[3], row[-1]) for row in rows),
                         [('own a', '0'), ('own b', '0'), ('own c', '0')])
        headers, rows, source = self.run_artifact(googleCalendar, 'get_calendar_calendars', paths)
        self.assertEqual(headers[-1], 'Android User')
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        self.assertEqual(sorted(row[-1] for row in rows), ['0', '150'])
        self.assertEqual(len(source.splitlines()), 2)

    def test_settings_search(self):
        paths = self.tree('com.android.settings.intelligence/databases/search_index.db', search_db,
                          ['wifi', 'battery'], [])
        headers, rows, _ = self.run_artifact(settingsSearch, 'get_settingsSearch', paths)
        self.assertEqual(headers[-1], 'Android User')
        self.assertEqual(sorted((row[1], row[2]) for row in rows), [('battery', '0'), ('wifi', '0')])

    def test_my_files_recent(self):
        paths = self.tree('com.sec.android.app.myfiles/databases/myfiles.db', myfiles_db,
                          ['own1.txt', 'own2.txt'], ['secure.txt'])
        headers, rows, _ = self.run_artifact(smyfilesRecents, 'get_smyfilesRecents', paths)
        self.assertEqual(headers[-1], 'Android User')
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        self.assertEqual(sorted((row[1], row[-1]) for row in rows),
                         [('own1.txt', '0'), ('own2.txt', '0'), ('secure.txt', '150')])


if __name__ == '__main__':
    unittest.main()
