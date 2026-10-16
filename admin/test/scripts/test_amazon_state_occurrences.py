"""Saved-state byte occurrences survive unchanged regex matching."""
import base64
import gzip
import pathlib
import tempfile
import unittest
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.amazonShopping import get_amazon_webview_state

QUOTED = b'https://example.test/path?q=1,""'
GREEDY = b'http://first.test/a https://second.test/b'
CAPPED = b'http://' + b'x' * 501
PAYLOAD = b'prefix\x00' + QUOTED + b'\x00repeat\x01' + QUOTED + b'\x00' + GREEDY + b'\x00' + CAPPED + b'\x00http://abc\x00'


def write_state(path, data=PAYLOAD):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64encode(gzip.compress(data, mtime=0)))
    return path


class AmazonStateOccurrencesTest(unittest.TestCase):
    def test_quotes_repeated_greedy_and_capped_matches_are_lossless(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_state(pathlib.Path(folder) / '1700000000123MASHWebFragment1')
            headers, rows, source = get_amazon_webview_state.__wrapped__(context(folder, [path]))
            self.assertEqual(len(rows), 4)
            self.assertEqual(headers[0], ('State Timestamp', 'datetime'))
            self.assertEqual(source, str(path))
            first_offset = PAYLOAD.index(QUOTED)
            expected = [(QUOTED, first_offset), (QUOTED, PAYLOAD.index(QUOTED, first_offset + len(QUOTED))), (GREEDY, PAYLOAD.index(GREEDY)), (CAPPED[:-1], PAYLOAD.index(CAPPED))]
            for index, (row, (matched, offset)) in enumerate(zip(rows, expected), 1):
                self.assertEqual(row[2], index)
                self.assertEqual(row[3], offset)
                self.assertEqual(row[4].encode('ascii'), matched)
                self.assertEqual(PAYLOAD[offset:offset + len(matched)], matched)
                self.assertEqual(row[5], matched.decode('ascii').rstrip('"'))
                self.assertEqual(row[6], path.name)
            self.assertEqual(rows[0][4], rows[1][4])
            self.assertNotEqual(rows[0][3], rows[1][3])
            self.assertTrue(rows[0][4].endswith('""'))
            self.assertFalse(rows[0][5].endswith('"'))

    def test_occurrence_numbers_reset_and_zero_match_file_gives_no_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            first = write_state(pathlib.Path(folder) / '1700000000123MASHWebFragment1', b'abc\x00https://example.test/one\x00')
            second = write_state(pathlib.Path(folder) / '1700000001123MASHWebFragment2', b'\x00https://example.test/two\x00')
            empty = write_state(pathlib.Path(folder) / '1700000002123MASHWebFragment3', b'http://abc\x00ordinary bytes')
            _headers, rows, source = get_amazon_webview_state.__wrapped__(context(folder, [first, second, empty]))
            self.assertEqual(len(rows), 2)
            self.assertEqual([row[2] for row in rows], [1, 1])
            self.assertEqual([row[3] for row in rows], [4, 1])
            self.assertEqual([row[6] for row in rows], [first.name, second.name])
            self.assertEqual(source, str(first))
