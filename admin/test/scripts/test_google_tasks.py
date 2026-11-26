"""Google Tasks reads the shared data.db from each known Google package's files/tasks folder.

The store sits at files/tasks/<folder>/data.db or files/tasks-<folder>/data.db. These tests
pin the path globs against both layouts and the five packages, the segment match that keeps
a decoy package and a nested folder out, the collapse of the data/data and data/user/0
spellings of one store, a second Android user kept apart, a store whose tables are only in
its -wal, and the column decode, including a task with no field 2.2.
"""
import fnmatch
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import blackboxprotobuf  # pylint: disable=wrong-import-position
from scripts.artifacts.googleTasks import __artifacts_v2__, get_googleTasks  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

PACKAGES = ('com.google.android.apps.tasks', 'com.google.android.gm', 'com.google.android.calendar',
            'com.google.android.apps.dynamite', 'com.google.android.keep')
TASK = {
    '2': {'3': b'Task title'},
    '3': {'1': 1700000001, '2': 500000000},
    '9': {'1': {'4': b'Europe/Lisbon', '6': {'1': 1700003600}}},
    '11': {'1': 1700000000, '2': 0},
}
DONE_TASK = {
    '2': {'2': b'Done title', '3': b'Done details', '5': {'1': 1700000500, '2': 0}},
    '3': {'1': 1700000600, '2': 0},
    '11': {'1': 1700000000, '2': 0},
}
TASK_LIST = {'2': {'1': b'List A'}}
SCHEMA = ('CREATE TABLE Tasks (TaskId TEXT, TaskListId TEXT, DueDate TEXT, Completed INTEGER, '
          'EffectiveTask BLOB, ShardId TEXT)',
          'CREATE TABLE TaskLists (ShardId TEXT, TaskListIdWithoutShard TEXT, EffectiveTaskList BLOB)')


def _typedef(message):
    typedef = {}
    for key, value in message.items():
        if isinstance(value, dict):
            typedef[key] = {'type': 'message', 'name': '', 'message_typedef': _typedef(value)}
        elif isinstance(value, bytes):
            typedef[key] = {'type': 'bytes', 'name': ''}
        else:
            typedef[key] = {'type': 'int', 'name': ''}
    return typedef


def _blob(message):
    return blackboxprotobuf.encode_message(message, _typedef(message))


