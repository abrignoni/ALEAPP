"""Constructed SQL rows exercise Threema message decoding, schema drift, key files and media."""
# pylint: disable=protected-access
import datetime
import hashlib
import json
import os
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from scripts.artifacts import Threema

MESSAGE_COLUMNS = ('uid,identity,outbox,type,body,caption,apiMessageId,quotedMessageId,state,'
                   'isRead,isStatusMessage,createdAtUtc,deliveredAtUtc,readAtUtc')
KEY = bytes(range(32))
JPEG = b'\xff\xd8\xff\xe0' + b'jpeg' * 10
UID_A, UID_B, UID_C, UID_D = ('a' * 32, 'b' * 32, 'c' * 32, 'd' * 32)


def utc(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc)


def dashed(uid):
    """A 32 hex digit uid written as a UUID, the way the database stores it."""
    return f'{uid[:8]}-{uid[8:12]}-{uid[12:16]}-{uid[16:20]}-{uid[20:]}'


def message(uid, kind, body, outbox=0, api=None, quoted=None, created=1700000000000,
            caption=None, status=0, identity='CONTACT'):
    return (uid, identity, outbox, kind, body, caption, api, quoted, 'READ', 1, status,
            created, None, None)


class ThreemaMessageProjectionTest(unittest.TestCase):
    def project(self, records, group_records=(), container=None, key=None, extra_columns=''):
        connection = sqlite3.connect(':memory:')
        connection.execute('CREATE TABLE contacts(identity,firstName,lastName,publicNickName)')
        connection.execute("INSERT INTO contacts VALUES('CONTACT','First','Last','Nickname')")
        connection.execute(f'CREATE TABLE message({MESSAGE_COLUMNS}{extra_columns})')
        width = MESSAGE_COLUMNS.count(',') + 1 + extra_columns.count(',')
        connection.executemany(f'INSERT INTO message VALUES({",".join("?" * width)})', records)
        if group_records:
            connection.execute('CREATE TABLE m_group(id,name)')
            connection.execute("INSERT INTO m_group VALUES(1,'Team')")
            connection.execute(f'CREATE TABLE m_group_message({MESSAGE_COLUMNS},groupId)')
            connection.executemany(
                f'INSERT INTO m_group_message VALUES({",".join("?" * 15)})', group_records)
        context = SimpleNamespace(get_files_found=lambda: [])
        container = {'db': 'store', 'media': {}, 'keys': [key] if key else []} | (container or {})
        store = Threema._Store(connection, container)
        with patch.object(Threema, '_decrypted_connections', return_value=[store]), \
                patch.object(Threema, 'unique_files', return_value=[]):
            return Threema.threema_messages.__wrapped__(context)

    def test_file_body_is_read_by_serializer_position(self):
        current = json.dumps(['blob', 'key', 'image/jpeg', 42, 'photo.jpg', 1, True, 'body caption',
                              'image/jpeg', {'w': 1, 'h': 2}])
        without_rendering_type = json.dumps(['blob', 'key', 'video/mp4', 7, 'clip.mp4', True,
                                             'old caption', None, {'d': 12.6}])
        headers, rows, source = self.project([
            message('u1', 8, current, created=1700000000000),
            message('u2', 8, without_rendering_type, created=1700000001000, caption='column caption'),
        ])
        self.assertEqual(headers[:3], (('Created', 'datetime'), ('Delivered', 'datetime'),
                                       ('Read At', 'datetime')))
        self.assertEqual(source, 'store')
        index = {name if isinstance(name, str) else name[0]: i for i, name in enumerate(headers)}
        self.assertEqual([rows[0][index[c]] for c in ('Text / Filename / Address', 'MIME Type',
                                                       'Size (bytes)', 'Message')],
                         ['photo.jpg', 'image/jpeg', 42, 'body caption'])
        self.assertEqual([rows[1][index[c]] for c in ('Text / Filename / Address', 'MIME Type',
                                                       'Message', 'Media Duration (s)')],
                         ['clip.mp4', 'video/mp4', 'column caption', 13])
        self.assertEqual(rows[0][index['Media Status']], 'Not on device')

    def test_calls_status_rows_quotes_and_legacy_media(self):
        records = [
            message('a', 0, 'hello', api='orig', created=1700000000000),
            message('b', 0, 'reply', api='rep', quoted='orig', outbox=1, created=1700000001000),
            message('c', 4, json.dumps([12.5, -45.5, 3, 'Address', None]), created=1700000002000),
            message('d', 9, json.dumps([1, {'status': 2, 'duration': 188}]), created=1700000003000),
            message('e', 9, json.dumps([1, {'status': 1, 'callId': 77}]), created=1700000004000),
            message('f', 12, json.dumps([3, {'status': 3, 'quantity': 0, 'staticText': None}]),
                    status=1, created=1700000005000),
            message('g', 3, json.dumps([5, True, 'keyhex', 'blobhex']), created=1700000006000),
            message('h', 1, json.dumps([True, '', '', '']), caption='a picture',
                    created=1700000007000),
            message('i', 2, json.dumps([20, True, '', '', 3000]), created=1700000008000),
        ]
        headers, rows, _ = self.project(records)
        col = {name if isinstance(name, str) else name[0]: i for i, name in enumerate(headers)}
        by = {row[col['Created']]: row for row in rows}
        get = lambda ms, name: by[utc(ms)][col[name]]  # noqa: E731
        self.assertEqual(get(1700000001000, 'Quoted Message'), 'hello')
        self.assertEqual(get(1700000001000, 'Direction'), 'Sent')
        self.assertEqual(get(1700000001000, 'Sender'), 'Local account')
        self.assertEqual(get(1700000000000, 'Sender'), 'First Last')
        self.assertEqual(get(1700000000000, 'Conversation'), 'First Last (CONTACT)')
        self.assertEqual(get(1700000002000, 'Message'), 'Address')
        self.assertEqual(get(1700000003000, 'Call Status'), 2)
        self.assertEqual(get(1700000003000, 'Message'), 'Call Finished (188 s)')
        self.assertEqual(get(1700000003000, 'Call Duration (s)'), 188)
        self.assertIsNone(get(1700000003000, 'Call ID'))
        self.assertEqual(get(1700000004000, 'Call ID'), 77)
        self.assertEqual(get(1700000004000, 'Message'), 'Call Missed')
        self.assertEqual(get(1700000005000, 'Direction'), 'Status')
        self.assertEqual(get(1700000005000, 'Message'), 'Forward security established')
        self.assertEqual(get(1700000006000, 'Content Type'), 'Voice Message')
        self.assertEqual(get(1700000006000, 'Media Duration (s)'), 5)
        self.assertNotIn('keyhex', [str(v) for v in by[utc(1700000006000)]])
        self.assertEqual(get(1700000007000, 'Message'), 'a picture')
        self.assertEqual(get(1700000008000, 'Size (bytes)'), 3000)
        # Edited and Deleted are absent from this schema and come out blank.
        self.assertIsNone(get(1700000000000, 'Edited'))

    def test_reactions_from_table_and_legacy_state(self):
        def with_state(row_id, row, state):
            return (row_id,) + row[:8] + (state,) + row[9:]
        records = [
            with_state(1, message('a', 0, 'received', created=1700000000000), 'USERACK'),
            with_state(2, message('b', 0, 'sent', outbox=1, created=1700000001000), 'USERDEC'),
            with_state(3, message('c', 0, 'both', created=1700000002000), 'USERACK'),
        ]
        connection = sqlite3.connect(':memory:')
        connection.execute('CREATE TABLE contacts(identity,firstName,lastName,publicNickName)')
        connection.execute("INSERT INTO contacts VALUES('CONTACT','First','Last','Nickname')")
        connection.execute(f'CREATE TABLE message(id,{MESSAGE_COLUMNS})')
        connection.executemany(f'INSERT INTO message VALUES({",".join("?" * 15)})', records)
        connection.execute('CREATE TABLE contact_reactions(messageId,senderIdentity,'
                           'emojiSequence,reactedAt)')
        connection.execute("INSERT INTO contact_reactions VALUES(3,'CONTACT','❤️',1700000005000)")
        store = Threema._Store(connection, {'db': 'store', 'media': {}, 'keys': []})
        with patch.object(Threema, '_decrypted_connections', return_value=[store]), \
                patch.object(Threema, 'unique_files', return_value=[]):
            headers, rows, _ = Threema.threema_messages.__wrapped__(
                SimpleNamespace(get_files_found=lambda: []))
        col = headers.index('Reactions')
        self.assertEqual([row[col] for row in rows], [
            '\U0001F44D Local account',
            '\U0001F44E First Last',
            # A reaction table row wins over the legacy state on the same message.
            '❤️ First Last (2023-11-14 22:13:25 UTC)',
        ])

    def test_group_rows_join_the_same_table(self):
        group = [
            ('g1', '', 0, 0, 'Group created.', None, None, None, None, 0, 1, 1700000000000,
             None, None, 1),
            ('g2', 'CONTACT', 0, 0, 'hi all', None, 'gapi', None, None, 1, 0, 1700000001000,
             None, None, 1),
            ('g3', '', 1, 0, 'hello', None, None, 'gapi', None, 1, 0, 1700000002000,
             None, None, 1),
        ]
        headers, rows, _ = self.project([message('a', 0, 'one-to-one')], group)
        col = {name if isinstance(name, str) else name[0]: i for i, name in enumerate(headers)}
        self.assertEqual(len(rows), 4)
        groups = [row for row in rows if row[col['Conversation']] == 'Group: Team (#1)']
        self.assertEqual([r[col['Direction']] for r in groups], ['Status', 'Received', 'Sent'])
        self.assertEqual([r[col['Content Type']] for r in groups], ['Status', 'Text', 'Text'])
        self.assertEqual(groups[1][col['Sender']], 'First Last')
        self.assertEqual(groups[2][col['Quoted Message']], 'hi all')

    def test_media_decrypts_and_falls_back_to_thumbnail(self):
        plain = b'\xff\xd8\xff\xe0' + b'jpeg' * 10
        with tempfile.TemporaryDirectory() as tmp:
            def write(name, data):
                path = os.path.join(tmp, name)
                iv = bytes(16)
                with open(path, 'wb') as f:
                    f.write(iv + AES.new(KEY, AES.MODE_CBC, iv).encrypt(pad(data, 16)))
                return path
            media = {f'.{UID_A}': write('a', plain), f'.{UID_B}_T': write('b', plain),
                     f'.{UID_C}': os.path.join(tmp, 'broken'), f'.{UID_D}': write('d', b'plain text')}
            with open(media[f'.{UID_C}'], 'wb') as f:
                f.write(bytes(40))  # not a whole number of AES blocks
            body = json.dumps([None, None, 'image/jpeg', 1, 'x.jpg', 1, True, None, None, {}])
            records = [message(dashed(UID_A), 8, body, created=1700000000000),
                       message(dashed(UID_B), 8, body, created=1700000001000),
                       message(dashed(UID_C), 8, body, created=1700000002000),
                       message(dashed(UID_D), 8, body, created=1700000003000)]
            with patch.object(Threema, 'check_in_embedded_media',
                              side_effect=lambda path, data, name: hashlib.sha1(data).hexdigest()):
                headers, rows, _ = self.project(records, container={'media': media}, key=KEY)
        col = {name if isinstance(name, str) else name[0]: i for i, name in enumerate(headers)}
        self.assertEqual([r[col['Media Status']] for r in rows],
                         ['File', 'Thumbnail only', 'Decryption failed',
                          'File (type not recognised)'])
        self.assertEqual(rows[0][col['Media']], hashlib.sha1(plain).hexdigest())
        self.assertEqual(rows[2][col['Media']], '')


