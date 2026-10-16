"""Exercise stored preference retention with the actual XML and AES readers."""
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import appLockerfishingnetpat as parser

class Context:
    def __init__(self, root, files):
        self.root, self.files = root, files
    def get_files_found(self):
        return self.files
    def get_relative_path(self, path):
        return str(pathlib.Path(path).relative_to(self.root))

def encrypted(value):
    return AES.new(bytes.fromhex('526e7934384e693861506a59436e5549'), AES.MODE_CBC, bytes.fromhex('526e7934384e693861506a59436e5549')).encrypt(pad(value, 16)).hex()

def write_xml(path, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    root = ET.Element('map')
    for value in values:
        ET.SubElement(root, 'string', name='85B064D26810275C89F1F2CC15E20B442E98874398F16F6717BBD5D34920E3F8').text = value
    ET.ElementTree(root).write(path, encoding='utf-8')

def make_fixture(root):
    path = root/'data/data/com.hld.anzenbokusufake/shared_prefs/share_privacy_safe.xml'
    values = [encrypted(b'\x00\xff\x80payload'), encrypted(b'\x00\xff\x80payload'), None, '', 'abc', 'zz', '00', encrypted(b'')]
    write_xml(path, values)
    other = root/'data/user/10/com.hld.anzenbokusufake/shared_prefs/share_privacy_safe.xml'
    write_xml(other, [])
    invalid = root/'bad/com.hld.anzenbokusufake/shared_prefs/share_privacy_safe.xml'
    invalid.parent.mkdir(parents=True, exist_ok=True)
    invalid.write_text('<map>')
    return [path, other, invalid]

class TestAppLockerPreferences(unittest.TestCase):
    def test_actual_xml_aes_values_repeats_sources_and_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            files = make_fixture(root)
            with patch.object(parser, 'logfunc') as log:
                headers, rows, sources = parser.get_appLockerfishingnetpat.__wrapped__(Context(root, [files[0], files[0], *files[1:], root/'absent.xml']))
            self.assertEqual(len(rows), 9)
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual(rows[0], rows[1])
            self.assertEqual(bytes.fromhex(rows[0][1]), b'\x00\xff\x80payload')
            self.assertEqual(rows[-1][:3], (None, '', 'Missing preference'))
            self.assertEqual(rows[4][2], 'Invalid hex text')
            self.assertEqual(rows[6][2], 'Invalid AES block length')
            self.assertEqual(rows[7][1:3], ('', 'Completed (output not authenticated)'))
            self.assertEqual(sources.splitlines(), [str(files[0]), str(files[1])])
            self.assertEqual(log.call_count, 2)
            self.assertEqual([r[-1] for r in rows], [str(files[0].relative_to(root))]*8+[str(files[1].relative_to(root))])

    def test_padding_and_single_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            path = root/'one.xml'
            invalid = AES.new(bytes.fromhex('526e7934384e693861506a59436e5549'), AES.MODE_CBC, bytes.fromhex('526e7934384e693861506a59436e5549')).encrypt(b'\x00'*16).hex()
            write_xml(path, [invalid, '  ', encrypted(b'valid')])
            headers, rows, _ = parser.get_appLockerfishingnetpat.__wrapped__(Context(root, [path]))
            self.assertEqual(len(headers), 3)
            self.assertEqual(rows[0][2], 'Invalid PKCS7 padding')
            self.assertEqual(rows[1], ('  ', '', 'No stored text'))
            self.assertEqual(bytes.fromhex(rows[2][1]), b'valid')

if __name__ == '__main__':
    unittest.main()