class TestGoogleTasks(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.data = pathlib.Path(self.tmpdir) / 'data'
        Context.clear()
        Context.set_report_folder(self.tmpdir)
        Context.set_data_folder(str(self.data))

    def tearDown(self):
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _store(self, relative, tasks=((TASK, 0),)):
        db_path = self.data / relative
        db_path.parent.mkdir(parents=True)
        db = sqlite3.connect(db_path)
        for statement in SCHEMA:
            db.execute(statement)
        for number, (message, completed) in enumerate(tasks):
            db.execute('INSERT INTO Tasks VALUES (?, "L1", "2023-11-14", ?, ?, "u:")',
                       (f'u:T{number}', completed, _blob(message)))
        db.execute('INSERT INTO TaskLists VALUES ("u:", "L1", ?)', (_blob(TASK_LIST),))
        db.commit()
        db.close()
        return str(db_path)

    def _run(self, files):
        Context.set_files_found(files)
        headers, rows, source = get_googleTasks.__wrapped__(Context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        return names, [dict(zip(names, row)) for row in rows], source

    def _selected(self):
        globs = __artifacts_v2__['get_googleTasks']['paths']
        return [str(found) for found in sorted(self.data.rglob('*'))
                if found.is_file() and any(fnmatch.fnmatch(str(found), g) for g in globs)]

    def test_paths_match_both_layouts_in_every_package(self):
        globs = __artifacts_v2__['get_googleTasks']['paths']
        for package in PACKAGES:
            for layout in ('files/tasks/123/data.db', 'files/tasks-123/data.db', 'files/tasks-123/data.db-wal'):
                path = f'/root/data/data/{package}/{layout}'
                self.assertTrue(any(fnmatch.fnmatch(path, g) for g in globs), path)
        decoy = '/root/data/data/com.example.decoy/files/tasks/123/data.db'
        self.assertFalse(any(fnmatch.fnmatch(decoy, g) for g in globs))

    def test_packages_users_and_spellings(self):
        self._store('data/data/com.google.android.gm/files/tasks/111/data.db',
                    tasks=((TASK, 0), (DONE_TASK, 1)))
        self._store('data/user/0/com.google.android.gm/files/tasks/111/data.db',
                    tasks=((TASK, 0), (DONE_TASK, 1)))
        self._store('data/user/10/com.google.android.gm/files/tasks/111/data.db')
        self._store('data/data/com.google.android.calendar/files/tasks/uuid-1/data.db')
        self._store('data/data/com.google.android.apps.dynamite/files/tasks-222/data.db')
        self._store('data/data/com.google.android.gm/files/tasks/111/nested/data.db', tasks=((TASK, 0),) * 3)
        self._store('data/data/com.example.decoy/files/tasks/111/data.db', tasks=((TASK, 0),) * 5)
        files = self._selected() + [str(self.data / 'data/data/com.example.decoy/files/tasks/111/data.db')]
        _names, rows, source = self._run(files)
        found = sorted((r['App'], r['Android User'], r['Store Folder']) for r in rows)
        self.assertEqual(found, [
            ('com.google.android.apps.dynamite', '0', 'tasks-222'),
            ('com.google.android.calendar', '0', 'uuid-1'),
            ('com.google.android.gm', '0', '111'),
            ('com.google.android.gm', '0', '111'),
            ('com.google.android.gm', '10', '111'),
        ])
        self.assertEqual(len(source.split('\n')), 4)
        self.assertNotIn('decoy', source)
        self.assertNotIn('nested', source)
        self.assertNotIn('data/user/0/', source)

    def test_columns(self):
        _names, rows, _source = self._run(
            [self._store('data/data/com.google.android.gm/files/tasks/111/data.db',
                         tasks=((TASK, 0), (DONE_TASK, 1)))])
        open_row, done_row = rows
        self.assertEqual(str(open_row['Time (field 11)']), '2023-11-14 22:13:20+00:00')
        self.assertEqual(str(open_row['Time (field 3)']), '2023-11-14 22:13:21.500000+00:00')
        self.assertEqual(open_row['Time (field 2.5)'], '')
        self.assertEqual(str(open_row['Time (field 9.1.6.1)']), '2023-11-14 23:13:20+00:00')
        self.assertEqual(open_row['Zone (field 9.1.4)'], 'Europe/Lisbon')
        self.assertEqual(open_row['Text (field 2.2)'], '')
        self.assertEqual(open_row['Text (field 2.3)'], 'Task title')
        self.assertEqual(open_row['Task List Text (field 2.1)'], 'List A')
        self.assertEqual(open_row['Completed'], 'No')
        self.assertEqual(open_row['Due Date (as stored)'], '2023-11-14')
        self.assertEqual(open_row['Store Folder'], '111')
        self.assertEqual(done_row['Completed'], 'Yes')
        self.assertEqual(str(done_row['Time (field 2.5)']), '2023-11-14 22:21:40+00:00')
        self.assertEqual(done_row['Text (field 2.2)'], 'Done title')
        self.assertEqual(done_row['Time (field 9.1.6.1)'], '')

    def test_store_without_tasks_table_is_skipped(self):
        db_path = self.data / 'data/data/com.google.android.keep/files/tasks/1/data.db'
        db_path.parent.mkdir(parents=True)
        db = sqlite3.connect(db_path)
        db.execute('CREATE TABLE Other (x)')
        db.commit()
        db.close()
        _names, rows, source = self._run([str(db_path)])
        self.assertEqual(rows, [])
        self.assertEqual(source, '')

    def _wal_only_store(self):
        """A Gmail store whose tables and rows exist only in its -wal."""
        db_path = self.data / 'data/data/com.google.android.gm/files/tasks/111/data.db'
        db_path.parent.mkdir(parents=True)
        build = pathlib.Path(self.tmpdir) / 'build' / 'data.db'
        build.parent.mkdir()
        db = sqlite3.connect(build)
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
        db.execute(SCHEMA[0])
        db.execute('INSERT INTO Tasks VALUES ("u:T0", "L1", "", 0, ?, "u:")', (_blob(TASK),))
        db.commit()
        # Copy while the connection is open: closing it would checkpoint the log into the file.
        for suffix in ('', '-wal'):
            shutil.copyfile(f'{build}{suffix}', f'{db_path}{suffix}')
        db.close()
        return db_path

    def test_wal_only_store_is_read_through_declared_paths(self):
        db_path = self._wal_only_store()
        bare = sqlite3.connect(f'{db_path.as_uri()}?immutable=1', uri=True)
        tables = bare.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        bare.close()
        self.assertEqual(tables, [], 'fixture must keep its tables out of the main file')
        selected = self._selected()
        self.assertIn(f'{db_path}-wal', selected)
        _names, rows, _source = self._run(selected)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Text (field 2.3)'], 'Task title')

    def test_wal_only_store_reads_empty_without_its_wal(self):
        """Control: the store above yields nothing when its -wal is not collected."""
        db_path = self._wal_only_store()
        pathlib.Path(f'{db_path}-wal').unlink()
        _names, rows, _source = self._run(self._selected())
        self.assertEqual(rows, [])


if __name__ == '__main__':
    unittest.main()
