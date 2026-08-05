#!/usr/bin/env python3
"""Round-trip checks for the Telegram Android TL message decoder.

The decoder in scripts/artifacts/telegramAndroid.py reads the TL wire format
that Telegram stores in cache4.db. Some of the structures it handles are not
present in any extraction available here: no test image carries a group
membership event or a group call invite, so those readers cannot be exercised
against real data.

These tests encode the structures instead, following the field order and flag
bits published by the client's own serialisers, and assert that the decoder
reads back what was written. That verifies the implementation against the
documented wire format. It does not substitute for corpus validation of the
structures that real images do contain, which is done separately.
"""

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from scripts.artifacts.telegramAndroid import _decode_message_blob  # noqa: E402

PEER_USER = 0x59511722
VECTOR = 0x1CB5C415


def i32(value):
    return struct.pack('<i', value)


def u32(value):
    return struct.pack('<I', value)


def i64(value):
    return struct.pack('<q', value)


def tl_string(text):
    """TL string: a length byte, the bytes, then padding to a 4-byte boundary."""
    raw = text.encode('utf-8')
    out = bytes([len(raw)]) + raw
    return out + b'\x00' * ((4 - len(out) % 4) % 4)


def tl_vector_int64(values):
    return u32(VECTOR) + i32(len(values)) + b''.join(i64(v) for v in values)


def peer_user(user_id):
    return u32(PEER_USER) + i64(user_id)


def peer_user_legacy(user_id):
    """Layer 132 and older wrote the peer id as an Int32."""
    return u32(0x9DB1BC6D) + i32(user_id)


def service_message(action, date=1700000000, peer=555, mid=42):
    """A TL_messageService_layer195 with no from_id and no reply header."""
    return (u32(0x2B085862) + u32(0) + i32(mid) + peer_user(peer)
            + i32(date) + action)


def text_message(text, date=1700000000, peer=555, mid=7, with_flags2=False):
    """A TL_message with no optional headers; text follows the date."""
    if with_flags2:
        head = u32(0x9815CEC8) + u32(0) + u32(0)     # TL_message_layer216
    else:
        head = u32(0x76BEC211) + u32(0)              # TL_message_layer173
    return head + i32(mid) + peer_user(peer) + i32(date) + tl_string(text)


class TelegramTextMessageTest(unittest.TestCase):

    def test_plain_message(self):
        blob = text_message('hello there')
        decoded = _decode_message_blob(blob, 1700000000)
        self.assertEqual(decoded.get('text'), 'hello there')
        self.assertTrue(decoded.get('structural'))

    def test_message_with_second_flags_word(self):
        """Layer 179 and newer read a second flags integer before the id."""
        blob = text_message('newer layer', with_flags2=True)
        decoded = _decode_message_blob(blob, 1700000000)
        self.assertEqual(decoded.get('text'), 'newer layer')

    def test_string_padding_is_consumed(self):
        for text in ('a', 'ab', 'abc', 'abcd', 'abcde'):
            decoded = _decode_message_blob(text_message(text), 1700000000)
            self.assertEqual(decoded.get('text'), text)

    def test_unknown_constructor_is_reported(self):
        decoded = _decode_message_blob(u32(0xDEADBEEF) + b'\x00' * 16, 1700000000)
        self.assertEqual(decoded.get('unknown'), 0xDEADBEEF)


class TelegramLegacyPeerTest(unittest.TestCase):
    """Peers stored by Telegram builds on layer 132 and older.

    Those constructors carry an Int32 id. Reading one as the current 64-bit
    form misaligns every field after it, so a message from an older build
    would decode to nothing useful. No extraction available here is old
    enough to contain one.
    """

    def test_legacy_peer_message_decodes(self):
        blob = (u32(0x76BEC211) + u32(0) + i32(7) + peer_user_legacy(12345)
                + i32(1700000000) + tl_string('sent from an older build'))
        decoded = _decode_message_blob(blob, 1700000000)
        self.assertEqual(decoded.get('text'), 'sent from an older build')
        self.assertTrue(decoded.get('structural'))

    def test_current_peer_still_decodes(self):
        decoded = _decode_message_blob(text_message('current build'), 1700000000)
        self.assertEqual(decoded.get('text'), 'current build')


