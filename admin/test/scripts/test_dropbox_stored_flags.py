"""Dropbox file flags retain SQLite values without inferred boolean labels."""
import ast
from pathlib import Path
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts.dropbox import dropbox_files  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import convert_unix_ts_to_utc  # pylint: disable=wrong-import-position

FLAGS = [None, 0, 1, -1, 2, '', '0', '1', 'false', 'unknown', 0.0, 1.0, -1.5,
         '<b>unknown</b>']
FLAG_INDICES = (8, 9, 11, 12)
RAW_HEADERS = ('is_dir (as stored)', 'is_favorite (as stored)',
               'read_only (as stored)', 'is_vault_folder (as stored)')


def query_text():
    tree = ast.parse(Path(sys.modules[dropbox_files.__module__].__file__).read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'dropbox_files')
    return next(n.value.value for n in function.body if isinstance(n, ast.Assign)
                and any(getattr(t, 'id', None) == 'query' for t in n.targets))


def make_database(root, name='one-db.db'):
    path = Path(root) / 'data/user/0/com.dropbox.android/databases' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE dropbox(server_modified_millis,modified_millis,local_modified,'
                'accessed_millis,_display_name,path,bytes,mime_type,is_dir,is_favorite,'
                'shared_folder_id,read_only,is_vault_folder,revision)')
    rows = []
    for i in range(len(FLAGS)):
        row = [1700000000123, 1700000001123, 1700000002123, 1700000003123,
               'name', '/path', 12, 'text/plain', None, None, 'shared', None, None, 'rev']
        for offset, index in enumerate(FLAG_INDICES):
            row[index] = FLAGS[(i + offset * 3) % len(FLAGS)]
        rows.append(tuple(row))
    rows.extend([rows[0], (None, 0, None, 0, '', '', 0, '', None, 0, None, '', -1, None)])
    con.executemany('INSERT INTO dropbox VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', rows)
    con.commit()
    assert con.execute('PRAGMA quick_check').fetchone()[0] == 'ok'
    con.close()
    return path, rows


class DropboxStoredFlagsTest(unittest.TestCase):
    def test_native_flags_dates_duplicates_and_other_cells(self):
        with tempfile.TemporaryDirectory() as root:
            path, inputs = make_database(root)
            headers, rows, source = dropbox_files.__wrapped__(
                SimpleNamespace(get_relative_path=str, get_files_found=lambda: [str(path)]))
            con = sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True)
            selected = con.execute(query_text()).fetchall()
            storage = con.execute('SELECT typeof(is_dir),typeof(is_favorite),'
                                  'typeof(read_only),typeof(is_vault_folder) FROM dropbox').fetchall()
            con.close()
            self.assertEqual(len(rows), len(inputs))
            self.assertEqual(len(headers), 15)
            self.assertEqual(source, str(path))
            self.assertEqual(headers[:4], (('Server Modified', 'datetime'), ('Modified', 'datetime'),
                                          ('Local Modified', 'datetime'), ('Accessed', 'datetime')))
            self.assertEqual(tuple(headers[i] for i in FLAG_INDICES), RAW_HEADERS)
            self.assertEqual(headers[-1], 'Source File')
            for actual, record in zip(rows, selected):
                expected = (tuple(convert_unix_ts_to_utc(v) if v else '' for v in record[:4]) + record[4:]
                            + (str(path),))
                self.assertEqual(actual, expected)
                for index in FLAG_INDICES:
                    self.assertIs(type(actual[index]), type(record[index]))
            self.assertEqual(len(rows) - len(set(rows)), 1)
            for index in range(4):
                self.assertEqual({row[index] for row in storage}, {'null', 'integer', 'real', 'text'})

    def test_every_main_database_is_read_and_named(self):
        with tempfile.TemporaryDirectory() as root:
            first, inputs = make_database(root)
            second, _ = make_database(root, 'two-db.db')
            sidecars = [str(first) + suffix for suffix in ('-wal', '-shm', '-journal')]
            for mains in ([first, second], [second, first]):
                headers, rows, source = dropbox_files.__wrapped__(
                    SimpleNamespace(get_relative_path=str, get_files_found=lambda mains=mains: sidecars + list(map(str, mains))))
                self.assertEqual(sorted(source.split('\n')), sorted(map(str, mains)))
                self.assertEqual(len(rows), 2 * len(inputs))
                self.assertEqual({row[-1] for row in rows}, set(map(str, mains)))
                self.assertEqual(headers[-1], 'Source File')
