"""Zalo messages, reactions, contacts, groups and media files from synthetic stores.

Each test builds a small com.zing.zalo tree with the schema the app writes (ChatContent,
Reaction, contact_profile_friend_<account>, alias_friend, group_info_v6,
uid_hidden_chat_table) and runs the artifacts through the folder seeker. The values are
made up for the test.
"""
import contextlib
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts import zalo
from scripts.search_files import FileSeekerDir

ACCOUNT_A = '100'
ACCOUNT_B = '200'
PEER = '300'
GROUP = '400'
BASE_MS = 1767225600000  # 2026-01-01 00:00:00 UTC


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


def chat_db(path, rows, wal_rows=()):
    """A conversation database; wal_rows are left in its write-ahead log."""
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE ChatContent (SenderId INTEGER NOT NULL DEFAULT 0,
        CliMsgId INTEGER NOT NULL DEFAULT 0, GlbMsgId INTEGER NOT NULL DEFAULT 0,
        MsgStatus INTEGER NOT NULL DEFAULT 1, MsgType INTEGER NOT NULL DEFAULT 0,
        TimeStamp INTEGER NOT NULL DEFAULT 0, TTL INTEGER NOT NULL DEFAULT 0, MsgContent TEXT,
        RefCliMsgId INTEGER, BinNet BLOB, LocalPath TEXT, SeqId INTEGER DEFAULT 0,
        FLStatus INTEGER NOT NULL DEFAULT 0, E2EE TEXT, PRIMARY KEY (SenderId, CliMsgId))''')
    insert = ('INSERT INTO ChatContent (SenderId, CliMsgId, GlbMsgId, MsgType, TimeStamp, '
              'MsgContent, LocalPath) VALUES (?,?,?,?,?,?,?)')
    db.executemany(insert, rows)
    db.commit()
    if wal_rows:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
        db.executemany(insert, wal_rows)
        db.commit()
        # Copy the database and its log while the log is still unmerged.
        copy = path.with_name(path.name + '.copy')
        shutil.copyfile(path, copy)
        shutil.copyfile(str(path) + '-wal', str(copy) + '-wal')
        db.close()
        Path(str(path) + '-shm').unlink(missing_ok=True)
        path.unlink()
        Path(str(path) + '-wal').unlink(missing_ok=True)
        copy.rename(path)
        Path(str(copy) + '-wal').rename(str(path) + '-wal')
    else:
        db.close()


def ext_db(path, reactions):
    path.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.closing(sqlite3.connect(path)) as db:
        with db:
            db.execute('''CREATE TABLE Reaction (client_id INTEGER NOT NULL DEFAULT 0,
                global_id INTEGER NOT NULL DEFAULT 0, fuid INTEGER NOT NULL DEFAULT 0,
                sender_id INTEGER NOT NULL DEFAULT 0, count INTERGER NOT NULL DEFAULT 0, icon TEXT,
                timestamp INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (client_id, fuid, sender_id, icon))''')
            db.executemany('INSERT INTO Reaction VALUES (?,?,?,?,?,?,?)', reactions)


def main_db(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.closing(sqlite3.connect(path)) as db:
        with db:
            for account, name in ((ACCOUNT_A, 'Peer as A sees them'), (ACCOUNT_B, 'Peer as B sees them')):
                db.execute(f'''CREATE TABLE contact_profile_friend_{account} (uid primary key, dpn, usr,
                    avt, ged, dob, phone, stt, timestamp, isZaloFriend INTEGER)''')
                db.execute(f'INSERT INTO contact_profile_friend_{account} (uid, dpn, usr, ged, dob, '
                           'phone, timestamp, isZaloFriend) VALUES (?,?,?,?,?,?,?,?)',
                           (PEER, name, 'u', 1, '01/01/2000', '000', BASE_MS, 1))
            db.execute('''CREATE TABLE contact_profile_5 (uid primary key, dpn, usr, avt, ged, dob,
                phone, stt, timestamp, isZaloFriend INTEGER)''')
            db.execute('CREATE TABLE alias_friend (currentUserUid, uIdTo, aliasName, opt_1, opt_2)')
            db.execute('INSERT INTO alias_friend VALUES (?,?,?,NULL,NULL)', (ACCOUNT_A, PEER, 'Alias from A'))
            db.execute('''CREATE TABLE group_info_v6 (id, name, desc, creatorId, members, ts,
                currentUserUid, totalMem, member_uids, admin_uids)''')
            db.execute('INSERT INTO group_info_v6 (id, name, creatorId, ts, currentUserUid, totalMem, '
                       'member_uids) VALUES (?,?,?,?,?,?,?)',
                       (GROUP, 'Test group', PEER, str(BASE_MS), ACCOUNT_A, 2, f'{ACCOUNT_A},{PEER}'))
            db.execute('CREATE TABLE uid_hidden_chat_table (currentUserUid, uid)')
            db.execute('INSERT INTO uid_hidden_chat_table VALUES (?,?)', (ACCOUNT_B, PEER))


def media_file(root, relative, data):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


JXL = b'\xff\x0a' + b'\x00' * 30
PDF = b'%PDF-1.4\n' + b'\x00' * 20


class ZaloTests(unittest.TestCase):
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
            with patch.object(zalo, 'check_in_media', side_effect=lambda path, _name:
                              'media:' + context.get_relative_path(path)), \
                    patch.object(zalo, 'logfunc'):
                headers, rows, _source = function.__wrapped__(context)
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        self.assertTrue(all(len(row) == len(names) for row in rows))
        return [dict(zip(names, row)) for row in rows]

    def build_device(self, prefix='', user_dir='data/data'):
        app = self.root / prefix / user_dir / 'com.zing.zalo' / 'databases'
        main_db(app / 'zalo')
        chat_db(app / ACCOUNT_A / f'{PEER}.db', [
            (PEER, 1, 11, 0, BASE_MS, 'hello from peer', None),
            (ACCOUNT_A, 2, 12, 3, BASE_MS + 1000, '', 'zalo/picture/a.jxl'),
            (ACCOUNT_A, 3, 13, 22, 9223372036854775807, 'bad time', None),
        ], wal_rows=[(PEER, 4, 14, 0, BASE_MS + 2000, 'only in the log', None)])
        ext_db(app / ACCOUNT_A / f'{PEER}_ext.db', [(1, 11, PEER, ACCOUNT_A, 1, '/-heart', BASE_MS + 500)])
        chat_db(app / ACCOUNT_B / f'{PEER}.db', [(PEER, 1, 21, 0, BASE_MS, 'hello to B', None)])
        chat_db(app / ACCOUNT_A / f'group_{GROUP}.db', [(PEER, 5, 15, 0, BASE_MS, 'in the group', None)])
        media = Path(prefix) / 'data/media/0/Android/data/com.zing.zalo/files/zalo'
        media_file(self.root, media / 'picture/a.jxl', JXL)
        media_file(self.root, media / 'file_resource/orphan.pdf', PDF)

    def test_messages_are_read_with_the_log_and_keep_accounts_apart(self):
        self.build_device()
        rows = self.run_artifact(zalo.zalo_messages)
        self.assertEqual(len(rows), 6)
        texts = {row['Message'] for row in rows}
        self.assertIn('only in the log', texts)
        keys = {row['Conversation Key'] for row in rows}
        self.assertEqual(keys, {f'0/{ACCOUNT_A}/{PEER}', f'0/{ACCOUNT_B}/{PEER}',
                                f'0/{ACCOUNT_A}/group_{GROUP}'})
        by_text = {row['Message']: row for row in rows}
        self.assertEqual(by_text['hello from peer']['Conversation'], 'Alias from A')
        self.assertEqual(by_text['hello to B']['Conversation'], 'Peer as B sees them')
        self.assertEqual(by_text['hello to B']['Hidden Chat'], 'Yes')
        self.assertEqual(by_text['hello from peer']['Hidden Chat'], '')
        self.assertEqual(by_text['in the group']['Conversation'], 'Test group')
        self.assertEqual(by_text['in the group']['Group Chat'], 'Yes')
        self.assertEqual(by_text['bad time']['Timestamp'], '')
        self.assertEqual(by_text['hello from peer']['Direction'], 'Incoming')
        photo = by_text['']
        self.assertEqual(photo['Direction'], 'Outgoing')
        self.assertEqual(photo['Type Name'], 'chat.photo')
        self.assertEqual(photo['Media Format'], 'JPEG XL')
        self.assertEqual(photo['Media'],
                         'media:data/media/0/Android/data/com.zing.zalo/files/zalo/picture/a.jxl')

    def test_storage_spellings_are_one_app_folder(self):
        self.build_device()
        # The same conversation also under data/user/0, and a conversation kept only there.
        moved = self.root / 'data/user/0/com.zing.zalo/databases' / ACCOUNT_A
        moved.mkdir(parents=True)
        chat_db(moved / '500.db', [(PEER, 9, 19, 0, BASE_MS, 'only under user 0', None)])
        rows = self.run_artifact(zalo.zalo_messages)
        self.assertEqual(len(rows), 7)
        row, = [row for row in rows if row['Message'] == 'only under user 0']
        self.assertEqual(row['Sender Name'], 'Alias from A')
        self.assertEqual(row['Conversation Key'], f'0/{ACCOUNT_A}/500')

    def test_media_is_not_taken_from_another_device(self):
        self.build_device(prefix='device_a')
        other = Path('device_b/data/media/0/Android/data/com.zing.zalo/files/zalo/picture/b.jxl')
        media_file(self.root, other, JXL)
        (self.root / 'device_a/data/media/0/Android/data/com.zing.zalo/files/zalo/picture/a.jxl').unlink()
        media_file(self.root, other.with_name('a.jxl'), JXL)
        rows = self.run_artifact(zalo.zalo_messages)
        photo, = [row for row in rows if row['Type Name'] == 'chat.photo']
        self.assertEqual(photo['Media'], '')
        self.assertEqual(photo['Media Format'], 'File not in extraction')
        self.assertTrue(photo['Conversation Key'].startswith('device_a/'))

    def test_reactions_join_their_message(self):
        self.build_device()
        row, = self.run_artifact(zalo.zalo_reactions)
        self.assertEqual(row['Message Found'], 'Yes')
        self.assertEqual(row['Message'], 'hello from peer')
        self.assertEqual(row['Reaction (as stored)'], '/-heart')
        self.assertEqual(row['Conversation Key'], f'0/{ACCOUNT_A}/{PEER}')

    def test_contacts_and_groups(self):
        self.build_device()
        contacts = self.run_artifact(zalo.zalo_contacts)
        self.assertEqual(len(contacts), 2)
        self.assertEqual({row['Alias'] for row in contacts}, {'Alias from A', ''})
        group, = self.run_artifact(zalo.zalo_groups)
        self.assertEqual(group['Group Name'], 'Test group')
        self.assertEqual(group['Creator Name'], 'Alias from A')

    def test_media_files_list_named_and_unnamed_files(self):
        self.build_device()
        rows = self.run_artifact(zalo.zalo_media)
        by_name = {row['File Name']: row for row in rows}
        self.assertEqual(set(by_name), {'a.jxl', 'orphan.pdf'})
        self.assertEqual(by_name['a.jxl']['Named by a Message'], 'Yes')
        self.assertEqual(by_name['a.jxl']['Conversation Keys'], f'0/{ACCOUNT_A}/{PEER}')
        self.assertEqual(by_name['orphan.pdf']['Named by a Message'], 'No')
        self.assertEqual(by_name['orphan.pdf']['Media Format'], 'PDF')

    def test_mirror_only_database_keeps_its_media(self):
        app = self.root / 'data_mirror/data_ce/null/0/com.zing.zalo/databases'
        main_db(app / 'zalo')
        chat_db(app / ACCOUNT_A / f'{PEER}.db',
                [(ACCOUNT_A, 2, 12, 3, BASE_MS, '', 'zalo/picture/a.jxl')])
        media_file(self.root, 'data/media/0/Android/data/com.zing.zalo/files/zalo/picture/a.jxl', JXL)
        row, = self.run_artifact(zalo.zalo_messages)
        self.assertEqual(row['Media Format'], 'JPEG XL')
        media, = self.run_artifact(zalo.zalo_media)
        self.assertEqual(media['Named by a Message'], 'Yes')


if __name__ == '__main__':
    unittest.main()