class ThreemaKeyAndContainerTest(unittest.TestCase):
    def test_v2_master_key_unwraps_only_unprotected_files(self):
        def layer(field, data):
            return b'\0\0' + bytes([field << 3 | 2, len(data)]) + data
        plain = layer(1, layer(1, layer(1, KEY)))
        passphrase = layer(2, b'x' * 10)
        remote = layer(1, layer(2, b'y' * 10))
        with tempfile.TemporaryDirectory() as tmp:
            results = []
            for name, data in (('plain', plain), ('pass', passphrase), ('remote', remote),
                               ('short', plain[:-1])):
                path = os.path.join(tmp, name)
                with open(path, 'wb') as f:
                    f.write(data)
                results.append(Threema._read_v2_master_key(path))
        self.assertEqual(results, [KEY, None, None, None])

    def test_containers_pair_by_user_and_package(self):
        files = [
            '/x/data/data/ch.threema.app/databases/threema4.db',
            '/x/data/user/0/ch.threema.app/files/key.dat',
            '/x/data/user/10/ch.threema.app/databases/threema4.db',
            '/x/data/user/0/ch.threema.app.libre/databases/threema4.db',
            '/x/data/user/0/ch.threema.appx/databases/threema4.db',
            f'/x/data/media/0/Android/data/ch.threema.app/files/data/.{UID_A}',
            f'/x/data/media/10/Android/data/ch.threema.app/files/data/.{UID_B}_T',
            f'/x/data/user/0/ch.threema.app/files/user-data/.message-files/.{UID_A}',
            '/x/data/media/0/Android/data/ch.threema.app/files/data/.avatar/inner',
        ]
        containers = Threema._containers(files)
        self.assertEqual(set(containers), {('0', 'ch.threema.app'), ('10', 'ch.threema.app'),
                                           ('0', 'ch.threema.app.libre')})
        main = containers[('0', 'ch.threema.app')]
        self.assertEqual(main['db'], '/x/data/data/ch.threema.app/databases/threema4.db')
        self.assertEqual(main['key_v1'], '/x/data/user/0/ch.threema.app/files/key.dat')
        # The app data copy wins over the external storage copy of the same file.
        self.assertEqual(main['media'], {
            f'.{UID_A}': f'/x/data/user/0/ch.threema.app/files/user-data/.message-files/.{UID_A}'})
        self.assertEqual(containers[('10', 'ch.threema.app')]['media'], {
            f'.{UID_B}_T': f'/x/data/media/10/Android/data/ch.threema.app/files/data/.{UID_B}_T'})
        self.assertNotIn('key_v1', containers[('10', 'ch.threema.app')])
        self.assertEqual((main['user'], main['package']), ('0', 'ch.threema.app'))

    def test_containers_without_a_database_keep_their_files(self):
        external = f'/x/storage/emulated/0/Android/data/ch.threema.app.work/files/data/.{UID_A}'
        unplaced = f'/x/dump/ch.threema.app/files/user-data/.message-files/.{UID_A}'
        files = [external, unplaced,
                 # files/data/ inside the app data directory is not the legacy directory
                 f'/x/data/user/0/ch.threema.app/files/data/.{UID_A}']
        containers = Threema._containers(files)
        self.assertEqual(set(containers), {('0', 'ch.threema.app.work'), ('?', '/x/dump/ch.threema.app')})
        work = containers[('0', 'ch.threema.app.work')]
        self.assertEqual(work['package'], 'ch.threema.app.work')
        self.assertEqual(work['files'], [('media', f'.{UID_A}', external, 'external')])
        self.assertEqual(containers[('?', '/x/dump/ch.threema.app')]['package'], 'ch.threema.app')
        with patch.object(Threema, '_SQLCIPHER_AVAILABLE', True):
            self.assertEqual(Threema._decrypted_connections(files), [])
            stores = Threema._decrypted_connections(files, include_without_db=True)
        self.assertEqual([(s.connection, s.container['package']) for s in stores],
                         [(None, 'ch.threema.app.work'), (None, 'ch.threema.app')])
        self.assertEqual(Threema._source_paths(stores), f'{external}\n{unplaced}')

    def test_media_files_are_described_including_unreferenced_ones(self):
        uid = 'a264096f-fd78-4b0e-a233-d149d271d304'
        stem = uid.replace('-', '')
        picture = '.p-NCX35SCHUDRMKV2DPADHLJUTNCVUW7TSJPVCGFBQCLUTKBLQRPYQ'
        owners = ({stem: ('when', 'First Last (CONTACT)', 'photo.jpg')},
                  {picture[3:]: 'Liz D (T4UFS63T) - local account'}, {7: 'Team'})
        describe = Threema._describe_media
        self.assertEqual(describe('media', f'.{stem}', owners),
                         ('when', 'Message file', 'First Last (CONTACT)', 'photo.jpg'))
        self.assertEqual(describe('media', f'.{stem}_T', owners)[1:3],
                         ('Message thumbnail', 'First Last (CONTACT)'))
        self.assertEqual(describe('media', '.' + 'f' * 32, owners),
                         (None, 'Message file', 'Not referenced by the database', ''))
        self.assertEqual(describe('avatars', picture, owners)[1:3],
                         ('Profile picture (from contact)', 'Liz D (T4UFS63T) - local account'))
        self.assertEqual(describe('avatars', '.a-' + 'A' * 52, owners)[2],
                         'Not referenced by the database')
        self.assertEqual(describe('groups', '.gpp-7', owners)[1:3], ('Group picture', 'Group: Team (#7)'))
        self.assertEqual(describe('groups', '.grp-avatar-8', owners)[2], 'Not referenced by the database')
        self.assertEqual(describe('wallpapers', 'wallpaper.jpg', owners)[1], 'Default wallpaper')
        self.assertEqual(describe('wallpapers', '.w-abc', owners)[1], 'Chat wallpaper')
        # Without an opened database nothing is called unreferenced.
        self.assertEqual([describe(c, n, None)[2] for c, n in (
            ('media', f'.{stem}'), ('avatars', picture), ('groups', '.gpp-7'))],
            ['Database not opened'] * 3)
        self.assertEqual(describe('wallpapers', '.w-abc', None)[1:3], ('Chat wallpaper', ''))

    def test_legacy_media_directories_map_to_categories(self):
        base = '/x/data/media/0/Android/data/ch.threema.app/files/data'
        files = ['/x/data/user/0/ch.threema.app/databases/threema4.db',
                 f'{base}/.grp-avatar/.grp-avatar-3', f'{base}/.wallpaper/.w-xyz.nomedia',
                 f'{base}/wallpaper.jpg', f'{base}/.nomedia', f'{base}/.message-files-x/.abc',
                 '/x/data/user/0/ch.threema.app/files/user-data/.group-profile-pictures/.gpp-3',
                 '/x/data/user/0/ch.threema.app/files/user-data/.message-files/.not-a-uid']
        container = Threema._containers(files)[('0', 'ch.threema.app')]
        self.assertEqual(sorted((c, n, s) for c, n, _, s in container['files']), [
            ('groups', '.gpp-3', 'internal'), ('groups', '.grp-avatar-3', 'external'),
            # Names the client does not define are other files, never message files.
            ('other', '.message-files-x/.abc', 'external'),
            ('other', '.message-files/.not-a-uid', 'internal'), ('other', '.nomedia', 'external'),
            ('wallpapers', '.w-xyz', 'external'), ('wallpapers', 'wallpaper.jpg', 'external')])
        self.assertEqual(Threema._describe_media('other', '.nomedia', None)[1:3], ('Other file', ''))

    def test_profile_picture_name_is_hashed_identity(self):
        # pixel7a_a14 holds the account's own picture under this name.
        name = '.c-NCX35SCHUDRMKV2DPADHLJUTNCVUW7TSJPVCGFBQCLUTKBLQRPYQ'
        external = f'/x/data/media/0/Android/data/ch.threema.app/files/data/.avatar/{name}.nomedia'
        files = ['/x/data/user/0/ch.threema.app/databases/threema4.db', external]
        container = Threema._containers(files)[('0', 'ch.threema.app')]
        self.assertEqual(container['avatars'], {name: external})
        container['keys'] = [KEY]
        with patch.object(Threema, '_decrypt_media', return_value=JPEG) as decrypt, \
                patch.object(Threema, 'check_in_embedded_media', return_value='ref'):
            self.assertEqual(Threema._profile_picture(container, 'T4UFS63T', '.c-'), 'ref')
            self.assertEqual(Threema._profile_picture(container, 'T4UFS63T', '.p-'), '')
        decrypt.assert_called_once_with(external, KEY)
        container['keys'] = []
        self.assertEqual(Threema._profile_picture(container, 'T4UFS63T', '.c-'), '')

    def test_every_key_is_tried_and_a_recognised_type_wins(self):
        wrong, right = bytes(32), KEY
        # The wrong key happens to pass the padding check but yields no known type.
        decrypts = {wrong: b'\x00' * 40, right: JPEG}
        with patch.object(Threema, '_decrypt_media', side_effect=lambda p, k: decrypts[k]):
            self.assertEqual(Threema._decrypt_file('f', [wrong, right]), (JPEG, 'image/jpeg'))
            self.assertEqual(Threema._decrypt_file('f', [wrong]), (b'\x00' * 40, None))
            self.assertEqual(Threema._decrypt_file('f', []), (None, None))
        name = '.c-NCX35SCHUDRMKV2DPADHLJUTNCVUW7TSJPVCGFBQCLUTKBLQRPYQ'
        container = {'avatars': {name: 'f'}, 'keys': [wrong]}
        # A profile picture is taken only when it decrypts to an image.
        with patch.object(Threema, '_decrypt_media', side_effect=lambda p, k: decrypts[k]):
            self.assertEqual(Threema._profile_picture(container, 'T4UFS63T', '.c-'), '')