class TelegramServiceActionTest(unittest.TestCase):

    def decode_action(self, action):
        decoded = _decode_message_blob(service_message(action), 1700000000)
        self.assertTrue(decoded.get('service'))
        return decoded.get('action') or ''

    def test_chat_add_user_reads_member_vector(self):
        action = u32(0x15CEFD00) + tl_vector_int64([111, 222])
        result = self.decode_action(action)
        self.assertIn('User added to chat', result)
        self.assertIn('111', result)
        self.assertIn('222', result)

    def test_chat_create_reads_title_and_members(self):
        action = u32(0xBD47CBAD) + tl_string('Case Group') + tl_vector_int64([7, 8, 9])
        result = self.decode_action(action)
        self.assertIn('Group created', result)
        self.assertIn('Case Group', result)
        self.assertIn('7, 8, 9', result)

    def test_invite_to_group_call_reads_call_and_users(self):
        call = u32(0xD8AA840F) + i64(1234) + i64(5678)   # TL_inputGroupCall
        action = u32(0x502F92F7) + call + tl_vector_int64([31337])
        result = self.decode_action(action)
        self.assertIn('Invited to group call', result)
        self.assertIn('31337', result)

    def test_phone_call_reads_outcome_and_duration(self):
        # flags: reason (1) and duration (2) both present.
        action = (u32(0x80E11A7F) + u32(1 | 2) + i64(999)
                  + u32(0x57ADC690) + i32(96))          # hung up, 96 seconds
        result = self.decode_action(action)
        self.assertIn('Phone call', result)
        self.assertIn('hung up', result)
        self.assertIn('96', result)

    def test_phone_call_without_optional_fields(self):
        action = u32(0x80E11A7F) + u32(0) + i64(999)
        result = self.decode_action(action)
        self.assertIn('Phone call', result)
        self.assertNotIn('duration', result)

    def test_auto_delete_timer_reads_period(self):
        action = u32(0x3C134D7B) + u32(0) + i32(86400)
        result = self.decode_action(action)
        self.assertIn('Auto-delete timer changed', result)
        self.assertIn('86400', result)

    def test_screenshot_taken_is_named(self):
        self.assertEqual(self.decode_action(u32(0x4792929B)), 'Screenshot taken')

    def test_history_cleared_is_named(self):
        self.assertEqual(self.decode_action(u32(0x9FBAB604)), 'History cleared')

    def test_unknown_action_is_reported_by_id(self):
        result = self.decode_action(u32(0xDEADBEEF))
        self.assertIn('Unrecognised action', result)
        self.assertIn('0xdeadbeef', result)

    def test_oversized_vector_count_is_rejected(self):
        """A bad count must not drive a huge read."""
        action = u32(0x15CEFD00) + u32(VECTOR) + i32(50000)
        result = self.decode_action(action)
        self.assertIn('User added to chat', result)


class TelegramChatFullTest(unittest.TestCase):
    """Group and channel detail records.

    Only one such record exists across the extractions available here, a
    channel carrying a participant count and an empty description, so the
    description text, the remaining counts and the basic group record shape
    are encoded here rather than read from an image.
    """

    def decode(self, blob):
        from scripts.artifacts.telegramAndroid import _decode_chat_full
        return _decode_chat_full(blob)

    def test_channel_with_counts(self):
        # TL_channelFull_layer225: flags, flags2, id, about, then the counts.
        # Flags set: participants (1), admins (2), kicked/banned (4), online (8192).
        blob = (u32(0xE4E0B29D) + u32(1 | 2 | 4 | 8192) + u32(0) + i64(1667989259)
                + tl_string('Trading signals') + i32(124) + i32(3) + i32(2)
                + i32(1) + i32(17))
        record = self.decode(blob)
        self.assertEqual(record['about'], 'Trading signals')
        self.assertEqual(record['participants'], 124)
        self.assertEqual(record['admins'], 3)
        self.assertEqual(record['kicked'], 2)
        self.assertEqual(record['banned'], 1)
        self.assertEqual(record['online'], 17)

    def test_channel_with_only_participants(self):
        """The shape actually present in the test corpus."""
        blob = (u32(0xE4E0B29D) + u32(1) + u32(0) + i64(1667989259)
                + tl_string('') + i32(124))
        record = self.decode(blob)
        self.assertEqual(record['about'], '')
        self.assertEqual(record['participants'], 124)
        self.assertNotIn('admins', record)

    def test_older_channel_without_second_flags_word(self):
        # TL_channelFull_layer121: flags, id, about, then the counts.
        blob = (u32(0xF0E6672A) + u32(1) + i64(42) + tl_string('older layer')
                + i32(9))
        record = self.decode(blob)
        self.assertEqual(record['about'], 'older layer')
        self.assertEqual(record['participants'], 9)

    def test_basic_group_record_has_description_only(self):
        # TL_chatFull carries a description but no counts in the readable prefix.
        blob = u32(0x2633421B) + u32(0) + i64(77) + tl_string('Family group')
        record = self.decode(blob)
        self.assertEqual(record['about'], 'Family group')
        self.assertNotIn('participants', record)

    def test_unknown_record_is_reported(self):
        record = self.decode(u32(0xDEADBEEF) + b'\x00' * 16)
        self.assertEqual(record.get('unknown'), 0xDEADBEEF)


