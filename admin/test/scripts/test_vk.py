"""VK messages, dialogs and users from a synthetic vkim-<number>.sqlite.

The database is built with the columns the artifacts read; every value is made up.
"""
import fnmatch
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts import vk

MS = 1767225600000  # 2026-01-01 00:00:00 UTC


class EvidenceContext:
    def __init__(self, root):
        self.root = root

    def get_files_found(self):
        return [str(path) for path in sorted(self.root.rglob('*')) if path.is_file()]

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace('\\', '/')


def vkim(path, extra_message=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE messages (local_id INTEGER PRIMARY KEY, dialog_id INTEGER,
        cnv_msg_id INTEGER, time INTEGER, from_member_type INTEGER, from_member_id INTEGER,
        is_incoming INTEGER, type INTEGER, body TEXT, is_edited INTEGER, is_hidden INTEGER,
        expire_ttl INTEGER, delete_ttl INTEGER)''')
    db.execute('''CREATE TABLE dialogs (id INTEGER PRIMARY KEY, count_unread INTEGER,
        last_msg_cnv_id INTEGER, chat_settings_title TEXT, chat_settings_members_count INTEGER)''')
    db.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, first_name_nom TEXT, last_name_nom TEXT,
        domain TEXT, mobile_phone TEXT, friend_status INTEGER, blocked INTEGER, blocked_by_me INTEGER,
        deactivated TEXT, online_last_seen INTEGER, birthday_day INTEGER, birthday_month INTEGER,
        birthday_year INTEGER)''')
    db.execute('CREATE TABLE groups (id INTEGER PRIMARY KEY, title TEXT)')
    db.execute('''CREATE TABLE message_attaches (msg_local_id INTEGER, content_type INTEGER,
        position INTEGER)''')
    db.execute("INSERT INTO users VALUES (10, 'Ann', 'Example', 'ann', '', 3, 0, 0, NULL, ?, 1, 2, NULL)",
               (MS,))
    db.execute("INSERT INTO groups VALUES (20, 'A Group')")
    db.execute("INSERT INTO dialogs VALUES (10, 0, 2, NULL, NULL)")
    db.execute("INSERT INTO dialogs VALUES (-20, 1, 1, NULL, NULL)")
    db.execute("INSERT INTO dialogs VALUES (2000000001, 0, 1, 'Chat title', 3)")
    rows = [(1, 10, 1, MS, 1, 10, 1, 1, 'hello', 0, 0, None, None),
            (2, 10, 2, MS + 1000, 1, 10, 0, 1, 'reply', 1, 0, None, None),
            (3, -20, 1, MS + 2000, 3, 20, 1, 1, 'group post', 0, 0, None, None),
            (4, 2000000001, 1, MS + 3000, 1, 10, 1, 2, '', 0, 0, None, None)]
    if extra_message:
        rows.append(extra_message)
    db.executemany('INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', rows)
    db.executemany('INSERT INTO message_attaches VALUES (?,?,?)', [(1, 9, 0), (1, 3, 1)])
    db.commit()
    db.close()


class VkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'evidence'

    def tearDown(self):
        self.temp.cleanup()

    def run_artifact(self, function):
        context = EvidenceContext(self.root)
        patterns = vk.__artifacts_v2__[function.__name__]['paths']
        for path in context.get_files_found():
            relative = 'root/' + context.get_relative_path(path)
            if not relative.endswith(('-journal', '-wal', '-shm')):
                self.assertTrue(any(fnmatch.fnmatch(relative, p) for p in patterns), relative)
        headers, rows, _ = function.__wrapped__(context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        self.assertTrue(all(len(row) == len(names) for row in rows))
        return [dict(zip(names, row)) for row in rows]

    def test_messages_name_sender_conversation_type_and_attachments(self):
        vkim(self.root / 'data/data/com.vkontakte.android/databases/vkim-123.sqlite')
        rows = {row['Local ID']: row for row in self.run_artifact(vk.vk_messages)}
        first = rows[1]
        self.assertEqual(first['Timestamp'], datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual((first['Direction'], first['Sender'], first['Conversation'], first['Attachments']),
                         ('Incoming', 'Ann Example', 'Ann Example', 'Image, AudioMsg'))
        self.assertEqual((rows[2]['Direction'], rows[2]['Edited']), ('Outgoing', 'Yes'))
        self.assertEqual((rows[3]['Sender'], rows[3]['Sender Type'], rows[3]['Conversation'],
                          rows[3]['Dialog Kind']), ('A Group', 'GROUP', 'A Group', 'Group'))
        self.assertEqual((rows[4]['Message'], rows[4]['Conversation'], rows[4]['Dialog Kind']),
                         ('[CHAT_CREATE]', 'Chat title', 'Chat'))
        self.assertEqual(first['Account Number'], '123')

    def test_dialogs_and_users(self):
        vkim(self.root / 'data/data/com.vkontakte.android/databases/vkim-123.sqlite')
        dialogs = {row['Dialog ID']: row for row in self.run_artifact(vk.vk_dialogs)}
        self.assertEqual(dialogs[10]['Messages in Database'], 2)
        self.assertEqual(dialogs[2000000001]['Members Count'], 3)
        users = self.run_artifact(vk.vk_users)
        self.assertEqual((users[0]['First Name'], users[0]['Birthday'], users[0]['Last Seen']),
                         ('Ann', '2-1', datetime(2026, 1, 1, tzinfo=timezone.utc)))

    def test_copies_are_joined_and_a_damaged_copy_is_skipped(self):
        vkim(self.root / 'data/data/com.vkontakte.android/databases/vkim-123.sqlite')
        vkim(self.root / 'data/user/0/com.vkontakte.android/databases/vkim-123.sqlite',
             extra_message=(5, 10, 3, MS + 4000, 1, 10, 1, 1, 'only here', 0, 0, None, None))
        rows = self.run_artifact(vk.vk_messages)
        self.assertEqual(sorted(row['Local ID'] for row in rows), [1, 2, 3, 4, 5])
        damaged = self.root / 'data/user/10/com.vkontakte.android/databases/vkim-9.sqlite'
        damaged.parent.mkdir(parents=True)
        damaged.write_bytes(b'SQLite format 3\x00' + b'\xff' * 4000)
        self.assertEqual(len(self.run_artifact(vk.vk_messages)), 5)


    def test_dialog_kind_follows_the_app_ranges(self):
        cases = {5: 'User', 2147483648: 'User', 2000000001: 'Chat', 1900000005: 'Contact',
                 -20: 'Group', -2000000001: 'Email', -2147483649: 'Group', 0: 'Unknown'}
        self.assertEqual({k: vk._dialog_kind(k) for k in cases}, cases)  # pylint: disable=protected-access

if __name__ == '__main__':
    unittest.main()
