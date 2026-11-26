"""Every Firefox recently_closed_tabs store is read and named, each row names its Android user,
and a created_at of 0 is not shown as 1970. All values here are made up."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import firefoxRecentlyClosedTabs as firefox

STORE = 'org.mozilla.firefox/databases/recently_closed_tabs'


def run(stores):
    with tempfile.TemporaryDirectory() as folder:
        root = pathlib.Path(folder)
        files = []
        for relative, created in stores:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE recently_closed_tabs (uuid TEXT, title TEXT, url TEXT, created_at INTEGER NOT NULL)')
            db.execute('INSERT INTO recently_closed_tabs VALUES (?, ?, ?, ?)', (relative, 'Title', 'https://example.com/', created))
            db.commit()
            db.close()
            files.append(str(path))
        context = SimpleNamespace(get_files_found=lambda: files,
                                  get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))
        headers, rows, source = firefox.get_firefoxRecentlyClosedTabs.__wrapped__(context)
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows], [p for p in source.split('\n') if p]


class Stores(unittest.TestCase):
    def test_every_user_store_is_read_and_named(self):
        rows, source = run([(f'data/user/0/{STORE}', 1700000000000), (f'data/user/10/{STORE}', 1700000000000)])
        self.assertEqual(sorted(r['Android User'] for r in rows), ['0', '10'])
        self.assertEqual(len(source), 2)

    def test_a_zero_time_is_blank(self):
        rows, _source = run([(f'data/data/{STORE}', 0)])
        self.assertEqual(rows[0]['Created At'], '')

    def test_a_time_keeps_its_milliseconds(self):
        rows, _source = run([(f'data/data/{STORE}', 1700000000123)])
        self.assertEqual(rows[0]['Created At'].isoformat(), '2023-11-14T22:13:20.123000+00:00')


if __name__ == '__main__':
    unittest.main()
