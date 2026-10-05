"""Focused binary-decoding tests. Run from ALEAPP with unittest.

Fixtures here are synthetic, not casework and not DF020 corpus validation.
The CRC check is the published crc64 crate vector; XOR fixture uses a
precomputed key independently checked against pydjirecord's table decoder.
"""
import datetime
import math
import struct
import unittest
from scripts.artifacts import djiFlightRecordTxt as module


TIME_MS = 1530000000123


def details():
    result = bytearray(436)
    result[40:48] = b'TestCity'
    struct.pack_into('<qddfifff', result, 91, TIME_MS, -105.0, 40.0,
                     100.0, 20000, 10.0, 5.0, 2.0)
    return bytes(result)


def record(kind, payload, version):
    if version >= 7:
        # Known key for record 5, first byte 65, computed by independent decoder.
        keys = {5: bytes.fromhex('3f1bb88a0f511ff5')}
        key = keys[kind]
        payload = b'\x41' + bytes(b ^ key[i % 8] for i, b in enumerate(payload)) + b'\0'
    return bytes((kind, len(payload))) + payload + b'\xff'


def log(version, records=b''):
    prefix_size = 12 if version < 6 else 100
    prefix = bytearray(prefix_size)
    detail_offset = prefix_size + len(records) if version < 12 else 100
    struct.pack_into('<QHB', prefix, 0, detail_offset, 436, version)
    return bytes(prefix) + (records + details() if version < 12 else details() + records)


def osd(lat=40, lon=-105):
    result = bytearray(50)
    struct.pack_into('<dd7h', result, 0, math.radians(lon), math.radians(lat),
                     123, 30, 40, -10, 25, -35, 905)
    result[36], result[40] = 12, 87
    struct.pack_into('<H', result, 42, 155)
    return bytes(result)


