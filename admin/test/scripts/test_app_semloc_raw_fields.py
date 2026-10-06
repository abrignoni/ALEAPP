"""Actual LevelDB log/table and protobuf fixtures test structure, not field meanings."""
import collections
import datetime
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from scripts.artifacts import appSemloc as module
from scripts.ccl import ccl_leveldb
from admin.test.scripts.test_fcm_skype_raw_events import varint, field, checksum


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
    return varint(index << 3) + varint(value)


def payload(one=123456789, two=987654321, three=1234, six=1700000000123):
    return field(1, field(1, number(1, one) + number(2, two) + number(3, three) + number(6, six)))


def write_log(path):
    """Valid write batches include repeats, old versions, zeros and undecodable values."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [(b'\xff\0key', payload(), 1), (b'\xff\0key', payload(one=456), 1),
               (b'zero', payload(0, 0, 0, 0), 1),
               (b'huge-time', payload(six=2**63-1), 1),
               (b'deleted', b'', 0), (b'invalid', b'\x80', 1),
               (b'missing', field(1, field(1, number(1, 5))), 1),
               (b'wrong-type', field(1, field(1, field(1, b'text') + number(2, 2)
                                                 + number(3, 3) + number(6, 4))), 1)]
    batch = struct.pack('<QI', 0, len(records))
    for key, value, state in records:
        batch += bytes([state]) + varint(len(key)) + key
        if state:
            batch += varint(len(value)) + value
    block = struct.pack('<IHB', checksum(b'\x01'+batch), len(batch), 1) + batch
    path.write_bytes(block + block)  # Exact duplicate observations remain visible.
    return path


def write_table(path):
    """Minimal uncompressed LevelDB table with genuine block/footer encoding."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = [struct.pack('<Q', 14 << 8 | 1), b'a'+struct.pack('<Q', 11 << 8 | 1),
            b'b'+struct.pack('<Q', 12 << 8 | 1), b'c'+struct.pack('<Q', 13 << 8)]
    entries = list(zip(keys, [payload(one=789), payload(), payload(one=456), b'']))

    def block(items):
        data = b''
        for key, value in items:
            data += varint(0) + varint(len(key)) + varint(len(value)) + key + value
        data += struct.pack('<II', 0, 1)
        return data + b'\0' + struct.pack('<I', checksum(data+b'\0')), len(data)

    data, size = block(entries)
    meta, meta_size = block([])
    index, index_size = block([(keys[-1], varint(0)+varint(size))])
    footer = varint(len(data))+varint(meta_size)+varint(len(data)+len(meta))+varint(index_size)
    footer = footer.ljust(40, b'\0') + struct.pack('<Q', ccl_leveldb.LdbFile.MAGIC)
    path.write_bytes(data + meta + index + footer)
    return path


