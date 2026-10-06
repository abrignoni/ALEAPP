"""Index observations stay within their owning physical/evidence parent."""
import pathlib
import struct
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.androidUsers import android_users, _root


def write_xml(path, text):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


def make_fixture(root):
    root = pathlib.Path(root)
    paths = [write_xml(root/'A/system/users/userlist.xml', '<users><user id="0"/><user id="10"/><user id="10"/><user id="01"/><user id="02"/><user id="20"/><user id="30"/><user id=""/></users>'),
             write_xml(root/'B/system/users/userlist.xml', '<users><user id="1"/></users>'),
             write_xml(root/'A/system/users/0.xml', '<user id="0" created="1700000000123" serialNumber="0"><name>A</name></user>'),
             write_xml(root/'A/system/users/01.xml', '<user id="1"><name>Different ID</name></user>'),
             write_xml(root/'A/system/users/02.xml', '<user><name>Leading zero</name></user>'),
             write_xml(root/'B/system/users/0.xml', '<user id="0"><name>B</name></user>'),
             write_xml(root/'C/system/users/0.xml', '<user id="0"><name>No index</name></user>'),
             write_xml(root/'A/system/users/20.xml', '<broken'),
             write_xml(root/'A/system/users/30.xml', '<settings/>')]
    return paths


def write_abx(path, xml):
    """Small real ABX byte stream, strings written as fresh interned values."""
    def raw(value):
        data = value.encode('utf-8')
        return struct.pack('>h', len(data)) + data
    def interned(value):return b'\xff\xff' + raw(value)
    def element(node):
        data = b'\x32' + interned(node.tag)
        for key,value in node.attrib.items():data += b'\x2f' + interned(key) + raw(value)
        if node.text:data += b'\x24' + raw(node.text)
        for child in node:data += element(child)
        return data + b'\x33' + interned(node.tag)
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'ABX\x00\x10' + element(ET.fromstring(xml)) + b'\x11')
    return path


class AndroidUserIndexesTest(unittest.TestCase):
    def test_scoped_rows_duplicates_missing_invalid_and_leading_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = make_fixture(folder)
            with patch('scripts.artifacts.androidUsers.logfunc') as log:
                headers, rows, sources = android_users.__wrapped__(context(folder, paths))
            self.assertEqual(headers[-2:], ('Record Status','Source File'))
            records = [r for r in rows if r[-2]=='User record']
            self.assertEqual([r[3] for r in records], ['0','1','02','0','0'])
            self.assertEqual([r[9] for r in records], [True,False,True,False,False])
            index = rows[len(records):]
            self.assertEqual([r[3] for r in index], ['10','10','01','20','30','1'])
            for row in index:
                self.assertEqual(row[:3], ('','',''))
                self.assertEqual(row[4:9], ('','','','',''))
                self.assertTrue(row[9])
                self.assertEqual(row[10], '')
                self.assertIn('Index entry without returned user record', row[-2])
                self.assertTrue(row[-1].endswith('userlist.xml'))
            self.assertTrue(any('unreadable' in row[-2] for row in index))
            self.assertTrue(any('not user' in row[-2] for row in index))
            self.assertEqual(len(sources.splitlines()), 7)
            self.assertTrue(log.called)

    def test_physical_and_evidence_parents_both_required(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            index = write_xml(root/'A/system/users/userlist.xml', '<users><user id="0"/></users>')
            record = write_xml(root/'A/system/users/0.xml', '<user id="0"/>')
            paths = [index,record]
            mapping={str(index):'RootA/system/users/userlist.xml',str(record):'RootB/system/users/0.xml'}
            ctx=SimpleNamespace(get_files_found=lambda:paths,get_relative_path=lambda p:mapping[str(p)])
            with patch('scripts.artifacts.androidUsers.logfunc'):
                _headers,rows,_sources=android_users.__wrapped__(ctx)
            self.assertEqual([r[9] for r in rows],[False,True])
            record2=write_xml(root/'B/system/users/0.xml','<user id="0"/>')
            mapping[str(record2)]='RootA/system/users/0.xml'
            ctx=SimpleNamespace(get_files_found=lambda:[index,record2],get_relative_path=lambda p:mapping[str(p)])
            with patch('scripts.artifacts.androidUsers.logfunc'):
                _headers,rows,_sources=android_users.__wrapped__(ctx)
            self.assertEqual([r[9] for r in rows],[False,True])

    def test_actual_abx_reader_and_invalid_index_root(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder)/'system/users'
            index=write_abx(root/'userlist.xml','<users><user id="0"/><user id="10"/></users>')
            record=write_abx(root/'0.xml','<user id="0" serialNumber="4"><name>ABX Name</name></user>')
            self.assertEqual(_root(record).find('name').text,'ABX Name')
            with patch('scripts.artifacts.androidUsers.logfunc'):
                _headers,rows,_source=android_users.__wrapped__(context(folder,[index,record]))
            self.assertEqual([r[3] for r in rows],['0','10'])
            self.assertEqual(rows[0][4],'ABX Name')
            write_xml(index,'<wrong/>')
            with patch('scripts.artifacts.androidUsers.logfunc') as log:
                _headers,rows,_source=android_users.__wrapped__(context(folder,[index,record]))
            self.assertEqual(len(rows),1)
            self.assertFalse(rows[0][9])
            self.assertTrue(any('non-users index root' in call.args[0] for call in log.call_args_list))
