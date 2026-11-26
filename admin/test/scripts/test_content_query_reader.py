"""Unit tests for scripts/content_query_reader.py, on invented content query text."""
import os
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import content_query_reader as reader  # pylint: disable=wrong-import-position

SMS = ('Row: 0 _id=12, address=+15550100001, body=See you at 8, date=1767225600000\n'
       'Row: 1 _id=13, address=+15550100001, body=First line\n'
       'second line\n'
       '\n'
       'Row: 7 of the list, date=1767229200000\n'
       'Row: 2 _id=14, address=+15550100002, body=Order 77 confirmed, total=40 USD, date=1767232800000\n')


def values(dump):
    return [dict(record.pairs) for record in dump.records]


class ParseRowsTest(unittest.TestCase):
    def test_rows_and_multi_line_values(self):
        dump = reader.parse_text(SMS)
        self.assertEqual(dump.status, reader.ROWS)
        self.assertEqual(dump.columns, ('_id', 'address', 'body', 'date'))
        self.assertEqual([record.line for record in dump.records], [1, 2, 6])
        rows = values(dump)
        self.assertEqual(rows[1]['body'], 'First line\nsecond line\n\nRow: 7 of the list')
        self.assertEqual(rows[1]['date'], '1767229200000')
        self.assertEqual(rows[2]['body'], 'Order 77 confirmed, total=40 USD')
        self.assertEqual([record.note for record in dump.records], ['', '', ''])

    def test_crlf_reads_like_lf(self):
        self.assertEqual(reader.parse_text(SMS.replace('\n', '\r\n')), reader.parse_text(SMS))

    def test_value_holding_next_column_name_is_flagged(self):
        dump = reader.parse_text('Row: 0 _id=1, body=a, seen=b, seen=1\nRow: 1 _id=2, body=c, seen=0\n')
        self.assertEqual(dump.columns, ('_id', 'body', 'seen'))
        self.assertIn('", seen="', dump.records[0].note)
        self.assertEqual(dump.records[1].note, '')

    def test_null_blob_and_empty_are_kept_as_printed(self):
        dump = reader.parse_text('Row: 0 _id=1, a=NULL, b=BLOB, c=, d=x\n')
        self.assertEqual(values(dump), [{'_id': '1', 'a': 'NULL', 'b': 'BLOB', 'c': '', 'd': 'x'}])

    def test_value_ending_with_a_line_break(self):
        dump = reader.parse_text('Row: 0 _id=1, hash_id=aGFzaDE=\n\nRow: 1 _id=2, hash_id=aGFzaDI=\n\n')
        self.assertEqual([row['hash_id'] for row in values(dump)], ['aGFzaDE=\n', 'aGFzaDI=\n'])

    def test_row_line_out_of_sequence_is_a_value_line(self):
        dump = reader.parse_text('Row: 0 _id=1, body=one\nRow: 0 _id=9, body=two\nRow: 1 _id=2, body=three\n')
        self.assertEqual(len(dump.records), 2)
        self.assertEqual(values(dump)[0]['body'], 'one\nRow: 0 _id=9, body=two')

    def test_row_not_holding_the_columns_is_not_split(self):
        dump = reader.parse_text('Row: 0 _id=1, a=x, b=y\nRow: 1 _id=2, a=x, b=y\nRow: 2 _id=3, b=y\n')
        self.assertEqual(dump.records[2].pairs, [])
        self.assertIn('not split', dump.records[2].note)
        self.assertTrue(any('not split' in warning for warning in dump.warnings))

    def test_repeated_column_name_is_not_split(self):
        dump = reader.parse_text('Row: 0 _id=1, body=the form says, seen=yes, seen=1\n')
        self.assertEqual(dump.columns, ('_id', 'body', 'seen', 'seen'))
        self.assertEqual(dump.records[0].pairs, [])
        self.assertIn('more than once', dump.records[0].note)
        self.assertIn('_id=1, body=the form says, seen=yes, seen=1', dump.records[0].note)
        self.assertEqual(reader.Values(dump.records[0])['absent'], '')

    def test_repeated_name_in_one_row_of_many_is_flagged_not_learned(self):
        dump = reader.parse_text('Row: 0 _id=1, body=the form says, seen=yes, seen=1\n'
                                 'Row: 1 _id=2, body=b, seen=0\nRow: 2 _id=3, body=c, seen=1\n')
        self.assertEqual(dump.columns, ('_id', 'body', 'seen'))
        self.assertIn('", seen="', dump.records[0].note)

    def test_row_lines_inside_a_value_do_not_outvote_the_first_column(self):
        dump = reader.parse_text('Row: 0 _id=1, body=quoted:\nRow: 1 example=x\nRow: 2 example=y, seen=1\n')
        self.assertEqual(dump.status, reader.ROWS)
        self.assertEqual(len(dump.records), 1)
        self.assertEqual(values(dump)[0]['body'], 'quoted:\nRow: 1 example=x\nRow: 2 example=y')

    def test_row_like_line_before_the_rows_does_not_set_the_first_column(self):
        dump = reader.parse_text('Row: 0 example=x\nRow: 0 _id=1, body=a\nRow: 1 _id=2, body=b\n')
        self.assertEqual(dump.columns, ('_id', 'body'))
        self.assertEqual([row['_id'] for row in values(dump)], ['1', '2'])
        self.assertTrue(any('before the first row' in warning for warning in dump.warnings))

    def test_single_row_with_row_lines_in_its_value_keeps_the_first_row_zero(self):
        dump = reader.parse_text('Row: 0 _id=1, body=quoted:\nRow: 0 example=x\nRow: 1 example=y\n')
        self.assertEqual(dump.columns, ('_id', 'body'))
        self.assertEqual(values(dump)[0]['body'], 'quoted:\nRow: 0 example=x\nRow: 1 example=y')

    def test_quoted_sequence_does_not_replace_rows_with_an_unsplit_one(self):
        dump = reader.parse_text('Row: 0 _id=1, body=a, seen=1\nRow: 1 _id=2, body=b, seen=0\n'
                                 'Row: 2 _id=3, body=quoted:\nRow: 0 example=x\nRow: 1 example=y\n')
        self.assertEqual(dump.columns, ('_id', 'body', 'seen'))
        self.assertEqual(len(dump.records), 3)
        self.assertEqual([record.number for record in dump.records], [0, 1, 2])

    def test_large_dump_with_a_quoted_row_zero_is_read(self):
        # The second reading makes the whole text one row of many names; the repeated-name check
        # over that list was quadratic and did not finish on a dump of this size.
        lines = [f'Row: {n} _id={n}, _data=/x/IMG_{n}.jpg, mime_type=image/jpeg' for n in range(20000)]
        lines[5] += '\nRow: 0 quoted=x'
        dump = reader.parse_text('\n'.join(lines) + '\n')
        self.assertEqual(len(dump.records), 20000)
        self.assertEqual(dump.columns[0], '_id')

    def test_delimiter_at_the_start_of_a_value_is_flagged(self):
        dump = reader.parse_text('Row: 0 _id=1, body=, seen=yes, read=1, seen=1\n'
                                 'Row: 1 _id=2, body=b, read=0, seen=0\nRow: 2 _id=3, body=c, read=1, seen=1\n')
        self.assertEqual(dump.columns, ('_id', 'body', 'read', 'seen'))
        self.assertEqual(values(dump)[0]['body'], ', seen=yes')
        self.assertIn('", seen="', dump.records[0].note)
        plain = reader.parse_text('Row: 0 _id=1, body=seen=yes, seen=1\n')
        self.assertEqual(plain.records[0].note, '')

    def test_text_before_first_row_is_reported(self):
        dump = reader.parse_text('WARNING: linker: something\nRow: 0 _id=1\n')
        self.assertEqual(len(dump.records), 1)
        self.assertTrue(dump.warnings)


