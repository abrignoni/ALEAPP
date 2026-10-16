"""Calls retain decoded decision values without claiming verified outcomes."""
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts import blackboxprotobuf
from scripts.ilapfuncs import decode_protobuf
from scripts.artifacts import googleVoice as parser
from scripts.artifacts.googleVoice import _raw_call_value_json as raw_value_json
from admin.test.scripts.test_sdhms_stat_sources import context


def make_fixture(root):
    path = root/'data/data/com.google.android.apps.googlevoice/files/accounts/1/LegacyMsgDbInstance.db'
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE message_t(message_blob BLOB, conversation_id TEXT)')
    cases = [(0,None,'int'),(1,None,'int'),(2,None,'int'),(3,None,'int'),
             (99,0,'int'),(0,1,'int'),(0,b'raw','bytes'),(0,{'1':7},'message'),
             (0,[0,2],'int'),(0,b'','bytes'),(0,None,'int')]
    blobs = []
    for index,(code,field22,kind) in enumerate(cases):
        message = {'1':b'message-id', '2':1700000000000, '3':b'local', '4':{'1':b'other'}, '13':code}
        types = {'1':{'name':'','type':'bytes'},'2':{'name':'','type':'int'},'3':{'name':'','type':'bytes'},
                 '4':{'name':'','type':'message','message_typedef':{'1':{'name':'','type':'bytes'}}},'13':{'name':'','type':'int'}}
        if field22 is not None:
            message['22'] = field22
            types['22'] = {'name':'','type':kind}
            if kind=='message':types['22']['message_typedef']={'1':{'name':'','type':'int'}}
        if index==10:message['1']=b'welcome_voicemail';message['13']=3
        blob=blackboxprotobuf.encode_message(message,types);blobs.append(blob)
        db.execute('INSERT INTO message_t VALUES(?,?)',(blob,'unused'))
    db.execute('INSERT INTO message_t SELECT * FROM message_t LIMIT 1')
    blobs.append(blobs[0]);db.commit();db.close()
    return path, blobs


class GoogleVoiceCallEvidenceTest(unittest.TestCase):
    def test_actual_wire_and_sqlite_membership_types_multiplicity(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);path,blobs=make_fixture(root)
            headers,rows,source=parser.googlevoice_calls.__wrapped__(context(root,[path]))
            self.assertEqual(headers[0],('Timestamp','datetime'))
            self.assertEqual(headers[5],'Call Status (existing parser classification)')
            self.assertEqual(len(rows),11);self.assertEqual(source,str(path))
            self.assertEqual(rows[0],rows[-1])
            expected=[decode_protobuf(bytes(b))[0] for i,b in enumerate(blobs) if i!=10]
            for row,value in zip(rows,expected):
                self.assertEqual(row[6],json.dumps({'type':'int','decimal':str(value['13'])},separators=(',',':')))
                self.assertEqual(row[7],'Yes' if '22' in value else 'No')
                self.assertEqual(row[8],raw_value_json(value['22']) if '22' in value else '')
                self.assertEqual(len(row),12)
            self.assertEqual(rows[4][8],'{"type":"int","decimal":"0"}')
            self.assertEqual(json.loads(rows[6][8]),{'type':'bytes','hex':b'raw'.hex()})
            self.assertEqual(json.loads(rows[7][8])['type'],'dict')
            self.assertEqual(json.loads(rows[8][8])['type'],'list')
            self.assertEqual(rows[9][7],'Yes')

    def test_typed_json_tags_cannot_collide_and_numeric_boundaries(self):
        pairs=[b'raw',{'type':'bytes','hex':'726177'},[0,b'raw'],None,False,0,2**80,-1,1.25,'',bytearray(b'raw')]
        encoded=[raw_value_json(v) for v in pairs]
        self.assertEqual(len(set(encoded)),len(pairs))
        self.assertEqual(json.loads(encoded[6]),{'type':'int','decimal':str(2**80)})
        self.assertEqual(json.loads(encoded[8]),{'type':'float','hex':float(1.25).hex()})
        self.assertNotEqual(json.loads(encoded[0])['type'],json.loads(encoded[1])['type'])


if __name__=='__main__':
    unittest.main()
