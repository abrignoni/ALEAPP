"""Published layer132 prefix widths, paired counts and SQL row projection regression."""
import os
import sqlite3
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from scripts.artifacts import telegramAndroid  # noqa: E402


def encode_string(raw):
    lead = bytes([len(raw)]) if len(raw) < 254 else b'\xfe' + len(raw).to_bytes(3, 'little')
    value = lead + raw
    return value + b'\0' * (-len(value) % 4)


class Layer132PrefixTest(unittest.TestCase):
    def test_channel_signed32_ids_and_distinct_paired_counts(self):
        for ident in (-2147483648, -1, 0, 1, 2147483647):
            for flags in (0, 1, 2, 4, 8192, 8199):
                blob = struct.pack('<IIi', 0x2F532F3C, flags, ident) + encode_string(b'known')
                expected = {'about': 'known'}
                for mask, fields in ((1, [('participants', 101)]), (2, [('admins', -202)]),
                                     (4, [('kicked', 303), ('banned', -404)]),
                                     (8192, [('online', 0)])):
                    if flags & mask:
                        for key, value in fields:
                            blob += struct.pack('<i', value)
                            expected[key] = value
                self.assertEqual(telegramAndroid._decode_chat_full(blob), expected)  # pylint: disable=protected-access

    def test_basic32_string_boundaries_and_ignored_suffix(self):
        for raw in (b'', b'a', b'ab', b'abc', b'abcd', b'x' * 253, b'x' * 254,
                    b'x' * 255, 'Ω用户'.encode(), b'bad\xffutf8'):
            blob = struct.pack('<IIi', 0x49A0A5D9, 8199, -1) + encode_string(raw) + b'\x01\x02\x03\x04'
            self.assertEqual(telegramAndroid._decode_chat_full(blob),  # pylint: disable=protected-access
                             {'about': raw.decode('utf-8', 'replace')})

    def test_other_recognized_prefixes_keep64bit_width(self):
        # This asserts preservation of the local prefix contract, not vendor validity of all layers.
        excluded = {0x2F532F3C, 0x49A0A5D9}
        constructors = telegramAndroid._CHAT_FULL - excluded  # pylint: disable=protected-access
        self.assertEqual(len(constructors), 44)
        for constructor in constructors:
            blob = struct.pack('<II', constructor, 0)
            if constructor in telegramAndroid._CHAT_FULL_A:  # pylint: disable=protected-access
                blob += struct.pack('<I', 0)
            blob += struct.pack('<q', 2 ** 40) + encode_string(b'unchanged')
            self.assertEqual(telegramAndroid._decode_chat_full(blob), {'about': 'unchanged'})  # pylint: disable=protected-access

    def test_actual_sqlite_keeps_uid_names_repeated_rows_and_source(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'data/data/org.telegram.messenger/files/cache4.db'
            path.parent.mkdir(parents=True)
            blob = struct.pack('<IIi', 0x2F532F3C, 4, -1) + encode_string(b'row') + struct.pack('<ii', 3, 4)
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE chats(uid, name)')
                db.execute('CREATE TABLE chat_settings_v2(uid, info)')
                db.executemany('INSERT INTO chats VALUES(?,?)', [(1, 'first'), (1, 'last')])
                db.executemany('INSERT INTO chat_settings_v2 VALUES(?,?)', [(1, blob), (1, blob)])
            context = SimpleNamespace(get_files_found=lambda: [str(path)])
            headers, rows, source = telegramAndroid.get_telegramChatDetails.__wrapped__(context)
            self.assertEqual(len(headers), 8)
            self.assertEqual(rows, [(1, 'last', 'row', '', '', 3, 4, '')] * 2)
            self.assertEqual(source, str(path))


if __name__ == '__main__':
    unittest.main()
