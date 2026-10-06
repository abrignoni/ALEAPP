"""Real XML/ABX bytes test raw app-op evidence without adding operation meanings."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scripts.artifacts import appops as module


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        if not isinstance(path, str):
            raise TypeError('Source path requires a string')
        return str(Path(path).relative_to(self.root))


def fixture_xml():
    root = ET.Element('app-ops', {'v': '3', 'unknown': 'raw root'})
    pkg = ET.SubElement(root, 'pkg', {'n': 'test.raw', 'unknown': 'raw package'})
    uid = ET.SubElement(pkg, 'uid', {'n': '00123', 'm': '0', 'unknown': 'raw uid'})
    for index, code in enumerate(['0', '120', '121', '99999', '-1', '000', 'text', '', None]):
        attributes = {'m': '0', 'd': '-1', 'unknown': '<raw> & "é"', 'flag': 'true', 'nullable': 'None'}
        if code is not None:
            attributes['n'] = code
        if index in (0, 2):
            attributes.update({'tp': '0', 'tc': '1700000000123', 'tb': '', 'tf': '1700000002123',
                               'tfs': '1700000003123', 'tt': '1700000004123', 'rp': '1700000005123',
                               'rt': 'raw reject', 'rfs': '0', 'rf': '', 'rb': '-1', 'rc': 'other',
                               'pp': 'legacy.proxy', 'pu': '0'})
        op = ET.SubElement(uid, 'op', attributes)
        for _ in range(2):
            ET.SubElement(op, 'st', {'n': '000', 'id': '0', 't': '1700000000123', 'r': '0',
                                     'd': '0', 'pp': 'proxy.raw', 'pu': '0', 'unknown': 'raw state'})
    return ET.tostring(root, encoding='unicode')


def write_xml(path, xml=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(fixture_xml() if xml is None else xml, encoding='utf-8')
    return path


def write_abx(path, xml=None, typed=False):
    """Real ABX interned tags and actual int/long/bool/null tokens, no mocked roots."""
    def raw(value):
        data = value.encode('utf-8')
        return struct.pack('>h', len(data)) + data

    def interned(value):
        return b'\xff\xff' + raw(value)

    def attribute(key, value):
        name = interned(key)
        if typed and key == 'flag':
            return b'\xcf' + name
        if typed and key == 'nullable':
            return b'\x1f' + name
        if typed and value and value.lstrip('-').isdigit() and (value == '0' or not value.startswith('0')):
            numeric = int(value)
            if -(2**31) <= numeric < 2**31:
                return b'\x6f' + name + struct.pack('>i', numeric)
            return b'\x8f' + name + struct.pack('>q', numeric)
        return b'\x2f' + name + raw(value)

    def element(node):
        data = b'\x32' + interned(node.tag)
        for key, value in node.attrib.items():
            data += attribute(key, value)
        for child in node:
            data += element(child)
        return data + b'\x33' + interned(node.tag)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'ABX\0\x10' + element(ET.fromstring(fixture_xml() if xml is None else xml)) + b'\x11')
    return path


class AppopsRawSourcesTest(unittest.TestCase):
    def test_xml_typed_abx_exact_projection_raw_attributes_and_repeats(self):
        with tempfile.TemporaryDirectory() as folder:
            xml = write_xml(Path(folder)/'xml/system/appops.xml')
            binary = write_abx(Path(folder)/'abx/system/appops.xml', typed=True)
            for function, count, width in [(module.get_appops, 18, 10), (module.get_appops_legacy, 2, 13)]:
                a = function.__wrapped__(Context(folder, [xml]))
                b = function.__wrapped__(Context(folder, [binary]))
                self.assertEqual(a[:2], b[:2])
                self.assertEqual((len(a[0]), len(a[1])), (width, count))
                self.assertEqual(a[2], str(xml))
            headers, rows, _ = module.get_appops.__wrapped__(Context(folder, [xml]))
            self.assertEqual(headers[:2], (('Access Timestamp', 'datetime'), ('Reject Timestamp', 'datetime')))
            codes = ['0', '120', '121', '99999', '-1', '000', 'text', '', None]
            for index, code in enumerate(codes):
                row = rows[index*2]
                self.assertEqual(row, rows[index*2+1])
                self.assertEqual(row[6], code)
                self.assertEqual(row[7], module.PERMISSION_OP.get(code, code))
                self.assertEqual(row[8], '000')
                self.assertEqual(row[0].timestamp(), 1700000000.123)
                self.assertEqual(row[1].timestamp(), 0)
                attributes = json.loads(row[9])
                self.assertEqual(attributes['container']['attributes']['n'], '00123')
                self.assertEqual(attributes['entry']['attributes']['d'], '0')
                self.assertEqual(attributes['operation']['attributes']['nullable'], 'None')
                self.assertEqual(attributes['operation']['attributes']['unknown'], '<raw> & "é"')
            _, legacy, _ = module.get_appops_legacy.__wrapped__(Context(folder, [binary]))
            self.assertEqual([r[10] for r in legacy], ['0', '121'])
            self.assertEqual(legacy[0][0].timestamp(), 0)
            self.assertEqual(legacy[0][2], '')
            self.assertEqual(json.loads(legacy[0][12])['operation']['attributes']['rt'], 'raw reject')

    def test_identical_known_aliases_collapse_but_changed_bytes_survive(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            a = write_xml(root/'data/data/pkg/system/appops.xml')
            b = write_xml(root/'data/user/0/pkg/system/appops.xml')
            for function, count, width in [(module.get_appops, 18, 10), (module.get_appops_legacy, 2, 13)]:
                headers, rows, source = function.__wrapped__(Context(root, [a,b,a]))
                self.assertEqual((len(headers), len(rows)), (width, count))
                self.assertEqual(source, str(a))
            b.write_text(b.read_text(encoding='utf-8').replace('test.raw', 'test.changed'), encoding='utf-8')
            for function, count, width in [(module.get_appops, 36, 11), (module.get_appops_legacy, 4, 14)]:
                headers, rows, source = function.__wrapped__(Context(root, [a,b]))
                self.assertEqual((len(headers), len(rows)), (width, count))
                self.assertEqual(headers[-1], 'Source File')
                self.assertEqual(source.splitlines(), list(map(str,[a,b])))
                self.assertEqual(set(r[-1] for r in rows), {str(p.relative_to(root)) for p in [a,b]})
            # Equal decoded trees with different XML/ABX bytes are distinct original states.
            write_abx(b,typed=True)
            headers,rows,source=module.get_appops.__wrapped__(Context(root,[a,b]))
            self.assertEqual((len(headers),len(rows)),(11,36))
            self.assertEqual(source.splitlines(),list(map(str,[a,b])))

    def test_different_namespaces_and_encodings_never_content_deduplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paths = [write_xml(root/view/'appops.xml') for view in
                     ['data/system','system','prefix/data/system','data/user/10/pkg/system',
                      'data/user_de/0/pkg/system','unknown/system']]
            paths.append(write_abx(root/'data/data/pkg/system/appops.xml'))
            headers, rows, source = module.get_appops.__wrapped__(Context(root, paths))
            self.assertEqual((len(headers), len(rows)), (11,126))
            self.assertEqual(source.splitlines(), list(map(str,paths)))
            self.assertEqual(len(set(r[-1] for r in rows)), 7)

    def test_bad_roots_missing_package_invalid_dates_keep_later_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bad = write_xml(root/'bad/system/appops.xml','<broken')
            abx = write_xml(root/'truncated/system/appops.xml','');abx.write_bytes(b'ABX\0\x32')
            unsupported = write_xml(root/'unsupported/system/appops.xml','<app-ops><pkg><uid><op><st/></op></uid></pkg></app-ops>')
            good = write_xml(root/'good/system/appops.xml',fixture_xml().replace('1700000000123','invalid-time'))
            before = {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in [bad,abx,unsupported,good]}
            with patch.object(module,'logfunc') as log:
                headers, rows, source = module.get_appops.__wrapped__(Context(root,[bad,abx,unsupported,good]))
            self.assertEqual((len(headers),len(rows)),(10,18))
            self.assertEqual(source,str(good))
            self.assertTrue(all(r[0]=='' for r in rows))
            self.assertEqual(json.loads(rows[0][9])['entry']['attributes']['t'],'invalid-time')
            self.assertIn('unsupported package',str(log.call_args_list))
            self.assertIn('invalid stored time',str(log.call_args_list))
            self.assertTrue(all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in before.items()))
            with patch.object(module,'logfunc'):
                _, legacy, _ = module.get_appops_legacy.__wrapped__(Context(root,[good]))
            self.assertEqual(len(legacy),2)
            self.assertEqual(legacy[0][1],'')
            self.assertEqual(json.loads(legacy[0][12])['operation']['attributes']['tc'],'invalid-time')

    def test_empty_sources_wrong_names_and_repairs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            good = write_xml(root/'good/system/appops.xml','<app-ops><pkg n="a&b"><uid><op n="121"><st t="0"/></op></uid></pkg></app-ops>')
            empty = write_xml(root/'empty/system/appops.xml','<app-ops/>')
            wrong = write_xml(root/'other/system/appops.xml.bak')
            wrong_dir = write_xml(root/'other/appops.xml')
            headers,rows,source = module.get_appops.__wrapped__(Context(root,[empty,wrong,wrong_dir,good]))
            self.assertEqual((len(headers),len(rows)),(10,1))
            self.assertEqual(rows[0][2],'a&b')
            self.assertEqual(source,str(good))
            headers,rows,source = module.get_appops_legacy.__wrapped__(Context(root,[good,empty]))
            self.assertEqual((len(headers),rows,source),(13,[],''))

    def test_diagnostic_limit_and_unreadable_fingerprint_no_false_collapse(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            a=write_xml(root/'data/data/pkg/system/appops.xml',fixture_xml().replace('1700000000123','invalid'))
            b=write_xml(root/'data/user/0/pkg/system/appops.xml',a.read_text(encoding='utf-8'))
            real_open=Path.open

            def open_file(path,*args,**kwargs):
                if args and args[0]=='rb' and 'system' in path.parts:
                    raise PermissionError('fixture fingerprint denial')
                return real_open(path,*args,**kwargs)

            with patch.object(Path,'open',open_file), patch.object(module,'logfunc'):
                headers,rows,_=module.get_appops.__wrapped__(Context(root,[a,b]))
            self.assertEqual((len(headers),len(rows)),(11,36))
            many=write_xml(root/'many/system/appops.xml',a.read_text(encoding='utf-8').replace('</op>','<st t="invalid" r="invalid"/>'*5+'</op>'))
            with patch.object(module,'logfunc') as log:
                _,rows,_=module.get_appops.__wrapped__(Context(root,[many]))
            self.assertEqual(len(rows),63)
            self.assertEqual(log.call_count,21)
            self.assertIn('only the first 20',str(log.call_args))


if __name__=='__main__':
    unittest.main()
