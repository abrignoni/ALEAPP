"""WhatsApp Business tools: linked chat names and stored attachments."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.artifacts.whatsAppBusinessTools import (  # noqa: E402
    whatsapp_business_chat_lists, whatsapp_business_customer_notes, whatsapp_business_quick_reply_attachments)

LID = '100@lid'
PHONE = '15550000001@s.whatsapp.net'


def labels(headers):
    return [header[0] if isinstance(header, tuple) else header for header in headers]


class WhatsAppBusinessTools(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name)
        self.folder = self.root / 'data/data/com.whatsapp.w4b/databases'
        self.folder.mkdir(parents=True)
        con = sqlite3.connect(self.folder / 'msgstore.db')
        con.executescript(f'''
            CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
            CREATE TABLE jid_map(lid_row_id INTEGER, jid_row_id INTEGER, sort_id INTEGER);
            CREATE TABLE labels(_id INTEGER PRIMARY KEY, label_name TEXT, sort_id INTEGER);
            CREATE TABLE labeled_jid(_id INTEGER PRIMARY KEY, label_id INTEGER, jid_row_id INTEGER);
            CREATE TABLE quick_replies(_id INTEGER PRIMARY KEY, title TEXT, content TEXT, associated_label_ids TEXT);
            CREATE TABLE quick_reply_attachments(_id INTEGER PRIMARY KEY, quick_reply_id TEXT NOT NULL,
                uri TEXT NOT NULL, caption TEXT, media_type INTEGER);
            CREATE TABLE props(key TEXT, value TEXT);
            INSERT INTO jid VALUES (1, '{LID}'), (2, '{PHONE}'), (3, '200@lid');
            INSERT INTO jid_map VALUES (1, 2, 0);
            INSERT INTO labels VALUES (1, 'List', 1);
            INSERT INTO labeled_jid VALUES (1, 1, 1), (2, 1, 3);
            INSERT INTO quick_replies VALUES (7, 'shortcut', 'text', NULL);
            INSERT INTO quick_reply_attachments VALUES (1, '7', '/stored/path.jpg', 'caption', 1),
                (2, '99', '/stored/orphan.jpg', NULL, NULL);
            INSERT INTO props VALUES ('greeting_on', 'true');
        ''')
        con.commit()
        con.close()
        con = sqlite3.connect(self.folder / 'wa.db')
        con.executescript(f'''
            CREATE TABLE wa_contacts(jid TEXT, display_name TEXT, wa_name TEXT);
            CREATE TABLE wa_biz_profiles(_id INTEGER PRIMARY KEY, jid TEXT, business_description TEXT, email TEXT,
                address TEXT, latitude REAL, longitude REAL, hours_note TEXT, time_zone TEXT);
            INSERT INTO wa_contacts VALUES ('{PHONE}', 'Linked Name', NULL);
            INSERT INTO wa_biz_profiles VALUES (1, '{PHONE}', '', '', '', 0, 0, '', '');
        ''')
        con.commit()
        con.close()
        con = sqlite3.connect(self.folder / 'smb.db')
        con.executescript(f'''
            CREATE TABLE wa_notes(created_at INTEGER, modified_at INTEGER, chat_jid TEXT, note_content TEXT);
            INSERT INTO wa_notes VALUES (1700000000000, 1700000000000, '{LID}', 'note');
        ''')
        con.commit()
        con.close()
        files = [str(self.folder / name) for name in ('msgstore.db', 'wa.db', 'smb.db')]
        self.context = SimpleNamespace(
            get_files_found=lambda: files,
            get_relative_path=lambda path: str(pathlib.Path(path).relative_to(self.root)))

    def rows(self, function):
        headers, rows, _source = function.__wrapped__(self.context)
        names = labels(headers)
        return [dict(zip(names, row)) for row in rows]

    def test_lid_chat_name_comes_through_jid_map(self):
        rows = self.rows(whatsapp_business_chat_lists)
        self.assertEqual([(row['Chat'], row['Chat Name']) for row in rows], [(LID, 'Linked Name'), ('200@lid', '')])
        note = self.rows(whatsapp_business_customer_notes)[0]
        self.assertEqual((note['Chat'], note['Chat Name']), (LID, 'Linked Name'))

    def test_attachments_are_reported_as_stored(self):
        rows = self.rows(whatsapp_business_quick_reply_attachments)
        self.assertEqual([(r['Shortcut'], r['Attachment Path (as stored)'], r['Caption'], r['Media Type (as stored)'])
                          for r in rows], [('shortcut', '/stored/path.jpg', 'caption', 1),
                                           ('', '/stored/orphan.jpg', '', '')])


if __name__ == '__main__':
    unittest.main()
