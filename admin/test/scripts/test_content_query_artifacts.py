"""Unit tests for the MMS joins of scripts/artifacts/contentQuery.py, on invented files."""
import os
import pathlib
import sys
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import content_query_reader as reader  # pylint: disable=wrong-import-position
from scripts.artifacts import contentQuery  # pylint: disable=wrong-import-position

MMS = ('Row: 0 _id=7, thread_id=5, date=1767243600, msg_box=1\n'
       'Row: 1 _id=8, thread_id=5, date=1767247200, msg_box=2\n'
       'Row: 2 _id=, thread_id=5, date=1767250800, msg_box=2\n')
ADDR = ('Row: 0 _id=30, msg_id=7, address=+15550100003, type=137\n'
        'Row: 1 _id=31, msg_id=, address=+15550100004, type=151\n'
        'Row: 2 _id=32, msg_id=NULL, address=+15550100005, type=151\n')
ERROR = 'Error while accessing provider:mms\njava.lang.IllegalStateException: cursor closed\n'


class StubContext:
    def __init__(self, root, files):
        self.root = root
        self.files = files
        self.seeker = object()

    def get_files_found(self):
        return list(self.files)

    def get_relative_path(self, path):
        return os.path.relpath(path, self.root)

    def get_seeker(self):
        return self.seeker


class MmsJoinTest(unittest.TestCase):
    def setUp(self):
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.mms_dir = os.path.join(self.folder.name, 'content_provider_SYNTH', 'mms')
        os.makedirs(self.mms_dir)

    def write(self, name, text):
        path = os.path.join(self.mms_dir, name)
        with open(path, 'w', encoding='utf-8', newline='') as handle:
            handle.write(text)
        return path

    def rows(self, key, *paths):
        headers, rows, sources = contentQuery._read(StubContext(self.folder.name, paths), key)  # pylint: disable=protected-access
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        return [dict(zip(names, row)) for row in rows], sources.split('\n')

    def test_sources_name_the_sibling_read(self):
        mms, addr = self.write('mms.txt', MMS), self.write('mms_addr.txt', ADDR)
        rows, sources = self.rows('mms', mms, addr)
        self.assertEqual(sources, [mms, addr])
        self.assertTrue(all(row['Source File'].endswith('mms.txt') for row in rows))
        rows, sources = self.rows('mms_addr', addr, mms)
        self.assertEqual(sources, [addr, mms])
        self.assertTrue(all(row['Source File'].endswith('mms_addr.txt') for row in rows))

    def test_empty_and_null_keys_are_not_matched(self):
        mms, addr = self.write('mms.txt', MMS), self.write('mms_addr.txt', ADDR)
        rows, _sources = self.rows('mms', mms, addr)
        self.assertEqual(rows[0]['From'], '+15550100003')
        self.assertEqual(rows[1]['To'], '')
        self.assertEqual(rows[1]['Parse Note'], contentQuery.NOTE_NO_ADDRESS_ROWS)
        self.assertEqual(rows[2]['To'], '')
        self.assertEqual(rows[2]['Parse Note'], contentQuery.NOTE_NO_MMS_KEY)
        rows, _sources = self.rows('mms_addr', addr, mms)
        self.assertEqual([row['MMS Row'] for row in rows], ['yes', '', ''])
        self.assertEqual(rows[1]['Parse Note'], contentQuery.NOTE_NO_ADDR_KEY)
        self.assertEqual(rows[2]['Parse Note'], contentQuery.NOTE_NO_ADDR_KEY)

    def test_incomplete_address_list_makes_unmatched_messages_unknown(self):
        mms = self.write('mms.txt', MMS)
        addr = self.write('mms_addr.txt', ADDR.split('Row: 1 ')[0] + ERROR)
        rows, _sources = self.rows('mms', mms, addr)
        self.assertEqual(rows[0]['From'], '+15550100003')
        self.assertIn('addresses may be partial', rows[0]['Parse Note'])
        self.assertIn('incomplete (1 row, then provider error', rows[0]['Parse Note'])
        self.assertIn('addresses unknown', rows[1]['Parse Note'])
        self.assertIn('incomplete (1 row, then provider error', rows[1]['Parse Note'])

    def test_complete_address_list_adds_no_partial_note(self):
        mms = self.write('mms.txt', MMS)
        addr = self.write('mms_addr.txt', ADDR)
        rows, _sources = self.rows('mms', mms, addr)
        self.assertNotIn('partial', rows[0]['Parse Note'])

    def test_unreadable_or_error_address_file_makes_messages_unknown(self):
        mms = self.write('mms.txt', MMS)
        for text in ('', 'some text\n', ERROR):
            addr = self.write('mms_addr.txt', text)
            reader.clear_cache()
            rows, _sources = self.rows('mms', mms, addr)
            self.assertIn('addresses unknown', rows[0]['Parse Note'], text)
            self.assertNotIn(contentQuery.NOTE_NO_ADDRESS_ROWS, rows[0]['Parse Note'])

    def test_no_result_address_file_is_a_full_empty_list(self):
        mms, addr = self.write('mms.txt', MMS), self.write('mms_addr.txt', 'No result found.\n')
        rows, _sources = self.rows('mms', mms, addr)
        self.assertEqual(rows[0]['Parse Note'], contentQuery.NOTE_NO_ADDRESS_ROWS)

    def test_incomplete_mms_list_leaves_mms_row_unknown(self):
        mms = self.write('mms.txt', MMS.split('Row: 1 ')[0] + ERROR)
        addr = self.write('mms_addr.txt', 'Row: 0 _id=30, msg_id=7, address=a, type=137\n'
                                          'Row: 1 _id=31, msg_id=8, address=b, type=137\n')
        rows, _sources = self.rows('mms_addr', addr, mms)
        self.assertEqual([row['MMS Row'] for row in rows], ['yes', ''])
        self.assertIn('mms.txt is incomplete', rows[1]['Parse Note'])


if __name__ == '__main__':
    unittest.main()
