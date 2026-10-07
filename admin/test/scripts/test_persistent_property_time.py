"""Matched text observations retain invalid time and source occurrences."""
import datetime
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import persistentProp
from scripts.ilapfuncs import decode_protobuf


def context(root, paths):
    return SimpleNamespace(get_files_found=lambda: paths,
                           get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))


def write(root, relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return str(path)


def varint(value):
    data = bytearray()
    while value > 127:
        data.append((value & 127) | 128)
        value >>= 7
    return bytes(data + bytes([value]))


def field(number, value):
    return varint(number * 8 + 2) + varint(len(value)) + value


def synthetic_wire():
    """Fixture-only schema, not an Android property-store format claim."""
    entry = field(1, b'fixture.name') + field(2, b'\nreboot,1700000000\nreboot,bad\n')
    return field(1, entry)


class PersistentPropertyTimeTest(unittest.TestCase):
    def test_three_rules_raw_values_invalid_then_healthy(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(persistentProp, 'logfunc') as logger:
            root = pathlib.Path(folder)
            content = b'ignored\r\npersist.sys.boot.reason.historyDreboot,0\r\nreboot,factory_reset,-1\nreboot,+001700000000\nreboot,bad\nreboot,\nreboot,999999999999999999999999999999999\nreboot,extra,123\nreboot,1700000001\nreboot,1700000001\n'
            path = write(root, 'data/property/persistent_properties', content)
            headers, rows, source = persistentProp.get_persistentProp.__wrapped__(context(root, [path]))
            self.assertEqual(len(headers), 6)
            self.assertEqual(len(rows), 8)
            self.assertEqual(source, 'data/property/persistent_properties')
            self.assertEqual([r[4] for r in rows], [2, 3, 4, 5, 6, 7, 9, 10])
            self.assertEqual(rows[0][:3], (datetime.datetime.fromtimestamp(0, datetime.timezone.utc), '0', 'persist.sys.boot.reason.historyDreboot'))
            self.assertEqual(rows[1][2], 'reboot factory_reset')
            self.assertEqual(rows[2][1], '+001700000000')
            self.assertTrue(all(r[0] == '' for r in rows[3:6]))
            self.assertEqual(rows[-1][:4], rows[-2][:4])
            self.assertEqual(logger.call_count, 3)

    def test_actual_wire_scanner_limit_and_replacement_text(self):
        wire = synthetic_wire()
        self.assertIsInstance(decode_protobuf(wire)[0], dict)
        with tempfile.TemporaryDirectory() as folder, patch.object(persistentProp, 'logfunc'):
            root = pathlib.Path(folder)
            path = write(root, 'data/property/persistent_properties', wire+b'reboot,\xff\nreboot,1700000001\n')
            _, rows, _ = persistentProp.get_persistentProp.__wrapped__(context(root, [path]))
            self.assertEqual([r[1] for r in rows], ['1700000000', 'bad', '\ufffd', '1700000001'])
            self.assertEqual(rows[2][5], 'reboot,\ufffd')
            self.assertEqual(rows[2][0], '')

    def test_actual_contributors_repeats_and_bounded_diagnostics(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(persistentProp, 'logfunc') as logger:
            root = pathlib.Path(folder)
            first = write(root, 'data/property/persistent_properties', b'reboot,1700000000\n')
            last = write(root, 'other/property/persistent_properties', b'reboot,1700000001\n')
            empty = write(root, 'empty/property/persistent_properties', b'irrelevant\n')
            ctx = context(root, [first, empty, last, first])
            headers, rows, source = persistentProp.get_persistentProp.__wrapped__(ctx)
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual(source, 'data/property/persistent_properties\nother/property/persistent_properties')
            self.assertEqual([r[-1] for r in rows], ['data/property/persistent_properties', 'other/property/persistent_properties', 'data/property/persistent_properties'])
            headers, rows, _ = persistentProp.get_persistentProp.__wrapped__(context(root, [first, empty, first]))
            self.assertEqual(len(headers), 6)
            self.assertEqual(len(rows), 2)
            bad = write(root, 'bad/property/persistent_properties', b'reboot,bad\n')
            ctx = context(root, [bad]);ctx.get_relative_path = lambda p: 'line\n"'+'x'*1000
            persistentProp.get_persistentProp.__wrapped__(ctx)
            message = logger.call_args.args[0]
            self.assertNotIn('\n', message)
            self.assertIn('\\n', message)
            self.assertIn('input line ordinal 1; branch reboot', message)
            self.assertLess(len(message), 450)


if __name__ == '__main__':
    unittest.main()
