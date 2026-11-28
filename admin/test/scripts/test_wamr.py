"""WAMR captured notifications, WhatsApp chats, media copies and monitored apps.

Each test builds a small com.drilens.wamr tree with the schema WAMR 2.4.1 writes (notifs.db,
textmess.db, media.db, settings.db) and runs the artifacts through the folder seeker. The
values are made up for the test.
"""
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
from scripts.artifacts import wamr
from scripts.search_files import FileSeekerDir

JPEG = b'\xff\xd8\xff\xe0' + b'\x00' * 32
OGG = b'OggS' + b'\x00' * 32
ALNUM = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


def chat_table(name):
    """WAMR's table name for a chat (i31.i): UTF-16 units outside [A-Za-z0-9] as %04x."""
    data = name.encode('utf-16-be')
    units = [int.from_bytes(data[i:i + 2], 'big') for i in range(0, len(data), 2)]
    return 'chat_' + ''.join(chr(u) if chr(u) in ALNUM else f'{u:04x}' for u in units)


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


def make_db(path, statements, rows=()):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    for statement in statements:
        db.execute(statement)
    for sql, values in rows:
        db.execute(sql, values)
    db.commit()
    db.close()


def notifs_db(path, apps):
    statements, rows = [], []
    for package, entries in apps.items():
        table = f'"app_{package}"'
        statements.append(f'CREATE TABLE {table} (_id INTEGER PRIMARY KEY, app TEXT NOT NULL, '
                          'title TEXT NOT NULL, subtext TEXT, content TEXT NOT NULL, time TEXT NOT NULL)')
        for title, subtext, content, stamp in entries:
            rows.append((f'INSERT INTO {table} (app, title, subtext, content, time) VALUES (?,?,?,?,?)',
                         (package, title, subtext, content, stamp)))
    make_db(path, statements, rows)


def textmess_db(path, chats):
    statements, rows = [], []
    for chat, entries in chats.items():
        table = '"' + chat_table(chat) + '"'
        statements.append(f'CREATE TABLE IF NOT EXISTS {table} (_id integer primary key, author text not null, '
                          'content text not null, received_at text not null, deleted integer not null)')
        for content, stamp, deleted in entries:
            rows.append((f'INSERT INTO {table} (author, content, received_at, deleted) VALUES (?,?,?,?)',
                         (chat, content, stamp, deleted)))
    make_db(path, statements, rows)


def media_db(path, entries):
    make_db(path, ['CREATE TABLE MediaMessages (_id integer primary key, file_name text not null, '
                   'media_type integer not null, author text, download_at text not null, '
                   'deleted_at text, deleted integer not null)'],
            [('INSERT INTO MediaMessages (file_name, media_type, download_at, deleted) VALUES (?,?,?,?)',
              entry) for entry in entries])


def settings_db(path, monitored):
    make_db(path, ['CREATE TABLE Settings (_id integer primary key, key_name text, value text)'],
            [("INSERT INTO Settings (key_name, value) VALUES ('monitored_apps', ?)", (monitored,))])


class WamrTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'evidence'
        self.root.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def run_artifact(self, function):
        with tempfile.TemporaryDirectory() as staging:
            seeker = FileSeekerDir(str(self.root), staging)
            context = EvidenceContext(self.root, seeker)
            with patch.object(wamr, 'check_in_media', side_effect=lambda path, _name:
                              'media:' + context.get_relative_path(path)):
                headers, rows, _source = function.__wrapped__(context)
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        self.assertTrue(all(len(row) == len(names) for row in rows))
        return [dict(zip(names, row)) for row in rows]

    def app(self, user_dir='data/data'):
        return self.root / user_dir / 'com.drilens.wamr' / 'databases'

    def media(self, user='0'):
        return self.root / 'data/media' / user / 'Android/data/com.drilens.wamr/files/WAMR'

    def test_notifications_parse_the_time_and_blank_the_null_word(self):
        notifs_db(self.app() / 'notifs.db', {
            'org.example.chat': [('Alice', None, 'null', '2026-01-02 03:04:05_678'),
                                 ('null', 'Group', 'hi', 'not a time')],
            'org.example.empty': []})
        rows = self.run_artifact(wamr.wamr_notifications)
        self.assertEqual(len(rows), 2)
        first = rows[0]
        self.assertEqual(first['Captured'],
                         datetime(2026, 1, 2, 3, 4, 5, 678000, tzinfo=timezone.utc))
        self.assertEqual((first['App'], first['Title'], first['Content']),
                         ('org.example.chat', 'Alice', ''))
        self.assertEqual((rows[1]['Captured'], rows[1]['Title'], rows[1]['Subtext']), ('', '', 'Group'))

    def test_chat_is_the_author_and_the_table_name_is_not_decoded(self):
        # 'F422' is kept as it is, while U+F422 is written as f422: both chats share one table.
        textmess_db(self.app() / 'textmess.db', {
            'Team chat \U0001F600': [('Bob: hello', '2026-01-02 03:04:05_000', 0)],
            'F422': [('one', '2026-01-02 03:04:06_000', 1)],
            '': [('two', '2026-01-02 03:04:07_000', 0)]})
        rows = self.run_artifact(wamr.wamr_whatsapp_chats)
        by_content = {row['Content']: row for row in rows}
        self.assertEqual(by_content['Bob: hello']['Chat'], 'Team chat \U0001F600')
        self.assertEqual(by_content['Bob: hello']['Chat Table'], 'chat_Team0020chat0020d83dde00')
        self.assertEqual(by_content['one']['Chat Table'], by_content['two']['Chat Table'])
        self.assertEqual((by_content['one']['Chat'], by_content['two']['Chat']), ('F422', ''))
        self.assertEqual(by_content['one']['Marked Deleted'], 'Yes')
        self.assertEqual(by_content['two']['Marked Deleted'], 'No')

    def test_media_rows_find_the_copy_and_list_files_no_row_names(self):
        media_db(self.app() / 'media.db', [
            ('PTT-1.mp3', 1, '2026-01-02 03:04:05', 1),
            ('IMG-1.jpg', 2, '2026-01-02 03:04:06', 0),
            ('VID-1.mp4', 3, '2026-01-02 03:04:07', 0)])
        for name, data in (('Voice Notes/PTT-1.mp3', OGG), ('Images/IMG-1.jpg', JPEG),
                           ('Images/IMG-orphan.jpg', JPEG)):
            target = self.media() / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        rows = {row['File Name']: row for row in self.run_artifact(wamr.wamr_media)}
        self.assertEqual(rows['PTT-1.mp3']['Media Format'], 'Ogg')
        self.assertEqual(rows['PTT-1.mp3']['Media Type'], '1 (Voice Notes)')
        self.assertEqual(rows['PTT-1.mp3']['Original Deleted'], 'Yes')
        self.assertEqual(rows['IMG-1.jpg']['Media'],
                         'media:data/media/0/Android/data/com.drilens.wamr/files/WAMR/Images/IMG-1.jpg')
        self.assertEqual(rows['VID-1.mp4']['Media Format'], 'File not in extraction')
        self.assertEqual(rows['IMG-orphan.jpg']['In media.db'], 'No')
        self.assertEqual(rows['IMG-1.jpg']['In media.db'], 'Yes')

    def test_users_are_kept_apart_and_storage_views_read_once(self):
        for user_dir in ('data/data', 'data/user/0'):
            media_db(self.app(user_dir) / 'media.db', [('IMG-1.jpg', 2, '2026-01-02 03:04:06', 0)])
        media_db(self.app('data/user/10') / 'media.db', [('IMG-1.jpg', 2, '2026-01-02 03:04:06', 0)])
        target = self.media('0') / 'Images/IMG-1.jpg'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(JPEG)
        rows = self.run_artifact(wamr.wamr_media)
        found = sorted((row['Android User'], row['Media Format']) for row in rows)
        self.assertEqual(found, [('0', 'JPEG'), ('10', 'File not in extraction')])

    def test_monitored_apps_join_the_list_and_the_tables(self):
        settings_db(self.app() / 'settings.db', 'org.example.chat;org.example.listed')
        notifs_db(self.app() / 'notifs.db', {
            'org.example.chat': [('Alice', None, 'hi', '2026-01-02 03:04:05_678')],
            'org.example.earlier': []})
        rows = {row['App']: row for row in self.run_artifact(wamr.wamr_monitored_apps)}
        self.assertEqual((rows['org.example.chat']['In Monitored List'],
                          rows['org.example.chat']['Captured Notifications']), ('Yes', 1))
        self.assertEqual((rows['org.example.listed']['Notification Table'],
                          rows['org.example.listed']['Captured Notifications']), ('No', ''))
        self.assertEqual((rows['org.example.earlier']['In Monitored List'],
                          rows['org.example.earlier']['Captured Notifications']), ('No', 0))


if __name__ == '__main__':
    unittest.main()
