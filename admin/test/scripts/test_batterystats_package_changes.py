"""Pin the package change rows of scripts/artifacts/batterystats.py.

The XML is written in the layout AOSP BatteryStatsImpl writes (android-14.0.0_r1,
services/core/java/com/android/server/power/stats/BatteryStatsImpl.java lines 11200 to
11222): item elements with start and end, dis and chg step lists, then upd elements with
pkg and ver, or rem elements with pkg. Every value is invented. The expected values are
written out, never read back from the code.
"""
import pathlib
import sys
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import batterystats as bs  # pylint: disable=wrong-import-position

DAILY = ('<daily-items>'
         '<item start="1700000000000" end="1700086400000">'
         '<dis><s v="O-5a-1f4"/></dis>'
         '<upd pkg="com.example.one" ver="42"/>'
         '<upd pkg="com.example.gone" ver="0"/>'
         '<upd pkg="com.example.one" ver="42"/>'
         '</item>'
         '<item start="1700086400000" end="1700172800000">'
         '<chg><s v="o-60-3e8"/></chg>'
         '</item>'
         '<item start="1700172800000" end="1700259200000">'
         '<rem pkg="com.example.old"/>'
         '<unknown pkg="com.example.skip"/>'
         '</item>'
         '</daily-items>')

DAY1 = datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)
DAY2 = datetime(2023, 11, 15, 22, 13, 20, tzinfo=timezone.utc)
DAY3 = datetime(2023, 11, 16, 22, 13, 20, tzinfo=timezone.utc)
DAY4 = datetime(2023, 11, 17, 22, 13, 20, tzinfo=timezone.utc)


class PackageChangeRows(unittest.TestCase):
    def test_rows_in_file_order(self):
        rows = bs.package_change_rows(ET.fromstring(DAILY))
        self.assertEqual(rows, [
            (DAY1, DAY2, 'upd', 'com.example.one', '42', 1),
            (DAY1, DAY2, 'upd', 'com.example.gone', '0', 1),
            (DAY1, DAY2, 'upd', 'com.example.one', '42', 1),
            (DAY3, DAY4, 'rem', 'com.example.old', '', 3),
        ])

    def test_item_without_changes_gives_no_rows(self):
        root = ET.fromstring('<daily-items><item start="1" end="2"><dis/></item></daily-items>')
        self.assertEqual(bs.package_change_rows(root), [])

    def test_missing_and_bad_times_are_blank(self):
        root = ET.fromstring('<daily-items><item end="x"><upd pkg="p"/></item>'
                             '<item start="0" end="0"><upd pkg="q" ver="1"/></item></daily-items>')
        self.assertEqual(bs.package_change_rows(root), [('', '', 'upd', 'p', '', 1),
                                                        ('', '', 'upd', 'q', '1', 2)])


if __name__ == '__main__':
    unittest.main()
