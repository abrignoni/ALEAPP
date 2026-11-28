"""Telekom Mail: messages and attachments from telekom-database and files/attachments.

Each test builds a small app data folder with a subset of the columns the app writes and runs the artifacts
through the folder seeker. The values are made up for the test.
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
from scripts.artifacts import telekomMail as tk
from scripts.search_files import FileSeekerDir

PKG = 'de.telekom.mail'
PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 32
MS = 1767225600000  # 2026-01-01 00:00:00 UTC
ACCOUNT = '000000000000-0001'


class EvidenceContext:
    def __init__(self, root, seeker):
        self.root = root
        self.seeker = seeker

    def get_files_found(self):
        return [str(path) for path in sorted(self.root.rglob('*')) if path.is_file()]

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace('\\', '/')

    def get_seeker(self):
        return self.seeker


def database(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE Mail (id INTEGER PRIMARY KEY, xguid TEXT, messageId TEXT, accountId TEXT,
        folderPath TEXT, subject TEXT, recipients TEXT, dateAndTime INTEGER, hasAttachments INTEGER,
        isForwarded INTEGER, priority TEXT, isAnswered INTEGER, isRead INTEGER, isReadLocally INTEGER,
        isDeletedLocally INTEGER, previewText TEXT, outboxState TEXT, attachments TEXT,
        sender_name TEXT, sender_address TEXT, html TEXT, plain TEXT, reply_to_name TEXT,
        reply_to_address TEXT)''')
    db.execute('CREATE TABLE Folder (accountId TEXT, name TEXT, path TEXT)')
    db.execute('CREATE TABLE Account (accountId TEXT, email TEXT)')
    db.execute("INSERT INTO Folder VALUES (?, 'Posteingang', 'INBOX')", (ACCOUNT,))
    db.execute("INSERT INTO Account VALUES (?, 'me@example.com')", (ACCOUNT,))
    uri = f'content://de.telekom.mail.fileprovider/internal_files/attachments/{ACCOUNT}/INBOX/mail%3A%3A2/fulls/0/logo'
    attachments = json.dumps([
        {'fileName': 'logo', 'mediaType': 'image', 'subType': 'png', 'sizeInBytes': 40, 'isInline': True,
         'index': 0, 'full': {'path': uri, 'status': 'NotAvailable'}, 'preview': {'path': '', 'status': ''}},
        {'fileName': 'gone', 'mediaType': 'image', 'subType': 'png', 'sizeInBytes': 40, 'isInline': True,
         'index': 1, 'full': {'path': uri.replace('/0/logo', '/1/gone'), 'status': 'NotAvailable'},
         'preview': {'path': '', 'status': ''}}])
    recipients = json.dumps([{'address': 'to@example.com', 'type': 'to'},
                             {'address': 'cc@example.com', 'type': 'cc', 'name': 'Cc Name'}])
    db.execute('''INSERT INTO Mail (id, xguid, messageId, accountId, folderPath, subject, recipients,
        dateAndTime, hasAttachments, isForwarded, priority, isAnswered, isRead, isDeletedLocally,
        previewText, attachments, sender_name, sender_address, html) VALUES
        (2, 'x', 'm', ?, 'INBOX', 'Hi', ?, ?, 0, 0, 'NORMAL', 0, 1, 0, 'Pre', ?, 'Sender',
         'from@example.com', '<div>Hello <a href="https://example.com">there</a></div>')''',
               (ACCOUNT, recipients, MS, attachments))
    db.commit()
    db.close()


class TelekomMailTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        app = self.root / 'data' / 'data' / PKG
        database(app / 'databases' / 'telekom-database')
        files = app / 'files' / 'attachments' / ACCOUNT
        (files / 'INBOX' / 'mail::2' / 'fulls' / '0').mkdir(parents=True)
        (files / 'INBOX' / 'mail::2' / 'fulls' / '0' / 'logo').write_bytes(PNG)
        (files / 'INBOX' / 'Sent' / 'mail::abc' / 'previews' / '3').mkdir(parents=True)
        (files / 'INBOX' / 'Sent' / 'mail::abc' / 'previews' / '3' / 'pic.jpeg').write_bytes(PNG)

    def tearDown(self):
        self.temp.cleanup()

    def run_artifact(self, function):
        with tempfile.TemporaryDirectory() as staging:
            seeker = FileSeekerDir(str(self.root), staging)
            context = EvidenceContext(self.root, seeker)
            patterns = tk.__artifacts_v2__[function.__name__]['paths']
            for path in context.get_files_found():
                relative = 'root/' + context.get_relative_path(path)
                self.assertTrue(any(fnmatch.fnmatch(relative, p) for p in patterns), relative)
            with patch.object(tk, 'check_in_media', side_effect=lambda path, _name: 'media:' + Path(path).name):
                headers, rows, _source = function.__wrapped__(context)
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        self.assertTrue(all(len(row) == len(names) for row in rows))
        return [dict(zip(names, row)) for row in rows]

    def test_messages(self):
        rows = self.run_artifact(tk.telekom_mail_messages)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['Date'], datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual((row['Body Text'], row['Body Format']), ('Hello there', 'HTML'))
        self.assertEqual((row['To'], row['Cc']), ('to@example.com', 'Cc Name <cc@example.com>'))
        self.assertEqual((row['Folder Name'], row['Account Email']), ('Posteingang', 'me@example.com'))
        self.assertEqual((row['Attachment'], row['Attachments Listed']), ('media:logo', 2))

    def test_attachments_link_by_recorded_path_and_keep_unnamed_files(self):
        rows = self.run_artifact(tk.telekom_mail_attachments)
        self.assertEqual(len(rows), 3)
        named = {row['File Name']: row for row in rows if row['Named by a Mail'] == 'Yes'}
        self.assertEqual((named['logo']['Media'], named['logo']['Media Format']), ('media:logo', 'PNG'))
        self.assertEqual(named['gone']['Media Format'], 'File not in extraction')
        unnamed = [row for row in rows if row['Named by a Mail'] == 'No']
        self.assertEqual(len(unnamed), 1)
        self.assertEqual((unnamed[0]['Copy'], unnamed[0]['Mail Folder Path'], unnamed[0]['Attachment Index'],
                          unnamed[0]['Media Format']), ('Preview', 'INBOX/Sent', '3', 'PNG'))

    def test_provider_uri_outside_its_roots_is_not_followed(self):
        self.assertIsNone(tk._provider_tail(  # pylint: disable=protected-access
            'content://de.telekom.mail.fileprovider/external_files/Download/x'))
        self.assertIsNone(tk._provider_tail(  # pylint: disable=protected-access
            'content://de.telekom.mail.fileprovider/internal_files/../databases/x'))


if __name__ == '__main__':
    unittest.main()
