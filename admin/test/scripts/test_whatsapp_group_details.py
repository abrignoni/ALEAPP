"""WhatsApp - Group Details: groups on every chat_view shape, LID creators, and avatars.

The artifact joined chat_view.jid_row_id, a column older msgstore.db files do not have:
their chat_view carries raw_string_jid instead. The query then failed, the module's query
helper returned an empty list, and the artifact reported no groups on images that hold
them. It now reads the chat table, which carries jid_row_id on every schema seen.

A creator that wa.db records by a LID jid (...@lid) is matched to wa.db contacts through
msgstore.db jid_map. Group Picture and Creator WA Profile Picture are the files in the
app's files/Avatars folder named after the group's jid and the creator's jid, with a .j
extension, taken only from the container that holds the msgstore.db read.

These tests build synthetic databases and files (no real evidence bytes).
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
CREATOR_LID = '100000000000001@lid'
PEER = '000000000002@s.whatsapp.net'
CREATED_MS = 1767225600000
CREATED = '2026-01-01 00:00:00'

# (_id, raw_string); user and server are split from raw_string
JIDS = [(1, GROUP), (2, PEER), (3, CREATOR_LID), (4, CREATOR)]
# (_id, jid_row_id, subject, created_timestamp); only chat 1 carries a subject
CHATS = [(1, 1, 'Club', CREATED_MS), (2, 2, None, CREATED_MS + 1000)]

OLD_VIEW = ('CREATE VIEW chat_view AS SELECT chat._id AS _id, jid.raw_string AS raw_string_jid, '
            'chat.subject AS subject, chat.created_timestamp AS created_timestamp '
            'FROM chat chat LEFT JOIN jid jid ON chat.jid_row_id = jid._id')
NEW_VIEW = ('CREATE VIEW chat_view AS SELECT chat._id AS _id, chat.subject AS subject, '
            'chat.created_timestamp AS created_timestamp, '
            'CAST(COALESCE(chat.account_jid_row_id, chat.jid_row_id) AS INTEGER) AS jid_row_id, '
            'chat.jid_row_id AS original_jid_row_id FROM chat AS chat')

CONTAINER = 'Dump/data/data/com.whatsapp'


class WhatsAppGroupDetailsTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data_folder = os.path.join(self.tmp.name, 'report', 'data')
        Context.set_data_folder(self.data_folder)
        folder = os.path.join(self.data_folder, CONTAINER, 'databases')
        os.makedirs(folder)
        self.msgstore = os.path.join(folder, 'msgstore.db')
        self.wa = os.path.join(folder, 'wa.db')
        self.extra = []

    def tearDown(self):
        Context.clear()
        self.tmp.cleanup()

    def _build(self, view, creator_column=True, creator=CREATOR, jid_map=True):
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
        if jid_map:
            con.execute('CREATE TABLE jid_map(lid_row_id INTEGER PRIMARY KEY NOT NULL, '
                        'jid_row_id INTEGER NOT NULL, sort_id INTEGER)')
            con.execute('INSERT INTO jid_map(lid_row_id, jid_row_id) VALUES (3, 4)')
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
                        (GROUP, creator))
        else:
            con.execute('CREATE TABLE wa_group_admin_settings(jid TEXT PRIMARY KEY, restrict_mode INTEGER)')
            con.execute('INSERT INTO wa_group_admin_settings(jid, restrict_mode) VALUES (?, 0)', (GROUP,))
        con.commit()
        con.close()

    def _avatar(self, container, name):
        path = os.path.join(self.data_folder, container, 'files', 'Avatars', name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as handle:
            handle.write(b'\xff\xd8\xff\xe0')
        self.extra.append(path)
        return path

    def _run(self, with_wa=True):
        files = [self.msgstore, self.wa] if with_wa else [self.msgstore]
        Context.set_files_found(files + self.extra)
        with mock.patch.object(WhatsApp, '_media', side_effect=lambda p: f'media:{p}' if p else ''):
            headers, rows, _source = _GROUP_DETAILS(Context)
        self.assertEqual([h[0] if isinstance(h, tuple) else h for h in headers], [
            'Chat Created Timestamp', 'Group Name', 'Group Picture', 'Creator JID',
            'Creator JID (via jid_map)', 'Creator WA User Name', 'Creator WA Number',
            'Creator WA Profile Picture'])
        return [(r[0].strftime('%Y-%m-%d %H:%M:%S'),) + tuple(r[1:]) for r in rows]

    def test_older_chat_view_without_jid_row_id(self):
        self._build(OLD_VIEW)
        self.assertEqual(self._run(),
                         [(CREATED, 'Club', '', CREATOR, None, 'Creator', '+000000000001', '')])

    def test_newer_chat_view_gives_the_same_row(self):
        self._build(NEW_VIEW)
        self.assertEqual(self._run(),
                         [(CREATED, 'Club', '', CREATOR, None, 'Creator', '+000000000001', '')])

    def test_wa_db_without_creator_jid_keeps_the_group(self):
        self._build(OLD_VIEW, creator_column=False)
        self.assertEqual(self._run(), [(CREATED, 'Club', '', None, None, None, None, '')])

    def test_no_wa_db_keeps_the_group(self):
        self._build(NEW_VIEW)
        self.assertEqual(self._run(with_wa=False), [(CREATED, 'Club', '', None, None, None, None, '')])

    def test_lid_creator_is_matched_through_jid_map(self):
        self._build(NEW_VIEW, creator=CREATOR_LID)
        self.assertEqual(self._run(),
                         [(CREATED, 'Club', '', CREATOR_LID, CREATOR, 'Creator', '+000000000001', '')])

    def test_lid_creator_without_jid_map_is_kept_unmatched(self):
        self._build(NEW_VIEW, creator=CREATOR_LID, jid_map=False)
        self.assertEqual(self._run(), [(CREATED, 'Club', '', CREATOR_LID, None, None, None, '')])

    def test_pictures_come_from_the_same_container_named_by_jid(self):
        self._build(NEW_VIEW, creator=CREATOR_LID)
        group = self._avatar(CONTAINER, f'{GROUP}.j')
        creator = self._avatar(CONTAINER, f'{CREATOR}.j')
        # Decoys: another Android user's container, and a nested folder in this one.
        self._avatar('Dump/data/user/10/com.whatsapp', f'{GROUP}.j')
        self._avatar(f'{CONTAINER}/files/Avatars/nested', f'{GROUP}.j')
        rows = self._run()
        self.assertEqual([(r[2], r[7]) for r in rows], [(f'media:{group}', f'media:{creator}')])

    def test_a_query_that_cannot_run_is_logged(self):
        con = sqlite3.connect(':memory:')
        with mock.patch.object(WhatsApp, 'logfunc') as log:
            self.assertEqual(WhatsApp._run(con.cursor(), 'SELECT missing FROM nowhere'), [])  # pylint: disable=protected-access
        log.assert_called_once()
        self.assertIn('no such table: nowhere', log.call_args[0][0])


if __name__ == '__main__':
    unittest.main()
