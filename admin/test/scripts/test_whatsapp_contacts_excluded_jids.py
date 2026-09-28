"""WhatsApp - Contacts: which wa_contacts rows are reported, and what each column holds.

wa.db's wa_contacts holds rows for @newsletter jids and for status@broadcast. On the tested
images those rows carried no name and no number, so the artifact showed their jid in every
column; they are left out. wa_name is reported in its own column, never merged into Name,
Number is the number column as stored, without falling back to the jid, and status and
status_timestamp (milliseconds, 0 shown blank) are reported beside them. These tests build a
synthetic wa.db (no real evidence bytes), and check that a wa.db lacking those columns still
reports its rows.
"""
import datetime
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

STATUS_MS = 1767225600123  # 2026-01-01 00:00:00.123 UTC
STATUS_AT = datetime.datetime(2026, 1, 1, 0, 0, 0, 123000, tzinfo=datetime.timezone.utc)

# (jid, number, display_name, wa_name, status, status_timestamp)
ROWS = [
    ('000000000001@s.whatsapp.net', '+000000000001', 'Alice', 'Ally', 'Busy', STATUS_MS),
    ('000000000002@s.whatsapp.net', None, None, 'Bob', 'Hello', 0),
    ('000000000003@s.whatsapp.net', '', None, None, None, 0),
    ('120363000000000001@g.us', None, 'Club', None, None, 0),
    ('100000000000001@lid', None, None, None, None, 0),
    ('120363000000000002@newsletter', None, None, None, None, 0),
    ('120363000000000003@newsletter', None, None, None, None, 0),
    ('status@broadcast', None, None, None, None, 0),
]

EXPECTED = [
    ('Alice', 'Ally', '000000000001@s.whatsapp.net', '+000000000001', 'Busy', STATUS_AT),
    ('000000000002@s.whatsapp.net', 'Bob', '000000000002@s.whatsapp.net', None, 'Hello', None),
    ('000000000003@s.whatsapp.net', None, '000000000003@s.whatsapp.net', '', None, None),
    ('Club', None, '120363000000000001@g.us', None, None, None),
    ('100000000000001@lid', None, '100000000000001@lid', None, None, None),
]


class WhatsAppContactsExcludedJidsTest(unittest.TestCase):

    def _build(self, with_wa_name=True):
        extra = ', wa_name TEXT, status TEXT, status_timestamp INTEGER' if with_wa_name else ''
        con = sqlite3.connect(self.wa)
        con.execute('CREATE TABLE wa_contacts(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid TEXT NOT NULL, '
                    'is_whatsapp_user BOOLEAN NOT NULL, number TEXT, display_name TEXT, '
                    f'given_name TEXT, family_name TEXT{extra})')
        if with_wa_name:
            con.executemany('INSERT INTO wa_contacts(jid, is_whatsapp_user, number, display_name, wa_name, '
                            'status, status_timestamp) VALUES (?, 1, ?, ?, ?, ?, ?)', ROWS)
        else:
            con.executemany('INSERT INTO wa_contacts(jid, is_whatsapp_user, number, display_name) '
                            'VALUES (?, 1, ?, ?)', [r[:3] for r in ROWS])
        con.commit()
        con.close()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        data_folder = os.path.join(self.tmp.name, 'report', 'data')
        Context.set_data_folder(data_folder)
        folder = os.path.join(data_folder, 'Dump/data/data/com.whatsapp/databases')
        os.makedirs(folder)
        self.wa = os.path.join(folder, 'wa.db')

    def tearDown(self):
        Context.clear()
        self.tmp.cleanup()

    def test_newsletter_and_status_broadcast_rows_are_left_out(self):
        self._build()
        Context.set_files_found([self.wa])
        headers, rows, _source = _CONTACTS(Context)
        self.assertEqual(headers, ('Name', 'WhatsApp Name', 'JID', 'Number', 'Status Text',
                                   ('Status Timestamp', 'datetime')))
        self.assertEqual(rows, EXPECTED)

    def test_wa_name_is_its_own_column_and_number_is_as_stored(self):
        self._build()
        Context.set_files_found([self.wa])
        _headers, rows, _source = _CONTACTS(Context)
        # wa_name is never merged into Name, and Number never takes the jid.
        self.assertEqual([r[1] for r in rows], ['Ally', 'Bob', None, None, None])
        self.assertEqual([r[0] for r in rows][1], '000000000002@s.whatsapp.net')
        self.assertFalse(any(r[3] == r[2] for r in rows))

    def test_status_timestamp_is_milliseconds_and_zero_is_blank(self):
        self._build()
        Context.set_files_found([self.wa])
        _headers, rows, _source = _CONTACTS(Context)
        self.assertEqual([(r[4], r[5]) for r in rows],
                         [('Busy', STATUS_AT), ('Hello', None), (None, None), (None, None), (None, None)])

    def test_a_wa_db_without_wa_name_or_status_still_reports_its_rows(self):
        self._build(with_wa_name=False)
        Context.set_files_found([self.wa])
        _headers, rows, _source = _CONTACTS(Context)
        self.assertEqual(rows, [(r[0], None, r[2], r[3], None, None) for r in EXPECTED])


if __name__ == '__main__':
    unittest.main()
