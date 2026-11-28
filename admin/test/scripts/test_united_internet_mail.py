"""WEB.DE, GMX and 1&1 mail: messages, attachments, body files, identities and receivers.

Each test builds a small app data folder with the schema the apps write (mail_room.db,
identitiy_db, known_receivers and the cache files) and runs the artifacts through the folder
seeker. The values are made up for the test.
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
from scripts.artifacts import unitedInternetMail as uimail
from scripts.search_files import FileSeekerDir

PKG = 'de.web.mobile.android.mail'
ACCOUNT_UUID = '00000000-0000-0000-0000-000000000001'
JPEG = b'\xff\xd8\xff\xe0' + b'\x00' * 32
MS = 1767225600000  # 2026-01-01 00:00:00 UTC

# The fixture files each artifact reads, by a part of their path; each must match its paths.
READS = {
    'ui_mail_messages': ('/mail_room.db', '/identitiy_db', '/cache/attachment_', '/room_mail_bodies/'),
    'ui_mail_attachments': ('/mail_room.db', '/identitiy_db', '/cache/attachment_'),
    'ui_mail_body_files': ('/mail_room.db', '/room_mail_bodies/'),
    'ui_mail_accounts': ('/identitiy_db',),
    'ui_mail_known_receivers': ('/known_receivers',),
}


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


def mail_room(path, mails, attachments=(), folders=((1, 'INBOX', 0),)):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE mail (textbody TEXT, remote_mail_uid TEXT NOT NULL, folderId INTEGER
        NOT NULL, account_uid TEXT NOT NULL, account_id INTEGER NOT NULL, subject TEXT, sender TEXT
        NOT NULL, email_from TEXT, replyTo TEXT, email_to TEXT, cc TEXT, bcc TEXT, date INTEGER,
        priority INTEGER, body TEXT, preview TEXT, mailType TEXT NOT NULL, _id INTEGER PRIMARY KEY,
        internalDate INTEGER, isUnread INTEGER, isForwarded INTEGER, isAnswered INTEGER,
        isStarred INTEGER)''')
    db.execute('''CREATE TABLE attachment (_id INTEGER PRIMARY KEY, mailId INTEGER NOT NULL,
        contentType TEXT NOT NULL, name TEXT, size INTEGER NOT NULL, status INTEGER NOT NULL,
        localPathUri TEXT, uri TEXT NOT NULL, inline INTEGER NOT NULL)''')
    db.execute('CREATE TABLE folder (_id INTEGER PRIMARY KEY, name TEXT NOT NULL, type INTEGER NOT NULL)')
    db.executemany('INSERT INTO folder VALUES (?,?,?)', folders)
    for mail_id, subject, date, body in mails:
        db.execute('''INSERT INTO mail (_id, textbody, remote_mail_uid, folderId, account_uid,
            account_id, subject, sender, email_from, email_to, date, body, mailType, internalDate,
            isUnread, isForwarded, isAnswered, isStarred)
            VALUES (?, 'text', 'uid', 1, ?, 1, ?, 'Sender', 'sender@example.com',
                    'to@example.com', ?, ?, 'email', ?, 1, 0, 0, 0)''',
                   (mail_id, ACCOUNT_UUID, subject, date, body, date))
    db.executemany('''INSERT INTO attachment (_id, mailId, contentType, name, size, status,
        localPathUri, uri, inline) VALUES (?,?,?,?,?,?,?,?,0)''', attachments)
    db.commit()
    db.close()


def identities(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE Identity (id INTEGER PRIMARY KEY, accountId INTEGER NOT NULL,
        name TEXT NOT NULL, email TEXT NOT NULL, isDefaultSender INTEGER NOT NULL,
        isDefaultReceiver INTEGER NOT NULL, type TEXT NOT NULL, uri TEXT NOT NULL,
        entryDate TEXT NOT NULL, isDeletable INTEGER NOT NULL, signature TEXT)''')
    db.execute("INSERT INTO Identity VALUES (1, 1, 'Other', 'alias@example.com', 0, 0, 'MANAGED', "
               "'u', '2026-01-01T00:00:00Z', 1, NULL)")
    db.execute("INSERT INTO Identity VALUES (2, 1, 'Owner', 'owner@example.com', 1, 1, 'MANAGED', "
               "'u', '2026-01-01T00:00:00Z', 0, NULL)")
    db.commit()
    db.close()


class UnitedInternetMailTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'evidence'
        self.root.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def app(self, user_dir='data/data'):
        return self.root / user_dir / PKG

    def write(self, relative, data):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def run_artifact(self, function):
        with tempfile.TemporaryDirectory() as staging:
            seeker = FileSeekerDir(str(self.root), staging)
            context = EvidenceContext(self.root, seeker)
            patterns = uimail.__artifacts_v2__[function.__name__]['paths']
            reads = READS[function.__name__]
            for path in context.get_files_found():
                relative = 'root/' + context.get_relative_path(path)
                if relative.endswith(('-journal', '-wal', '-shm')) or not any(
                        part in relative for part in reads):
                    continue
                self.assertTrue(any(fnmatch.fnmatch(relative, pattern) for pattern in patterns),
                                f'{relative} matches no path of {function.__name__}')
            with patch.object(uimail, 'check_in_media', side_effect=lambda path, _name:
                              'media:' + context.get_relative_path(path)):
                headers, rows, _source = function.__wrapped__(context)
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        self.assertTrue(all(len(row) == len(names) for row in rows))
        return [dict(zip(names, row)) for row in rows]

    def build(self, user_dir='data/data'):
        app = self.app(user_dir)
        body = f'file:///data/user/0/{PKG}/cache/room_mail_bodies/{ACCOUNT_UUID}/abc.html'
        mail_room(app / 'databases' / 'mail_room.db', [
            (1, 'With file', MS, body), (2, 'With thumbnail', MS + 1000, None),
            (3, 'No date', 0, f'file:///data/user/0/{PKG}/cache/room_mail_bodies/{ACCOUNT_UUID}/gone.html'),
        ], attachments=[
            (10, 1, 'image/jpeg', 'a.jpg', 36, 2, f'file:///data/user/0/{PKG}/cache/attachment_10.temp',
             '../../Mail/111/Attachment/MF8x'),
            (11, 2, 'image/jpeg', 'b.jpg', 36, 1, None, '../../Mail/222/Attachment/MF8y'),
        ])
        identities(app / 'databases' / 'identitiy_db')
        self.write(f'{user_dir}/{PKG}/cache/attachment_10.temp', JPEG)
        self.write(f'{user_dir}/{PKG}/cache/attachment_thumbnail_222_Attachment_MF8y_120x90.temp', JPEG)
        self.write(f'{user_dir}/{PKG}/cache/attachment_thumbnail_999_Attachment_MF8z_120x90.temp', JPEG)
        self.write(f'{user_dir}/{PKG}/cache/room_mail_bodies/{ACCOUNT_UUID}/abc.html', b'<html></html>')
        self.write(f'{user_dir}/{PKG}/cache/room_mail_bodies/{ACCOUNT_UUID}/1700000000000.html', b'<p>')

    def test_messages_join_folder_identity_attachment_and_body(self):
        self.build()
        rows = {row['Subject']: row for row in self.run_artifact(uimail.ui_mail_messages)}
        first = rows['With file']
        self.assertEqual(first['Header Date'], datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual((first['Folder'], first['Folder Type'], first['Account Email']),
                         ('INBOX', 'Inbox', 'owner@example.com'))
        self.assertEqual(first['Attachment'], f'media:data/data/{PKG}/cache/attachment_10.temp')
        self.assertEqual((first['HTML Body'], first['Unread'], first['App']), ('Found', 'Yes', PKG))
        self.assertEqual(rows['With thumbnail']['Attachment'],
                         f'media:data/data/{PKG}/cache/attachment_thumbnail_222_Attachment_MF8y_120x90.temp')
        self.assertEqual((rows['No date']['Header Date'], rows['No date']['HTML Body']),
                         ('', 'File not in extraction'))

    def test_attachments_list_thumbnails_and_unnamed_files(self):
        self.build()
        rows = self.run_artifact(uimail.ui_mail_attachments)
        named = {row['Name']: row for row in rows if row['In mail_room.db'] == 'Yes'}
        self.assertEqual(named['a.jpg']['Media Format'], 'JPEG')
        self.assertEqual(named['b.jpg']['Media'], '')
        self.assertTrue(named['b.jpg']['Thumbnail'].endswith('MF8y_120x90.temp'))
        orphans = [row['Name'] for row in rows if row['In mail_room.db'] == 'No']
        self.assertEqual(orphans, ['attachment_thumbnail_999_Attachment_MF8z_120x90.temp'])

    def test_body_files_say_which_mail_names_them(self):
        self.build()
        rows = {row['File Name']: row for row in self.run_artifact(uimail.ui_mail_body_files)}
        self.assertEqual((rows['abc.html']['Named by a Mail'], rows['abc.html']['Mail Subject']),
                         ('Yes', 'With file'))
        self.assertEqual(rows['1700000000000.html']['Named by a Mail'], 'No')

    def test_identities_and_receivers(self):
        self.build()
        accounts = self.run_artifact(uimail.ui_mail_accounts)
        self.assertEqual(sorted(row['Email'] for row in accounts), ['alias@example.com', 'owner@example.com'])
        db_path = self.app() / 'databases' / 'known_receivers'
        db = sqlite3.connect(db_path)
        db.execute('CREATE TABLE contacts (_id INTEGER PRIMARY KEY, data1 TEXT NOT NULL, '
                   'display_name TEXT, times_contacted INTEGER NOT NULL, flags INTEGER NOT NULL)')
        db.execute("INSERT INTO contacts VALUES (1, 'peer@example.com', 'Peer', 2, 0)")
        db.commit()
        db.close()
        rows = self.run_artifact(uimail.ui_mail_known_receivers)
        self.assertEqual([(row['Address'], row['Times Contacted (as stored)']) for row in rows],
                         [('peer@example.com', 2)])

    def test_copies_are_joined_and_a_damaged_copy_is_skipped(self):
        self.build('data/data')
        mail_room(self.app('data/user/0') / 'databases' / 'mail_room.db',
                  [(1, 'With file', MS, None), (4, 'Only here', MS + 5000, None)])
        damaged = self.app('data/user/0') / 'databases' / 'identitiy_db'
        damaged.write_bytes(b'SQLite format 3\x00' + b'\xff' * 4000)
        rows = self.run_artifact(uimail.ui_mail_messages)
        subjects = sorted(row['Subject'] for row in rows)
        # Mail 1 differs between the copies (body), so it is listed once per version.
        self.assertEqual(subjects, ['No date', 'Only here', 'With file', 'With file', 'With thumbnail'])
        self.assertTrue(all(row['Account Email'] == 'owner@example.com'
                            for row in rows if row['Subject'] != 'Only here'))

    def test_a_rollback_snapshot_keeps_its_user(self):
        mail_room(self.root / f'data/misc_ce/10/rollback/42/{PKG}/databases/mail_room.db',
                  [(1, 'Snapshot', MS, None)])
        rows = self.run_artifact(uimail.ui_mail_messages)
        self.assertEqual([(row['Subject'], row['Android User']) for row in rows], [('Snapshot', '10')])


    def test_every_thumbnail_size_and_differing_copy_is_listed(self):
        self.build('data/data')
        tail = f'{PKG}/cache/attachment_thumbnail_222_Attachment_MF8y_'
        self.write(f'data/data/{tail}240x180.temp', JPEG)
        self.write(f'data/user/0/{tail}120x90.temp', JPEG + b'different')
        rows = [row for row in self.run_artifact(uimail.ui_mail_attachments) if row['Name'] == 'b.jpg']
        self.assertEqual(sorted(row['Thumbnail'] for row in rows), sorted([
            f'media:data/data/{tail}120x90.temp', f'media:data/data/{tail}240x180.temp',
            f'media:data/user/0/{tail}120x90.temp']))

if __name__ == '__main__':
    unittest.main()
