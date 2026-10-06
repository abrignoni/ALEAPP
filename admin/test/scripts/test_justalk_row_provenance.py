"""Real filesystem Realm fixtures exercise contributor-only provenance."""
import datetime
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.justalk_realm_fixture import emit, call_row
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.realm_parser import parse_realm_file, realm_rows
from scripts.artifacts import justalk as parser


def fixture(root, name, rows, kids=False):
    package='com.justalk.kids.android' if kids else 'com.juphoon.justalk'
    path=root/'data/data'/package/'files'/(name+'.realm')
    declared=emit(path,rows)
    decoded=parse_realm_file(path)
    assert decoded['reason'] is None
    assert all(not t['unsupported_columns'] for t in decoded['active'].values())
    assert list(realm_rows(path,'class_CallLog'))==declared['class_CallLog']
    return path


def expected_message(row):
    return (datetime.datetime.fromtimestamp(row['timestamp'],datetime.timezone.utc),
            'Incoming' if row['incoming'] else 'Outgoing',row['senderName'],row['content'],'',row['name'],
            row['type'],'','','','','','','',row['senderUid'],row['uid'],row['imdnId'],row['logId'],row['state'],row['readState'])


def expected_call(row):
    return (datetime.datetime.fromtimestamp(row['timestamp'],datetime.timezone.utc),
            'Incoming' if row['incoming'] else 'Outgoing',row['type'],row['name'],2.5,2500,
            row['uid'],row['serverCallId'],row['logId'],row['state'],row['reason'])


class JusTalkRowProvenanceTest(unittest.TestCase):
    def test_multiple_realms_kids_and_native_cells(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder)
            for kids in [False,True]:
                message=call_row('a','Text',1700000000,False);call=call_row('c','AudioCall',1700000001,True)
                zero=fixture(root,'zero',[],kids);a=fixture(root,'a',[message,message,call],kids)
                other=call_row('b','Text',1700000010,True);othercall=call_row('d','VideoCall',1700000011,False)
                b=fixture(root,'b',[other,othercall],kids)
                messages=parser.justalk_kids_messages if kids else parser.justalk_messages
                calls=parser.justalk_kids_calls if kids else parser.justalk_calls
                ctx=context(root,[zero,a,b,zero])
                headers,rows,source=messages.__wrapped__(ctx)
                self.assertEqual(len(headers),21);self.assertEqual(headers[-1],'Source File')
                self.assertEqual(rows,[expected_message(message)+(str(a.relative_to(root)),)]*2+
                                 [expected_message(other)+(str(b.relative_to(root)),)])
                self.assertEqual(source,'\n'.join(map(str,[a,b])))
                headers,rows,source=calls.__wrapped__(ctx)
                self.assertEqual(len(headers),12)
                self.assertEqual(rows,[expected_call(call)+(str(a.relative_to(root)),),
                                       expected_call(othercall)+(str(b.relative_to(root)),)])
                self.assertEqual(source,'\n'.join(map(str,[a,b])))

    def test_split_empty_and_repeated_selected_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);message=call_row('text','Text',1700000000,False);call=call_row('call','AudioCall',1700000001,True)
            zero=fixture(root,'zero',[]);a=fixture(root,'messages',[message]);b=fixture(root,'calls',[call])
            ctx=context(root,[zero,a,b,zero])
            headers,rows,source=parser.justalk_messages.__wrapped__(ctx)
            self.assertEqual(len(headers),20);self.assertEqual(rows,[expected_message(message)]);self.assertEqual(source,str(a))
            headers,rows,source=parser.justalk_calls.__wrapped__(ctx)
            self.assertEqual(len(headers),11);self.assertEqual(rows,[expected_call(call)]);self.assertEqual(source,str(b))
            for function,size in [(parser.justalk_messages,20),(parser.justalk_calls,11)]:
                headers,rows,source=function.__wrapped__(context(root,[zero]))
                self.assertEqual(len(headers),size);self.assertEqual(rows,[]);self.assertEqual(source,'')
            headers,rows,source=parser.justalk_messages.__wrapped__(context(root,[a,a,zero]))
            self.assertEqual(len(headers),20);self.assertEqual(rows,[expected_message(message)]*2);self.assertEqual(source,str(a))


if __name__=='__main__':
    unittest.main()
