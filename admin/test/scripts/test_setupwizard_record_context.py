"""Retain nested setupwizard XML observations without inferred operation meaning."""
import datetime
import json
import pathlib
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_android_user_indexes import write_abx
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.appopSetupWiz import get_appopSetupWiz


def write_fixture(path, values, binary=False):
    root = ET.Element('app-ops')
    package = ET.SubElement(root, 'pkg', n='com.google.android.setupwizard')
    child = ET.SubElement(package, 'uid', n='0010', extra='<&quoted"')
    operation = ET.SubElement(child, 'op', n='87', custom='unknown')
    for value in values:
        attrs = {'n':'opaque-state', 'repeated':'yes'}
        if value is not None:attrs['t'] = value
        ET.SubElement(operation, 'unexpected-state-tag', attrs)
    other = ET.SubElement(root, 'pkg', n='other.package')
    ET.SubElement(ET.SubElement(ET.SubElement(other, 'uid'), 'op'), 'st', t='1234')
    path.parent.mkdir(parents=True, exist_ok=True)
    if binary:write_abx(path, ET.tostring(root, encoding='unicode'))
    else:ET.ElementTree(root).write(path, encoding='utf-8')
    return path


def make_fixture(root, unsafe=True):
    values = [None, '0', '-1', '1700000000123', '1700000000123', '1700000000999']
    if unsafe:values += ['', ' ', 'invalid', '9'*100, '1700000001000']
    first = write_fixture(root/'A/system/appops.xml', values)
    second = write_fixture(root/'B/system/appops.xml', ['1700000002000'], binary=True)
    empty = write_fixture(root/'EMPTY/system/appops.xml', [])
    return [first, second, empty]


class SetupwizardRecordContextTest(unittest.TestCase):
    def test_actual_xml_raw_identity_timestamp_boundaries_repeats(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            files = make_fixture(root)
            headers, rows, sources = get_appopSetupWiz.__wrapped__(context(root, files))
            self.assertEqual(headers[:2], (('Timestamp','datetime'), 'Stored t'))
            self.assertEqual(len(rows), 12)
            self.assertEqual([r[1] for r in rows[:6]], [None,'0','-1','1700000000123','1700000000123','1700000000999'])
            self.assertEqual(rows[3], rows[4])
            self.assertEqual([r[2] for r in rows[6:10]], ['Invalid integer']*3+['Out of range'])
            self.assertEqual(rows[0][2], 'Missing')
            self.assertEqual(rows[1][2], 'Nonpositive')
            self.assertEqual(rows[10][0], datetime.datetime.fromtimestamp(1700000001,datetime.timezone.utc))
            self.assertEqual(json.loads(rows[0][5]), {'n':'0010','extra':'<&quoted"'})
            self.assertEqual(json.loads(rows[0][7]), {'n':'87','custom':'unknown'})
            self.assertEqual(rows[0][8], 'unexpected-state-tag')
            self.assertNotIn('t', json.loads(rows[0][9]))
            self.assertEqual(sources.splitlines(), [str(files[0]),str(files[1])])
            self.assertEqual([r[-1] for r in rows], ['A/system/appops.xml']*11+['B/system/appops.xml'])

    def test_abx_actual_reader_and_empty_last_not_contributor(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            files = make_fixture(root, unsafe=False)
            headers, rows, sources = get_appopSetupWiz.__wrapped__(context(root, files[1:]))
            self.assertNotIn('Source File', headers)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][1], '1700000002000')
            self.assertEqual(json.loads(rows[0][9])['n'], 'opaque-state')
            self.assertEqual(sources, str(files[1]))
            _, rows, sources = get_appopSetupWiz.__wrapped__(context(root, [files[2]]))
            self.assertEqual((rows,sources),([],''))

if __name__ == '__main__':
    unittest.main()
