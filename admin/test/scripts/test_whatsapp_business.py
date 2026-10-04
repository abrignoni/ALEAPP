"""WhatsApp Business (com.whatsapp.w4b) artifacts: one row set per app container, none from WhatsApp.

WhatsAppBusiness.py runs WhatsApp.py's artifact bodies against com.whatsapp.w4b's own
files, once per app container. These tests build synthetic stores (no real evidence
bytes: every name, number, jid and message below is invented) and stage them through the
directory seeker with each artifact's own `paths`, as a run does, over one tree holding:

  * com.whatsapp.w4b under data/data and data/user/0, the same container twice, which
    must be read once;
  * com.whatsapp.w4b under data/user/10, a second Android user with one more contact,
    call, message and group message, which must add its own rows;
  * com.whatsapp under data/data, the WhatsApp app with the same layout, which must add
    nothing to the Business artifacts and take nothing from them.

The committed case zips (admin/test/cases/data/WhatsAppBusiness) hold one container
built by build_container(..., avatars=False) below, with no media files. test_module.py
replaces check_in_media in the module under test, and these artifacts reach it through
WhatsApp.py's own binding, so a media or Avatars file the case could resolve would run
the real check_in_media without a run's output parameters. Media and Avatars lookup are
covered here instead, where that binding is patched.
"""
import importlib.util
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, REPO_ROOT)

from scripts.context import Context  # noqa: E402  pylint: disable=wrong-import-position
from scripts.search_files import FileSeekerDir  # noqa: E402  pylint: disable=wrong-import-position
from scripts.artifacts import WhatsApp, WhatsAppBusiness  # noqa: E402  pylint: disable=wrong-import-position

# admin/scripts is not a package, so load the column-order check from its path.
_spec = importlib.util.spec_from_file_location(
    'check_conversation_column_order',
    os.path.join(REPO_ROOT, 'admin', 'scripts', 'check_conversation_column_order.py'))
column_order = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(column_order)

BUSINESS = 'com.whatsapp.w4b'
PERSONAL = 'com.whatsapp'

T0 = 1767225600000  # 2026-01-01 00:00:00 UTC, in milliseconds
MINUTE = 60000
DAY = 86400000

CUSTOMER_A_PN = '000000000101@s.whatsapp.net'
CUSTOMER_A_LID = '100000000000101@lid'
CUSTOMER_B_PN = '000000000102@s.whatsapp.net'
UNSAVED_PN = '000000000103@s.whatsapp.net'
CUSTOMER_C_PN = '000000000104@s.whatsapp.net'
GROUP = '120363000000000101@g.us'
GROUP_2 = '120363000000000102@g.us'
CHANNEL = '120363000000000901@newsletter'

JIDS = [(1, CUSTOMER_A_PN), (2, CUSTOMER_A_LID), (3, CUSTOMER_B_PN), (4, UNSAVED_PN),
        (5, GROUP), (6, CHANNEL), (7, CUSTOMER_C_PN), (8, GROUP_2)]

# Each container's own media and app-folder names, as the two apps lay them out.
LAYOUT = {
    BUSINESS: {'prefs': 'com.whatsapp.w4b_preferences_light.xml', 'media_root': 'WhatsApp Business',
               'images': 'WhatsApp Business Images'},
    PERSONAL: {'prefs': 'com.whatsapp_preferences_light.xml', 'media_root': 'WhatsApp',
               'images': 'WhatsApp Images'},
}

