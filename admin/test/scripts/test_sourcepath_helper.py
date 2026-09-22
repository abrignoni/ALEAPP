"""get_results_with_extra_sourcepath_if_needed must not publish the staged path.

When more than one store matches, the helper appends a 'Source Path' column to every
row. That value is a data row value and is written verbatim to the HTML, TSV and LAVA
outputs, so it has to be reduced to the evidence relative path where it enters the row.
The third return element is the one the wrapper normalizes, and it has to be real
paths, newline joined, not prose.
"""
import os
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, REPO_ROOT)

from scripts.context import Context  # noqa: E402  pylint: disable=wrong-import-position
from scripts.ilapfuncs import get_results_with_extra_sourcepath_if_needed  # noqa: E402  pylint: disable=wrong-import-position


def _make_db(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE t (v TEXT)')
    con.execute('INSERT INTO t VALUES (?)', (value,))
    con.commit()
    con.close()


class SourcePathHelperTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_folder = os.path.join(self.tmp.name, 'report', 'data')
        Context.set_data_folder(self.data_folder)
        self.paths = [
            os.path.join(self.data_folder, 'data', 'system_ce', '0', 'accounts_ce.db'),
            os.path.join(self.data_folder, 'data', 'system_ce', '10', 'accounts_ce.db'),
        ]
        _make_db(self.paths[0], 'user0')
        _make_db(self.paths[1], 'user10')

    def tearDown(self):
        Context.clear()
        self.tmp.cleanup()

    def test_multiple_stores_reduce_the_source_path_column(self):
        headers, rows, _source_path = get_results_with_extra_sourcepath_if_needed(
            self.paths, 'SELECT v FROM t', ('Value',))
        self.assertEqual(headers[-1], 'Source Path')
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertNotIn(self.data_folder, row[-1], 'staged prefix reached the row')
            self.assertFalse(os.path.isabs(row[-1]), 'row value is still an absolute path')
        self.assertEqual({r[-1] for r in rows},
                         {'data/system_ce/0/accounts_ce.db', 'data/system_ce/10/accounts_ce.db'})

    def test_multiple_stores_return_real_paths_not_prose(self):
        _headers, _rows, source_path = get_results_with_extra_sourcepath_if_needed(
            self.paths, 'SELECT v FROM t', ('Value',))
        self.assertEqual(source_path.split('\n'), self.paths)

    def test_single_store_keeps_the_shape(self):
        headers, rows, source_path = get_results_with_extra_sourcepath_if_needed(
            self.paths[:1], 'SELECT v FROM t', ('Value',))
        self.assertEqual(headers, ('Value',))
        self.assertEqual(rows, [('user0',)])
        self.assertEqual(source_path, self.paths[0])


if __name__ == '__main__':
    unittest.main()
