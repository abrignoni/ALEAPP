"""Positional tokens preserve text occurrences and established device side effects."""
import copy
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts import ilapfuncs
from scripts.artifacts import artGlobals, usagestatsVersion as parser


class VersionFieldsTest(unittest.TestCase):
    def setUp(self):
        self.identifiers = copy.deepcopy(ilapfuncs.identifiers)
        self.version = artGlobals.versionf
        ilapfuncs.identifiers.clear()

    def tearDown(self):
        ilapfuncs.identifiers.clear()
        ilapfuncs.identifiers.update(self.identifiers)
        artGlobals.versionf = self.version

    def test_tokens_and_actual_accumulator(self):
        raw = b'1\r\n\n A;B;C \r\nD;E;F;\nG;H;I;; tail \nJ;K;L;4;;6;\nA;B;C\n'
        expected = [('Android Version','A'),('Codename','B'),('Build version','C'),
                    ('Android Version','D'),('Codename','E'),('Build version','F'),('Field 4 (as stored)',''),
                    ('Android Version','G'),('Codename','H'),('Build version','I'),('Field 4 (as stored)',''),('Field 5 (as stored)',' tail'),
                    ('Android Version','J'),('Codename','K'),('Build version','L'),('Field 4 (as stored)','4'),('Field 5 (as stored)',''),('Field 6 (as stored)','6'),('Field 7 (as stored)',''),
                    ('Android Version','A'),('Codename','B'),('Build version','C')]
        with tempfile.TemporaryDirectory() as directory:
            first = pathlib.Path(directory)/'first'/'version';first.parent.mkdir();first.write_bytes(raw)
            last = pathlib.Path(directory)/'last'/'version';last.parent.mkdir();last.write_text('ignored;later;source;extra')
            with patch.object(parser, 'logfunc') as log:
                headers, rows, source = parser.usagestatsVersion.__wrapped__(SimpleNamespace(get_files_found=lambda:[str(first),str(last)]))
            self.assertEqual(headers, ('Property','Property Value'));self.assertEqual(rows,expected);self.assertEqual(source,str(first))
            self.assertEqual(artGlobals.versionf,'A');self.assertEqual(log.call_count,5)
            self.assertEqual(set(ilapfuncs.identifiers['Usagestats']),{'Android version','Codename','Build version'})
            for label, values in [('Android version',['A','D','G','J','A']),('Codename',['B','E','H','K','B']),('Build version',['C','F','I','L','C'])]:
                observed=ilapfuncs.identifiers['Usagestats'][label]
                self.assertEqual([v['value'] for v in observed],values)
                self.assertTrue(all(v['source_file']=='' and v['artifact']=='usagestatsVersion' for v in observed))

    def test_empty_short_and_unicode(self):
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/'version';path.write_text('\nshort;two\nα;β;γ;δ\n',encoding='utf-8')
            _, rows, _=parser.usagestatsVersion.__wrapped__(SimpleNamespace(get_files_found=lambda:[str(path)]))
            self.assertEqual(rows,[('Android Version','α'),('Codename','β'),('Build version','γ'),('Field 4 (as stored)','δ')])
            path.write_bytes(b'\nonly;two\n');artGlobals.versionf='unchanged'
            _, rows, _=parser.usagestatsVersion.__wrapped__(SimpleNamespace(get_files_found=lambda:[str(path)]))
            self.assertEqual(rows,[]);self.assertEqual(artGlobals.versionf,'unchanged')


if __name__ == '__main__':
    unittest.main()
