"""Unit tests for the MMS joins of scripts/artifacts/contentQuery.py, on invented files."""
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

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


    def test_missing_join_columns_leave_the_relation_unknown(self):
        mms = self.write('mms.txt', MMS)
        addr = self.write('mms_addr.txt', 'Row: 0 _id=30, address=+15550100003, type=137\n')
        rows, _sources = self.rows('mms', mms, addr)
        self.assertIn('addresses unknown', rows[0]['Parse Note'])
        self.assertIn('msg_id', rows[0]['Parse Note'])
        self.assertNotIn(contentQuery.NOTE_NO_ADDRESS_ROWS, rows[0]['Parse Note'])
        mms = self.write('mms.txt', 'Row: 0 thread_id=5, date=1767243600, msg_box=1\n')
        addr = self.write('mms_addr.txt', ADDR)
        rows, _sources = self.rows('mms_addr', addr, mms)
        self.assertEqual(rows[0]['MMS Row'], '')
        self.assertIn('_id', rows[0]['Parse Note'])


class UnreadableFileTest(unittest.TestCase):
    """A file that cannot be opened is reported and does not stop the other folders."""

    def setUp(self):
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        good = os.path.join(self.folder.name, 'content_provider_A', 'call_log')
        bad = os.path.join(self.folder.name, 'content_provider_B', 'call_log')
        os.makedirs(good)
        # A folder where the file should be: opening it raises an OSError on every platform.
        os.makedirs(os.path.join(bad, 'call_log_calls.txt'))
        self.good = os.path.join(good, 'call_log_calls.txt')
        self.bad = os.path.join(bad, 'call_log_calls.txt')
        with open(self.good, 'w', encoding='utf-8') as handle:
            handle.write('Row: 0 _id=1, number=+15550100001, date=1767225600000, duration=4, type=1\n')
        self.context = StubContext(self.folder.name, [self.bad, self.good])

    def test_artifact_keeps_the_other_folders(self):
        _headers, rows, sources = contentQuery._read(self.context, 'call_log')  # pylint: disable=protected-access
        self.assertEqual(len(rows), 1)
        self.assertEqual(sorted(sources.split('\n')), sorted([self.bad, self.good]))

    def test_files_artifact_shows_the_file_as_unreadable(self):
        _headers, rows, _sources = contentQuery.content_query_files.__wrapped__(self.context)
        calls = [row for row in rows if row[2] == 'content://call_log/calls']
        self.assertEqual(sorted(row[4] for row in calls), sorted([reader.ROWS, reader.UNREADABLE]))
        unreadable = next(row for row in calls if row[4] == reader.UNREADABLE)
        self.assertTrue(unreadable[7].startswith('could not be read: '))
        self.assertNotIn(self.folder.name, unreadable[7])