class ThreemaGalleryTest(unittest.TestCase):
    def test_gallery_folders_are_located_per_user_and_flavour(self):
        locate = Threema._locate_gallery
        self.assertEqual(locate('/x/data/media/0/Pictures/Threema/a.jpg'),
                         ('0', 'Threema', 'Pictures/Threema', 'a.jpg'))
        self.assertEqual(locate('/x/storage/emulated/10/Movies/ThreemaWork/v.mp4'),
                         ('10', 'ThreemaWork', 'Movies/ThreemaWork', 'v.mp4'))
        self.assertEqual(locate('/x/sdcard/Threema/Threema Pictures/b.jpg'),
                         ('0', 'Threema', 'Threema/Threema Pictures', 'b.jpg'))
        # Not a flavour's folder, a deeper file, and no user readable off the path.
        self.assertIsNone(locate('/x/data/media/0/Pictures/ThreemaX/a.jpg'))
        self.assertIsNone(locate('/x/data/media/0/Pictures/Threema/sub/a.jpg'))
        self.assertIsNone(locate('/x/elsewhere/Pictures/Threema/a.jpg'))

    def test_gallery_copies_join_only_their_users_matching_install(self):
        files = ['/x/data/data/ch.threema.app/databases/threema4.db',
                 '/x/data/user/10/ch.threema.app/databases/threema4.db',
                 '/x/data/user/0/ch.threema.app.work/databases/threema4.db',
                 '/x/data/media/0/Pictures/Threema/a.jpg',
                 '/x/data/media/10/Pictures/Threema/b.jpg',
                 '/x/data/media/0/Pictures/ThreemaWork/c.jpg']
        containers = Threema._containers(files)
        self.assertEqual(containers[('0', 'ch.threema.app')]['gallery'],
                         [('a.jpg', 'Pictures/Threema', '/x/data/media/0/Pictures/Threema/a.jpg')])
        self.assertEqual([g[0] for g in containers[('10', 'ch.threema.app')]['gallery']], ['b.jpg'])
        self.assertEqual([g[0] for g in containers[('0', 'ch.threema.app.work')]['gallery']],
                         ['c.jpg'])

    def test_gallery_links_only_identical_bytes_tie(self):
        def body(name):
            return json.dumps([None, None, 'image/jpeg', 1, name, 1, True, None, None, {}])
        rows = [{'uid': dashed(UID_A), 'apiMessageId': 'aa11', 'type': 8, 'body': body('x.jpg')},
                {'uid': dashed(UID_B), 'apiMessageId': 'BB22', 'type': 8, 'body': body('y.jpg')},
                {'uid': dashed(UID_C), 'apiMessageId': 'cc33', 'type': 8, 'body': body('z.jpg')},
                {'uid': dashed(UID_D), 'apiMessageId': 'cc33', 'type': 8, 'body': body('z.jpg')}]
        with tempfile.TemporaryDirectory() as tmp:
            def put(name, data, encrypt=False):
                path = os.path.join(tmp, name)
                if encrypt:
                    iv = bytes(16)
                    data = iv + AES.new(KEY, AES.MODE_CBC, iv).encrypt(pad(data, 16))
                with open(path, 'wb') as f:
                    f.write(data)
                return path
            photo, thumb = JPEG + b'full', JPEG + b'thumb'
            gallery = [('x.jpg', 'Pictures/Threema', put('g1', photo)),
                       ('t.jpg', 'Pictures/Threema', put('g2', thumb)),
                       ('threema-20240101-120000-bb22.jpg', 'Pictures/Threema', put('g3', b'other')),
                       ('threema-20240101-120000-cc33.jpg', 'Pictures/Threema', put('g4', b'other2')),
                       ('threema-20240101-120000-ff00.jpg', 'Pictures/Threema', put('g5', b'other3')),
                       ('y.jpg', 'Pictures/Threema', put('g6', b'other4')),
                       ('y (1).jpg', 'Pictures/Threema', put('g7', b'other5')),
                       # The apiMessageId of one message, but the bytes of another: bytes win.
                       ('threema-20240101-120000-aa11.jpg', 'Pictures/Threema', put('g8', thumb))]
            container = {'gallery': gallery, 'keys': [KEY],
                         'media': {f'.{UID_A}': put('m1', photo, True),
                                   f'.{UID_C}_T': put('m2', thumb, True)}}
            links = Threema._gallery_links(container, rows)
            without_db = Threema._gallery_links(container, None)
        self.assertEqual([links[g[2]] for g in gallery], [
            (UID_A, 'Identical to the message file', False),
            (UID_C, 'Identical to the message thumbnail', False),
            (None, 'Name carries bb22, the apiMessageId of 1 message; not tied', False),
            (None, 'Name carries cc33, the apiMessageId of 2 messages; not tied', False),
            (None, 'Name carries ff00, the apiMessageId of no message in the database; '
                   'not tied', False),
            (None, '', False),    # the stored file name of one message is not a tie
            (None, '', False),    # nor is it with a ' (n)' suffix
            (UID_C, 'Identical to the message thumbnail', False),
        ])
        # Without the database the bytes still decide, and the pointer gives no count.
        self.assertEqual(without_db[gallery[0][2]], (UID_A, 'Identical to the message file', False))
        self.assertEqual(without_db[gallery[2][2]],
                         (None, 'Name carries bb22; not tied', False))
        self.assertEqual(Threema._gallery_links({'gallery': []}, rows), {})

    def test_gallery_links_tie_only_one_message(self):
        same = b'%PDF-1.4 the same bytes'
        with tempfile.TemporaryDirectory() as tmp:
            def put(name, data, encrypt=False):
                path = os.path.join(tmp, name)
                if encrypt:
                    iv = bytes(16)
                    data = iv + AES.new(KEY, AES.MODE_CBC, iv).encrypt(pad(data, 16))
                with open(path, 'wb') as f:
                    f.write(data)
                return path
            gallery = [('copy.pdf', 'Documents/Threema', put('g1', same))]
            container = {'gallery': gallery, 'keys': [KEY],
                         'media': {f'.{UID_C}': put('m1', same, True),
                                   f'.{UID_D}': put('m2', same, True)}}
            links = Threema._gallery_links(container, [])
        self.assertEqual(links[gallery[0][2]],
                         (None, 'Identical to the files of 2 messages', True))

    def test_no_key_means_no_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'g1')
            with open(path, 'wb') as f:
                f.write(JPEG)
            container = {'gallery': [('x.jpg', 'Pictures/Threema', path)], 'keys': [],
                         'media': {f'.{UID_A}': path}}
            links = Threema._gallery_links(container, [])
        self.assertEqual(links[path], (None, '', False))


if __name__ == '__main__':
    unittest.main()
