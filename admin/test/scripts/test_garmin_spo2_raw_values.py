"""Source measurements and averages remain distinct despite missing or zero values."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from scripts.artifacts import GarminSPo2 as garmin
from admin.test.scripts.test_history_doclist_all_sources import Context

SOURCE_ROWS=[(1,'start','end',95,96,'[95,96]'),(2,'start','end',94,None,None),
             (3,'start','end',0,0,'[]'),(4,None,None,-1,99,'unknown'),
             (5,'start','end','source','average','stored'),(2,'start','end',94,None,None),
             (6,'start','end',None,97,'average-only')]


def create_spo2_fixture(root):
    path=Path(root)/'data/data/com.garmin.android.apps.connectmobile/databases/cache-database'
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path)
    db.execute('CREATE TABLE acclimation_pulse_ox_details(userProfilePk,startTimestampGMT,endTimestampGMT,spo2Value,spo2ValueAverage,spo2ValuesArray)')
    db.executemany('INSERT INTO acclimation_pulse_ox_details VALUES(?,?,?,?,?,?)',SOURCE_ROWS)
    db.commit();db.close();return str(path)


class TestGarminSpo2RawValues(unittest.TestCase):
    def test_actual_sqlite_value_average_null_zero_and_repeats(self):
        with tempfile.TemporaryDirectory() as root:
            path=create_spo2_fixture(root)
            headers,rows,_=garmin.get_garmin_spo2.__wrapped__(Context(root,[path,path+'-wal',path+'-shm']))
            db=sqlite3.connect(path)
            source=db.execute('SELECT startTimestampGMT,endTimestampGMT,userProfilePk,spo2Value,spo2ValueAverage,spo2ValuesArray FROM acclimation_pulse_ox_details WHERE spo2Value IS NOT NULL').fetchall()
            db.close()
            self.assertEqual(rows,source)
            self.assertEqual(len(rows),6)
            self.assertEqual(rows[1],rows[-1])
            self.assertIsNone(rows[1][4])
            self.assertEqual(rows[2][3:5],(0,0))
            self.assertEqual([type(v) for v in rows[4]],[type(v) for v in source[4]])
            self.assertEqual(headers[:2],('Start Timestamp GMT','End Timestamp GMT'))

    def test_unsupported_table_is_explicit_not_silent_empty(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'cache-database';sqlite3.connect(path).close()
            with patch.object(garmin,'logfunc') as log:
                self.assertEqual(garmin.get_garmin_spo2.__wrapped__(Context(root,[str(path)]))[1],[])
            self.assertTrue(any('no such table: acclimation_pulse_ox_details' in str(call) for call in log.call_args_list))
