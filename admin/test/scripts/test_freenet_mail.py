"""freenet Mail: emaildb.db messages, and mail.db messages and attachments.

Each test builds a small app data folder with the columns the artifacts read and runs the
artifacts through the folder seeker. Names, addresses and text are made up for the test.
"""
import fnmatch
import json
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
from scripts.artifacts import freenetMail as fm
from scripts.search_files import FileSeekerDir

PKG = 'de.freenet.mail'
JPEG = b'\xff\xd8\xff\xe0' + b'\x00' * 32
MS = 1767225600000  # 2026-01-01 00:00:00 UTC


class EvidenceContext:
    def __init__(self, root, seeker):
        self.root = root
        self.seeker = seeker

    def get_files_found(self):
        return [str(path) for path in sorted(self.root.rglob('*'))
                if path.is_file() and 'databases' in path.parts]

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace('\\', '/')

    def get_seeker(self):
        return self.seeker


def emaildb(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE message (body TEXT, cc TEXT NOT NULL, bcc TEXT NOT NULL, date INTEGER
        NOT NULL, has_attachments INTEGER NOT NULL, is_seen INTEGER NOT NULL, is_html INTEGER NOT NULL,
        is_answered INTEGER NOT NULL, is_forwarded INTEGER NOT NULL,
        status TEXT NOT NULL, subject TEXT, "to" TEXT NOT NULL, message_type TEXT NOT NULL,
        preview TEXT, from_email TEXT NOT NULL, from_name TEXT, message_uid TEXT NOT NULL,
        message_folder_account_id TEXT NOT NULL, message_folder_id TEXT NOT NULL)''')
    db.execute('CREATE TABLE folders (display_name TEXT, type TEXT, folder_id TEXT)')
    db.execute('CREATE TABLE accounts (account_id TEXT, email TEXT)')
    db.execute("INSERT INTO folders VALUES ('Posteingang', 'inbox', 'f1')")
    db.execute("INSERT INTO accounts VALUES ('a1', 'me@example.com')")
    to = json.dumps([{'email': 'to@example.com', 'imageUrl': None, 'name': 'To Name'}])
    db.execute('''INSERT INTO message VALUES ('<p>Hello <a href="https://example.com/x">link</a></p>
        <style>p {color: red}</style><script>alert(1)</script>', '[]', '[]', ?, 0, 1, 1, 1, 0,
        'DOWNLOADED', 'Subject', ?, 'new', 'Hello', 'from@example.com', 'From', 'u1', 'a1', 'f1')''',
               (MS, to))
    db.commit()
    db.close()


def mail_db(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE mail (answered SMALLINT, bcc VARCHAR, cc VARCHAR, deleted SMALLINT,
        email VARCHAR, folder_id VARCHAR, "from" VARCHAR, has_attachment SMALLINT, _id VARCHAR,
        received_date BIGINT, replyto VARCHAR, send_date BIGINT, size INTEGER, store VARCHAR,
        subject VARCHAR, "to" VARCHAR, unseen SMALLINT)''')
    db.execute('CREATE TABLE mail_body (html VARCHAR, _id INTEGER PRIMARY KEY, mail_hash_id VARCHAR, '
               'plain VARCHAR)')
    db.execute('''CREATE TABLE attachment (_id VARCHAR, download_finished SMALLINT, is_inline SMALLINT,
        local_file_path VARCHAR, mail VARCHAR, name VARCHAR, part_id VARCHAR, size BIGINT,
        type VARCHAR)''')
    db.execute('CREATE TABLE folder (email VARCHAR, folder_id VARCHAR, title VARCHAR)')
    db.execute("INSERT INTO folder VALUES ('me@example.com', 'INBOX', 'Posteingang')")
    sender = json.dumps([{'email': 'from@example.com', 'realname': 'From Name'}])
    db.execute('''INSERT INTO mail VALUES (0, '[]', '[]', 0, 'me@example.com', 'INBOX', ?, 1, 'm1',
        1767225600, '[]', 1767225500, 10, 'IMAP', 'Legacy', '[]', 1)''', (sender,))
    db.execute('''INSERT INTO mail VALUES (0, '[]', '[]', 0, 'me@example.com', 'INBOX', '[]', 0, 'm2',
        0, '[]', 1767225500, 10, 'MAIL_AD', 'Ad', '[]', 0)''')
    db.execute("INSERT INTO mail_body VALUES (NULL, 1, 'm1', 'plain text')")
    db.execute("INSERT INTO mail_body VALUES ('<b>only html</b>', 2, 'gone', NULL)")
    db.execute('''INSERT INTO attachment VALUES ('a1', 1, 0,
        'file:///storage/emulated/0/Download/my%20photo%20%5B1%5D.jpg', 'm1', 'my photo [1].jpg', '1',
        36, 'image/jpeg')''')
    db.execute('''INSERT INTO attachment VALUES ('a2', 1, 0,
        'file:///storage/emulated/0/Download/missing.jpg', 'm1', 'missing.jpg', '2', 36,
        'image/jpeg')''')
    db.execute("INSERT INTO attachment VALUES ('a3', 0, 0, NULL, 'nomail', 'x.pdf', '1', 5, 'application/pdf')")
    db.commit()
    db.close()


class FreenetMailTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        app = self.root / 'data' / 'data' / PKG / 'databases'
        emaildb(app / 'emaildb.db')
        mail_db(app / 'mail.db')
        download = self.root / 'media' / '0' / 'Download'
        download.mkdir(parents=True)
        (download / 'my photo [1].jpg').write_bytes(JPEG)
        (download / 'other.jpg').write_bytes(JPEG)

    def tearDown(self):
        self.temp.cleanup()

    def run_artifact(self, function):
        with tempfile.TemporaryDirectory() as staging:
            seeker = FileSeekerDir(str(self.root), staging)
            context = EvidenceContext(self.root, seeker)
            patterns = fm.__artifacts_v2__[function.__name__]['paths']
            for path in context.get_files_found():
                relative = 'root/' + context.get_relative_path(path)
                if Path(path).name in ('emaildb.db', 'mail.db') and (
                        ('emaildb' in relative) == (function.__name__ == 'freenet_mail_messages')):
                    self.assertTrue(any(fnmatch.fnmatch(relative, p) for p in patterns), relative)
            with patch.object(fm, 'check_in_media', side_effect=lambda path, _name: 'media:' + Path(path).name):
                headers, rows, _source = function.__wrapped__(context)
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        self.assertTrue(all(len(row) == len(names) for row in rows))
        return [dict(zip(names, row)) for row in rows]

    def test_messages_read_html_as_text_without_markup(self):
        rows = self.run_artifact(fm.freenet_mail_messages)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['Date'], datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(row['Body Text'], 'Hello link')
        self.assertNotIn('<', row['Body Text'])
        self.assertEqual((row['Folder'], row['Folder Type'], row['Account Email']),
                         ('Posteingang', 'inbox', 'me@example.com'))
        self.assertEqual(row['To'], 'To Name <to@example.com>')
        self.assertEqual((row['Seen'], row['Body Format']), ('Yes', 'HTML'))
        self.assertEqual((row['Answered'], row['Forwarded']), ('Yes', 'No'))

    def test_legacy_messages_read_seconds_and_keep_unmatched_bodies(self):
        rows = self.run_artifact(fm.freenet_mail_legacy_messages)
        self.assertEqual(len(rows), 3)
        first = next(row for row in rows if row['Mail ID'] == 'm1')
        self.assertEqual(first['Received (received_date)'], datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(first['Body Text'], 'plain text')
        self.assertEqual(first['From'], 'From Name <from@example.com>')
        self.assertEqual((first['Attachment'], first['Attachment Count']), ('media:my photo [1].jpg', 2))
        ad = next(row for row in rows if row['Mail ID'] == 'm2')
        self.assertEqual(ad['Received (received_date)'], '')
        orphan = next(row for row in rows if row['Mail ID'] == 'gone')
        self.assertEqual((orphan['In mail Table'], orphan['Body Text']), ('No', 'only html'))

    def test_legacy_attachments_find_the_saved_file_by_its_escaped_name(self):
        rows = {row['Attachment ID']: row for row in self.run_artifact(fm.freenet_mail_legacy_attachments)}
        self.assertEqual(len(rows), 3)
        self.assertEqual((rows['a1']['Media'], rows['a1']['Media Format']),
                         ('media:my photo [1].jpg', 'JPEG'))
        self.assertEqual((rows['a2']['Media'], rows['a2']['Media Format']), ('', 'File not in extraction'))
        self.assertEqual((rows['a3']['Media Format'], rows['a3']['Mail in mail Table']), ('', 'No'))


    def test_copies_are_joined_within_each_copy(self):
        second = self.root / 'data' / 'user' / '0' / PKG / 'databases' / 'mail.db'
        mail_db(second)
        db = sqlite3.connect(second)
        db.execute("UPDATE mail SET subject = 'Changed' WHERE _id = 'm1'")
        db.execute("UPDATE mail_body SET plain = 'changed text' WHERE mail_hash_id = 'm1'")
        db.commit()
        db.close()
        rows = [row for row in self.run_artifact(fm.freenet_mail_legacy_messages) if row['Mail ID'] == 'm1']
        self.assertEqual(sorted((row['Subject'], row['Body Text']) for row in rows),
                         [('Changed', 'changed text'), ('Legacy', 'plain text')])

if __name__ == '__main__':
    unittest.main()
