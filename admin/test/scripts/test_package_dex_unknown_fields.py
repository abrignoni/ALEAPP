"""Actual protobuf wire fields, bounded summaries and unchanged known projections."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import packageDexUsage as artifact  # pylint: disable=wrong-import-position


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def varint(value):
    out = bytearray()
    while value > 127:
        out.append((value & 127) | 128)
        value >>= 7
    return bytes(out + bytes([value]))


def field(number, wire, value):
    tag = varint((number << 3) | wire)
    if wire == 0:
        return tag + varint(value)
    if wire == 2:
        return tag + varint(len(value)) + value
    return tag + value


def unknowns():
    return (field(90, 0, 7) + field(91, 1, b'SECRET64') +
            field(92, 2, b'PAYLOAD_SECRET\n\x00') + field(93, 5, b'HIDE') + field(90, 0, 8))


def fixture(with_unknown=False):
    extra = unknowns() if with_unknown else b''
    owner = b'example.owner'
    def primary_record(loader, stamp):
        return field(1, 2, loader) + field(2, 0, 1) + field(3, 0, stamp) + extra
    primary = (field(1, 2, b'/data/app/owner/base.apk') +
               field(2, 2, primary_record(owner, 1700000000000)) * 2 +
               field(2, 2, primary_record(b'example.other', 1700000000001)) + extra)
    secondary = b''
    for index in range(3):
        user = b'' if index == 0 else field(2, 2, (field(1, 0, 10) if index == 2 else b'') + extra)
        record = (field(1, 2, b'example.loader') + field(3, 2, b'PCL[]') +
                  field(4, 2, b'arm64-v8a') + field(5, 0, 1700000000000 + index) + extra)
        message = field(1, 2, f'/data/user/0/owner/secondary{index}.dex'.encode()) + user + field(3, 2, record) + extra
        secondary += field(3, 2, message)
    package = field(1, 2, owner) + field(2, 2, primary) + secondary + extra
    return field(1, 2, package) + extra


def write_store(root, data, tenant=''):
    path = Path(root) / tenant / 'data/system/package-dex-usage.pb'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o444)
    return path


class TestUnknownFields(unittest.TestCase):
    def test_all_schema_scopes_and_same_known_rows(self):
        with tempfile.TemporaryDirectory() as root:
            known = write_store(root, fixture(), 'known')
            unknown = write_store(root, fixture(True), 'unknown')
            for function in [artifact.package_dex_usage_app_code,
                             artifact.package_dex_usage_cross_package,
                             artifact.package_dex_usage_secondary]:
                with patch.object(artifact, 'logfunc') as log:
                    headers, rows, _ = function.__wrapped__(Context(root, [known]))
                log.assert_not_called()
                with patch.object(artifact, 'logfunc') as log:
                    new_headers, new_rows, sources = function.__wrapped__(Context(root, [unknown]))
                self.assertEqual(headers, new_headers)
                self.assertEqual([r[:-1] for r in rows], [r[:-1] for r in new_rows])
                self.assertEqual(sources, str(unknown))
                self.assertTrue(all(r[-1] == str(unknown.relative_to(root)) for r in new_rows))
                self.assertEqual(log.call_count, 1)
                message = log.call_args[0][0]
                self.assertIn(function.__name__, message)
                self.assertNotIn(root, message)
                self.assertNotIn('PAYLOAD_SECRET', message)
                self.assertNotIn('SECRET64', message)
                self.assertIn('DexUseProto:field=90/wire=0/count=2', message)
                self.assertIn('PackageDexUseProto:field=90/wire=0/count=2', message)
                if function is artifact.package_dex_usage_secondary:
                    self.assertEqual(len(new_rows), 3)
                    self.assertEqual([r[3] for r in new_rows], [10, 0, ''])
                    self.assertIs(type(new_rows[1][3]), int)
                    self.assertIn('Int32Value:field=90/wire=0/count=4', message)
                    self.assertIn('SecondaryDexUseProto:field=90/wire=0/count=6', message)
                    self.assertIn('SecondaryDexUseRecordProto:field=90/wire=0/count=6', message)
                else:
                    self.assertEqual(len(new_rows), 2 if function is artifact.package_dex_usage_app_code else 1)
                    self.assertIn('PrimaryDexUseProto:field=90/wire=0/count=2', message)
                    self.assertIn('PrimaryDexUseRecordProto:field=90/wire=0/count=6', message)

    def test_optional_decoder_mapping_and_cap_occurrences(self):
        raw = field(1, 0, 3) + field(1, 2, b'repeat') + b''.join(field(n, 0, 1) for n in range(100, 140)) + field(100, 0, 2) * 2
        with patch.object(artifact, 'logfunc') as log:
            old_default = artifact._wire_fields(raw, {1})  # pylint: disable=protected-access
        log.assert_not_called()
        self.assertEqual(old_default, {'1': [3, b'repeat']})
        collector = artifact._UnknownFields()  # pylint: disable=protected-access
        self.assertEqual(artifact._wire_fields(raw, {1}, collector, 'DexUseProto'), old_default)  # pylint: disable=protected-access
        self.assertEqual(len(collector.counts), 32)
        self.assertEqual(collector.counts[('DexUseProto', 100, 0)], 3)
        self.assertEqual(collector.unlisted_occurrences, 8)
        with patch.object(artifact, 'logfunc') as log:
            collector.emit('relative\n\x00/path', 'package_dex_usage_app_code')
        self.assertEqual(log.call_count, 1)
        message = log.call_args[0][0]
        self.assertIn('unlisted_occurrences=8', message)
        self.assertNotIn('\n', message)
        self.assertNotIn('\x00', message)
        self.assertLessEqual(len(message), 8192)

    def test_store_wrapper_and_run_isolation(self):
        with tempfile.TemporaryDirectory() as root:
            paths = [write_store(root, fixture(True), 'one'), write_store(root, fixture(), 'two')]
            context = Context(root, paths)
            with patch.object(artifact, 'logfunc') as log:
                native = artifact._primary_rows(context)  # pylint: disable=protected-access
                stores = artifact._stores(context)  # pylint: disable=protected-access
            log.assert_not_called()
            self.assertEqual(len(stores), 2)
            self.assertEqual([len(native[0]), len(native[1])], [4, 2])
            for _ in range(2):
                with patch.object(artifact, 'logfunc') as log:
                    artifact.package_dex_usage_app_code.__wrapped__(context)
                    artifact.package_dex_usage_cross_package.__wrapped__(context)
                    artifact.package_dex_usage_secondary.__wrapped__(context)
                self.assertEqual(log.call_count, 3)
                self.assertTrue(all('one/data/system/' in c.args[0] for c in log.call_args_list))

    def test_bounded_format_for_oversized_accepted_field_number(self):
        # Anomalous number, not claimed to be a valid protobuf field: the old parser skips it.
        raw = field(1 << 15000, 0, 1)
        collector = artifact._UnknownFields()  # pylint: disable=protected-access
        self.assertEqual(artifact._wire_fields(raw, {1}), {})  # pylint: disable=protected-access
        self.assertEqual(artifact._wire_fields(raw, {1}, collector, 'DexUseProto'), {})  # pylint: disable=protected-access
        with patch.object(artifact, 'logfunc') as log:
            collector.emit('\x00' * 240, 'package_dex_usage_app_code')
        self.assertIn('oversized(bits=15001)', log.call_args[0][0])
        self.assertLessEqual(len(log.call_args[0][0]), 8192)
        # Explicit size boundary is safe even for an unexpected private scope string.
        collector.add('long' * 3000, 99, 0)
        with patch.object(artifact, 'logfunc') as log:
            collector.emit('relative', 'package_dex_usage_app_code')
        self.assertEqual(len(log.call_args[0][0]), 8192)
        self.assertTrue(log.call_args[0][0].endswith('summary_text_truncated=true'))


if __name__ == '__main__':
    unittest.main()