# Messages: (_id, chat_row_id, from_me, sender_jid_row_id, offset in minutes, message_type,
# text, recipient_count). Chats: 1 LID-keyed chat with customer A, 2 customer B, 3 an unsaved
# number, 4 a group, 5 a channel, 6 customer C, 7 a second group with no recorded creator.
_MESSAGES = [
    (1, 1, 0, None, 1, 0, 'incoming in a lid chat', 0),
    (2, 1, 1, None, 2, 0, 'outgoing in a lid chat', 0),
    (3, 2, 0, None, 3, 1, None, 0),
    (4, 2, 1, None, 4, 5, None, 0),
    (5, 2, 0, None, 5, 16, None, 0),
    (6, 3, 0, None, 6, 0, 'incoming from an unsaved number', 0),
    (7, 4, 1, None, 7, 7, None, 2),
    (8, 4, 0, 2, 8, 0, 'group post by a lid sender', 2),
    (9, 4, 0, 3, 9, 0, 'group post by a phone sender', 2),
    (10, 4, 1, None, 10, 0, 'outgoing group post', 2),
    (11, 5, 0, None, 11, 0, 'channel post', 0),
    (14, 4, 0, 3, 14, 1, None, 2),
    (15, 4, 1, None, 15, 16, None, 2),
    (16, 7, 0, 2, 16, 0, 'post in the second group', 2),
]
# The second Android user's container holds these as well.
_EXTRA_MESSAGES = [
    (12, 6, 0, None, 12, 0, 'incoming from customer C', 0),
    (13, 4, 0, 7, 13, 0, 'group post by customer C', 2),
]
# Calls: (_id, jid_row_id, from_me, offset in minutes, video_call, duration in seconds,
# group_jid_row_id)
_CALLS = [
    (1, 2, 0, 20, 0, 30, 0),
    (2, 3, 1, 21, 1, 45, 0),
    (3, 4, 0, 22, 0, 0, 0),
    (4, 3, 0, 23, 0, 120, 5),
]
_EXTRA_CALLS = [(5, 7, 0, 24, 1, 15, 0)]


def _text(label, text):
    return f'[{label}] {text}' if text else text


def _write_msgstore(path, package, label, extra):
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE jid(_id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT NOT NULL, '
                'server TEXT NOT NULL, agent INTEGER, device INTEGER, type INTEGER, raw_string TEXT)')
    con.execute('CREATE TABLE jid_map(lid_row_id INTEGER PRIMARY KEY NOT NULL, '
                'jid_row_id INTEGER NOT NULL, sort_id INTEGER NOT NULL DEFAULT 0)')
    con.execute('CREATE TABLE chat(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid_row_id INTEGER UNIQUE, '
                'hidden INTEGER, subject TEXT, created_timestamp INTEGER)')
    con.execute('CREATE TABLE message(_id INTEGER PRIMARY KEY AUTOINCREMENT, chat_row_id INTEGER NOT NULL, '
                'from_me INTEGER NOT NULL, key_id TEXT NOT NULL, sender_jid_row_id INTEGER, '
                'status INTEGER, timestamp INTEGER, received_timestamp INTEGER, message_type INTEGER, '
                'text_data TEXT, recipient_count INTEGER)')
    con.execute('CREATE TABLE message_media(message_row_id INTEGER PRIMARY KEY, chat_row_id INTEGER, '
                'file_path TEXT, file_size INTEGER, mime_type TEXT)')
    con.execute('CREATE TABLE message_location(message_row_id INTEGER PRIMARY KEY, chat_row_id INTEGER, '
                'latitude REAL, longitude REAL, live_location_share_duration INTEGER, '
                'live_location_final_latitude REAL, live_location_final_longitude REAL, '
                'live_location_final_timestamp INTEGER)')
    con.execute('CREATE TABLE call_log(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid_row_id INTEGER, '
                'from_me INTEGER, call_id TEXT, timestamp INTEGER, video_call INTEGER, duration INTEGER, '
                'call_result INTEGER, group_jid_row_id INTEGER NOT NULL DEFAULT 0)')
    for row_id, raw in JIDS:
        user, server = raw.split('@')
        con.execute('INSERT INTO jid(_id, user, server, raw_string) VALUES (?, ?, ?, ?)',
                    (row_id, user, server, raw))
    con.execute('INSERT INTO jid_map(lid_row_id, jid_row_id) VALUES (2, 1)')
    con.executemany('INSERT INTO chat(_id, jid_row_id, subject, created_timestamp) VALUES (?, ?, ?, ?)', [
        (1, 2, None, T0 - DAY), (2, 3, None, T0 - DAY), (3, 4, None, T0 - DAY),
        (4, 5, _text(label, 'group'), T0 - 2 * DAY), (5, 6, _text(label, 'channel'), T0 - 3 * DAY),
        (6, 7, None, T0 - DAY), (7, 8, _text(label, 'second group'), T0 - 2 * DAY)])
    for (row_id, chat, from_me, sender, minutes, kind, text, recipients) in (
            _MESSAGES + (_EXTRA_MESSAGES if extra else [])):
        con.execute('INSERT INTO message(_id, chat_row_id, from_me, key_id, sender_jid_row_id, status, '
                    'timestamp, received_timestamp, message_type, text_data, recipient_count) '
                    'VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?)',
                    (row_id, chat, from_me, f'SYNTHETICKEY{row_id:04d}', sender, T0 + minutes * MINUTE,
                     0 if from_me else T0 + minutes * MINUTE + 1000, kind, _text(label, text), recipients))
    con.executemany('INSERT INTO message_media(message_row_id, chat_row_id, file_path, file_size, mime_type) '
                    'VALUES (?, ?, ?, ?, ?)', [
                        (3, 2, media_db_path(package, 1), len(SYNTHETIC_JPEG), 'image/jpeg'),
                        (14, 4, media_db_path(package, 2), len(SYNTHETIC_JPEG), 'image/jpeg')])
    con.execute('INSERT INTO message_location(message_row_id, chat_row_id, latitude, longitude) '
                'VALUES (4, 2, 10.5, 20.25)')
    con.execute('INSERT INTO message_location(message_row_id, chat_row_id, latitude, longitude, '
                'live_location_share_duration, live_location_final_latitude, live_location_final_longitude, '
                'live_location_final_timestamp) VALUES (5, 2, 10.5, 20.25, 900, 10.75, 20.5, ?)',
                (T0 + 20 * MINUTE,))
    con.execute('INSERT INTO message_location(message_row_id, chat_row_id, latitude, longitude, '
                'live_location_share_duration, live_location_final_latitude, live_location_final_longitude, '
                'live_location_final_timestamp) VALUES (15, 4, 30.5, 40.25, 600, 30.75, 40.5, ?)',
                (T0 + 25 * MINUTE,))
    for (row_id, jid_row, from_me, minutes, video, duration, group) in _CALLS + (_EXTRA_CALLS if extra else []):
        con.execute('INSERT INTO call_log(_id, jid_row_id, from_me, call_id, timestamp, video_call, duration, '
                    'call_result, group_jid_row_id) VALUES (?, ?, ?, ?, ?, ?, ?, 5, ?)',
                    (row_id, jid_row, from_me, f'SYNTHETICCALL{row_id:04d}', T0 + minutes * MINUTE, video,
                     duration, group))
    con.commit()
    con.close()