class ParserTests(unittest.TestCase):
    def test_crc_known_vector(self):
        self.assertEqual(module._crc64(0, b'123456789'), 0xE9C6D914C4B8D9CA)  # pylint: disable=protected-access

    def test_units_and_coordinates(self):
        summary, rows = module.parse_txt(log(6, record(1, osd(), 6)))
        row = rows[0]
        self.assertAlmostEqual(row['latitude'], 40)
        self.assertAlmostEqual(row['longitude'], -105)
        self.assertEqual((row['altitude'], row['speed'], row['heading']), (12.3, 5.0, 90.5))
        self.assertEqual((row['satellites'], row['battery'], row['flight_time']), (12, 87, 15.5))
        self.assertIsNone(row['timestamp'])
        self.assertEqual(summary['timestamp'].tzinfo, datetime.timezone.utc)

    def test_version_layouts(self):
        for version in (1, 5, 6, 12):
            payload = struct.pack('<ffq', 5, 2, TIME_MS)
            # v12 XOR is covered separately below.
            records = record(5, b'\0\0' + payload, 6 if version < 7 else 12)
            summary, rows = module.parse_txt(log(version, records))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['timestamp'], summary['timestamp'])

    def test_xor_versions(self):
        for version in (7, 8, 9, 10, 11, 12):
            raw = b'\0\0' + struct.pack('<ffq', 5, 2, TIME_MS)
            _, rows = module.parse_txt(log(version, record(5, raw, version)))
            self.assertEqual(rows[0]['speed'], 5)
            self.assertEqual(rows[0]['distance'], 2)
            self.assertIsNotNone(rows[0]['timestamp'])

    def test_timestamp_attribution(self):
        records = record(1, osd(), 6) + record(5, b'\0\0' + struct.pack('<ffq', 5, 2, TIME_MS), 6) + record(1, osd(), 6)
        _, rows = module.parse_txt(log(6, records))
        self.assertIsNone(rows[0]['timestamp'])
        self.assertEqual(rows[1]['timestamp'], rows[2]['timestamp'])
        self.assertEqual(rows[2]['timestamp_basis'], 'Preceding Custom record')
        self.assertNotIn('latitude', rows[1])

    def test_invalid_timestamp_clears_previous(self):
        good = record(5, b'\0\0' + struct.pack('<ffq', 5, 2, TIME_MS), 6)
        bad = record(5, b'\0\0' + struct.pack('<ffq', 5, 2, -1), 6)
        _, rows = module.parse_txt(log(6, good + bad + record(1, osd(), 6)))
        self.assertIsNone(rows[-1]['timestamp'])

    def test_invalid_gps_not_plotted(self):
        for lat, lon in ((0, 0), (91, 1), (float('nan'), 1)):
            _, rows = module.parse_txt(log(6, record(1, osd(lat, lon), 6)))
            self.assertIsNone(rows[0]['latitude'])
            self.assertEqual(rows[0]['altitude'], 12.3)

    def test_gimbal(self):
        _, rows = module.parse_txt(log(6, record(3, struct.pack('<3h', -450, 10, 900), 6)))
        self.assertEqual((rows[0]['gimbal_pitch'], rows[0]['gimbal_roll'], rows[0]['gimbal_yaw']), (-45, 1, 90))

    def test_home_keeps_position_separate_from_aircraft(self):
        payload = struct.pack('<ddfBBH', math.radians(-105), math.radians(40), 125, 1, 0, 60)
        _, rows = module.parse_txt(log(6, record(2, payload, 6)))
        row = rows[0]
        self.assertAlmostEqual(row['home_latitude'], 40)
        self.assertAlmostEqual(row['home_longitude'], -105)
        self.assertEqual((row['home_altitude'], row['home_recorded'], row['return_height']), (12.5, True, 60))
        self.assertNotIn('latitude', row)

    def test_controller_raw_units_and_buttons(self):
        payload = struct.pack('<5H3B', 1024, 1100, 990, 1010, 1200, 0, 8, 192)
        _, rows = module.parse_txt(log(6, record(4, payload, 6)))
        row = rows[0]
        self.assertEqual((row['rc_aileron'], row['rc_elevator'], row['rc_throttle'], row['rc_rudder'], row['rc_gimbal']), (1024, 1100, 990, 1010, 1200))
        self.assertTrue(row['rc_return'] and row['rc_shutter'] and row['rc_record'])

    def test_smart_battery_offsets_and_units(self):
        payload = bytearray(30)
        struct.pack_into('<H', payload, 0, 340)
        struct.pack_into('<H', payload, 24, 15200)
        payload[26] = 87
        _, rows = module.parse_txt(log(6, record(8, payload, 6)))
        self.assertEqual((rows[0]['battery_voltage'], rows[0]['battery_time'], rows[0]['battery']), (15.2, 340, 87))

    def test_camera_photo_state_is_not_any_nonzero_enum(self):
        for state in range(8):
            payload = bytearray(24)
            payload[0], payload[1], payload[4] = (state << 3) | 64, 2, 1
            struct.pack_into('<H', payload, 21, 45)
            _, rows = module.parse_txt(log(6, record(25, payload, 6)))
            self.assertEqual(rows[0]['camera_photo'], state == 1)
            self.assertEqual((rows[0]['camera_recording'], rows[0]['camera_sd'], rows[0]['camera_record_time']), (True, True, 45))

    def test_short_camera_does_not_invent_extended_fields(self):
        _, rows = module.parse_txt(log(6, record(25, b'\0\0', 6)))
        self.assertNotIn('camera_mode', rows[0])

    def test_new_record_truncation_preserves_payload(self):
        for kind in (2, 4, 8, 25):
            _, rows = module.parse_txt(log(6, record(kind, b'\x01', 6)))
            self.assertTrue(rows[0]['status'].startswith('Short'))
            self.assertEqual(rows[0]['payload_hex'], '01')

    def test_unknown_preserved(self):
        _, rows = module.parse_txt(log(6, record(99, b'abcd', 6)))
        self.assertEqual(rows[0]['payload_hex'], '61626364')

    def test_bad_record_stops_without_resync(self):
        valid = record(3, struct.pack('<3h', -450, 10, 900), 6)
        summary, rows = module.parse_txt(log(6, valid + b'\x01\xfe\0' + valid))
        self.assertEqual(len(rows), 1)
        self.assertEqual(summary['status'], 'Partial parse; see warnings')

    def test_short_payload_keeps_record(self):
        _, rows = module.parse_txt(log(6, record(1, b'abc', 6)))
        self.assertEqual(rows[0]['status'], 'Short OSD payload')

    def test_jpeg_framing(self):
        _, rows = module.parse_txt(log(6, b'\xff\xd8test\xff\xd9' + record(99, b'abc', 6)))
        self.assertEqual([row['type'] for row in rows], [255, 99])

    def test_reject_truncation(self):
        for value in (b'', b'csv,not,evidence', log(6)[:120]):
            with self.assertRaises(ValueError):
                module.parse_txt(value)

    def test_reject_unknown_version(self):
        with self.assertRaises(ValueError):
            module.parse_txt(log(15))

    def test_encrypted_auxiliary_metadata(self):
        # Key independently checked against pydjirecord's CRC table decoder.
        key = bytes.fromhex('e3c6b4f466514c5d')
        info = b'\x01' + struct.pack('<H', len(details())) + details() + b'\0\0'
        payload = b'\x41' + bytes(b ^ key[i % 8] for i, b in enumerate(info))
        auxiliary = b'\0' + struct.pack('<H', len(payload)) + payload
        aux_version = b'\x01\x03\0\x02\0\x03'
        for version in (13, 14):
            for recover in (False, True):
                prefix = bytearray(100)
                start = 100 + len(auxiliary) + len(aux_version)
                struct.pack_into('<QHB', prefix, 0, 0 if recover else start, 436, version)
                summary, rows = module.parse_txt(bytes(prefix) + auxiliary + aux_version + b'encrypted bytes')
                self.assertEqual(rows, [])
                self.assertEqual(summary['city'], 'TestCity')
                self.assertEqual(summary['latitude'], 40)
                self.assertEqual(summary['longitude'], -105)
                self.assertIn('Encrypted', summary['status'])
                self.assertEqual(summary['timestamp'].microsecond, 123000)

    def test_encrypted_truncated_auxiliary(self):
        prefix = bytearray(104)
        struct.pack_into('<QHB', prefix, 0, 110, 436, 14)
        struct.pack_into('<H', prefix, 101, 436)
        with self.assertRaisesRegex(ValueError, 'encrypted'):
            module.parse_txt(bytes(prefix))


if __name__ == '__main__':
    unittest.main()
