"""WhatsApp - Group Details must read groups whatever chat_view looks like.

The artifact joined chat_view.jid_row_id, a column older msgstore.db files do not have:
their chat_view carries raw_string_jid instead. The query then failed, the module's query
helper returned an empty list, and the artifact reported no groups on images that hold
them. It now reads the chat table, which carries jid_row_id on every schema seen.

These tests build synthetic databases (no real evidence bytes): a group and a contact in
wa.db naming its creator, under the older chat_view and the newer one, with a wa.db that
lacks creator_jid, and with no wa.db at all. The old-view, no-creator_jid and no-wa.db
tests fail on the pre-fix code.
"""
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, REPO_ROOT)

from scripts.context import Context  # noqa: E402  pylint: disable=wrong-import-position
from scripts.artifacts import WhatsApp  # noqa: E402  pylint: disable=wrong-import-position

_GROUP_DETAILS = WhatsApp.get_whatsapp_group_details.__wrapped__

GROUP = '120363000000000001@g.us'
CREATOR = '000000000001@s.whatsapp.net'
PEER = '000000000002@s.whatsapp.net'
CREATED_MS = 1767225600000

# (_id, raw_string); user and server are split from raw_string
JIDS = [(1, GROUP), (2, PEER)]
# (_id, jid_row_id, subject, created_timestamp); only chat 1 carries a subject
CHATS = [(1, 1, 'Club', CREATED_MS), (2, 2, None, CREATED_MS + 1000)]

OLD_VIEW = ('CREATE VIEW chat_view AS SELECT chat._id AS _id, jid.raw_string AS raw_string_jid, '
            'chat.subject AS subject, chat.created_timestamp AS created_timestamp '
            'FROM chat chat LEFT JOIN jid jid ON chat.jid_row_id = jid._id')
NEW_VIEW = ('CREATE VIEW chat_view AS SELECT chat._id AS _id, chat.subject AS subject, '
            'chat.created_timestamp AS created_timestamp, '
            'CAST(COALESCE(chat.account_jid_row_id, chat.jid_row_id) AS INTEGER) AS jid_row_id, '
            'chat.jid_row_id AS original_jid_row_id FROM chat AS chat')


class WhatsAppGroupDetailsTest(unittest.TestCase):

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

    def _build(self, view, creator_column=True):
        con = sqlite3.connect(self.msgstore)
        con.execute('CREATE TABLE jid(_id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT NOT NULL, '
                    'server TEXT NOT NULL, raw_string TEXT)')
        con.execute('CREATE TABLE chat(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid_row_id INTEGER, '
                    'account_jid_row_id INTEGER, subject TEXT, created_timestamp INTEGER)')
        con.execute(view)
        for row_id, raw in JIDS:
            user, server = raw.split('@')
            con.execute('INSERT INTO jid(_id, user, server, raw_string) VALUES (?, ?, ?, ?)',
                        (row_id, user, server, raw))
        con.executemany('INSERT INTO chat(_id, jid_row_id, subject, created_timestamp) '
                        'VALUES (?, ?, ?, ?)', CHATS)
        con.commit()
        con.close()

        con = sqlite3.connect(self.wa)
        con.execute('CREATE TABLE wa_contacts(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid TEXT NOT NULL, '
                    'is_whatsapp_user BOOLEAN NOT NULL, number TEXT, display_name TEXT, wa_name TEXT)')
        con.execute("INSERT INTO wa_contacts(jid, is_whatsapp_user, number, wa_name) "
                    "VALUES (?, 1, '+000000000001', 'Creator')", (CREATOR,))
        if creator_column:
            con.execute('CREATE TABLE wa_group_admin_settings(jid TEXT PRIMARY KEY, creator_jid TEXT)')
            con.execute('INSERT INTO wa_group_admin_settings(jid, creator_jid) VALUES (?, ?)',
                        (GROUP, CREATOR))
        else:
            con.execute('CREATE TABLE wa_group_admin_settings(jid TEXT PRIMARY KEY, restrict_mode INTEGER)')
            con.execute('INSERT INTO wa_group_admin_settings(jid, restrict_mode) VALUES (?, 0)', (GROUP,))
        con.commit()
        con.close()

    def _run(self, with_wa=True):
        Context.set_files_found([self.msgstore, self.wa] if with_wa else [self.msgstore])
        _headers, rows, _source = _GROUP_DETAILS(Context)
        # (Group Creation Timestamp, Group Name, Creator JID, Creator WA User Name, Creator WA Number)
        return [(r[0].strftime('%Y-%m-%d %H:%M:%S'), r[1], r[2], r[3], r[4]) for r in rows]

    def test_older_chat_view_without_jid_row_id(self):
        self._build(OLD_VIEW)
        self.assertEqual(self._run(),
                         [('2026-01-01 00:00:00', 'Club', CREATOR, 'Creator', '+000000000001')])

    def test_newer_chat_view_gives_the_same_row(self):
        self._build(NEW_VIEW)
        self.assertEqual(self._run(),
                         [('2026-01-01 00:00:00', 'Club', CREATOR, 'Creator', '+000000000001')])

    def test_wa_db_without_creator_jid_keeps_the_group(self):
        self._build(OLD_VIEW, creator_column=False)
        self.assertEqual(self._run(), [('2026-01-01 00:00:00', 'Club', None, None, None)])

    def test_no_wa_db_keeps_the_group(self):
        self._build(NEW_VIEW)
        self.assertEqual(self._run(with_wa=False), [('2026-01-01 00:00:00', 'Club', None, None, None)])

    def test_a_query_that_cannot_run_is_logged(self):
        con = sqlite3.connect(':memory:')
        with mock.patch.object(WhatsApp, 'logfunc') as log:
            self.assertEqual(WhatsApp._run(con.cursor(), 'SELECT missing FROM nowhere'), [])  # pylint: disable=protected-access
        log.assert_called_once()
        self.assertIn('no such table: nowhere', log.call_args[0][0])


if __name__ == '__main__':
    unittest.main()
