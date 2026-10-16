"""Legacy revoked schemas retain rows even when wa.db contacts are attached."""
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.artifacts import whatsAppExtended as module  # pylint: disable=wrong-import-position

class Context:
    def __init__(self, files):
        self.files = [str(p) for p in files]
    def get_files_found(self):
        return self.files
    def get_relative_path(self, path):
        return pathlib.Path(path).name

class TestRevokedSchema(unittest.TestCase):
    def parse(self, modern):
        with tempfile.TemporaryDirectory() as directory:
            msg = pathlib.Path(directory) / 'msgstore.db'
            wa = pathlib.Path(directory) / 'wa.db'
            with sqlite3.connect(wa) as db:
                db.executescript("CREATE TABLE wa_contacts(jid TEXT, wa_name TEXT); INSERT INTO wa_contacts VALUES('sender', 'Contact');")
            with sqlite3.connect(msg) as db:
                db.executescript('''CREATE TABLE message(_id INTEGER, timestamp INTEGER, received_timestamp INTEGER, from_me INTEGER, sender_jid_row_id INTEGER, chat_row_id INTEGER, message_type INTEGER, text_data TEXT);
                    INSERT INTO message VALUES(1,1700000000000,1700000001000,0,1,1,64,'retained text');
                    CREATE TABLE jid(_id INTEGER, raw_string TEXT); INSERT INTO jid VALUES(1,'sender');
                    CREATE TABLE chat(_id INTEGER, jid_row_id INTEGER, subject TEXT); INSERT INTO chat VALUES(1,1,'Chat');''')
                extra = ', revoke_timestamp INTEGER, admin_jid_row_id INTEGER' if modern else ''
                db.execute('CREATE TABLE message_revoked(message_row_id INTEGER, revoked_key_id TEXT' + extra + ')')
                if modern:
                    db.execute("INSERT INTO message_revoked VALUES(1,'key',1700000002000,1)")
                else:
                    db.execute("INSERT INTO message_revoked VALUES(1,'key')")
            with patch.object(module, 'logfunc') as logger:
                result = module.get_whatsapp_revoked_messages.__wrapped__(Context([msg, wa]))
                self.assertFalse(any('query failed' in str(call) for call in logger.call_args_list))
            return result

    def test_legacy_schema_retains_row_and_contact_with_empty_optional_fields(self):
        headers, rows, _ = self.parse(False)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(headers), len(rows[0]))
        self.assertEqual(rows[0][0], '')
        self.assertIsNone(rows[0][6])
        self.assertEqual(rows[0][5], 'Contact')
        self.assertEqual(rows[0][-1], 'retained text')

    def test_modern_schema_preserves_revoke_time_and_admin(self):
        _, rows, _ = self.parse(True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0].year, 2023)
        self.assertEqual(rows[0][6], 'sender')

if __name__ == '__main__':
    unittest.main()