class TelegramAttachPathTest(unittest.TestCase):
    """The local media path the client appends when storing a message.

    Only one message across the available extractions carries one, and the file
    it names is no longer on the device, so the accept and reject behaviour is
    encoded here rather than read from an image.
    """

    def decode(self, blob):
        from scripts.artifacts.telegramAndroid import _attach_path
        return _attach_path(blob)

    def trailing(self, path):
        raw = path.encode()
        out = bytes([len(raw)]) + raw
        return out + b'\x00' * ((4 - len(out) % 4) % 4)

    def test_reads_trailing_path(self):
        p = '/storage/emulated/0/Android/data/org.telegram.messenger/cache/-1_-2.jpg'
        blob = b'\x11' * 40 + self.trailing(p)
        self.assertEqual(self.decode(blob), p)

    def test_rejects_when_field_does_not_reach_the_end(self):
        """A run of bytes that looks like a string but is not the last field."""
        p = '/storage/emulated/0/whatever.jpg'
        blob = b'\x11' * 20 + self.trailing(p) + b'\x42' * 16
        self.assertEqual(self.decode(blob), '')

    def test_ignores_non_path_trailing_string(self):
        blob = b'\x11' * 20 + self.trailing('not a path')
        self.assertEqual(self.decode(blob), '')

    def test_no_path_present(self):
        self.assertEqual(self.decode(b'\x00' * 32), '')

    def test_handles_all_padding_residues(self):
        for extra in ('a', 'ab', 'abc', 'abcd'):
            p = f'/data/{extra}'
            blob = b'\x11' * 12 + self.trailing(p)
            self.assertEqual(self.decode(blob), p)


class TelegramUserFullTest(unittest.TestCase):
    """Profile detail records: bio and blocked state."""

    def decode(self, blob):
        from scripts.artifacts.telegramAndroid import _decode_user_full
        return _decode_user_full(blob)

    def test_bio_and_blocked(self):
        # TL_userFull_layer223: flags, flags2, id, about. blocked is bit 0,
        # about is bit 1.
        blob = (u32(0xA02BC13E) + u32(1 | 2) + u32(0) + i64(8299732043)
                + tl_string("I'm a chemistry teacher."))
        record = self.decode(blob)
        self.assertEqual(record['about'], "I'm a chemistry teacher.")
        self.assertTrue(record['blocked'])

    def test_not_blocked_and_no_bio(self):
        blob = u32(0xA02BC13E) + u32(0) + u32(0) + i64(1)
        record = self.decode(blob)
        self.assertEqual(record['about'], '')
        self.assertFalse(record['blocked'])

    def test_older_record_without_second_flags_word(self):
        # TL_userFull_layer175 reads no flags2.
        blob = u32(0xB9B12C6C) + u32(2) + i64(5) + tl_string('older bio')
        record = self.decode(blob)
        self.assertEqual(record['about'], 'older bio')


if __name__ == '__main__':
    unittest.main()
