"""Every Digital Wellbeing app_usage store is read once, whatever storage paths it appears under, and
each row names its Android user. All values here are made up."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import wellbeing

STORE = 'com.google.android.apps.wellbeing/databases/app_usage'


def make_store(path, package):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE packages (_id INTEGER PRIMARY KEY, package_name TEXT)')
    db.execute('CREATE TABLE events (_id INTEGER PRIMARY KEY, timestamp INTEGER, type INTEGER, package_id INTEGER)')
    db.execute('CREATE TABLE components (_id INTEGER PRIMARY KEY, package_id INTEGER, component_name TEXT)')
    db.execute('CREATE TABLE component_events (_id INTEGER PRIMARY KEY, timestamp INTEGER, type INTEGER, component_id INTEGER)')
    db.execute('INSERT INTO packages VALUES (1, ?)', (package,))
    db.execute('INSERT INTO events VALUES (1, 1700000000000, 1, 1)')
    db.execute('INSERT INTO components VALUES (1, 1, ?)', (package + '.Main',))
    db.execute('INSERT INTO component_events VALUES (1, 1700000000000, 1, 1)')
    db.commit()
    db.close()


def run(artifact, relative_paths):
    with tempfile.TemporaryDirectory() as folder:
        root = pathlib.Path(folder)
        files = []
        for number, relative in enumerate(relative_paths):
            make_store(root / relative, f'com.example.app{number}')
            files.append(str(root / relative))
        context = SimpleNamespace(get_files_found=lambda: files,
                                  get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))
        headers, rows, source = getattr(wellbeing, artifact).__wrapped__(context)
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows], [p for p in source.split('\n') if p]


class Users(unittest.TestCase):
    def test_events_from_every_user_are_read(self):
        for artifact in ('get_wellbeing', 'get_wellbeing_url'):
            with self.subTest(artifact):
                rows, source = run(artifact, [f'data/user/0/{STORE}', f'data/user/10/{STORE}'])
                self.assertEqual(sorted(r['Android User'] for r in rows), ['0', '10'])
                self.assertEqual(len(source), 2)

    def test_storage_views_of_one_store_are_read_once(self):
        rows, source = run('get_wellbeing', [f'data/data/{STORE}', f'data/user/0/{STORE}'])
        self.assertEqual((len(rows), len(source)), (1, 1))


    def test_a_damaged_store_does_not_hide_the_others(self):
        for artifact in ('get_wellbeing', 'get_wellbeing_url'):
            with self.subTest(artifact):
                with tempfile.TemporaryDirectory() as folder:
                    root = pathlib.Path(folder)
                    good = root / f'data/user/0/{STORE}'
                    bad = root / f'data/user/10/{STORE}'
                    make_store(good, 'com.example.good')
                    bad.parent.mkdir(parents=True)
                    bad.write_bytes(b'SQLite format 3\x00' + b'\xff' * 4080)
                    files = [str(good), str(bad)]
                    context = SimpleNamespace(get_files_found=lambda f=files: f,
                                              get_relative_path=lambda p, r=root: str(pathlib.Path(p).relative_to(r)))
                    _headers, rows, _source = getattr(wellbeing, artifact).__wrapped__(context)
                self.assertEqual(len(rows), 1)


if __name__ == '__main__':
    unittest.main()