def _write_wa(path, label, extra):
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE wa_contacts(_id INTEGER PRIMARY KEY AUTOINCREMENT, jid TEXT NOT NULL, '
                'is_whatsapp_user BOOLEAN NOT NULL, status TEXT, status_timestamp INTEGER, number TEXT, '
                'display_name TEXT, given_name TEXT, family_name TEXT, wa_name TEXT)')
    con.execute('CREATE TABLE wa_group_admin_settings(_id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'jid TEXT UNIQUE, creator_jid TEXT)')
    contacts = [
        (CUSTOMER_A_PN, None, 0, '+15550101', None, 'Synthetic', 'Customer A', _text(label, 'A')),
        (CUSTOMER_B_PN, _text(label, 'status of B'), T0 - DAY, '+15550102', 'Customer B', None, None,
         _text(label, 'B')),
        (GROUP, None, 0, None, None, None, None, None),
        (CHANNEL, None, 0, None, None, None, None, None),
        ('status@broadcast', None, 0, None, None, None, None, None),
    ]
    if extra:
        contacts.append((CUSTOMER_C_PN, None, 0, '+15550104', 'Customer C', None, None, _text(label, 'C')))
    con.executemany('INSERT INTO wa_contacts(jid, is_whatsapp_user, status, status_timestamp, number, '
                    'display_name, given_name, family_name, wa_name) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)', contacts)
    con.execute('INSERT INTO wa_group_admin_settings(jid, creator_jid) VALUES (?, ?)', (GROUP, CUSTOMER_A_LID))
    con.commit()
    con.close()


def _prefs_xml(strings):
    lines = ["<?xml version='1.0' encoding='utf-8' standalone='yes' ?>", '<map>']
    lines += [f'    <string name="{name}">{value}</string>' for name, value in strings]
    lines.append('</map>')
    return '\n'.join(lines) + '\n'


