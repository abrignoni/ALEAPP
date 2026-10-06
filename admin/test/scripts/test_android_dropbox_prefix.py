"""Bounded decompressed prefixes retain accepted bytes and disclose unread remainders."""
import gzip
import pathlib
import random
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import androidDropbox as module  # pylint: disable=wrong-import-position
from scripts.artifacts.androidDropbox import (  # pylint: disable=wrong-import-position
    _READ_CAP, _read_prefix, _read, _tombstone_proto_fields,
)


def context(root, paths):
    return SimpleNamespace(get_files_found=lambda: [str(p) for p in paths],
                           get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))


def make_entries(root, malformed=False):
    folder = pathlib.Path(root) / 'data/system/dropbox'
    folder.mkdir(parents=True, exist_ok=True)
    boot = b'Build: Constructed\nHardware: hardware\n\n[[TRUNCATED]]\n'
    process = b'Process: process\nPID: 42\nTimestamp: 2024-01-01 00:00:00.000+0000\n\nFailure\n'
    payloads = {
        'SYSTEM_BOOT@1700000000000.txt.gz': gzip.compress(boot + b'x' * (_READ_CAP + 20)),
        'SYSTEM_RESTART@1700000001000.txt.gz': gzip.compress(b'Build: LaterMarker\n\n' + b'x' * _READ_CAP + b'[[TRUNCATED]]'),
        'SYSTEM_BOOT@1700000002000.lost': b'',
        'data_app_crash@1700000003000.txt.gz': gzip.compress(process + random.Random(4).randbytes(_READ_CAP + 20000)),
        'data_app_crash@1700000004000.lost': b'',
        'event_log@1700000005000.txt.gz': gzip.compress(b'first line\n' + b'x' * (_READ_CAP + 20)),
        'event_data@1700000006000.dat': b'not-read',
        'event_log@1700000007000.lost': b'',
    }
    if malformed:
        data = bytearray(gzip.compress(b'Build: Partial\n\n' + b'x' * (128 * 1024)))
        data[-8] ^= 1
        payloads['SYSTEM_BOOT@1700000008000.txt.gz'] = data
        payloads['data_app_crash@1700000009000.txt.gz'] = b'not gzip'
        payloads['event_log@1700000010000.txt.gz'] = b'\x1f\x8b\x08'
    paths = []
    for name, data in payloads.items():
        p = folder / name
        p.write_bytes(data)
        paths.append(p)
    return paths


