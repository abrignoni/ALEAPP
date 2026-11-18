"""Real LevelDB log and table fixtures holding raw signal records, read by all three artifacts."""
import datetime
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest

from scripts.artifacts import appSemloc as module
from scripts.vendor.ccl import ccl_leveldb
from admin.test.scripts.test_fcm_skype_raw_events import varint, field, checksum

STORE = 'com.google.android.gms/app_semanticlocation_rawsignal_db'


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        if not isinstance(path, str):
            raise TypeError('Source-path API requires a string')
        return str(Path(path).relative_to(self.root))


def number(index, value):
    return varint(index << 3) + varint(value & 0xFFFFFFFFFFFFFFFF)


def single(index, value):
    return varint(index << 3 | 5) + struct.pack('<f', value)


def zigzag(value):
    return (value << 1) ^ (value >> 63)


def position(lat=407128000, lng=-740060000, accuracy=12345, altitude=10.5, source=1,
             time=1700000000123, speed=1.5):
    body = (number(1, lat) + number(2, lng) + number(3, accuracy) + single(4, altitude)
            + number(5, source) + number(6, time) + single(7, speed))
    return field(1, field(1, body)) + number(2, time)


def wifi(time=1700000001000, macs=(0x001122334455, 0xAABBCCDDEEFF), levels=(-40, -85)):
    packed_macs = b''.join(varint(mac) for mac in macs)
    packed_levels = b''.join(varint(zigzag(level)) for level in levels)
    body = number(1, time) + field(3, packed_macs) + field(4, packed_levels) + number(6, 2)
    return field(1, field(2, body))


def activity(time=1700000002000, types=(3, 7), confidences=(0.75, 0.25)):
    body = (number(2, time) + field(3, b''.join(varint(t) for t in types))
            + field(4, b''.join(struct.pack('<f', c) for c in confidences)))
    return field(1, field(3, body))


def key(time, kind):
    return struct.pack('>Q', time) + bytes([kind])


RECORDS = [(key(1700000000123, 0), position(), 1),
           (key(1700000000123, 0), position(source=9), 1),  # a later version of one key
           (key(1700000001000, 1), wifi(), 1),
           (key(1700000002000, 2), activity(), 1),
           (key(1700000003000, 0), b'', 0),                  # a deletion
           (b'invalid', b'\x80', 1)]


def write_log(path, records=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    records = RECORDS if records is None else records
    batch = struct.pack('<QI', 0, len(records))
    for rec_key, value, state in records:
        batch += bytes([state]) + varint(len(rec_key)) + rec_key
        if state:
            batch += varint(len(value)) + value
    block = struct.pack('<IHB', checksum(b'\x01' + batch), len(batch), 1) + batch
    path.write_bytes(block)
    return path


def write_table(path):
    """Minimal uncompressed LevelDB table with genuine block and footer encoding."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = [(key(1700000005000, 0) + struct.pack('<Q', 21 << 8 | 1), position(time=1700000005000))]

    def block(items):
        data = b''
        for item_key, value in items:
            data += varint(0) + varint(len(item_key)) + varint(len(value)) + item_key + value
        data += struct.pack('<II', 0, 1)
        return data + b'\0' + struct.pack('<I', checksum(data + b'\0')), len(data)

    data, size = block(entries)
    meta, meta_size = block([])
    index, index_size = block([(entries[-1][0], varint(0) + varint(size))])
    footer = (varint(len(data)) + varint(meta_size) + varint(len(data) + len(meta))
              + varint(index_size))
    footer = footer.ljust(40, b'\0') + struct.pack('<Q', ccl_leveldb.LdbFile.MAGIC)
    path.write_bytes(data + meta + index + footer)
    return path


class AppSemlocRawSignalsTest(unittest.TestCase):
    def test_positions_decode_sourced_fields_and_keep_every_version(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_log(Path(folder) / f'data/data/{STORE}/000001.log')
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            headers, rows, source = module.get_appSemloc.__wrapped__(Context(folder, [path]))
            self.assertEqual(len(headers), 11)
            self.assertEqual(source, str(path.parent))
            self.assertEqual(len(rows), 2)
            first = rows[0]
            self.assertEqual(first[0], datetime.datetime(2023, 11, 14, 22, 13, 20, 123000,
                                                         tzinfo=datetime.timezone.utc))
            self.assertEqual(first[1:4], (40.7128, -74.006, 12.345))
            self.assertAlmostEqual(first[4], 10.5)
            self.assertEqual(first[5], 'GPS')
            self.assertAlmostEqual(first[6], 1.5)
            self.assertEqual(first[8], key(1700000000123, 0).hex())
            self.assertEqual(first[9], 'Log')
            self.assertEqual(rows[1][5], 'Unknown (9)')
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)

    def test_wifi_scan_macs_and_signed_levels(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_log(Path(folder) / f'data/data/{STORE}/000001.log')
            headers, rows, _ = module.get_appSemlocWifiScans.__wrapped__(Context(folder, [path]))
            self.assertEqual(len(headers), 7)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], datetime.datetime(2023, 11, 14, 22, 13, 21,
                                                         tzinfo=datetime.timezone.utc))
            self.assertEqual(rows[0][1], 2)
            self.assertEqual(rows[0][2], '00:11:22:33:44:55 -40, aa:bb:cc:dd:ee:ff -85')

    def test_activity_record_names_and_top_candidate(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_log(Path(folder) / f'data/data/{STORE}/000001.log')
            headers, rows, _ = module.get_appSemlocActivityRecords.__wrapped__(
                Context(folder, [path]))
            self.assertEqual(len(headers), 8)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][1:4], ('STILL', 0.75, 'STILL 0.75, WALKING 0.25'))

    def test_unreadable_table_file_is_skipped_and_the_rest_is_read(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Path(folder) / f'data/data/{STORE}'
            table = write_table(store / '000002.ldb')
            log = write_log(store / '000003.log')
            broken = store / '000004.ldb'
            broken.write_bytes(table.read_bytes()[:-8])  # no footer magic, as a cut-off write
            headers, rows, _ = module.get_appSemloc.__wrapped__(
                Context(folder, [table, log, broken]))
            self.assertEqual(len(rows), 3)
            self.assertEqual([row[9] for row in rows], ['Ldb', 'Log', 'Log'])
            self.assertEqual(len(headers), 11)

    def test_storage_views_read_once_and_other_users_get_a_source_column(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = write_log(root / f'data/data/{STORE}/000001.log')
            view = write_log(root / f'data/user/0/{STORE}/000001.log')
            other = write_log(root / f'data/user/10/{STORE}/000001.log')
            headers, rows, source = module.get_appSemloc.__wrapped__(
                Context(root, [first, view]))
            self.assertEqual(len(rows), 2)
            self.assertEqual(len(headers), 11)
            headers, rows, source = module.get_appSemloc.__wrapped__(
                Context(root, [first, view, other]))
            self.assertEqual(len(rows), 4)
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual(len(source.splitlines()), 2)
            self.assertTrue(all(not Path(row[-1]).is_absolute() for row in rows))

    def test_non_data_files_and_empty_store_give_no_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Path(folder) / f'data/data/{STORE}'
            store.mkdir(parents=True)
            current = store / 'CURRENT'
            current.write_text('MANIFEST-000001\n')
            headers, rows, source = module.get_appSemloc.__wrapped__(Context(folder, [current]))
            self.assertEqual(rows, [])
            self.assertEqual(source, '')
            self.assertEqual(len(headers), 11)


if __name__ == '__main__':
    unittest.main()
