#!/usr/bin/env python3
"""A Telegram-layout client under another package, with the older messages table.

The message and service records are encoded in the field order the client's own readers
take (0x81FF9C4A and 0x8C75C832), and the stores are built with the tables the artifact
looks for. The package name and every value are made up for the test.
"""

# pylint: disable=protected-access
import os
import sqlite3
import struct
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from scripts.artifacts import telegramAndroid  # noqa: E402
from scripts.artifacts.telegramAndroid import _decode_message_blob  # noqa: E402

PEER_USER_LEGACY = 0x9DB1BC6D
PHONE_CALL = 0x80E11A7F
FORK_MESSAGE = 0x81FF9C4A
FORK_SERVICE = 0x8C75C832
DATE = 1767225600
PACKAGE = 'org.example.forkclient'


def i32(value):
    return struct.pack('<i', value)


def u32(value):
    return struct.pack('<I', value)


def tl_string(text):
    raw = text.encode('utf-8')
    out = bytes([len(raw)]) + raw
    return out + b'\x00' * ((4 - len(out) % 4) % 4)


def peer(user_id):
    return u32(PEER_USER_LEGACY) + i32(user_id)


def fork_message(text, sender=None, reply=None, forwarded=False):
    flags = (1 << 8 if sender is not None else 0) | (1 << 3 if reply is not None else 0) \
        | (1 << 2 if forwarded else 0)
    out = u32(FORK_MESSAGE) + u32(flags) + i32(0) + i32(7)
    if sender is not None:
        out += i32(sender)
    out += peer(200)
    if forwarded:
        out += u32(0xDEADBEEF) + i32(1) + i32(2)   # a forward header this parser cannot walk
    if reply is not None:
        out += i32(reply)
    return out + i32(DATE) + tl_string(text)


def fork_service(sender):
    out = u32(FORK_SERVICE) + u32(1 << 8) + i32(0) + i32(9) + i32(sender) + peer(200) + i32(DATE)
    return out + u32(PHONE_CALL) + i32(0) + struct.pack('<q', 5)


class ForkRecords(unittest.TestCase):
    def test_message_is_walked_to_its_text(self):
        result = _decode_message_blob(fork_message('hello', sender=100, reply=3), DATE)
        self.assertEqual((result['text'], result['sender'], result.get('structural')),
                         ('hello', 100, True))

    def test_forwarded_message_text_is_found_after_the_date(self):
        result = _decode_message_blob(fork_message('fwd text', sender=100, forwarded=True), DATE)
        self.assertEqual((result['text'], result['forwarded']), ('fwd text', True))

    def test_service_sender_is_the_from_id_not_the_message_id(self):
        result = _decode_message_blob(fork_service(sender=555), DATE)
        self.assertTrue(result['service'])
        self.assertEqual(result['sender'], 555)
        self.assertTrue(result['action'].startswith('Phone call'))


class Context:
    def __init__(self, root):
        self.root = root

    def get_files_found(self):
        return [str(path) for path in sorted(self.root.rglob('*')) if path.is_file()]

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace('\\', '/')

    def get_seeker(self):
        return None


def cache4(path, table, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE dialogs (did INTEGER PRIMARY KEY)')
    db.execute('CREATE TABLE users (uid INTEGER PRIMARY KEY, name TEXT, status INTEGER, data BLOB)')
    db.execute(f'CREATE TABLE {table} (mid INTEGER, uid INTEGER, read_state INTEGER, send_state '
               'INTEGER, date INTEGER, data BLOB, out INTEGER)')
    db.executemany(f'INSERT INTO {table} (mid, uid, read_state, date, data, out) VALUES (?,?,1,?,?,0)',
                   rows)
    db.commit()
    db.close()


class ForkStores(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'evidence'

    def tearDown(self):
        self.temp.cleanup()

    def test_other_package_is_read_only_by_content_and_only_for_messages(self):
        cache4(self.root / f'data/data/{PACKAGE}/files/account4/cache4.db', 'messages',
               [(7, 200, DATE, fork_message('from the fork', sender=100))])
        bogus = self.root / 'data/data/org.example.other/files/cache4.db'
        bogus.parent.mkdir(parents=True)
        sqlite3.connect(bogus).execute('CREATE TABLE something (a)').connection.close()
        context = Context(self.root)
        opted = telegramAndroid._cache4_mains(context, any_package=True)
        self.assertEqual([relative for _, relative in opted],
                         [f'data/data/{PACKAGE}/files/account4/cache4.db'])
        self.assertEqual(telegramAndroid._cache4_mains(context), [])

    def test_legacy_messages_table_is_read_when_messages_v2_is_absent(self):
        cache4(self.root / f'data/data/{PACKAGE}/files/cache4.db', 'messages',
               [(7, 200, DATE, fork_message('legacy row', sender=100))])
        context = Context(self.root)
        with unittest.mock.patch.object(telegramAndroid, '_device_path_index', return_value={}), \
                unittest.mock.patch.object(telegramAndroid, '_downloads_by_message', return_value={}):
            headers, rows, _ = telegramAndroid.get_telegramMessages.__wrapped__(context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        self.assertEqual([row[names.index('Message')] for row in rows], ['legacy row'])

    def test_fourth_account_maps_to_its_userconfing_slot(self):
        own = {'root': {4: 999}}
        self.assertEqual(telegramAndroid._own_id_for_db('root/files/account4/cache4.db', own), 999)


if __name__ == '__main__':
    unittest.main()
