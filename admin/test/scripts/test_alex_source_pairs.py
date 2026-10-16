"""Source pairs are retained without expanding device attributes."""
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.alexDeviceInfo import alex_device_info

FIXTURE = [
    {'format': 'PRFS', 'duplicate': 'first', 'first_dash': '-'},
    {'duplicate': 7, 'hyphen': '-', 'zero': 0, 'false': False, 'null': None, 'literal': 'None'},
    {'duplicate': 'last', 'nested': {'items': [0, False, None, '-']}, 'list': [1, 'two', {'k': None}]},
]


def write_info(path, value):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')
    return path


class AlexSourcePairsTest(unittest.TestCase):
    def test_native_values_order_duplicates_and_unchanged_device_subset(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_info(pathlib.Path(folder) / 'device_info_alex.json', FIXTURE)
            with patch('scripts.artifacts.alexDeviceInfo.device_info') as device:
                headers, rows, source = alex_device_info.__wrapped__(context(folder, [path]))
            expected = [(key, value) for obj in FIXTURE for key, value in obj.items()]
            self.assertEqual(rows, expected)
            self.assertEqual(headers, ('Key', 'Value'))
            self.assertEqual(source, str(path))
            for report, original in zip(rows, expected):
                self.assertIs(type(report[1]), type(original[1]))
            old_subset = [('ADB Live (ALEX)', key, value) for obj in FIXTURE[1:] for key, value in obj.items() if value != '-']
            self.assertEqual([call.args for call in device.call_args_list], old_subset)
            self.assertEqual(len(rows), 12)
            self.assertEqual(len(old_subset), 8)

    def test_empty_invalid_shapes_and_invalid_json_diagnostics(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'device_info_alex.json'
            for value, expected in [([], []), ({'not': 'a list'}, []), (['not an object', {'valid': 2}], [('valid', 2)])]:
                write_info(path, value)
                with patch('scripts.artifacts.alexDeviceInfo.device_info') as device, patch('scripts.artifacts.alexDeviceInfo.logfunc') as log:
                    _headers, rows, _source = alex_device_info.__wrapped__(context(folder, [path]))
                self.assertEqual(rows, expected)
                self.assertEqual(bool(log.call_args_list), value != [])
                if isinstance(value, dict):device.assert_not_called()
                if expected:device.assert_called_once_with('ADB Live (ALEX)', 'valid', 2)
            path.write_text('{broken', encoding='utf-8')
            with patch('scripts.artifacts.alexDeviceInfo.logfunc') as log:
                _headers, rows, _source = alex_device_info.__wrapped__(context(folder, [path]))
            self.assertEqual(rows, [])
            self.assertTrue(any('cannot read device_info_alex.json' in call.args[0] for call in log.call_args_list))
