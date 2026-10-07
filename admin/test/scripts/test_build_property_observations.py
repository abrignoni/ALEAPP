"""Actual property bytes retain occurrences without changing legacy identity output."""
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import build as parser, artGlobals
from scripts.ilapfuncs import OutputParameters

KEYS = ['ro.product.vendor.manufacturer','ro.product.system.manufacturer',
        'ro.product.vendor.brand','ro.product.system.brand','ro.product.vendor.model',
        'ro.product.system.model','ro.product.vendor.device','ro.product.system.device',
        'ro.vendor.build.version.release','ro.build.version.release',
        'ro.vendor.build.version.sdk','ro.build.version.sdk','ro.system.build.version.release']


def fixture(root):
    vendor=root/'vendor/build.prop';system=root/'system/build.prop'
    vendor.parent.mkdir(parents=True);system.parent.mkdir(parents=True)
    records=[b'# comment\r\n']+[key.encode()+b'=value'+str(i).encode()+b'\r\n' for i,key in enumerate(KEYS)]
    records += [b'ro.product.vendor.brand=\n',b'ro.product.vendor.model=invalid\xff\r',
                b'ro.product.vendor.device=one=two\n',b'ro.build.version.sdk=inside\x0bvalue\n',b'unknown=omit\n']
    vendor.write_bytes(b''.join(records));system.write_bytes(b'ro.build.version.release=system\nro.build.version.release=system\n')
    return vendor,system,records


def context(root,paths):
    return SimpleNamespace(get_files_found=lambda:[str(p) for p in paths],get_relative_path=lambda p:str(pathlib.Path(p).relative_to(root)))


class BuildPropertyObservationsTest(unittest.TestCase):
    def test_bytes_keys_occurrences_and_no_sideeffects(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);vendor,system,records=fixture(root);original=artGlobals.versionf;artGlobals.versionf='keep'
            try:
                with patch.object(parser,'logfunc') as log,patch.object(parser,'logdevinfo') as dev:
                    headers,rows,source=parser.get_build_property_observations.__wrapped__(context(root,[system,vendor,system]))
                self.assertEqual(len(headers),6);self.assertEqual(source,'vendor/build.prop\nsystem/build.prop');self.assertEqual(len(rows),21)
                self.assertEqual([r[0] for r in rows[:13]],KEYS)
                self.assertEqual([r[3] for r in rows[:13]],list(range(2,15)))
                self.assertEqual([bytes.fromhex(r[4]) for r in rows[:17]],records[1:18])
                self.assertEqual([r[1] for r in rows[13:17]],['','invalid\ufffd','one=two','inside\x0bvalue'])
                self.assertEqual([r[2] for r in rows[-4:]],[2,2,3,3]);self.assertEqual(artGlobals.versionf,'keep');log.assert_not_called();dev.assert_not_called()
                headers,rows,source=parser.get_build_property_observations.__wrapped__(context(root,[vendor,vendor]))
                self.assertEqual(len(headers),5);self.assertEqual(len(rows),34);self.assertEqual(source,'vendor/build.prop')
            finally:artGlobals.versionf=original

    def test_actual_legacy_device_file_and_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);vendor,system,_=fixture(root);output=root/'device.html';output.write_text('prefix\n');oldpath=getattr(OutputParameters,'screen_output_file_path_devinfo',None);oldversion=artGlobals.versionf
            OutputParameters.screen_output_file_path_devinfo=str(output)
            try:
                for initial in [0,'already-known']:
                    artGlobals.versionf=initial;output.write_text('prefix\n')
                    with patch.object(parser,'logfunc') as log:
                        _,rows,source=parser.get_build.__wrapped__(context(root,[system,vendor]))
                    expected=[('Manufacturer','value0'),('Brand','value2'),('Model','value4'),('Device','value6'),('Android Version','value8'),('SDK','value10'),('Version Release','value12')]
                    self.assertEqual(rows,expected);self.assertEqual(source,str(vendor));self.assertEqual(artGlobals.versionf,'value8' if initial==0 else initial);log.assert_called_once_with('Android version per build.props: value8')
                    before=output.read_bytes();parser.get_build_property_observations.__wrapped__(context(root,[system,vendor]));self.assertEqual(output.read_bytes(),before)
                    self.assertEqual(before.count(b'<br>'),7)
            finally:
                if oldpath is None:del OutputParameters.screen_output_file_path_devinfo
                else:OutputParameters.screen_output_file_path_devinfo=oldpath
                artGlobals.versionf=oldversion

    def test_unreadable_cap_empty_and_newline_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);path=root/'system/build.prop';path.parent.mkdir();path.write_bytes(b'ro.build.version.release=one\rro.build.version.sdk=2\r\nunknown=x\nro.system.build.version.release=\n')
            absent=[root/f'absent\n{i}/system/build.prop' for i in range(12)]
            with patch.object(parser,'logfunc') as log:
                _,rows,_=parser.get_build_property_observations.__wrapped__(context(root,absent+[path]))
            self.assertEqual([r[3] for r in rows],[1,2,4]);self.assertEqual(log.call_count,11);self.assertIn('total=12, shown=10, suppressed=2',log.call_args.args[0]);self.assertTrue(all('\n' not in call.args[0] and str(root) not in call.args[0] for call in log.call_args_list))
            path.write_bytes(b'unknown=x\n');headers,rows,source=parser.get_build_property_observations.__wrapped__(context(root,[path]));self.assertEqual((len(headers),rows,source),(5,[],''))

    def test_unreadable_diagnostics_reject_absolute_and_escape_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory)
            origins=['/private/secret/build.prop',r'C:\private\secret\build.prop',
                     r'\\server\secret\build.prop',r'\private\secret\build.prop',
                     'relative/<script>&"\n\t\x01/é/build.prop','relative/'+('x'*1000)]
            paths=[root/f'missing{i}/build.prop' for i in range(len(origins))]
            mapping={str(path):origin for path,origin in zip(paths,origins)}
            ctx=SimpleNamespace(get_files_found=lambda:[str(path) for path in paths],
                                get_relative_path=lambda path:mapping[path])
            with patch.object(parser,'logfunc') as log:
                _,rows,source=parser.get_build_property_observations.__wrapped__(ctx)
            self.assertEqual((rows,source),([],''))
            messages=[call.args[0] for call in log.call_args_list]
            for message in messages[:4]:
                self.assertIn('[unavailable relative source]',message)
                self.assertNotIn('secret',message)
            for message in messages[:-1]:
                displayed=message.split('source ',1)[1]
                self.assertLessEqual(len(displayed),240)
                self.assertTrue(all(ch not in displayed for ch in '<>&\n\t\x01'))
                self.assertNotIn(str(root),message)
            self.assertIn(r'\u003cscript\u003e\u0026',messages[4])
            self.assertIn(r'\n',messages[4]);self.assertIn(r'\u00e9',messages[4])
            self.assertIn('total=6, shown=6, suppressed=0',messages[-1])


if __name__=='__main__':
    unittest.main()
