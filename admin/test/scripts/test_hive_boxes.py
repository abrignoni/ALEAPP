"""The Hive box inventory's own attribution and read-outcome phrases.

`_how_it_read` reports one of eight outcomes and the corpus images reach two of
them, so the rest are built here from synthetic frames. Two matter most: a read
that stops without the reader recording a frame, which only the byte accounting
catches, and an undecodable frame sitting before a stop, where the two clauses
can otherwise contradict each other.
"""
import struct
import unittest
import zlib

from scripts.artifacts.hiveBoxes import _how_it_read, _owning_app
from scripts.hive_parser import looks_encrypted, read_frames


def string_value(text):
    return b'\x04' + struct.pack('<I', len(text)) + text.encode()


def frame(key, value, bad_crc=False):
    """One Hive frame: length, key, value, CRC32 of everything before it."""
    # Key type 1 is KEY_UTF8: a uint8 length then the bytes. Type 0 is a uint32
    # key, which silently eats four bytes of whatever follows.
    body = b'\x01' + bytes([len(key)]) + key.encode() + value
    raw = struct.pack('<I', len(body) + 8) + body
    crc = zlib.crc32(raw) & 0xffffffff
    if bad_crc:
        crc ^= 0xffffffff
    return raw + struct.pack('<I', crc)


def read(blob):
    """What the module gets for a box holding these bytes."""
    frames = read_frames(blob)
    return _how_it_read(frames, looks_encrypted(frames), len(blob))


GOOD = frame('a', string_value('x'))


class OwningApp(unittest.TestCase):

    def test_package_under_data_data(self):
        self.assertEqual(
            _owning_app('data/data/com.example.app/app_flutter/box.hive'),
            'com.example.app')

    def test_package_under_a_user_id(self):
        self.assertEqual(
            _owning_app('data/user/0/com.example.app/app_flutter/box.hive'),
            'com.example.app')

    def test_package_carrying_one_dot(self):
        # The commonest shape, and the one a two-dot test would miss.
        self.assertEqual(
            _owning_app('data/data/com.kmplayer/databases/db/meta.hive'),
            'com.kmplayer')

    def test_windows_separators(self):
        self.assertEqual(
            _owning_app('data\\data\\com.example.app\\app_flutter\\box.hive'),
            'com.example.app')

    def test_no_package_directory(self):
        self.assertEqual(_owning_app('data/misc/box.hive'), '')

    def test_box_at_the_root(self):
        self.assertEqual(_owning_app('box.hive'), '')

    def test_a_package_named_later_in_the_path_does_not_win(self):
        # A substring test would read the examiner's own folder names, or the
        # second package, as the owner of the first package's box.
        self.assertEqual(
            _owning_app('data/data/com.example.app/files/com.other.app/box.hive'),
            'com.example.app')


class HowItRead(unittest.TestCase):

    def test_empty_file(self):
        self.assertEqual(read(b''), 'the file is empty')

    def test_bytes_but_no_frame_at_offset_zero(self):
        # Says the file holds bytes, rather than calling it frameless.
        said = read(struct.pack('<I', 2) + b'\x00\x00\x00\x00')
        self.assertEqual(said, 'no frame could be read at offset 0, in a file of 8 byte(s)')

    def test_clean_read(self):
        self.assertEqual(read(GOOD), 'the read reached the end of the file')

    def test_stopped_early_on_an_unusable_length(self):
        # A declared length below the 8-byte minimum: the reader records nothing
        # and stops, so only the byte accounting shows the read did not finish.
        blob = GOOD + struct.pack('<I', 2) + b'\x00\x00\x00\x00'
        self.assertEqual(
            read(blob),
            'the read stopped at offset 17, where no further frame could be read, '
            'leaving 8 byte(s) unread')

    def test_a_short_tail_is_not_called_a_clean_end(self):
        # Fewer than 8 bytes left ends the walk without a frame or a record.
        blob = GOOD + b'\x00\x00\x00'
        self.assertIn('leaving 3 byte(s) unread', read(blob))

    def test_truncated_frame(self):
        blob = GOOD + struct.pack('<I', 200) + b'\x00\x00\x00\x00'
        self.assertEqual(
            read(blob),
            'the read stopped at offset 17, where a frame is cut short by the end of the file')

    def test_failed_crc(self):
        blob = GOOD + frame('b', string_value('y'), bad_crc=True)
        self.assertEqual(
            read(blob),
            'the read stopped at offset 17, where a frame failed its own CRC')

    def test_frame_that_did_not_decode_cleanly(self):
        # Type id 20 is a reserved id the reader has no decoder for, so the frame
        # records a decode error while its own checksum still holds.
        blob = frame('a', bytes([20]) + b'\x00\x00\x00\x00')
        self.assertEqual(
            read(blob),
            '1 frame(s) did not decode cleanly and are left out of the entry and '
            'displaced counts')

    def test_an_undecoded_frame_before_a_stop_claims_nothing_about_the_rest(self):
        # Both clauses fire on this box. The undecoded clause must not say the
        # rest of the box was read while the clause beside it names a stop.
        blob = (frame('a', bytes([20]) + b'\x00\x00\x00\x00')
                + frame('b', string_value('y'), bad_crc=True))
        self.assertEqual(
            read(blob),
            'the read stopped at offset 16, where a frame failed its own CRC; '
            '1 frame(s) did not decode cleanly and are left out of the entry and '
            'displaced counts')

    def test_encrypted_box_claims_nothing_about_keys(self):
        # The table has no key column, so the phrase must not promise keys.
        blob = (frame('a', string_value('x'), bad_crc=True)
                + frame('b', string_value('y'), bad_crc=True))
        self.assertEqual(
            read(blob),
            'every frame failed its CRC while its keys read cleanly, which is how an '
            'encrypted box reads; values are not decoded')

    def test_a_stopped_read_is_reported_once(self):
        # A failed CRC already names the offset; the byte gap after it must not
        # add a second, contradictory stop.
        blob = GOOD + frame('b', string_value('y'), bad_crc=True) + b'\x00' * 32
        self.assertEqual(read(blob).count('the read stopped at offset'), 1)


if __name__ == '__main__':
    unittest.main()
