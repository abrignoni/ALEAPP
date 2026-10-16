"""Bounded diagnostics from actual CRC-valid Hive files, without value dumps."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

from scripts.artifacts import kmplayer
from scripts.artifacts.hiveReader import hive_entries


PRIVATE_VALUE = 'PRIVATE_VALUE_MUST_NOT_BE_LOGGED'
TOMBSTONE = object()


def encode_value(value):
    if value is None:
        return b'\x00'
    if isinstance(value, bool):
        return b'\x03' + bytes([value])
    if isinstance(value, (int, float)):
        return bytes([1 if isinstance(value, int) else 2]) + struct.pack('<d', value)
    if isinstance(value, (str, bytes)):
        raw = value.encode() if isinstance(value, str) else value
        return bytes([4 if isinstance(value, str) else 5]) + struct.pack('<I', len(raw)) + raw
    if isinstance(value, list):
        return b'\x0a' + struct.pack('<I', len(value)) + b''.join(map(encode_value, value))
    if isinstance(value, dict):
        return bytes([32, len(value)]) + b''.join(bytes([key]) + encode_value(item)
                                                 for key, item in value.items())
    raise TypeError(type(value))


def frame(key, value):
    if isinstance(key, int):
        encoded_key = b'\x00' + struct.pack('<I', key)
    else:
        raw = key.encode()
        encoded_key = b'\x01' + bytes([len(raw)]) + raw
    payload = encoded_key + (b'' if value is TOMBSTONE else encode_value(value))
    body = struct.pack('<I', len(payload) + 8) + payload
    return body + struct.pack('<I', zlib.crc32(body) & 0xffffffff)


def healthy(title, opened=1700000000000, source=0):
    return {0: source, 1: title, 3: 'content://media/' + title, 10: opened}


def mixed_frames():
    items = [('local', healthy('local')), ('remote', healthy('remote', source=1)),
             ('recovered', PRIVATE_VALUE), ('recovered', healthy('recovered', 1700000001000)),
             ('lost', healthy('lost')), ('lost', 9), ('null', None), ('integer', 4),
             ('real', 1.25), ('boolean', True), ('string', PRIVATE_VALUE),
             ('bytes', PRIVATE_VALUE.encode()), ('list', [PRIVATE_VALUE, 1]),
             ('tombstone', TOMBSTONE), ('"\n\t\u00e9' + 'x' * 70, None)]
    items.extend((index, 7) for index in range(100, 112))
    return b''.join(frame(key, value) for key, value in items)


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def write_box(root, prefix, data):
    path = Path(root) / prefix / kmplayer.BOX_SUFFIX
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


class KMPlayerDiagnosticsTest(unittest.TestCase):
    def test_live_overwrites_types_cap_and_private_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write_box(folder, 'data/user/0', mixed_frames())
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            live, _ = hive_entries(path)
            self.assertEqual(len(live), 25)
            self.assertIsNone(live['tombstone'])
            with patch.object(kmplayer, 'logfunc') as log:
                headers, rows, source = kmplayer.kmplayer_playback.__wrapped__(Context(folder, [path]))
            self.assertEqual(len(rows), 3)
            self.assertEqual([row[2] for row in rows], ['recovered', 'local', 'remote'])
            self.assertEqual([row[3] for row in rows], [0, 0, 1])
            self.assertEqual(headers[0], ('Opened', 'datetime'))
            self.assertEqual(source, str(path))
            messages = [call.args[0] for call in log.call_args_list]
            self.assertEqual(len(messages), 11)
            self.assertTrue(all('skipped live non-object entry;' in line for line in messages[:10]))
            summary = messages[-1]
            self.assertIn('skipped=22;', summary)
            self.assertIn('examples=10; omitted=12', summary)
            counts = json.loads(summary.split('decoded_types=')[1].split('; examples=')[0])
            self.assertEqual(counts, {'NoneType': 3, 'bool': 1, 'bytes': 1, 'float': 1,
                                      'int': 14, 'list': 1, 'str': 1})
            self.assertIn('key_length=74; key_truncated=True', messages[9])
            self.assertIn('\\n\\t\\u00e9', messages[9])
            self.assertNotIn(PRIVATE_VALUE, '\n'.join(messages))
            self.assertNotIn('deleted', '\n'.join(messages).lower())
            self.assertNotIn(str(Path(folder)), '\n'.join(messages))
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_per_box_cap_path_and_contributing_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            long_prefix = '/'.join(['p' * 100] * 6) + '/data/user/0'
            mixed = write_box(folder, long_prefix, mixed_frames())
            skipped = write_box(folder, 'data/user/10', frame(1, None) + frame(2, TOMBSTONE))
            good = write_box(folder, 'data/user/20', frame('ok', healthy('healthy')))
            with patch.object(kmplayer, 'logfunc') as log:
                _, rows, source = kmplayer.kmplayer_playback.__wrapped__(Context(folder, [mixed, skipped, good]))
            self.assertEqual(len(rows), 4)
            self.assertEqual(source.splitlines(), [str(mixed), str(good)])
            messages = [call.args[0] for call in log.call_args_list]
            self.assertEqual(len(messages), 14)
            self.assertIn('box_truncated=True', messages[0])
            encoded_path = messages[0].split('box=')[1].split('; box_length=')[0]
            self.assertEqual(len(json.loads(encoded_path)), 512)
            self.assertIn('skipped=2;', messages[-1])
            self.assertIn('examples=2; omitted=0', messages[-1])
            self.assertFalse(any('data/user/20' in message for message in messages))

    def test_healthy_only_empty_object_and_crc_stop(self):
        with tempfile.TemporaryDirectory() as folder:
            empty = write_box(folder, 'data/user/0', frame('empty', {}))
            with patch.object(kmplayer, 'logfunc') as log:
                _, rows, source = kmplayer.kmplayer_playback.__wrapped__(Context(folder, [empty]))
            self.assertEqual(rows, [('', '', '', '', str(empty.relative_to(folder)))])
            self.assertEqual(source, str(empty))
            log.assert_not_called()
            corrupt = bytearray(frame('unread', PRIVATE_VALUE))
            corrupt[-1] ^= 1
            box = write_box(folder, 'data/user/1', frame('ok', healthy('kept')) + corrupt)
            with patch('scripts.artifacts.hiveReader.logfunc') as reader_log, \
                    patch.object(kmplayer, 'logfunc') as log:
                _, rows, _ = kmplayer.kmplayer_playback.__wrapped__(Context(folder, [box]))
            self.assertEqual([row[2] for row in rows], ['kept'])
            self.assertIn('failed its own CRC', reader_log.call_args.args[0])
            log.assert_not_called()


if __name__ == '__main__':
    unittest.main()