class ParseStatusTest(unittest.TestCase):
    def test_no_result(self):
        self.assertEqual(reader.parse_text('No result found.\n').status, reader.NO_RESULT)
        self.assertEqual(reader.parse_text('No result found.\r\n').status, reader.NO_RESULT)

    def test_empty(self):
        self.assertEqual(reader.parse_text('').status, reader.EMPTY_FILE)
        self.assertEqual(reader.parse_text('\r\n\n').status, reader.EMPTY_FILE)

    def test_security_exception_is_access_denied(self):
        dump = reader.parse_text('Error while accessing provider:call_log\n'
                                 'java.lang.SecurityException: Permission Denial: requires READ_CALL_LOG\n'
                                 '\tat android.os.Parcel.createExceptionOrNull(Parcel.java:3011)\n')
        self.assertEqual(dump.status, reader.ACCESS_DENIED)
        self.assertIn('java.lang.SecurityException: Permission Denial', dump.detail)

    def test_other_exception_is_provider_error(self):
        dump = reader.parse_text('Error while accessing provider:mms\n'
                                 'java.lang.IllegalArgumentException: Unknown URL content://mms/addr\n')
        self.assertEqual(dump.status, reader.PROVIDER_ERROR)
        self.assertIn('IllegalArgumentException', dump.detail)

    def test_security_exception_subclass_name_is_not_access_denied(self):
        dump = reader.parse_text('Error while accessing provider:x\n'
                                 'android.example.NotASecurityException: no\n')
        self.assertEqual(dump.status, reader.PROVIDER_ERROR)

    def test_error_without_exception_line(self):
        dump = reader.parse_text('Error while accessing provider:x\n')
        self.assertEqual(dump.status, reader.PROVIDER_ERROR)

    def test_unrecognised_text(self):
        dump = reader.parse_text('/system/bin/sh: content: not found\n')
        self.assertEqual(dump.status, reader.UNRECOGNISED)
        self.assertEqual(dump.detail, '/system/bin/sh: content: not found')

    def test_rows_then_error(self):
        dump = reader.parse_text('Row: 0 _id=1, a=x\nRow: 1 _id=2, a=y\n'
                                 'Error while accessing provider:media\n'
                                 'java.lang.IllegalStateException: Couldn\'t read row 2\n')
        self.assertEqual(dump.status, reader.ROWS)
        self.assertEqual(values(dump)[1]['a'], 'y')
        self.assertIn('then provider error', dump.detail)
        self.assertIn('could also be the end of the last value', dump.records[1].note)
        self.assertEqual(dump.records[0].note, '')

    def test_error_lines_inside_last_value_with_columns_after_them_are_kept(self):
        dump = reader.parse_text('Row: 0 _id=1, body=line one\nError while accessing provider:sms\n'
                                 'java.lang.SecurityException: fake text, read=1\n')
        self.assertEqual(dump.detail, '')
        self.assertEqual(values(dump)[0]['read'], '1')
        self.assertEqual(values(dump)[0]['body'],
                         'line one\nError while accessing provider:sms\njava.lang.SecurityException: fake text')

    def test_error_text_inside_a_value_is_kept(self):
        dump = reader.parse_text('Row: 0 _id=1, body=it said\nError while accessing provider:x\n'
                                 'that was the message, a=1\n')
        self.assertEqual(dump.status, reader.ROWS)
        self.assertEqual(dump.detail, '')
        self.assertEqual(values(dump)[0]['body'], 'it said\nError while accessing provider:x\nthat was the message')


