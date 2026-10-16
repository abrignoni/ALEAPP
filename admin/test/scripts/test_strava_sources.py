"""Actual FIT records retain their file origins and route exports."""
import datetime
import io
import pathlib
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
import fitdecode
from PIL import Image
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.StravaGPS import get_gps


def make_fit(path, offset=0):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = 1073000000 + offset
    payload = bytes([0x40, 0, 0]) + struct.pack('<H', 20) + bytes([3, 253, 4, 0x86, 0, 4, 0x85, 1, 4, 0x85])
    for index in range(3):
        payload += bytes([0]) + struct.pack('<Iii', timestamp + index * 30, 450000000 + offset + index * 1000, -800000000 + index * 2000)
    payload += bytes([0x41, 0, 0]) + struct.pack('<H', 18) + bytes([4, 2, 4, 0x86, 5, 1, 0, 7, 4, 0x86, 9, 4, 0x86])
    payload += bytes([1]) + struct.pack('<IBII', timestamp, 1, 120000, 123400)
    header = struct.pack('<BBHI4s', 14, 0x20, 2100, len(payload), b'.FIT')
    header += struct.pack('<H', fitdecode.utils.compute_crc(header))
    data = header + payload
    path.write_bytes(data + struct.pack('<H', fitdecode.utils.compute_crc(data)))
    return path


class StravaSourcesTest(unittest.TestCase):
    def test_actual_fit_rows_routes_and_conditional_origins(self):
        with tempfile.TemporaryDirectory() as folder:
            first = make_fit(pathlib.Path(folder) / 'data/data/com.strava/files/a.fit')
            second = make_fit(pathlib.Path(folder) / 'data/user/10/com.strava/files/a.fit', 86400)
            exports = []
            def checkin(source, data, name, **_kwargs):
                exports.append((source, data, name))
                return name
            with patch('scripts.artifacts.StravaGPS.check_in_embedded_media', side_effect=checkin):
                headers, rows, sources = get_gps.__wrapped__(context(folder, [first, second]))
                single_headers, repeated, single_source = get_gps.__wrapped__(context(folder, [first, first]))
            self.assertEqual(headers[:2], (('Start Time', 'datetime'), ('End Time', 'datetime')))
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual([row[-1] for row in rows], [str(p.relative_to(folder)) for p in [first, second]])
            self.assertEqual(set(sources.splitlines()), {str(first), str(second)})
            self.assertNotIn('Source File', single_headers)
            self.assertEqual(repeated[0], repeated[1])
            self.assertEqual(single_source, str(first))
            self.assertEqual(rows[0][1] - rows[0][0], datetime.timedelta(seconds=120))
            self.assertEqual(rows[0][2:5], ('running', 2, 1.23))
            self.assertEqual(rows[1][0] - rows[0][0], datetime.timedelta(days=1))
            for source, data, name in exports:
                self.assertIn(source, [str(first), str(second)])
                if name.endswith('.png'):
                    Image.open(io.BytesIO(data)).load()
                else:
                    tree = ET.fromstring(data)
                    self.assertEqual(len(tree.find('.//{*}coordinates').text.strip().split()), 3)

    def test_failed_last_fit_cannot_replace_successful_source(self):
        with tempfile.TemporaryDirectory() as folder:
            first = make_fit(pathlib.Path(folder) / 'good.fit')
            bad = pathlib.Path(folder) / 'bad.fit'
            bad.write_bytes(b'invalid FIT')
            with patch('scripts.artifacts.StravaGPS.check_in_embedded_media', return_value='ref'), patch('scripts.artifacts.StravaGPS.logfunc') as log:
                headers, rows, source = get_gps.__wrapped__(context(folder, [first, bad]))
            self.assertEqual(len(rows), 1)
            self.assertEqual(source, str(first))
            self.assertNotIn('Source File', headers)
            self.assertTrue(any(str(bad) in call.args[0] for call in log.call_args_list))