class DropboxPrefixTest(unittest.TestCase):
    def test_plain_gzip_empty_exact_and_concatenated_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / 'entry'
            for data in [b'', b'a' * 63, b'a' * 64, b'a' * 65]:
                for compressed in [False, True]:
                    p = path.with_suffix('.gz' if compressed else '.txt')
                    p.write_bytes(gzip.compress(data) if compressed else data)
                    prefix, status = _read_prefix(str(p), 64)
                    self.assertEqual(prefix, data[:64])
                    self.assertEqual(status, 'Complete' if len(data) <= 64 else 'Capped prefix (remainder unchecked)')
            p = path.with_suffix('.gz')
            p.write_bytes(gzip.compress(b'a' * 40) + gzip.compress(b'b' * 40))
            self.assertEqual(_read_prefix(str(p), 64), (b'a' * 40 + b'b' * 24, 'Capped prefix (remainder unchecked)'))
            self.assertEqual(_read_prefix(str(p), 80), (b'a' * 40 + b'b' * 40, 'Complete'))

    def test_read_requests_and_accepted_decompressed_bytes_are_bounded(self):
        with tempfile.TemporaryDirectory() as folder:
            p = pathlib.Path(folder) / 'entry.gz'
            p.write_bytes(gzip.compress(b'x' * (96 * 1024)))
            calls = []
            original = gzip.GzipFile.read
            def tracked(stream, size=-1):
                data = original(stream, size)
                calls.append((size, len(data)))
                return data
            with patch.object(gzip.GzipFile, 'read', tracked), patch.object(gzip, 'decompress', side_effect=AssertionError('whole decompression')):
                prefix, status = _read_prefix(str(p), 8192)
            self.assertEqual((len(prefix), status), (8192, 'Capped prefix (remainder unchecked)'))
            self.assertEqual(sum(length for _, length in calls), 8193)
            self.assertTrue(all(0 < size <= 64 * 1024 for size, _ in calls))

    def test_actual_trailer_crc_and_header_errors_keep_only_accepted_prefixes(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(module, 'logfunc') as log:
            p = pathlib.Path(folder) / 'entry.gz'
            payload = b'header\n' + b'x' * (128 * 1024)
            valid = gzip.compress(payload)
            wrong_crc = bytearray(valid)
            wrong_crc[-8] ^= 1
            for data in [wrong_crc, valid[:-4], valid[:-50]]:
                p.write_bytes(data)
                prefix, status = _read_prefix(str(p), 256 * 1024)
                self.assertTrue(prefix)
                self.assertEqual(prefix, payload[:len(prefix)])
                self.assertEqual(status, 'Partial prefix (read failed)')
            p.write_bytes(b'\x1f\x8b\x08')
            self.assertEqual(_read_prefix(str(p), 64), (b'', 'Read failed'))
            p.unlink()
            self.assertEqual(_read_prefix(str(p), 64), (b'', 'Read failed'))
            self.assertTrue(log.called)

    def test_public_rows_marker_and_status_are_separate(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(module, 'logfunc'):
            paths = make_entries(folder, malformed=True)
            ctx = context(folder, paths)
            headers, rows, _ = module.dropbox_boot_records.__wrapped__(ctx)
            records = {row[headers.index('Source File')]: dict(zip([h[0] if isinstance(h, tuple) else h for h in headers], row)) for row in rows}
            first = next(v for k, v in records.items() if k.endswith('0000.txt.gz'))
            later = next(v for k, v in records.items() if k.endswith('1000.txt.gz'))
            self.assertEqual(first['Build'], 'Constructed')
            self.assertTrue(first['Truncated'])
            self.assertFalse(later['Truncated'])
            self.assertEqual(later['Content Read Status'], 'Capped prefix (remainder unchecked)')
            self.assertTrue(any(row['Content Read Status'] == 'Partial prefix (read failed)' for row in records.values()))
            headers, rows, _ = module.dropbox_process_errors.__wrapped__(ctx)
            self.assertEqual(headers[:2], (('Timestamp', 'datetime'), ('Reported At', 'datetime')))
            self.assertTrue(any(row[headers.index('Content Read Status')] == 'Read failed' for row in rows))
            headers, rows, _ = module.dropbox_other_entries.__wrapped__(ctx)
            self.assertEqual({row[headers.index('Content Read Status')] for row in rows},
                             {'Capped prefix (remainder unchecked)', 'Content lost', 'Not read (binary)', 'Read failed'})

    def test_uncapped_binary_and_anr_paths_keep_existing_decode_behavior(self):
        with tempfile.TemporaryDirectory() as folder:
            p = pathlib.Path(folder) / 'entry.gz'
            protobuf = b'\x4a\x07process\x28\x2a'
            p.write_bytes(gzip.compress(protobuf))
            original = gzip.decompress
            with patch.object(gzip, 'decompress', wraps=original) as decompress:
                self.assertEqual(_read(str(p), cap=None), protobuf)
                self.assertEqual(_tombstone_proto_fields(protobuf)['process'], 'process')
                self.assertEqual(_tombstone_proto_fields(protobuf)['pid'], 42)
                decompress.assert_called_once()
            anr = pathlib.Path(folder) / 'data/anr/anr_2024-01-01-00-00-00-000'
            anr.parent.mkdir(parents=True)
            anr.write_text('Subject: subject\n----- pid 42 at 2024-01-01 00:00:00 -----\nCmd line: process\n')
            _, rows, _ = module.android_anr_traces.__wrapped__(context(folder, [anr]))
            self.assertEqual(rows[0][1:5], ('subject', 'process', '42', 1))


if __name__ == '__main__':
    unittest.main()