class ReadFileTest(unittest.TestCase):
    def setUp(self):
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)

    def test_cache_is_scoped_to_one_run(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'sms.txt')
            with open(path, 'wb') as handle:
                handle.write(b'Row: 0 _id=1, body=aaaa\n')
            first_run, second_run = object(), object()
            self.assertEqual(values(reader.read_file(path, first_run))[0]['body'], 'aaaa')
            with open(path, 'wb') as handle:
                handle.write(b'Row: 0 _id=1, body=bbbb\n')
            # Same path and byte length: the same run keeps what it read, a new run reads the file again.
            self.assertEqual(values(reader.read_file(path, first_run))[0]['body'], 'aaaa')
            self.assertEqual(values(reader.read_file(path, second_run))[0]['body'], 'bbbb')
            self.assertEqual(values(reader.read_file(path))[0]['body'], 'bbbb')

    def test_bom_and_bytes_that_are_not_utf8(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, 'sms.txt')
            with open(path, 'wb') as handle:
                handle.write(b'\xef\xbb\xbfRow: 0 _id=1, body=caf\xe9\n')
            dump = reader.read_file(path)
        self.assertEqual(values(dump), [{'_id': '1', 'body': 'caf\ufffd'}])
        self.assertTrue(any('UTF-8' in warning for warning in dump.warnings))


