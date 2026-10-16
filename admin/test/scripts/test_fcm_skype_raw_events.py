"""Actual LevelDB log/protobuf fixtures retain recognized raw FCM observations."""
import collections
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
from unittest.mock import patch
from scripts.artifacts import FCMQueuedMessagesSkype as skype
from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from admin.test.scripts.test_history_doclist_all_sources import Context as BaseContext


class Context(BaseContext):
    def get_relative_path(self, path):
        if not isinstance(path, str):
            raise TypeError('The framework source-path API requires a string')
        return super().get_relative_path(path)


def varint(value):
    data = bytearray()
    while value > 127:
        data.append((value & 127) | 128)
        value >>= 7
    data.append(value)
    return bytes(data)


def field(number, value):
    return varint(number << 3 | 2) + varint(len(value)) + value


def checksum(data):
    crc = 0xffffffff
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x82f63b78 if crc & 1 else 0)
    crc ^= 0xffffffff
    return (((crc >> 15) | (crc << 17)) + 0xa282ead8) & 0xffffffff


def create_fcm_fixture(root):
    root = Path(root)
    files = []
    for user in [0, 10]:
        path = root/f'data/user/{user}/com.google.android.gms/app_fcm_queued_messages.ldb/fcm_queued_messages.ldb/000001.log'
        path.parent.mkdir(parents=True, exist_ok=True)
        kv = {'eventType': '308', 'payload': 'not JSON: <raw> "é", =: \\n', 'empty': ''}
        records = [('com.skype.raider', kv), ('com.skype.raider', kv),
                   ('com.skype.raider', {'eventType': '115'}),
                   ('com.microsoft.teams', {'eventType': '801', 'user': f'user{user}'}),
                   ('com.microsoft.teams', {'eventType': '803', 'raw': '{broken'}),
                   ('com.microsoft.teams', {'eventType': '200', 'conversationId': '19:chat',
                    'recipientId': 'receiver', 'rawPayload': json.dumps({'from': 'sender',
                    'content': 'existing message', 'originalarrivaltime': '1700000000000'})}),
                   ('com.skype.raider', {'eventType': '107', 'convoId': 'chat',
                    'callId': 'call', 'callerId': 'sender'}),
                   ('com.skype.raider', {'eventType': '404', 'title': 'notice', 'msg': 'text'}),
                   ('com.skype.raider', {'eventType': '405'}),
                   ('unrelated.package', {'eventType': '308'})]
        batch = struct.pack('<QI', 1, len(records))
        for index, (package, values) in enumerate(records):
            # Mirror the iterator's observed eight-byte key suffix convention.
            key_index = 0 if index == 1 else index
            key = f'fixture:1700000000000000%{key_index}'.encode() + b'\0'*8
            payload = field(5, package.encode())
            for name, value in values.items():
                payload += field(7, field(1, name.encode()) + field(2, value.encode()))
            value = field(2, payload)
            batch += b'\x01' + varint(len(key)) + key + varint(len(value)) + value
        path.write_bytes(struct.pack('<IHB', checksum(b'\x01'+batch), len(batch), 1)+batch)
        files.append(path)
    alias = root/'data/data/com.google.android.gms/app_fcm_queued_messages.ldb/fcm_queued_messages.ldb/000001.log'
    alias.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(files[0], alias)
    files.append(alias)
    return files


class TestFcmSkypeRawEvents(unittest.TestCase):
    def test_actual_decoder_raw_values_duplicates_and_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_fcm_fixture(directory)
            headers, rows, sources = skype.get_fcm_skype_other_events.__wrapped__(Context(directory, files))
            self.assertEqual(headers[0], ('FCM Timestamp', 'datetime'))
            self.assertEqual(len(rows), 10)
            self.assertEqual(len(sources.splitlines()), 2)
            self.assertEqual(collections.Counter(row[2] for row in rows),
                             {'308': 4, '115': 2, '801': 2, '803': 2})
            self.assertEqual(len({row[-1] for row in rows}), 2)
            for row in rows:
                self.assertFalse(Path(row[-1]).is_absolute())
                self.assertTrue((Path(directory)/row[-1]).is_file())
                self.assertEqual(json.loads(row[4])['eventType'], row[2])
            duplicate = [row for row in rows if row[2] == '308']
            self.assertEqual(duplicate[0], duplicate[1])
            self.assertEqual(json.loads(duplicate[0][4])['payload'],
                             'not JSON: <raw> "é", =: \\n')
            with FcmIterator(files[0].parent) as iterator:
                self.assertEqual(len(list(iterator)), 10)
            self.assertEqual(len(skype.get_fcm_skype.__wrapped__(Context(directory, files))[1]), 4)
            self.assertEqual(len(skype.get_fcm_skype_notifications.__wrapped__(Context(directory, files))[1]), 2)

    def test_failed_directory_does_not_drop_healthy_events(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_fcm_fixture(directory)
            bad = Path(directory)/'A/fcm_queued_messages.ldb/missing.log'
            with patch.object(skype, 'logfunc') as logs:
                rows = skype.get_fcm_skype_other_events.__wrapped__(Context(directory, [bad,*files]))[1]
            self.assertEqual(len(rows), 10)
            self.assertIn('A/fcm_queued_messages.ldb', logs.call_args[0][0])
            self.assertEqual(skype.get_fcm_skype_other_events.__wrapped__(Context(directory, []))[1], [])