class AlexPrfsTest(unittest.TestCase):
    """The extra/content_provider folder of an ALEX PRFS zip, with the .status.json beside each file."""

    def setUp(self):
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = os.path.join(self.folder.name, 'extra', 'content_provider')
        self.paths = []

    def write(self, name, text=None, status=None):
        base = os.path.join(self.root, *name.split('/'))
        os.makedirs(os.path.dirname(base), exist_ok=True)
        if text is not None:
            with open(base + '.txt', 'w', encoding='utf-8', newline='') as handle:
                handle.write(text)
            self.paths.append(base + '.txt')
        if status is not None:
            with open(base + '.status.json', 'w', encoding='utf-8', newline='') as handle:
                handle.write(status)
            self.paths.append(base + '.status.json')

    def files(self):
        headers, rows, sources = contentQuery.content_query_files.__wrapped__(StubContext(self.folder.name,
                                                                                        self.paths))
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        by_file = {row[3]: dict(zip(names, row)) for row in rows if row[3]}
        return names, by_file, [row for row in rows if not row[3]], sources.split('\n')

    def test_files_artifact(self):
        self.write('sms/sms', 'Row: 0 _id=12, address=+15550100001, body=Hi, date=1767225600000\n',
                   '{"uri": "content://sms", "status": "rows"}')
        self.write('call_log/call_log_calls', 'No result found.\n', '{"uri": "content://call_log/calls", '
                                                                    '"status": "empty"}')
        # ALEX's own parser finds no row when the first row-like line is not 'Row: 0'.
        self.write('mms/mms', 'Row: 1 note=x\nRow: 0 _id=7, thread_id=5, date=1767243600, msg_box=1\n',
                   '{"uri": "content://mms", "status": "error"}')
        self.write('mms/mms_addr', None, '{"uri": "content://mms/addr", "status": "empty"}')
        self.write('mms/mms_part', 'Row: 0 _id=40, mid=7, seq=0, ct=text/plain, text=Hi\n')
        self.write('com.android.contacts/com.android.contacts_contacts', 'Row: 0 _id=1, display_name=Ana\n',
                   'not json')
        self.write('sms/sms_inbox', 'Row: 0 _id=12, address=+15550100001, body=Hi\n',
                   '{"uri": "content://sms/inbox", "status": "rows"}')
        self.write('sms/sms_sent', None, '{"uri": "content://sms/sent", "status": "empty"}')
        names, by_file, no_file_name, sources = self.files()
        self.assertEqual(names[4:6], ['Status', 'Tool Status'])
        self.assertTrue(all(row['Layout'] == reader.ALEX_PRFS for row in by_file.values()))
        sms = by_file['sms/sms.txt']
        self.assertEqual((sms['Status'], sms['Tool Status'], sms['Rows'], sms['Detail']), (reader.ROWS, 'rows', 1, ''))
        self.assertEqual(sms['Folder'], 'extra/content_provider')
        calls = by_file['call_log/call_log_calls.txt']
        self.assertEqual((calls['Status'], calls['Tool Status'], calls['Detail']), (reader.NO_RESULT, 'empty', ''))
        mms = by_file['mms/mms.txt']
        self.assertEqual((mms['Status'], mms['Tool Status']), (reader.ROWS, 'error'))
        self.assertIn('ALEX wrote status error', mms['Detail'])
        addr = by_file['mms/mms_addr.txt']
        self.assertEqual((addr['Status'], addr['Tool Status'], addr['Read By']),
                         (reader.NO_FILE, 'empty', 'MMS Addresses (content query)'))
        self.assertEqual(addr['Detail'], 'the .status.json of this file is in this extraction but the file is not')
        part = by_file['mms/mms_part.txt']
        self.assertEqual((part['Tool Status'], part['Detail']), ('', 'no .status.json beside this file'))
        contacts = by_file['com.android.contacts/com.android.contacts_contacts.txt']
        self.assertEqual((contacts['Status'], contacts['Tool Status']), (reader.ROWS, ''))
        self.assertIn('not JSON', contacts['Detail'])
        media = by_file['media/media_external_file.txt']
        self.assertEqual((media['Status'], media['Tool Status']), (reader.NO_FILE, ''))
        self.assertIn('not in this extraction', media['Detail'])
        # A file no artifact reads takes its URI from the status file, and says so.
        inbox = by_file['sms/sms_inbox.txt']
        self.assertEqual((inbox['URI'], inbox['Tool Status'], inbox['Read By'], inbox['Detail']),
                         ('content://sms/inbox', 'rows', 'not read', contentQuery.NOTE_URI_FROM_STATUS))
        sent = by_file['sms/sms_sent.txt']
        self.assertEqual((sent['URI'], sent['Status'], sent['Tool Status'], sent['Read By']),
                         ('content://sms/sent', reader.NO_FILE, 'empty', 'not read'))
        self.assertIn(contentQuery.NOTE_URI_FROM_STATUS, sent['Detail'])
        # ALEX queries content://com.android.calendar/events in neither layout.
        self.assertEqual([row[2] for row in no_file_name], ['content://com.android.calendar/events'])
        self.assertEqual(sorted(sources), sorted(self.paths))

    def test_status_file_naming_another_uri_is_flagged(self):
        # The URI of a known file comes from its name; a status file that names another one is flagged.
        self.write('sms/sms', 'Row: 0 _id=12, body=Hi\n', '{"uri": "content://sms/inbox", "status": "rows"}')
        self.write('mms/mms_addr', None, '{"uri": "content://mms/part", "status": "empty"}')
        _names, by_file, _no_name, _sources = self.files()
        sms = by_file['sms/sms.txt']
        self.assertEqual((sms['URI'], sms['Tool Status']), ('content://sms', 'rows'))
        self.assertEqual(sms['Detail'], 'the status file names content://sms/inbox, not the URI of this file name')
        addr = by_file['mms/mms_addr.txt']
        self.assertEqual(addr['URI'], 'content://mms/addr')
        self.assertIn('the status file names content://mms/part, not the URI of this file name', addr['Detail'])

    def test_status_of_another_uri_is_not_compared_with_the_text(self):
        # A status file naming another URI describes another query: its status is shown as written
        # and the URI mismatch flagged, but it is not compared with this file's text.
        self.write('sms/sms', 'Row: 0 _id=12, body=Hi\n', '{"uri": "content://sms/inbox", "status": "empty"}')
        _names, by_file, _no_name, _sources = self.files()
        sms = by_file['sms/sms.txt']
        self.assertEqual((sms['URI'], sms['Status'], sms['Tool Status']), ('content://sms', reader.ROWS, 'empty'))
        self.assertEqual(sms['Detail'], 'the status file names content://sms/inbox, not the URI of this file name')

    def test_status_of_a_uri_that_is_not_text_is_not_compared_with_the_text(self):
        # A status file whose uri key holds no text cannot be tied to this query: its status is shown
        # as written, but not compared with the text, in Detail or in the log.
        for uri in ('7', '"content://\\udfff"'):
            with self.subTest(uri=uri):
                self.paths.clear()
                self.write('sms/sms', 'Row: 0 _id=12, body=Hi\n', '{"uri": %s, "status": "empty"}' % uri)
                with mock.patch.object(contentQuery, 'logfunc') as log:
                    _names, by_file, _no_name, _sources = self.files()
                sms = by_file['sms/sms.txt']
                self.assertEqual((sms['URI'], sms['Status'], sms['Tool Status']),
                                 ('content://sms', reader.ROWS, 'empty'))
                self.assertNotIn('ALEX wrote', sms['Detail'])
                self.assertIn(contentQuery.NOTE_STATUS_NOT_COMPARED, sms['Detail'])
                self.assertIn('status file holds a URI that is not', sms['Detail'])
                self.assertFalse([call for call in log.call_args_list if 'ALEX status' in str(call)])

    def test_nested_prfs_folder_keeps_its_own_status_files(self):
        # A PRFS folder inside another: each folder takes only the status files of its own files.
        self.write('call_log/call_log_calls', 'No result found.\n', '{"status": "empty"}')
        self.write('sms/x/extra/content_provider/sms/sms', 'Row: 0 _id=1, body=a\n', '{"status": "rows"}')
        _headers, rows, _sources = contentQuery.content_query_files.__wrapped__(StubContext(self.folder.name,
                                                                                          self.paths))
        inner = 'extra/content_provider/sms/x/extra/content_provider'
        by_folder_file = {(row[1], row[3]): row for row in rows if row[3]}
        self.assertEqual(by_folder_file[(inner, 'sms/sms.txt')][4:6], (reader.ROWS, 'rows'))
        self.assertEqual(by_folder_file[(inner, 'sms/sms.txt')][7], '')
        self.assertEqual(by_folder_file[('extra/content_provider', 'call_log/call_log_calls.txt')][5], 'empty')
        self.assertEqual([row for row in rows if row[1] == 'extra/content_provider' and 'x/extra' in row[3]], [])

    def test_status_file_that_cannot_be_read_stays_on_its_own_row(self):
        # A deeply nested status file: on any Python version its row says why it has no status,
        # and the other files keep theirs.
        self.write('sms/sms', 'Row: 0 _id=1, body=a\n', '[' * 100000 + ']' * 100000)
        self.write('call_log/call_log_calls', 'No result found.\n', '{"status": "empty"}')
        _names, by_file, _no_name, _sources = self.files()
        sms = by_file['sms/sms.txt']
        self.assertEqual((sms['Status'], sms['Tool Status']), (reader.ROWS, ''))
        self.assertTrue(sms['Detail'].startswith('status file '), sms['Detail'])
        calls = by_file['call_log/call_log_calls.txt']
        self.assertEqual((calls['Status'], calls['Tool Status'], calls['Detail']), (reader.NO_RESULT, 'empty', ''))

    def test_only_status_files(self):
        self.write('sms/sms', None, '{"uri": "content://sms", "status": "error"}')
        _names, by_file, _no_name, _sources = self.files()
        sms = by_file['sms/sms.txt']
        self.assertEqual((sms['Layout'], sms['Status'], sms['Tool Status']), (reader.ALEX_PRFS, reader.NO_FILE, 'error'))

    def test_data_artifacts_read_the_prfs_files(self):
        self.write('sms/sms', 'Row: 0 _id=12, address=+15550100001, body=Hi, date=1767225600000\n',
                   '{"uri": "content://sms", "status": "rows"}')
        self.write('mms/mms', 'Row: 0 _id=7, thread_id=5, date=1767243600, msg_box=1\n')
        txt = [path for path in self.paths if path.endswith('.txt')]
        _headers, rows, _sources = contentQuery._read(StubContext(self.folder.name, txt), 'sms')  # pylint: disable=protected-access
        self.assertEqual(len(rows), 1)
        _headers, rows, _sources = contentQuery._read(StubContext(self.folder.name, txt), 'mms')  # pylint: disable=protected-access
        self.assertIn(contentQuery.NOTE_ADDRESSES_ABSENT, rows[0][-3])  # Parse Note


if __name__ == '__main__':
    unittest.main()