# A 1x1 grey JPEG, generated with Pillow for these tests.
SYNTHETIC_JPEG = bytes.fromhex(
    'ffd8ffe000104a46494600010100000100010000ffdb004300100b0c0e0c0a100e0d0e1211101318281a181616183123251d'
    '283a333d3c3933383740485c4e404457453738506d51575f626768673e4d71797064785c656763ffc0000b08000100010101'
    '1100ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b51000020103030204030505'
    '04040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a'
    '25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a8384858687'
    '88898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2'
    'e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffda0008010100003f002bffd9')


def media_db_path(package, number=1):
    """The path msgstore.db records for a synthetic picture, relative to the app's media root."""
    return f"Media/{LAYOUT[package]['images']}/IMG-20260101-WA{number:04d}.jpg"


def build_container(root, data_dir, package=BUSINESS, label='w4b', extra=False, media_dir=None,
                    avatars=True):
    """Write one synthetic app container under root/data_dir/package.

    media_dir is the external storage root its media goes under (data/media/<user>), or
    None for no media files; avatars=False leaves files/Avatars empty.
    """
    container = os.path.join(root, *data_dir.split('/'), package)
    for sub in ('databases', 'shared_prefs', 'files/Avatars'):
        os.makedirs(os.path.join(container, *sub.split('/')), exist_ok=True)
    _write_msgstore(os.path.join(container, 'databases', 'msgstore.db'), package, label, extra)
    _write_wa(os.path.join(container, 'databases', 'wa.db'), label, extra)
    prefs = os.path.join(container, 'shared_prefs')
    with open(os.path.join(prefs, LAYOUT[package]['prefs']), 'w', encoding='utf-8', newline='\n') as f:
        f.write(_prefs_xml([('push_name', _text(label, 'owner')), ('my_current_status', _text(label, 'about')),
                            ('cc', '1'), ('ph', '5550100')]))
    with open(os.path.join(prefs, 'startup_prefs.xml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(_prefs_xml([('push_name', _text(label, 'owner, startup copy')), ('version', '2.26.1.1')]))
    for jid in (GROUP, CUSTOMER_A_PN) if avatars else ():
        with open(os.path.join(container, 'files', 'Avatars', f'{jid}.j'), 'wb') as f:
            f.write(SYNTHETIC_JPEG)
    for number in (1, 2) if media_dir else ():
        media = os.path.join(root, *media_dir.split('/'), 'Android', 'media', package,
                             LAYOUT[package]['media_root'], *media_db_path(package, number).split('/'))
        os.makedirs(os.path.dirname(media), exist_ok=True)
        with open(media, 'wb') as f:
            f.write(SYNTHETIC_JPEG)
    return container


def _row(headers, row):
    return dict(zip((h[0] if isinstance(h, tuple) else h for h in headers), row))


class WhatsAppBusinessTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.extraction = os.path.join(cls.tmp, 'extraction')
        build_container(cls.extraction, 'data/data', media_dir='data/media/0')
        shutil.copytree(os.path.join(cls.extraction, 'data', 'data', BUSINESS),
                        os.path.join(cls.extraction, 'data', 'user', '0', BUSINESS))
        build_container(cls.extraction, 'data/user/10', label='u10', extra=True)
        build_container(cls.extraction, 'data/data', package=PERSONAL, label='personal',
                        media_dir='data/media/0')
        cls.single = os.path.join(cls.tmp, 'single')
        build_container(cls.single, 'data/data', media_dir='data/media/0')

    @classmethod
    def tearDownClass(cls):
        Context.clear()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _run(self, module, name, extraction):
        """Stage the artifact's own paths through the directory seeker and run its body."""
        data_folder = tempfile.mkdtemp(dir=self.tmp)
        seeker = FileSeekerDir(extraction, data_folder)
        files_found = []
        for pattern in module.__artifacts_v2__[name]['paths']:
            files_found.extend(seeker.search(pattern))
        Context.clear()
        Context.set_data_folder(data_folder)
        Context.set_seeker(seeker)
        Context.set_files_found(files_found)
        resolved = []

        def fake_check_in_media(file_path, name=''):  # pylint: disable=unused-argument
            found = Context.get_source_file_path(file_path)
            resolved.append(Context.get_relative_path(found).replace('\\', '/') if found else None)
            return 'media-ref' if found else None

        with patch('scripts.artifacts.WhatsApp.check_in_media', fake_check_in_media):
            headers, rows, source = getattr(module, name).__wrapped__(Context)
        Context.clear()
        return headers, [_row(headers, r) for r in rows], source, resolved

    def test_single_container_rows(self):
        expected = {
            'get_whatsapp_business_contacts': 3,
            'get_whatsapp_business_call_logs': 4,
            'get_whatsapp_business_one_to_one_messages': 6,
            'get_whatsapp_business_group_messages': 7,
            'get_whatsapp_business_group_details': 2,
            'get_whatsapp_business_user_profile': 1,
        }
        for name, count in expected.items():
            with self.subTest(name):
                _headers, rows, source, _media = self._run(WhatsAppBusiness, name, self.single)
                self.assertEqual(len(rows), count)
                # One store per container, or the two preference files for the user profile.
                self.assertEqual(len(source.split('\n')), 2 if name.endswith('user_profile') else 1)

    def test_multi_container_arithmetic(self):
        """data/user/0 collapses into data/data, user 10 adds its own rows plus its delta,
        and com.whatsapp adds nothing."""
        delta = {'get_whatsapp_business_contacts': 1, 'get_whatsapp_business_call_logs': 1,
                 'get_whatsapp_business_one_to_one_messages': 1, 'get_whatsapp_business_group_messages': 1,
                 'get_whatsapp_business_group_details': 0, 'get_whatsapp_business_user_profile': 0}
        for name, extra in delta.items():
            with self.subTest(name):
                _h, single, _s, _m = self._run(WhatsAppBusiness, name, self.single)
                _h, rows, source, _m = self._run(WhatsAppBusiness, name, self.extraction)
                self.assertEqual(len(rows), 2 * len(single) + extra)
                column = 'Source Files' if name.endswith('user_profile') else 'Source File'
                by_source = {}
                for row in rows:
                    by_source.setdefault(row[column].split('/', 3)[2], []).append(row)
                # data/data/... and data/user/10/... : the third segment is the package or the user.
                self.assertEqual(sorted(by_source), ['10', BUSINESS])
                self.assertEqual(len(by_source[BUSINESS]), len(single))
                self.assertEqual(len(source.split('\n')), 2 if not name.endswith('user_profile') else 4)
                text = repr(rows)
                self.assertNotIn('[personal]', text)
                # Each container's rows carry only that container's own values.
                self.assertNotIn('[u10]', repr(by_source[BUSINESS]))
                self.assertNotIn('[w4b]', repr(by_source['10']))

    def test_whatsapp_artifacts_do_not_read_business(self):
        for name in ('get_whatsapp_contacts', 'get_whatsapp_call_logs', 'get_whatsapp_one_to_one_messages',
                     'get_whatsapp_group_messages', 'get_whatsapp_group_details', 'get_whatsapp_user_profile'):
            with self.subTest(name):
                _h, rows, source, _m = self._run(WhatsApp, name, self.extraction)
                self.assertTrue(rows)
                self.assertNotIn(BUSINESS, source)
                self.assertNotIn('[w4b]', repr(rows))
                self.assertNotIn('[u10]', repr(rows))

    def test_call_logs(self):
        _h, rows, _s, _m = self._run(WhatsAppBusiness, 'get_whatsapp_business_call_logs', self.single)
        self.assertEqual([(r['Call Direction'], r['Caller'], r['Caller JID'], r['Call Type'], r['Group Name'],
                           r['Call Duration']) for r in rows], [
            ('Incoming', '[w4b] A', CUSTOMER_A_PN, 'Audio', None, '00:00:30'),
            ('Outgoing', 'Self', '', 'Video', None, '00:00:45'),
            ('Incoming', UNSAVED_PN, UNSAVED_PN, 'Audio', None, '00:00:00'),
            ('Incoming', '[w4b] B', CUSTOMER_B_PN, 'Audio', '[w4b] group', '00:02:00'),
        ])
        self.assertEqual(rows[0]['Call Start Timestamp'].isoformat(), '2026-01-01T00:20:00+00:00')
        self.assertEqual(rows[0]['Call End Timestamp'].isoformat(), '2026-01-01T00:20:30+00:00')
        self.assertEqual({r['Source File'] for r in rows}, {f'data/data/{BUSINESS}/databases/msgstore.db'})

    def test_one_to_one_messages(self):
        _h, rows, _s, media = self._run(WhatsAppBusiness, 'get_whatsapp_business_one_to_one_messages',
                                        self.single)
        self.assertEqual([(r['Message Direction'], r['Other Participant WA User Name'], r['Message Type'],
                           r['Message']) for r in rows], [
            ('Incoming', '[w4b] A', 'Text', '[w4b] incoming in a lid chat'),
            ('Outgoing', '[w4b] A', 'Text', '[w4b] outgoing in a lid chat'),
            ('Incoming', '[w4b] B', 'Picture', None),
            ('Outgoing', '[w4b] B', 'Static Location', None),
            ('Incoming', '[w4b] B', 'Live Location', None),
            ('Incoming', UNSAVED_PN, 'Text', '[w4b] incoming from an unsaved number'),
        ])
        self.assertEqual(rows[0]['Sending Party JID'], CUSTOMER_A_PN)
        self.assertEqual(rows[2]['Local Path To Media'], media_db_path(BUSINESS))
        self.assertEqual(rows[2]['Media'], 'media-ref')
        self.assertEqual(media, [f'data/media/0/Android/media/{BUSINESS}/WhatsApp Business/'
                                 f'{media_db_path(BUSINESS)}'])
        self.assertEqual(rows[4]['Final Location Timestamp'].isoformat(), '2026-01-01T00:20:00+00:00')
        self.assertNotIn('[w4b] channel post', repr(rows))

    def test_group_messages(self):
        _h, rows, _s, media = self._run(WhatsAppBusiness, 'get_whatsapp_business_group_messages', self.single)
        self.assertEqual([(r['Message Direction'], r['Sending Party'], r['Sending Party JID'],
                           r['Conversation Name'], r['Message']) for r in rows], [
            ('Outgoing', 'Self', '', '[w4b] group', None),
            ('Incoming', '[w4b] A', CUSTOMER_A_PN, '[w4b] group', '[w4b] group post by a lid sender'),
            ('Incoming', '[w4b] B', CUSTOMER_B_PN, '[w4b] group', '[w4b] group post by a phone sender'),
            ('Outgoing', 'Self', '', '[w4b] group', '[w4b] outgoing group post'),
            ('Incoming', '[w4b] B', CUSTOMER_B_PN, '[w4b] group', None),
            ('Outgoing', 'Self', '', '[w4b] group', None),
            ('Incoming', '[w4b] A', CUSTOMER_A_PN, '[w4b] second group', '[w4b] post in the second group'),
        ])
        self.assertEqual((rows[4]['Message Type'], rows[4]['Local Path To Media']),
                         ('Picture', media_db_path(BUSINESS, 2)))
        self.assertEqual(media, [f'data/media/0/Android/media/{BUSINESS}/WhatsApp Business/'
                                 f'{media_db_path(BUSINESS, 2)}'])
        self.assertEqual((rows[5]['Message Type'], rows[5]['Final Live Latitude']), ('Live Location', 30.75))
        self.assertEqual(rows[5]['Final Location Timestamp'].isoformat(), '2026-01-01T00:25:00+00:00')

    def test_group_details(self):
        _h, rows, _s, media = self._run(WhatsAppBusiness, 'get_whatsapp_business_group_details', self.single)
        self.assertEqual(len(rows), 2)
        row = rows[0]
        self.assertEqual((row['Group Name'], row['Creator JID'], row['Creator JID (via jid_map)'],
                          row['Creator WA User Name'], row['Creator WA Number']),
                         ('[w4b] group', CUSTOMER_A_LID, CUSTOMER_A_PN, '[w4b] A', '+15550101'))
        self.assertEqual(row['Group Creation Timestamp'].isoformat(), '2025-12-30T00:00:00+00:00')
        # The second group has no creator in wa.db and no picture in Avatars.
        self.assertEqual((rows[1]['Group Name'], rows[1]['Creator JID'], rows[1]['Creator WA User Name'],
                          rows[1]['Group Picture'], rows[1]['Creator WA Profile Picture']),
                         ('[w4b] second group', None, None, '', ''))
        self.assertEqual(media, [f'data/data/{BUSINESS}/files/Avatars/{GROUP}.j',
                                 f'data/data/{BUSINESS}/files/Avatars/{CUSTOMER_A_PN}.j'])

    def test_contacts(self):
        _h, rows, _s, _m = self._run(WhatsAppBusiness, 'get_whatsapp_business_contacts', self.single)
        self.assertEqual([(r['Name'], r['WhatsApp Name'], r['JID'], r['Number'], r['Status Text'])
                          for r in rows], [
            ('Synthetic Customer A', '[w4b] A', CUSTOMER_A_PN, '+15550101', None),
            ('Customer B', '[w4b] B', CUSTOMER_B_PN, '+15550102', '[w4b] status of B'),
            (GROUP, None, GROUP, None, None),
        ])
        self.assertEqual(rows[1]['Status Timestamp'].isoformat(), '2025-12-31T00:00:00+00:00')
        self.assertEqual({r['Source File'] for r in rows}, {f'data/data/{BUSINESS}/databases/wa.db'})

    def test_user_profile_prefers_the_business_preferences_file(self):
        _h, rows, _s, _m = self._run(WhatsAppBusiness, 'get_whatsapp_business_user_profile', self.single)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual((row['Version'], row['Name'], row['User Status'], row['Country Code'],
                          row['Mobile Number']),
                         ('2.26.1.1', '[w4b] owner', '[w4b] about', '1', '5550100'))
        prefs = f'data/data/{BUSINESS}/shared_prefs'
        self.assertEqual(row['Source Files'],
                         f'{prefs}/com.whatsapp.w4b_preferences_light.xml; {prefs}/startup_prefs.xml')

    def test_user_profile_skips_a_malformed_file(self):
        root = os.path.join(self.tmp, 'malformed')
        container = build_container(root, 'data/data')
        with open(os.path.join(container, 'shared_prefs', 'startup_prefs.xml'), 'w', encoding='utf-8') as f:
            f.write('<map><string name="version">2.26')
        with patch('scripts.artifacts.WhatsAppBusiness.logfunc') as log:
            _h, rows, _s, _m = self._run(WhatsAppBusiness, 'get_whatsapp_business_user_profile', root)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]['Name'], rows[0]['Version']), ('[w4b] owner', ''))
        self.assertIn('startup_prefs.xml not read', log.call_args.args[0])

    def test_no_store_still_names_columns(self):
        empty = os.path.join(self.tmp, 'empty')
        os.makedirs(os.path.join(empty, 'data', 'data', BUSINESS, 'databases'))
        with open(os.path.join(empty, 'data', 'data', BUSINESS, 'databases', 'wa.db-journal'), 'wb'):
            pass
        headers, rows, source, _m = self._run(WhatsAppBusiness, 'get_whatsapp_business_call_logs', empty)
        self.assertEqual(rows, [])
        self.assertEqual(source, '')
        self.assertEqual(headers[-1], 'Source File')
        self.assertEqual(headers[0], ('Call Start Timestamp', 'datetime'))

    def test_conversation_columns_follow_the_declared_roles(self):
        """The column-order check cannot resolve these headers statically, so check them at run time."""
        for name in ('get_whatsapp_business_one_to_one_messages', 'get_whatsapp_business_group_messages'):
            with self.subTest(name):
                headers, _rows, _s, _m = self._run(WhatsAppBusiness, name, self.single)
                view = WhatsAppBusiness.__artifacts_v2__[name]['data_views']['conversation']
                names = [h[0] if isinstance(h, tuple) else h for h in headers]
                types = [h[1] if isinstance(h, tuple) else None for h in headers]
                for role, column in view.items():
                    if role.endswith('Column'):
                        self.assertIn(column, names)
                self.assertEqual(column_order.expected(names, types, view),
                                 list(range(len(names))))


if __name__ == '__main__':
    unittest.main()
