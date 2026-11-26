"""A stored 0 in a Waze favourite or shared place time is blank on rows read from user.db, and Last
Name holds no text the store does not hold. All values here are made up."""
# pylint: disable=protected-access
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import waze


class ZeroTimes(unittest.TestCase):
    def test_a_stored_zero_is_blank(self):
        for value in (0, '0', None, ''):
            with self.subTest(value):
                self.assertEqual(waze._unix_ts_or_blank(value), '')

    def test_a_time_is_converted(self):
        self.assertEqual(waze._unix_ts_or_blank(1700000000).isoformat(), '2023-11-14T22:13:20+00:00')


class LastName(unittest.TestCase):
    def test_a_nested_message_gives_no_name(self):
        self.assertEqual(waze._last_name({9: 'x'}), '')
        self.assertEqual(waze._last_name({}), '')

    def test_a_stored_name_is_kept(self):
        self.assertEqual(waze._last_name('Doe'), 'Doe')


if __name__ == '__main__':
    unittest.main()
