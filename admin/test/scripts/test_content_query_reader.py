"""Unit tests for scripts/content_query_reader.py, on invented content query text."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
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


# Ranks the 'Row: 0' names of the text on stdin with its own tracemalloc session, so a trace
# already running in the test process (PYTHONTRACEMALLOC=1) is neither counted nor stopped.
RANKING_PEAK = """
import json, sys, tracemalloc
sys.path.insert(0, sys.argv[1])
from scripts import content_query_reader as reader
candidates = reader._candidates(reader._lines(sys.stdin.buffer.read().decode('utf-8')))
if tracemalloc.is_tracing():
    sys.exit('tracemalloc was already tracing')
tracemalloc.start()
names = reader._row_zero_names(candidates)
_current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(json.dumps({'names': names, 'peak': peak}))
"""


def ranking_peak(text):
    """(names, peak bytes allocated while ranking) of ``text``, measured in a child process."""
    env = {key: value for key, value in os.environ.items() if key != 'PYTHONTRACEMALLOC'}
    done = subprocess.run([sys.executable, '-I', '-c', RANKING_PEAK, str(REPO_ROOT)], input=text.encode('utf-8'),
                          capture_output=True, env=env, check=True, timeout=120)
    result = json.loads(done.stdout)
    return result['names'], result['peak']


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

    def test_many_distinct_row_zero_names_are_not_all_collected(self):
        # At most MAX_READINGS names are ever tried; collecting every distinct name with a list
        # membership test was quadratic (40,000 names took over ten seconds).
        text = ('Row: 0 _id=1, body=x\n' + ''.join(f'Row: 0 n{i}=x\n' for i in range(40000))
                + 'Row: 1 _id=2, body=y\n')
        self.assertEqual(len(reader._row_zero_names(reader._candidates(reader._lines(text)))), reader.MAX_READINGS)  # pylint: disable=protected-access
        dump = reader.parse_text(text)
        self.assertEqual([row['_id'] for row in values(dump)], ['1', '2'])

    def test_choosing_row_zero_names_keeps_only_the_shortlist(self):
        # Only the shortlist choices are kept while the names are ranked, not every distinct
        # 'Row: 0' name (#2172): memory allocated by the call must not grow with their number.
        names, peak = ranking_peak(
            'Row: 0 _id=1, body=x\n' + ''.join(f'Row: 0 n{i}=x\n' for i in range(40000))
            + 'Row: 1 _id=2, body=y\n')
        self.assertEqual(names, ['_id', 'n0', 'n1', 'n2'])
        self.assertLess(peak, 64 * 1024)

    def test_row_zero_names_that_fit_are_returned_without_reading_row_one_names(self):
        # One 'Row: 0' name and many distinct 'Row: 1' names: the 'Row: 0' names fit in the
        # shortlist, so the 'Row: 1' names are not indexed (#2172 review).
        names, peak = ranking_peak(
            'Row: 0 _id=1, body=x\n' + ''.join(f'Row: 1 n{i}=x\n' for i in range(40000)))
        self.assertEqual(names, ['_id'])
        self.assertLess(peak, 64 * 1024)

    def test_few_row_zero_names_over_the_shortlist_do_not_index_many_row_one_names(self):
        # MAX_READINGS + 1 'Row: 0' names and many unrelated 'Row: 1' names: the 'Row: 0' side
        # is the smaller one, so the 'Row: 1' names are not all kept (#2172 review).
        lead = ''.join(f'Row: 0 a{i}=x\n' for i in range(reader.MAX_READINGS))
        names, peak = ranking_peak(
            'Row: 0 _id=1, body=x\n' + lead + ''.join(f'Row: 1 m{i}=x\n' for i in range(40000))
            + 'Row: 1 _id=2, body=y\n')
        self.assertEqual(names, ['_id', 'a0', 'a1', 'a2'])
        self.assertLess(peak, 64 * 1024)

    def test_repeated_row_zero_names_do_not_index_many_row_one_names(self):
        # The same MAX_READINGS + 1 'Row: 0' names repeated until they outnumber many unrelated
        # 'Row: 1' names: the side with fewer distinct names is indexed, not the one with fewer
        # lines (#2172 review).
        lead = ''.join(f'Row: 0 a{i % reader.MAX_READINGS}=x\n' for i in range(40004))
        names, peak = ranking_peak(
            'Row: 0 _id=1, body=x\n' + lead + ''.join(f'Row: 1 m{i}=x\n' for i in range(40000))
            + 'Row: 1 _id=2, body=y\n')
        self.assertEqual(names, ['_id', 'a0', 'a1', 'a2'])
        self.assertLess(peak, 64 * 1024)

    def test_sequence_index_rounds_resume_where_they_stopped(self):
        # A long prefix of a few repeated names, then many distinct names on both sides, so
        # both sides go over several caps: each side reads the candidates once in all, not
        # once per round (#2172 review). With the first and last scans of _row_zero_names,
        # that is at most four reads per candidate.
        class CountingList(list):
            reads = 0

            def __iter__(self):
                for row in list.__iter__(self):
                    CountingList.reads += 1
                    yield row

        distinct = reader.SEQUENCE_INDEX_CAP * 20
        text = ('Row: 0 _id=1, body=x\n' + ''.join(f'Row: {i % 2} a{i % 4}=x\n' for i in range(40000))
                + ''.join(f'Row: 0 z{i}=x\nRow: 1 m{i}=x\n' for i in range(distinct))
                + 'Row: 1 _id=2, body=y\n')
        candidates = CountingList(reader._candidates(reader._lines(text)))  # pylint: disable=protected-access
        names = reader._row_zero_names(candidates)  # pylint: disable=protected-access
        self.assertEqual(names, ['_id', 'a0', 'a2', 'z0'])
        self.assertLessEqual(CountingList.reads, 4 * len(candidates) + 20)
        self.assertEqual(names, reader._row_zero_names(list(candidates)))  # pylint: disable=protected-access

    def test_ranking_cost_is_linear_and_bounded_by_distinct_row_zero_names(self):
        # The cost written in _sequence_test, on every shape the reviews of #2172 raised, with a
        # small cap so that several rounds run: names held by the two sides at most
        # D0 + max(cap, 4 * D0), and at most four reads per candidate (plus one per round).
        cap = 4

        def row_zero(names, repeat=1):
            return ''.join(f'Row: 0 {name}=x\n' for name in names for _ in range(repeat))

        def row_one(names):
            return ''.join(f'Row: 1 {name}=x\n' for name in names)

        def distinct(prefix, count):
            return [f'{prefix}{i}' for i in range(count)]

        shapes = {
            'few Row: 0, many unrelated Row: 1': row_zero(distinct('a', 4)) + row_one(distinct('m', 2000)),
            'many Row: 0, one Row: 1': row_zero(distinct('a', 2000)),
            'many on both sides': row_zero(distinct('a', 2000)) + row_one(distinct('m', 2000)),
            'few Row: 0 repeated past many Row: 1': row_zero(distinct('a', 4), 600) + row_one(distinct('m', 2000)),
            'Row: 0 just past a cap, Row: 1 far past it': row_zero(distinct('a', 4 ** 4)) + row_one(distinct('m', 4 ** 5 + 1)),
            'repeated prefix, then many on both sides': ''.join(f'Row: {i % 2} p{i % 4}=x\n' for i in range(4000))
                                                        + row_zero(distinct('a', 600)) + row_one(distinct('m', 600)),
        }
        held = []

        class LastRowOne(reader._LastRowOne):  # pylint: disable=protected-access
            def scan(self, cap):
                done = super().scan(cap)
                held.append(('one', len(self.last)))
                return done

        class RowZeroInSequence(reader._RowZeroInSequence):  # pylint: disable=protected-access
            def scan(self, cap):
                done = super().scan(cap)
                held.append(('zero', len(self.first)))
                return done

        class CountingList(list):
            reads = 0

            def __iter__(self):
                for row in list.__iter__(self):
                    CountingList.reads += 1
                    yield row

        for shape, body in shapes.items():
            with self.subTest(shape=shape):
                text = 'Row: 0 _id=1, body=x\n' + body + 'Row: 1 _id=2, body=y\n'
                candidates = CountingList(reader._candidates(reader._lines(text)))  # pylint: disable=protected-access
                row_zero_names = {rest.split('=', 1)[0] for _index, number, rest in candidates if number == 0}
                del held[:]
                CountingList.reads = 0
                with mock.patch.object(reader, 'SEQUENCE_INDEX_CAP', cap), \
                        mock.patch.object(reader, '_LastRowOne', LastRowOne), \
                        mock.patch.object(reader, '_RowZeroInSequence', RowZeroInSequence):
                    names = reader._row_zero_names(candidates)  # pylint: disable=protected-access
                reads = CountingList.reads
                self.assertEqual(names, reader._row_zero_names(list(candidates)))  # pylint: disable=protected-access
                latest, most = {}, 0
                for side, count in held:
                    latest[side] = count
                    most = max(most, sum(latest.values()))
                d0 = len(row_zero_names)
                self.assertTrue(held)
                self.assertLessEqual(most, d0 + max(cap, 4 * d0))
                self.assertLessEqual(reads, 4 * len(candidates) + len(held))

    def test_row_zero_name_forming_a_sequence_is_tried_after_many_leading_lines(self):
        # More leading 'Row: 0' lines with distinct first columns than MAX_READINGS: the name
        # that forms a 'Row: 0'/'Row: 1' sequence must still be tried (#2130).
        lead = ''.join(f'Row: 0 n{i}=x\n' for i in range(reader.MAX_READINGS + 1))
        dump = reader.parse_text(lead + 'Row: 0 _id=1, body=a\nRow: 1 _id=2, body=b\n')
        self.assertEqual(dump.columns, ('_id', 'body'))
        self.assertEqual([row['_id'] for row in values(dump)], ['1', '2'])
        self.assertTrue(any('before the first row' in warning for warning in dump.warnings))

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
