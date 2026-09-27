"""WhatsApp 1:1 and group messages must resolve LID jids through msgstore.db jid_map.

Newer msgstore.db files key a 1:1 chat, and a group message's sender, by a LID jid
(``...@lid``). wa.db's wa_contacts.jid holds the ``...@s.whatsapp.net`` form, and
msgstore.db's jid_map links the LID jid row to that jid row. The 1:1 artifact joined
wa_contacts on the chat's own jid with an inner join, so every message in a LID-keyed
chat was dropped, and so was every message in a chat with no contact row. The group
artifact kept the rows but left the sender name empty for LID senders.

These tests build synthetic databases (no real evidence bytes): a LID-keyed chat with a
jid_map row, a chat keyed by the phone-number jid, a chat with no contact, and a group
with a LID sender. The third test runs a schema without jid_map, which older databases
have: the phone-keyed chat must still resolve and the LID chat must be kept, shown by jid.
All three fail on the pre-fix code.
"""
import os
import sqlite3
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, REPO_ROOT)

from scripts.context import Context  # noqa: E402  pylint: disable=wrong-import-position
from scripts.artifacts.WhatsApp import (  # noqa: E402  pylint: disable=wrong-import-position
    get_whatsapp_group_messages, get_whatsapp_one_to_one_messages)

_ONE_TO_ONE = get_whatsapp_one_to_one_messages.__wrapped__
_GROUP = get_whatsapp_group_messages.__wrapped__

ALICE_PN = '000000000001@s.whatsapp.net'
ALICE_LID = '100000000000001@lid'
BOB_PN = '000000000002@s.whatsapp.net'
UNKNOWN_PN = '000000000003@s.whatsapp.net'
GROUP = '120363000000000001@g.us'

# (_id, raw_string); user and server are split from raw_string
JIDS = [(1, ALICE_PN), (2, ALICE_LID), (3, BOB_PN), (4, UNKNOWN_PN), (5, GROUP)]
# (_id, jid_row_id, subject)
CHATS = [(1, 2, None), (2, 3, None), (3, 4, None), (4, 5, 'Club')]
# (_id, chat_row_id, from_me, sender_jid_row_id, timestamp, message_type, text_data, recipient_count)
MESSAGES = [
    (1, 1, 0, None, 1767225600000, 0, 'lid chat, incoming', 0),
    (2, 1, 1, None, 1767225660000, 0, 'lid chat, outgoing', 0),
    (3, 2, 0, None, 1767225720000, 0, 'phone chat, incoming', 0),
    (4, 3, 0, None, 1767225780000, 0, 'no contact, incoming', 0),
    (5, 4, 0, None, 1767225840000, 7, None, 2),
    (6, 4, 0, 2, 1767225900000, 0, 'group, lid sender', 2),
    (7, 4, 1, None, 1767225960000, 0, 'group, outgoing', 2),
]
# (jid, wa_name)
CONTACTS = [(ALICE_PN, 'Alice'), (BOB_PN, 'Bob')]


class WhatsAppLidContactsTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_folder = os.path.join(self.tmp.name, 'report', 'data')
        Context.set_data_folder(self.data_folder)
        folder = os.path.join(self.data_folder, 'Dump/data/data/com.whatsapp/databases')
        os.makedirs(folder)
        self.msgstore = os.path.join(folder, 'msgstore.db')
        self.wa = os.path.join(folder, 'wa.db')

    def tearDown(self):
        Context.clear()
        self.tmp.cleanup()

    def _build(self, with_jid_map=True):
        con = sqlite3.connect(self.msgstore)
        con.execute('CREATE TABLE jid(_id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT NOT NULL, '
                    'server TEXT NOT NULL, agent INTEGER, device INTEGER, type INTEGER, raw_string TEXT)')
        con.execute('CREATE TABLE chat(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid_row_id INTEGER, subject TEXT)')
        con.execute('CREATE TABLE message(_id INTEGER PRIMARY KEY AUTOINCREMENT, chat_row_id INTEGER NOT NULL, '
                    'from_me INTEGER NOT NULL, key_id TEXT NOT NULL, sender_jid_row_id INTEGER, '
                    'timestamp INTEGER, received_timestamp INTEGER, message_type INTEGER, '
                    'text_data TEXT, recipient_count INTEGER)')
        con.execute('CREATE TABLE message_media(message_row_id INTEGER PRIMARY KEY, file_path TEXT, '
                    'file_size INTEGER)')
        con.execute('CREATE TABLE message_location(message_row_id INTEGER PRIMARY KEY, latitude REAL, '
                    'longitude REAL, live_location_share_duration INTEGER, '
                    'live_location_final_latitude REAL, live_location_final_longitude REAL, '
                    'live_location_final_timestamp INTEGER)')
        for row_id, raw in JIDS:
            user, server = raw.split('@')
            con.execute('INSERT INTO jid(_id, user, server, raw_string) VALUES (?, ?, ?, ?)',
                        (row_id, user, server, raw))
        con.executemany('INSERT INTO chat(_id, jid_row_id, subject) VALUES (?, ?, ?)', CHATS)
        for row in MESSAGES:
            con.execute('INSERT INTO message(_id, chat_row_id, from_me, sender_jid_row_id, timestamp, '
                        'message_type, text_data, recipient_count, key_id, received_timestamp) '
                        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)', row + (f'key{row[0]}',))
        if with_jid_map:
            con.execute('CREATE TABLE jid_map(lid_row_id INTEGER PRIMARY KEY NOT NULL, '
                        'jid_row_id INTEGER NOT NULL, sort_id INTEGER)')
            con.execute('INSERT INTO jid_map(lid_row_id, jid_row_id) VALUES (2, 1)')
        con.commit()
        con.close()

        con = sqlite3.connect(self.wa)
        con.execute('CREATE TABLE wa_contacts(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid TEXT NOT NULL, '
                    'is_whatsapp_user BOOLEAN NOT NULL, number TEXT, display_name TEXT, wa_name TEXT)')
        con.executemany('INSERT INTO wa_contacts(jid, is_whatsapp_user, wa_name) VALUES (?, 1, ?)', CONTACTS)
        con.commit()
        con.close()

    def _run(self, artifact):
        Context.set_files_found([self.msgstore, self.wa])
        _headers, rows, _source = artifact(Context)
        return rows

    def test_one_to_one_keeps_lid_and_contactless_chats(self):
        self._build()
        rows = self._run(_ONE_TO_ONE)
        # (Message Direction, Other Participant WA User Name, Message, Sending Party JID)
        self.assertEqual([(r[3], r[4], r[5], r[7]) for r in rows], [
            ('Incoming', 'Alice', 'lid chat, incoming', ALICE_PN),
            ('Outgoing', 'Alice', 'lid chat, outgoing', ''),
            ('Incoming', 'Bob', 'phone chat, incoming', BOB_PN),
            ('Incoming', UNKNOWN_PN, 'no contact, incoming', UNKNOWN_PN),
        ])

    def test_group_names_lid_sender(self):
        self._build()
        rows = self._run(_GROUP)
        # (Message Direction, Sending Party, Message, Conversation Name, Sending Party JID)
        self.assertEqual([(r[3], r[4], r[5], r[7], r[8]) for r in rows], [
            ('Incoming', None, None, 'Club', None),
            ('Incoming', 'Alice', 'group, lid sender', 'Club', ALICE_PN),
            ('Outgoing', 'Self', 'group, outgoing', 'Club', ''),
        ])

    def test_without_jid_map_phone_keyed_chats_still_resolve(self):
        self._build(with_jid_map=False)
        rows = self._run(_ONE_TO_ONE)
        names = {r[5]: r[4] for r in rows}
        self.assertEqual(names['phone chat, incoming'], 'Bob')
        # Without jid_map the LID cannot be matched; the message is kept and shown by jid
        self.assertEqual(names['lid chat, incoming'], ALICE_LID)


if __name__ == '__main__':
    unittest.main()
