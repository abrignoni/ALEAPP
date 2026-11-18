"""timestampsconv: NSDate sentinels, and conversion that does not depend on the platform's gmtime.

NSDate.distantPast (Cocoa -63114076800) is 0000-12-30 in Python's proleptic Gregorian calendar,
two days before datetime.min, and raised ValueError. datetime.fromtimestamp fails on Windows before
1970 and after the year 3000; FailingFromtimestamp simulates that on any platform.
"""
import pathlib
import sys
import unittest
from datetime import datetime, timezone
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.ilapfuncs import timestampsconv  # pylint: disable=wrong-import-position


class TimestampsconvContract(unittest.TestCase):
    def test_sentinels_are_blank(self):
        for value in (-63114076800, -63114076800.0, 63113904000, 63113904000.0):
            with self.subTest(value=value):
                self.assertEqual(timestampsconv(value), '')

    def test_year_4001_that_is_not_the_sentinel_converts(self):
        self.assertEqual(timestampsconv(63113904001), datetime(4001, 1, 1, 0, 0, 1, tzinfo=timezone.utc))

    def test_epoch_fraction_and_modern_values(self):
        self.assertEqual(timestampsconv(0), datetime(2001, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(timestampsconv(700000000), datetime(2023, 3, 8, 20, 26, 40, tzinfo=timezone.utc))
        self.assertEqual(timestampsconv(700000000.5),
                         datetime(2023, 3, 8, 20, 26, 40, 500000, tzinfo=timezone.utc))

    def test_pre_1970_and_unix_epoch(self):
        self.assertEqual(timestampsconv(-978307200), datetime(1970, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(timestampsconv(-978307201), datetime(1969, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
        self.assertEqual(timestampsconv(-1009843200), datetime(1969, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(timestampsconv(-63113904000), datetime(1, 1, 1, tzinfo=timezone.utc))

    def test_fractional_pre_1970(self):
        self.assertEqual(timestampsconv(-978307200.5),
                         datetime(1969, 12, 31, 23, 59, 59, 500000, tzinfo=timezone.utc))

    def test_out_of_range_and_non_finite_raise_value_error(self):
        for value in (-63114076799, -63113904001, -1e30, 1e12, 1e30, float('inf'), float('-inf'), float('nan')):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    timestampsconv(value)


class FailingFromtimestamp(datetime):
    """datetime whose fromtimestamp fails the way Windows' gmtime does outside 1970 to 3000."""

    @classmethod
    def fromtimestamp(cls, *args, **kwargs):
        raise OSError(22, 'Invalid argument')


class TimestampsconvWithoutPlatformGmtime(unittest.TestCase):
    def test_converts_without_fromtimestamp(self):
        cases = ((-1009843200, datetime(1969, 1, 1, tzinfo=timezone.utc)),
                 (-978307200.5, datetime(1969, 12, 31, 23, 59, 59, 500000, tzinfo=timezone.utc)),
                 (700000000, datetime(2023, 3, 8, 20, 26, 40, tzinfo=timezone.utc)),
                 (63113904001, datetime(4001, 1, 1, 0, 0, 1, tzinfo=timezone.utc)))
        with mock.patch('scripts.ilapfuncs.datetime', FailingFromtimestamp):
            for value, expected in cases:
                with self.subTest(value=value):
                    self.assertEqual(timestampsconv(value), expected)


if __name__ == '__main__':
    unittest.main()