class LayoutTest(unittest.TestCase):
    TRIAGE = 'root/a1b2c3d4e5f60718/20261125_10_15_30_contentprovider'
    ALEX = 'root/x/content_provider_SYNTH0001'

    def test_triage_files(self):
        self.assertEqual(reader.layout_of(f'{self.TRIAGE}/calendar_events.txt'), (reader.TRIAGE, self.TRIAGE))
        self.assertEqual(reader.uri_of(reader.TRIAGE, f'{self.TRIAGE}/calendar_events.txt').key, 'calendar_events')
        self.assertIsNone(reader.layout_of(f'{self.TRIAGE}/20261125_10_15_30_contentprovider.txt'))
        self.assertIsNone(reader.layout_of(f'{self.TRIAGE}/content_providers_list.txt'))
        self.assertIsNone(reader.layout_of('root/my_contentprovider/calendar_events.txt'))

    def test_alex_files(self):
        path = f'{self.ALEX}/com.android.contacts/com.android.contacts_data_phones.txt'
        self.assertEqual(reader.layout_of(path), (reader.ALEX, self.ALEX))
        self.assertEqual(reader.uri_of(reader.ALEX, path).key, 'contact_phones')
        self.assertEqual(reader.uri_of(reader.ALEX, f'{self.ALEX}/sms/sms.txt').key, 'sms')
        self.assertEqual(reader.uri_of(reader.ALEX, f'{self.ALEX}/mms/mms_addr.txt').key, 'mms_addr')
        self.assertIsNone(reader.uri_of(reader.ALEX, f'{self.ALEX}/sms/sms_inbox.txt'))
        self.assertIsNone(reader.layout_of(f'{self.ALEX}/sms/other.txt'))
        self.assertIsNone(reader.layout_of('root/x/other/sms/sms.txt'))

    def test_windows_separators(self):
        path = '\\\\?\\C:\\case\\a1b2c3d4e5f60718\\20261125_10_15_30_contentprovider\\media_external_file.txt'
        layout, _folder = reader.layout_of(path)
        self.assertEqual(reader.uri_of(layout, path).key, 'media_files')


class TimeTest(unittest.TestCase):
    def test_units(self):
        moment = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(reader.epoch_to_utc('1767225600000', 'ms'), (moment, ''))
        self.assertEqual(reader.epoch_to_utc('1767225600', 's'), (moment, ''))

    def test_unset_and_bad_values(self):
        for text in ('', 'NULL', '0'):
            self.assertEqual(reader.epoch_to_utc(text, 'ms'), ('', ''))
        self.assertIn('not an integer', reader.epoch_to_utc('12a', 'ms')[1])
        self.assertIn('out of range', reader.epoch_to_utc('9' * 30, 's')[1])
        # More digits than Python's default int conversion limit (4,300) must not raise.
        self.assertIn('out of range', reader.epoch_to_utc('9' * 5000, 'ms')[1])
        self.assertIn('out of range', reader.epoch_to_utc('-' + '9' * 5000, 's')[1])


if __name__ == '__main__':
    unittest.main()
