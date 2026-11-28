"""Mail.ru Mail: messages, attachments, send message records and contacts.

Each test builds a small app data folder with a subset of the columns the app's databases carry
and runs the artifacts through the folder seeker. The values are made up for the test.
"""
import fnmatch
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts import mailRu as mr
from scripts.search_files import FileSeekerDir

PKG = 'ru.mail.mailapp'
JPEG = b'\xff\xd8\xff\xe0' + b'\x00' * 32
MS = 1767225600000  # 2026-01-01 00:00:00 UTC
PREFETCH = 'accounts/aaaa/attachments/bbbb/7/123/photo [1].jpg'


class EvidenceContext:
    def __init__(self, root, seeker):
        self.root = root
        self.seeker = seeker

    def get_files_found(self):
        return [str(path) for path in sorted(self.root.rglob('*')) if path.is_file()
                and ('databases' in path.parts or 'attachments' in path.parts)]

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace('\\', '/')

    def get_seeker(self):
        return self.seeker


def mailbox(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE mail_message (id INTEGER PRIMARY KEY, account TEXT, from_full TEXT,
        date BIGINT, mFolder BIGINT, has_content SMALLINT, _id TEXT, is_flagged SMALLINT,
        is_forwarded SMALLINT, is_new SMALLINT, is_newsletter SMALLINT, is_pinned SMALLINT,
        is_replied SMALLINT, mail_thread_id TEXT, snippet TEXT, theme TEXT)''')
    db.execute('''CREATE TABLE mail_message_content (id INTEGER PRIMARY KEY, account TEXT,
        blind_copy TEXT, copy TEXT, let_body_html TEXT, let_body_plain TEXT, _id TEXT, reply_to TEXT,
        subject TEXT, "to" TEXT)''')
    db.execute('CREATE TABLE folder (id INTEGER PRIMARY KEY, account TEXT, _id BIGINT, name TEXT, type TEXT)')
    db.execute('''CREATE TABLE mails_attachments (id INTEGER PRIMARY KEY, account TEXT, content_length BIGINT,
        content_type TEXT, name TEXT, disposition TEXT, mMessageContent_id INTEGER, _id TEXT,
        path_to_prefetch TEXT)''')
    db.execute('''CREATE TABLE send_message_persist_parameters (id INTEGER PRIMARY KEY, bcc TEXT, cc TEXT,
        create_date BIGINT, "from" TEXT, account TEXT, message_body_html TEXT, message_body_plain TEXT,
        sending_error_message TEXT, send_message_type TEXT, state TEXT, subject TEXT, "to" TEXT)''')
    db.execute('''CREATE TABLE attach_persist_info (id INTEGER PRIMARY KEY, file_path TEXT, full_name TEXT,
        send_params_id BIGINT, size BIGINT)''')
    db.execute("INSERT INTO folder VALUES (1, 'me@example.com', 0, 'Inbox', 'inbox')")
    db.execute('''INSERT INTO mail_message VALUES (1, 'me@example.com', 'From <from@example.com>', ?, 0, 1,
        'm1', 0, 0, 1, 0, 0, 1, 't1', 'snip', 'Theme')''', (MS,))
    db.execute('''INSERT INTO mail_message_content VALUES (5, 'me@example.com', '', '', '<p>Hi <a
        href="https://example.com">x</a></p>', NULL, 'm1', 'r@example.com', 'Subject', '<to@example.com>')''')
    db.execute('''INSERT INTO mails_attachments VALUES (1, 'me@example.com', 36, 'image/jpeg', 'photo [1].jpg',
        'attachment', 5, 'a1', ?)''', (PREFETCH,))
    db.execute('''INSERT INTO send_message_persist_parameters VALUES (1, '', '', ?, NULL, 'me@example.com',
        NULL, 'draft text', NULL, 'NEW_MAIL', 'EDIT', 'Draft', 'to@example.com')''', (MS,))
    db.execute('''INSERT INTO attach_persist_info VALUES (1,
        '/storage/emulated/0/Android/data/ru.mail.mailapp/files/Pictures/p.jpg', 'p.jpg', 1, 36)''')
    db.commit()
    db.close()


def contacts(path):
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE contact (_id INTEGER PRIMARY KEY, email TEXT, name TEXT, lastname TEXT,
        display_name TEXT, priority INTEGER, account TEXT, company TEXT, job_title TEXT, address TEXT,
        comment TEXT, birthday TEXT, labels TEXT, server_id TEXT)''')
    db.execute("INSERT INTO contact (email, display_name, priority, account, server_id) VALUES "
               "('c@example.com', 'C', 3, 'me@example.com', 's1')")
    db.commit()
    db.close()


class MailRuTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        dbs = self.root / 'data' / 'data' / PKG / 'databases'
        mailbox(dbs / 'mailbox_db')
        contacts(dbs / 'mail_contacts_v2.db')
        ext = self.root / 'data' / 'media' / '0' / 'Android' / 'data' / PKG / 'files'
        saved = ext / PREFETCH
        saved.parent.mkdir(parents=True)
        saved.write_bytes(JPEG)
        (saved.parent / '.nomedia').write_bytes(b'')
        other = ext / 'accounts/aaaa/attachments/bbbb/9/456/other.jpg'
        other.parent.mkdir(parents=True)
        other.write_bytes(JPEG)
        (ext / 'Pictures').mkdir()
        (ext / 'Pictures' / 'p.jpg').write_bytes(JPEG)

    def tearDown(self):
        self.temp.cleanup()

    def run_artifact(self, function):
        with tempfile.TemporaryDirectory() as staging:
            seeker = FileSeekerDir(str(self.root), staging)
            context = EvidenceContext(self.root, seeker)
            patterns = mr.__artifacts_v2__[function.__name__]['paths']
            for path in context.get_files_found():
                relative = 'root/' + context.get_relative_path(path)
                if Path(path).name == '.nomedia':
                    continue
                wanted = ('mail_contacts' in relative) == (function.__name__ == 'mailru_contacts') and (
                    '/attachments/' not in relative or function.__name__ in ('mailru_messages', 'mailru_attachments'))
                if wanted:
                    self.assertTrue(any(fnmatch.fnmatch(relative, p) for p in patterns), relative)
            with patch.object(mr, 'check_in_media', side_effect=lambda path, _name: 'media:' + Path(path).name):
                headers, rows, _source = function.__wrapped__(context)
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        self.assertTrue(all(len(row) == len(names) for row in rows))
        return [dict(zip(names, row)) for row in rows]

    def test_messages(self):
        rows = self.run_artifact(mr.mailru_messages)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['Date'], datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual((row['Body Text'], row['Subject'], row['Folder']), ('Hi x', 'Subject', 'Inbox'))
        self.assertEqual((row['Attachment'], row['Attachment Count']), ('media:photo [1].jpg', 1))
        self.assertEqual((row['Unread'], row['Replied']), ('Yes', 'Yes'))

    def test_attachments_keep_files_no_row_names(self):
        rows = self.run_artifact(mr.mailru_attachments)
        self.assertEqual(len(rows), 2)
        named = [row for row in rows if row['Named by a Row'] == 'Yes'][0]
        self.assertEqual((named['Media'], named['Media Format']), ('media:photo [1].jpg', 'JPEG'))
        other = [row for row in rows if row['Named by a Row'] == 'No'][0]
        self.assertEqual(other['Name'], 'other.jpg')

    def test_a_second_users_file_is_matched_to_that_users_database(self):
        mailbox(self.root / 'data' / 'user' / '10' / PKG / 'databases' / 'mailbox_db')
        saved = self.root / 'data' / 'media' / '10' / 'Android' / 'data' / PKG / 'files' / PREFETCH
        saved.parent.mkdir(parents=True)
        saved.write_bytes(JPEG)
        rows = [row for row in self.run_artifact(mr.mailru_attachments) if row['Android User'] == '10']
        self.assertEqual([(row['Named by a Row'], row['Media Format']) for row in rows], [('Yes', 'JPEG')])

    def test_send_message_records_show_their_attached_file(self):
        rows = self.run_artifact(mr.mailru_send_message_records)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]['Created'], rows[0]['Attachment'], rows[0]['Body Text']),
                         (datetime(2026, 1, 1, tzinfo=timezone.utc), 'media:p.jpg', 'draft text'))

    def test_table_cells_stay_apart_in_body_text(self):
        self.assertEqual(mr._html_text(  # pylint: disable=protected-access
            '<table><tr><td>Account</td><td>123</td></tr></table>'), 'Account\n123')

    def test_contacts(self):
        rows = self.run_artifact(mr.mailru_contacts)
        self.assertEqual([(r['Email'], r['Display Name'], r['Priority (as stored)']) for r in rows],
                         [('c@example.com', 'C', 3)])
        self.assertIn('Name', rows[0])


if __name__ == '__main__':
    unittest.main()
