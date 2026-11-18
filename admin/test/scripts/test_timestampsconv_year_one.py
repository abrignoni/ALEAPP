"""timestampsconv raised ValueError for NSDate.distantPast (year one in Cocoa seconds)."""
import pathlib
import sys
import unittest
from datetime import datetime, timezone

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

    def test_out_of_range_stays_a_value_error(self):
        for value in (-63114076799, -63113904001, -1e30, 1e12):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    timestampsconv(value)


if __name__ == '__main__':
    unittest.main()
