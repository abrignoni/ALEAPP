"""The Saved Messages self-chat is labelled from the account owner's own user id.

The own user id is read from the userconf* preference file that sits in the same
package container as the database; without that file the chat keeps its resolved
name (fail closed). The ids and names here are synthetic, not from any image.
"""
from pathlib import Path
import base64
import sqlite3
import struct
import tempfile
import unittest
from types import SimpleNamespace
from scripts.artifacts import telegramAndroid

OWN_ID = 5555500001          # synthetic account owner
PEER_ID = 4444400002         # synthetic other user


def _tl_string(text):
    raw = text.encode('utf-8')
    out = bytes([len(raw)]) + raw
    while len(out) % 4:
        out += b'\x00'
    return out


def _user_blob(own_id, first_name):
    """A TL_user record (constructor 0xB1B8CC83): flags, flags2, id, first_name."""
    flags = (1 << 1) | (1 << 10)                 # first_name present, self
    return (struct.pack('<I', 0xB1B8CC83)
            + struct.pack('<I', flags)
            + struct.pack('<I', 0)                # flags2
            + struct.pack('<q', own_id)
            + _tl_string(first_name))


def _userconfing_xml(own_id, first_name):
    blob = base64.b64encode(_user_blob(own_id, first_name)).decode('ascii')
    return (f"<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n"
            f'<map>\n    <string name="user">{blob}</string>\n'
            f'    <string name="last_call_phone_number">15550000000</string>\n</map>\n')


class TestTelegramSavedMessages(unittest.TestCase):
    def make_db(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path)
        con.execute('create table users(uid INTEGER PRIMARY KEY, name TEXT, status INTEGER, data BLOB)')
        con.execute('create table chats(uid INTEGER, name TEXT)')
        con.executemany('insert into users values(?,?,?,?)', [
            (OWN_ID, 'Account Owner;;;owner', 0, None),
            (PEER_ID, 'Other Person;;;other', 0, None),
        ])
        con.execute('create table messages_v2('
                    'mid INTEGER, uid INTEGER, date INTEGER, out INTEGER, read_state INTEGER, '
                    'data BLOB, PRIMARY KEY(mid, uid))')
        # A self-chat (Saved Messages) post: stored with out=0, no from_id.
        con.execute('insert into messages_v2 values(1,?,1700000000,0,1,?)',
                    (OWN_ID, b''))
        # A normal incoming message from the peer.
        con.execute('insert into messages_v2 values(2,?,1700000100,0,1,?)',
                    (PEER_ID, b''))
        con.execute('create table dialogs('
                    'did INTEGER, date INTEGER, unread_count INTEGER, pinned INTEGER, folder_id INTEGER)')
        con.executemany('insert into dialogs values(?,?,?,?,?)', [
            (OWN_ID, 1700000000, 0, 0, 0),
            (PEER_ID, 1700000100, 0, 0, 0),
        ])
        con.commit()
        con.close()

    def parse(self, root, found):
        context = SimpleNamespace(
            get_files_found=lambda: [str(p) for p in found],
            get_relative_path=lambda p: str(Path(p).relative_to(root)),
        )
        return telegramAndroid.get_telegramMessages.__wrapped__(context)

    def test_saved_messages_labelled_with_userconfing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / 'data/data/org.telegram.messenger'
            db = pkg / 'files/cache4.db'
            self.make_db(db)
            prefs = pkg / 'shared_prefs/userconfing.xml'
            prefs.parent.mkdir(parents=True, exist_ok=True)
            prefs.write_text(_userconfing_xml(OWN_ID, 'Account Owner'))

            _, rows, _ = self.parse(root, [db, prefs])
            by_dialog = {r[1]: r for r in rows}        # dialog id -> row
            # Chat is column index 2, Direction index 3.
            self.assertEqual(by_dialog[OWN_ID][2], 'Saved Messages')
            self.assertEqual(by_dialog[OWN_ID][3], 'Incoming')      # out as stored
            self.assertEqual(by_dialog[PEER_ID][2], 'Other Person (@other)')

    def test_chats_labels_self_dialog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / 'data/data/org.telegram.messenger'
            db = pkg / 'files/cache4.db'
            self.make_db(db)
            prefs = pkg / 'shared_prefs/userconfing.xml'
            prefs.parent.mkdir(parents=True, exist_ok=True)
            prefs.write_text(_userconfing_xml(OWN_ID, 'Account Owner'))
            context = SimpleNamespace(
                get_files_found=lambda: [str(db), str(prefs)],
                get_relative_path=lambda p: str(Path(p).relative_to(root)),
            )
            _, rows, _ = telegramAndroid.get_telegramChats.__wrapped__(context)
            by_dialog = {r[1]: r for r in rows}       # Chats: col 1 dialog id, col 2 chat
            self.assertEqual(by_dialog[OWN_ID][2], 'Saved Messages')
            self.assertEqual(by_dialog[PEER_ID][2], 'Other Person (@other)')

    def test_self_chat_not_relabelled_without_userconfing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / 'data/data/org.telegram.messenger/files/cache4.db'
            self.make_db(db)
            _, rows, _ = self.parse(root, [db])      # no prefs file
            by_dialog = {r[1]: r for r in rows}
            self.assertEqual(by_dialog[OWN_ID][2], 'Account Owner (@owner)')

    def test_own_id_paired_per_container(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / 'data/user/0/org.telegram.messenger/files/cache4.db'
            second = root / 'data/user/10/org.telegram.messenger/files/cache4.db'
            self.make_db(first)
            self.make_db(second)
            p1 = root / 'data/user/0/org.telegram.messenger/shared_prefs/userconfing.xml'
            p1.parent.mkdir(parents=True, exist_ok=True)
            p1.write_text(_userconfing_xml(OWN_ID, 'Account Owner'))
            # Second tenant has no prefs file: its self chat must not be relabelled.
            headers, rows, _ = self.parse(root, [first, second, p1])
            saved = [r for r in rows if r[2] == 'Saved Messages']
            # Only the container that carried a userconfing is labelled.
            self.assertEqual(len(saved), 1)
            self.assertIn('Source File', headers)
            self.assertTrue(all('data/user/0/' in r[-1] for r in saved))

    def test_own_id_for_db_path_mapping(self):
        own_for = telegramAndroid._own_id_for_db       # pylint: disable=protected-access
        own = {'/x/org.telegram.messenger': {0: 11, 2: 22}}
        slot0 = '/x/org.telegram.messenger/files/cache4.db'
        slot2 = '/x/org.telegram.messenger/files/account2/cache4.db'
        self.assertEqual(own_for(slot0, own), 11)
        self.assertEqual(own_for(slot2, own), 22)
        self.assertIsNone(own_for('/x/other.db', own))
        self.assertIsNone(own_for(slot0, {}))

    def test_current_user_constructor_decodes(self):
        decode = telegramAndroid._decode_account_user  # pylint: disable=protected-access
        decoded = decode(
            base64.b64encode(_user_blob(OWN_ID, 'Account Owner')).decode('ascii'))
        self.assertEqual(decoded.get('id'), OWN_ID)
        self.assertEqual(decoded.get('first_name'), 'Account Owner')


if __name__ == '__main__':
    unittest.main()
