"""CD0078: WhatsApp group conversations use JID identity independently of subject."""
import collections
import copy
import pathlib
import sqlite3
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from admin.test.scripts import test_whatsapp_lid_contacts as lid_fixture
from scripts.artifacts.WhatsApp import __artifacts_v2__, get_whatsapp_group_messages
from scripts.context import Context
from scripts import lavafuncs


class WhatsAppGroupIdentity(unittest.TestCase):
    def test_shared_null_and_empty_subjects_keep_group_identity(self):
        fixture = lid_fixture.WhatsAppLidContactsTest()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        fixture._build()  # pylint: disable=protected-access  # Reuse the tested modern-schema fixture.
        con = sqlite3.connect(fixture.msgstore)
        subjects = ('Club', 'Club', None, None, '', '')
        for index, subject in enumerate(subjects, 10):
            jid = f'1203630000000000{index}@g.us'
            con.execute('INSERT INTO jid(_id, raw_string, user, server) VALUES (?, ?, ?, ?)',
                        (index, jid, jid.split('@')[0], 'g.us'))
            con.execute('INSERT INTO chat(_id, jid_row_id, subject) VALUES (?, ?, ?)',
                        (index, index, subject))
            for direction in (0, 1):
                message_id = index * 2 + direction
                con.execute('INSERT INTO message(_id, chat_row_id, from_me, key_id, '
                            'sender_jid_row_id, timestamp, received_timestamp, message_type, '
                            'text_data, recipient_count) VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?, 2)',
                            (message_id, index, direction, f'key{message_id}', 2,
                             1767226000000 + message_id, f'group{index} direction{direction}'))
        con.commit()
        con.close()
        Context.set_files_found([fixture.msgstore, fixture.wa])
        headers, rows, _ = get_whatsapp_group_messages.__wrapped__(Context)
        self.assertEqual(len(headers), 18)
        self.assertEqual(headers[-1], 'Group JID')
        self.assertEqual(headers[5], 'Conversation Name')
        self.assertEqual(headers[8], 'Sending Party JID')
        self.assertEqual(len(rows), 15)  # Three original group rows plus twelve new ones.
        for index, subject in enumerate(subjects, 10):
            selected = [row for row in rows if row[-1] == f'1203630000000000{index}@g.us']
            self.assertEqual(len(selected), 2)
            self.assertEqual({row[3] for row in selected}, {'Incoming', 'Outgoing'})
            self.assertEqual([row[5] for row in selected], [subject, subject])
        identity_counts = collections.Counter(row[-1] for row in rows)
        self.assertEqual(len(identity_counts), 7)
        view = __artifacts_v2__['get_whatsapp_group_messages']['data_views']['conversation']
        self.assertEqual(view['conversationDiscriminatorColumn'], 'Group JID')
        self.assertEqual(view['conversationLabelColumn'], 'Conversation Name')
        # Use the actual report writer, including its column-name sanitization.
        lavafuncs.initialize_lava(fixture.tmp.name, fixture.tmp.name, 'fs')
        try:
            Context.set_artifact_info(__artifacts_v2__['get_whatsapp_group_messages'])
            Context.set_module_file_path(str(ROOT / 'scripts/artifacts/WhatsApp.py'))
            table, object_columns, column_map = lavafuncs.lava_process_artifact(
                'WhatsApp', 'WhatsApp', 'WhatsApp - Group Messages', headers,
                record_count=len(rows), func_name='get_whatsapp_group_messages',
                data_views=copy.deepcopy({'conversation': view}))
            lavafuncs.lava_insert_sqlite_data(table, rows, object_columns, headers, column_map)
            stored_view = lavafuncs.lava_data['artifacts']['WhatsApp'][0]['data_views']['conversation']
            self.assertEqual(stored_view['conversationDiscriminatorColumn'], 'group_jid')
            self.assertEqual(stored_view['conversationLabelColumn'], 'conversation_name')
            grouped = lavafuncs.lava_db.execute(
                f'SELECT group_jid, COUNT(*) FROM "{table}" GROUP BY group_jid').fetchall()
            self.assertEqual(dict(grouped), dict(identity_counts))
        finally:
            lavafuncs.lava_db.close()
            lavafuncs.lava_db = None
            lavafuncs.lava_data = None


if __name__ == '__main__':
    unittest.main()
