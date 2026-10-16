"""Exercise stored clipboard flags with actual SQLite storage and WAL states."""
import itertools
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts.artifacts import gboard


def context(root):
    return SimpleNamespace(
        get_files_found=lambda: [str(p) for p in root.rglob('*') if p.is_file()],
        get_relative_path=lambda p: str(Path(p).relative_to(root)))


class TestGboardStoredTypes(unittest.TestCase):
    def check_types(self, affinity):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root/'data/data/com.google.android.inputmethod.latin/databases/gboard_clipboard.db'
            path.parent.mkdir(parents=True)
            db = sqlite3.connect(path)
            try:
                db.execute('CREATE TABLE clips(timestamp,text,html_text,uri,item_type '+affinity+
                           ',entity_type '+affinity+',_id)')
                values = [None, 0, 1, 5, -1, 0.0, 1.0, 1.5, '', '0', '1', 'unknown',
                          b'', b'1', b'\x00\xff', 0, 1]
                for i, value in enumerate(values):
                    db.execute('INSERT INTO clips VALUES(?,?,?,?,?,?,?)',
                               (1700000000000, 'text', '<b>text</b>', '', value, values[-i-1], i))
                db.commit()
                expected = db.execute('SELECT item_type,entity_type,_id FROM clips').fetchall()
                headers, rows, source = gboard.get_gboardCache.__wrapped__(context(root))
                self.assertEqual([r[5:] for r in rows], expected)
                self.assertEqual(len(headers), 8)
                self.assertEqual(headers[5:7], ('item_type (as stored)', 'entity_type (as stored)'))
                self.assertEqual(source, str(path))
                self.assertEqual({type(v) for row in expected for v in row[:2]},
                                 {type(None), int, float, str, bytes})
            finally:
                db.close()

    def test_no_affinity_types(self):
        self.check_types('')

    def test_integer_affinity_types(self):
        self.check_types('INTEGER')

    def test_alias_selection_and_last_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = []
            for index, prefix in enumerate(['data/data', 'data/user/0', 'data/user/10']):
                path = root/prefix/'com.google.android.inputmethod.latin/databases/gboard_clipboard.db'
                path.parent.mkdir(parents=True)
                db = sqlite3.connect(path)
                try:
                    db.execute('CREATE TABLE clips(timestamp,text,html_text,uri,item_type,entity_type,_id)')
                    db.execute("INSERT INTO clips VALUES(1700000000000,'text','','',?,?,?)",
                               (index, index + 5, index))
                    db.commit()
                finally:
                    db.close()
                paths.append(str(path))
            for permutation in itertools.permutations(paths):
                ctx = SimpleNamespace(get_files_found=lambda selected=permutation: selected,
                                      get_relative_path=lambda p: str(Path(p).relative_to(root)))
                selected = gboard.unique_files(ctx)
                headers, rows, source = gboard.get_gboardCache.__wrapped__(ctx)
                expected = []
                for path in selected:
                    db = sqlite3.connect(path)
                    try:
                        expected.extend(db.execute('SELECT item_type,entity_type,_id FROM clips'))
                    finally:
                        db.close()
                self.assertEqual([r[5:] for r in rows], expected)
                self.assertEqual(source, selected[-1])
                self.assertEqual(len(headers), 8)

    def test_committed_wal_is_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root/'gboard_clipboard.db'
            db = sqlite3.connect(path)
            try:
                db.execute('CREATE TABLE clips(timestamp,text,html_text,uri,item_type,entity_type,_id)')
                db.execute("INSERT INTO clips VALUES(1700000000000,'text','','',0,1,1)")
                db.commit()
                db.execute('PRAGMA journal_mode=WAL')
                db.execute('PRAGMA wal_autocheckpoint=0')
                db.execute('UPDATE clips SET item_type=5,entity_type=NULL')
                db.execute('INSERT INTO clips SELECT * FROM clips')
                db.commit()
                rows = gboard.get_gboardCache.__wrapped__(context(root))[1]
                self.assertEqual([r[5:] for r in rows], [(5, None, 1), (5, None, 1)])
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
