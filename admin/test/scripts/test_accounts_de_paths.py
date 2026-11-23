"""The mirrored storage view is skipped by its evidence path, never by the name of the examiner's folder."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import accounts_de


def build(path):
    path.parent.mkdir(parents=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE accounts (_id INTEGER PRIMARY KEY, name TEXT, type TEXT, last_password_entry_time_millis_epoch INTEGER)')
    con.execute('CREATE TABLE debug_table (_id INTEGER, action_type TEXT, time TEXT, caller_uid INTEGER, table_name TEXT)')
    con.execute("INSERT INTO accounts VALUES (1, 'n', 't', 1700000000000)")
    con.execute("INSERT INTO debug_table VALUES (1, 'action', '2023-11-14 22:13:20', 1000, 'accounts')")
    con.commit()
    con.close()


def rows_for(report_folder, evidence_paths):
    with tempfile.TemporaryDirectory() as folder:
        root = pathlib.Path(folder) / report_folder / 'data'
        files = []
        for relative in evidence_paths:
            path = root / relative
            build(path)
            files.append(str(path))
        context = SimpleNamespace(get_files_found=lambda: files,
                                  get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))
        _headers, rows, _source = accounts_de.accounts_de.__wrapped__(context)
    return rows


class Paths(unittest.TestCase):
    LIVE = 'data/system_de/0/accounts_de.db'

    def test_plain_output_folder(self):
        self.assertEqual(len(rows_for('report', [self.LIVE])), 1)

    def test_output_folder_named_mirror_is_still_read(self):
        self.assertEqual(len(rows_for('mirror case', [self.LIVE])), 1)

    def test_archive_root_named_mirror_is_still_read(self):
        self.assertEqual(len(rows_for('report', ['mirror_export/data/system_de/0/accounts_de.db'])), 1)

    def test_mirrored_view_in_the_evidence_is_skipped(self):
        self.assertEqual(len(rows_for('report', [self.LIVE, 'data_mirror/data_de/null/system_de/0/accounts_de.db'])), 1)


if __name__ == '__main__':
    unittest.main()