class AppSemlocRawFieldsTest(unittest.TestCase):
    def test_actual_log_all_versions_raw_values_and_zero_dates(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_log(Path(folder)/'data/user/0/com.google.android.gms/app_semanticlocation_rawsignal_db/000001.log')
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            headers, rows, source = module.get_appSemloc.__wrapped__(Context(folder, [path]))
            self.assertEqual(len(headers), 13)
            self.assertEqual(len(rows), 8)
            self.assertEqual(source, str(path.parent))
            self.assertEqual(rows[:4], rows[4:])
            self.assertEqual(rows[0][1:9], (1700000000123, 0, b'\xff\0key'.hex(), 'Live', 'Log',
                                          123456789, 987654321, 1234))
            self.assertEqual(rows[1][3], rows[0][3])
            self.assertEqual(rows[1][2], 1)
            self.assertEqual(rows[1][6], 456)
            self.assertEqual(rows[0][0], datetime.datetime(2023, 11, 14, 22, 13, 20, 123000,
                                                         tzinfo=datetime.timezone.utc))
            self.assertEqual(rows[0][9:12], (123456789/1e7, 987654321/1e7, 1234/1000))
            self.assertEqual(rows[2][:2], ('', 0))
            self.assertEqual(rows[2][6:12], (0, 0, 0, 0.0, 0.0, 0.0))
            self.assertEqual(rows[3][:2], ('', 2**63-1))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
            with ccl_leveldb.RawLevelDb(path.parent) as db:
                records = list(db.iterate_records_raw())
            self.assertEqual(len(records), 16)
            self.assertEqual(collections.Counter(r.state.name for r in records), {'Live': 14, 'Deleted': 2})

    def test_actual_table_raw_internal_key_state_and_origin(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_table(Path(folder)/'db/000002.ldb')
            before = path.read_bytes()
            with ccl_leveldb.RawLevelDb(path.parent) as db:
                records = list(db.iterate_records_raw())
            self.assertEqual([r.state.name for r in records], ['Unknown', 'Live', 'Live', 'Deleted'])
            self.assertEqual([r.seq for r in records], [14, 11, 12, 13])
            headers, rows, _ = module.get_appSemloc.__wrapped__(Context(folder, [path]))
            self.assertEqual(len(headers), 13)
            self.assertEqual(len(rows), 3)
            self.assertEqual([r[4] for r in rows], ['Unknown', 'Live', 'Live'])
            self.assertTrue(all(r[5] == 'Ldb' for r in rows))
            self.assertEqual([r[3] for r in rows], [r.key.hex() for r in records if r.value])
            self.assertTrue(all(r[-1] == 'db/000002.ldb' for r in rows))
            self.assertEqual(path.read_bytes(), before)

    def test_combined_directories_only_and_file_order_keep_all_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = [write_table(root/'prefix/data/user/10/com.google.android.gms/app_semanticlocation_rawsignal_db/000002.ldb'),
                     write_log(root/'data/user/0/com.google.android.gms/app_semanticlocation_rawsignal_db/000001.log')]
            headers, rows, source = module.get_appSemloc.__wrapped__(Context(root, [*files, files[0]]))
            self.assertEqual(len(headers), 14)
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual(len(rows), 11)
            self.assertEqual(source.splitlines(), [str(p.parent) for p in files])
            self.assertEqual([r[-1] for r in rows[:3]], [str(files[0].relative_to(root))]*3)
            self.assertEqual([r[-1] for r in rows[3:]], [str(files[1].relative_to(root))]*8)
            self.assertTrue(all(not Path(r[-1]).is_absolute() for r in rows))

    def test_multiple_files_one_directory_preserve_library_order_without_source_column(self):
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder)/'db'
            table = write_table(parent/'000002.ldb')
            log = write_log(parent/'000001.log')
            headers, rows, source = module.get_appSemloc.__wrapped__(Context(folder, [table, log]))
            self.assertEqual(len(headers), 13)
            self.assertEqual(len(rows), 11)
            self.assertEqual([r[5] for r in rows], ['Log']*8 + ['Ldb']*3)
            self.assertEqual(source, str(parent))

    def test_unexpected_iteration_failure_propagates_and_closes_actual_reader(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_log(Path(folder)/'db/000001.log')
            data = bytearray(path.read_bytes())
            data[6] = 2  # First fragment followed by Full is a malformed log sequence.
            path.write_bytes(data)
            original = ccl_leveldb.RawLevelDb.close
            closed = []

            def close(reader):
                closed.append(reader.in_dir_path)
                original(reader)

            with patch.object(ccl_leveldb.RawLevelDb, 'close', close):
                with self.assertRaises(ValueError):
                    module.get_appSemloc.__wrapped__(Context(folder, [path]))
            self.assertEqual(closed, [path.parent])

    def test_empty_failed_directory_does_not_add_source_and_reader_closes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = write_log(root/'good/000001.log')
            empty = root/'empty/LOG';empty.parent.mkdir();empty.write_bytes(b'')
            missing = root/'missing/LOG'
            original = ccl_leveldb.RawLevelDb.close
            closed = []

            def close(reader):
                closed.append(reader.in_dir_path)
                original(reader)

            with patch.object(ccl_leveldb.RawLevelDb, 'close', close):
                headers, rows, source = module.get_appSemloc.__wrapped__(Context(root, [missing,empty,path]))
            self.assertEqual(len(headers), 13)
            self.assertEqual(len(rows), 8)
            self.assertEqual(source, str(path.parent))
            self.assertEqual(closed, [empty.parent, path.parent])


if __name__ == '__main__':
    unittest.main()
