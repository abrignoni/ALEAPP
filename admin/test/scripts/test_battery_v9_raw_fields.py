"""Actual SQLite and protobuf values retain their source distinctions."""
import base64
import pathlib
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts import blackboxprotobuf
from scripts.artifacts.battery_usage_v9 import get_battery_usage_v9
from admin.test.scripts.test_sdhms_stat_sources import context


def make_fixture(root):
    path = root/'data/user_de/0/com.android.settings/databases/battery-usage-db-v9'
    path.parent.mkdir(parents=True,exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE BatteryState(uid,packageName,timestamp,consumerType,isFullChargeCycleStart,batteryInformation,batteryInformationDebug)')
    cases = [({'2':2,'3':2},1000),({'2':0,'3':0},0),({'2':99,'3':99},None),({},None),({'2':2,'3':2},1000),({'2':-1,'3':-1},[1000,2000])]
    for index,(info,value) in enumerate(cases):
        proto = {'1':info,'3':1700000000123,'14':5000,'15':2000,'7':b'App','4':b'UTC','13':b'opaque'}
        if value is not None:proto['20']=value
        typedef = {'1':{'name':'','type':'message','message_typedef':{'2':{'name':'','type':'int'},'3':{'name':'','type':'int'}}},'3':{'name':'','type':'int'},'14':{'name':'','type':'int'},'15':{'name':'','type':'int'},'7':{'name':'','type':'bytes'},'4':{'name':'','type':'bytes'},'13':{'name':'','type':'bytes'},'20':{'name':'','type':'int'}}
        encoded=blackboxprotobuf.encode_message(proto,typedef)
        db.execute('INSERT INTO BatteryState VALUES(?,?,?,?,?,?,?)',(index,'test.package',1700000000123,0,0,base64.b64encode(encoded).decode(),'total_power: 10\nconsume_power: 2'))
    db.commit();db.close()
    return path


class BatteryV9RawFieldsTest(unittest.TestCase):
    def test_actual_protobuf_boundaries_repeat_and_native_types(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);path=make_fixture(root)
            headers,rows,source=get_battery_usage_v9.__wrapped__(context(root,[path]))
            self.assertEqual(len(rows),6)
            self.assertEqual(headers[:2],(('Timestamp','datetime'),'Boot Timestamp'))
            self.assertNotIn('Source File',headers)
            self.assertEqual(source,str(path))
            self.assertEqual([r[13] for r in rows],[2,0,99,None,2,-1])
            self.assertEqual([r[15] for r in rows],[2,0,99,None,2,-1])
            self.assertEqual([r[16] for r in rows],['Good','Unmapped','Unmapped','','Good','Unmapped'])
            self.assertEqual(rows[0],rows[4])
            self.assertIsInstance(rows[1][13],int)
            self.assertEqual([r[9] for r in rows],[1000,0,None,None,1000,[1000,2000]])
            self.assertEqual([r[10] for r in rows],[1,0,'','',1,''])
            self.assertEqual(rows[0][1],1700000000.123)

    def test_empty_and_existing_invalid_payload_skip(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);path=make_fixture(root);db=sqlite3.connect(path)
            db.execute('DELETE FROM BatteryState');db.commit()
            self.assertEqual(get_battery_usage_v9.__wrapped__(context(root,[path]))[1],[])
            db.execute('INSERT INTO BatteryState VALUES(1,?,1,0,0,?,?)',('invalid','/w==',''))
            db.commit();db.close()
            self.assertEqual(get_battery_usage_v9.__wrapped__(context(root,[path]))[1],[])

if __name__=='__main__':
    unittest.main()
