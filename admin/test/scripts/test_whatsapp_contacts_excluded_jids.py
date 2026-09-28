"""WhatsApp - Contacts must leave out @newsletter and status@broadcast wa_contacts rows.

wa.db's wa_contacts holds rows for @newsletter jids and for status@broadcast. On the tested
images those rows carried no name and no number, so the artifact showed their jid in every
column. This test builds a synthetic wa.db (no real evidence bytes) holding one of each kind
of row and checks which are reported. It fails on the code before the exclusion.
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
from scripts.artifacts.WhatsApp import get_whatsapp_contacts  # noqa: E402  pylint: disable=wrong-import-position

_CONTACTS = get_whatsapp_contacts.__wrapped__

# (jid, number, display_name)
ROWS = [
    ('000000000001@s.whatsapp.net', '+000000000001', 'Alice'),
    ('000000000002@s.whatsapp.net', None, None),
    ('120363000000000001@g.us', None, 'Club'),
    ('100000000000001@lid', None, None),
    ('120363000000000002@newsletter', None, None),
    ('120363000000000003@newsletter', None, None),
    ('status@broadcast', None, None),
]


class WhatsAppContactsExcludedJidsTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        data_folder = os.path.join(self.tmp.name, 'report', 'data')
        Context.set_data_folder(data_folder)
        folder = os.path.join(data_folder, 'Dump/data/data/com.whatsapp/databases')
        os.makedirs(folder)
        self.wa = os.path.join(folder, 'wa.db')
        con = sqlite3.connect(self.wa)
        con.execute('CREATE TABLE wa_contacts(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid TEXT NOT NULL, '
                    'is_whatsapp_user BOOLEAN NOT NULL, number TEXT, display_name TEXT, '
                    'given_name TEXT, family_name TEXT, wa_name TEXT)')
        con.executemany('INSERT INTO wa_contacts(jid, is_whatsapp_user, number, display_name) '
                        'VALUES (?, 1, ?, ?)', ROWS)
        con.commit()
        con.close()

    def tearDown(self):
        Context.clear()
        self.tmp.cleanup()

    def test_newsletter_and_status_broadcast_rows_are_left_out(self):
        Context.set_files_found([self.wa])
        _headers, rows, _source = _CONTACTS(Context)
        self.assertEqual(rows, [
            ('Alice', '000000000001@s.whatsapp.net', '+000000000001'),
            ('000000000002@s.whatsapp.net', '000000000002@s.whatsapp.net', '000000000002@s.whatsapp.net'),
            ('Club', '120363000000000001@g.us', '120363000000000001@g.us'),
            ('100000000000001@lid', '100000000000001@lid', '100000000000001@lid'),
        ])


if __name__ == '__main__':
    unittest.main()
