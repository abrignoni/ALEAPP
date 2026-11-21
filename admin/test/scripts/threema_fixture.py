"""Builds a constructed Threema install with a version 2 master_key.dat, for the Threema artifacts.

Every value is invented: the master key, Threema IDs, names, texts, times and pictures. The structure follows
the client: the master_key.dat layers of key-storage.proto (2-byte version, one length-delimited field per layer), a
SQLCipher 4 database keyed with the passphrase x"<master key hex>" and one key derivation iteration, the table definitions of
database schema version 114, the message body shapes the client writes, and the user files in the legacy external
directory, encrypted as AES-CBC with the IV in front.

Usage, from the repository root: python -m admin.test.scripts.threema_fixture
Writes one zip per Threema artifact into admin/test/cases/data/Threema/ and the case into testdata.Threema.json.
"""
import base64
import fnmatch
import hashlib
import io
import json
import os
import tempfile

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from PIL import Image
from sqlcipher3 import dbapi2 as sqlcipher

from admin.test.scripts import bugreport_fixture as base

CASE = 'casesynthetic_v2'
MASTER_KEY = hashlib.sha256(b'invented Threema fixture master key').digest()
APP = 'Dump/data/data/ch.threema.app'
EXTERNAL = 'Dump/data/media/0/Android/data/ch.threema.app/files/data'
GALLERY = 'Dump/data/media/0/Pictures/Threema'
OWN, CONTACT, NICK_ONLY, GROUP_ONLY = 'FIXTOWN1', 'FIXTCON1', 'FIXTCON2', 'FIXTGRP1'
PHOTO_UID = '0f1e2d3c-4b5a-4968-8776-a5b4c3d2e1f0'
ORPHAN_UID = '11112222-3333-4444-5555-666677778888'
T0 = base.epoch_ms('2026-11-01 09:00:00')

# The client's table columns at schema version 114.
SCHEMA = (
    "CREATE TABLE `contacts` (`identity` VARCHAR ,`publicKey` BLOB ,`firstName` VARCHAR ,`lastName` VARCHAR ,"
    "`publicNickName` VARCHAR ,`verificationLevel` INTEGER ,`state` VARCHAR DEFAULT 'ACTIVE' NOT NULL ,"
    "`androidContactId` VARCHAR ,`featureLevel` INTEGER DEFAULT 0 NOT NULL ,`idColorIndex` INTEGER ,"
    "`avatarExpires` BIGINT,`isWork` TINYINT DEFAULT 0,`type` INT DEFAULT 0,`profilePicBlobID` BLOB DEFAULT NULL,"
    "`dateCreated` BIGINT DEFAULT 0,`lastUpdate` INTEGER,`acquaintanceLevel` TINYINT DEFAULT 0 NOT NULL,"
    "`isRestored` TINYINT DEFAULT 0,`isArchived` TINYINT DEFAULT 0,`readReceipts` TINYINT DEFAULT 0,"
    "`typingIndicators` TINYINT DEFAULT 0,`forwardSecurityState` TINYINT DEFAULT 0,"
    "`syncState` INTEGER NOT NULL DEFAULT 0,`jobTitle` VARCHAR DEFAULT NULL,`department` VARCHAR DEFAULT NULL,"
    "`notificationTriggerPolicyOverride` BIGINT DEFAULT NULL,PRIMARY KEY (`identity`) )",
    "CREATE TABLE `message`(`id` INTEGER PRIMARY KEY AUTOINCREMENT , `uid` VARCHAR , `apiMessageId` VARCHAR , "
    "`identity` VARCHAR , `outbox` SMALLINT , `type` INTEGER , `body` VARCHAR , `correlationId` VARCHAR , "
    "`caption` VARCHAR , `isRead` SMALLINT , `isSaved` SMALLINT , `isQueued` TINYINT , `state` VARCHAR , "
    "`postedAtUtc` BIGINT , `createdAtUtc` BIGINT , `modifiedAtUtc` BIGINT , `isStatusMessage` SMALLINT ,"
    "`quotedMessageId` VARCHAR ,`messageContentsType` TINYINT ,`messageFlags` INT ,`deliveredAtUtc` DATETIME ,"
    "`readAtUtc` DATETIME ,`forwardSecurityMode` TINYINT DEFAULT 0 ,`displayTags` TINYINT DEFAULT 0 ,"
    "`editedAtUtc` DATETIME ,`deletedAtUtc` DATETIME )",
    "CREATE TABLE `m_group` (`id` INTEGER PRIMARY KEY AUTOINCREMENT , `apiGroupId` VARCHAR , `name` VARCHAR , "
    "`creatorIdentity` VARCHAR , `createdAt` VARCHAR , `lastUpdate` INTEGER, `synchronizedAt` BIGINT , "
    "`isArchived` TINYINT DEFAULT 0, `groupDesc` VARCHAR DEFAULT NULL, `changedGroupDescTimestamp` VARCHAR DEFAULT NULL, "
    "`colorIndex` INTEGER DEFAULT 0 NOT NULL, `userState` INTEGER DEFAULT 0 NOT NULL, "
    "`notificationTriggerPolicyOverride` BIGINT DEFAULT NULL )",
    "CREATE TABLE `m_group_message`(`id` INTEGER PRIMARY KEY AUTOINCREMENT , `uid` VARCHAR , `apiMessageId` VARCHAR , "
    "`groupId` INTEGER NOT NULL , `identity` VARCHAR , `outbox` SMALLINT , `type` INTEGER ,`correlationId` VARCHAR ,"
    "`body` VARCHAR ,`caption` VARCHAR ,`isRead` SMALLINT ,`isSaved` SMALLINT ,`isQueued` TINYINT ,`state` VARCHAR , "
    "`postedAtUtc` BIGINT , `createdAtUtc` BIGINT , `modifiedAtUtc` BIGINT , `isStatusMessage` SMALLINT ,"
    "`quotedMessageId` VARCHAR ,`messageContentsType` TINYINT ,`messageFlags` INT ,`deliveredAtUtc` DATETIME ,"
    "`readAtUtc` DATETIME ,`forwardSecurityMode` TINYINT DEFAULT 0 ,`groupMessageStates` VARCHAR ,"
    "`displayTags` TINYINT DEFAULT 0 ,`editedAtUtc` DATETIME ,`deletedAtUtc` DATETIME )",
    "CREATE TABLE `contact_reactions` (`messageId` INTEGER NOT NULL, `senderIdentity` VARCHAR NOT NULL, "
    "`emojiSequence` VARCHAR NOT NULL, `reactedAt` DATETIME NOT NULL, UNIQUE(`messageId`,`senderIdentity`,"
    "`emojiSequence`) ON CONFLICT REPLACE, CONSTRAINT `fk_contact_message_id` FOREIGN KEY(`messageId`) "
    "REFERENCES `message` (`id`) ON UPDATE CASCADE ON DELETE CASCADE )",
    "CREATE TABLE `group_reactions` (`messageId` INTEGER NOT NULL, `senderIdentity` VARCHAR NOT NULL, "
    "`emojiSequence` VARCHAR NOT NULL, `reactedAt` DATETIME NOT NULL, UNIQUE(`messageId`,`senderIdentity`,"
    "`emojiSequence`) ON CONFLICT REPLACE, CONSTRAINT `fk_group_message_id` FOREIGN KEY(`messageId`) "
    "REFERENCES `m_group_message` (`id`) ON UPDATE CASCADE ON DELETE CASCADE )",
)


def _layer(field, payload):
    """One key-storage.proto layer: version 0 as 2 bytes, then one length-delimited field."""
    return b'\x00\x00' + bytes([field << 3 | 2, len(payload)]) + payload


def master_key_dat():
    """An unprotected version 2 key file: plaintext intermediate, plaintext inner, the master key."""
    return _layer(1, _layer(1, _layer(1, MASTER_KEY)))


def _encrypt(data, iv_byte):
    iv = bytes([iv_byte]) * 16
    return iv + AES.new(MASTER_KEY, AES.MODE_CBC, iv).encrypt(pad(data, 16))


def _jpeg(colour, size):
    buffer = io.BytesIO()
    Image.new('RGB', size, colour).save(buffer, 'JPEG')
    return buffer.getvalue()


def _picture_name(prefix, identity):
    return prefix + base64.b32encode(hashlib.sha256(f'c-{identity}'.encode()).digest()).decode().rstrip('=')


def preferences():
    return ("<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n<map>\n"
            f'    <string name="identity">{OWN}</string>\n'
            '    <string name="nickname">Fixture Owner</string>\n'
            '    <string name="linked_mobile">+10000000000</string>\n'
            '</map>\n').encode()


def _message(uid, kind, body, outbox=0, created=0, **extra):
    row = {'uid': uid, 'apiMessageId': extra.pop('api', None), 'identity': extra.pop('identity', CONTACT),
           'outbox': outbox, 'type': kind, 'body': body, 'caption': extra.pop('caption', None),
           'isRead': 1, 'state': extra.pop('state', None), 'createdAtUtc': T0 + created * 60000,
           'modifiedAtUtc': T0 + created * 60000, 'isStatusMessage': extra.pop('status', 0),
           'quotedMessageId': extra.pop('quoted', None)}
    row.update(extra)
    return row


def messages():
    photo_body = json.dumps([None, None, 'image/jpeg', 0, 'fixture-photo.jpg', 1, True, 'A constructed picture',
                             'image/jpeg', {'w': 32, 'h': 24}], separators=(',', ':'))
    return [
        _message('a0000000-0000-4000-8000-000000000001', 0, 'Hello from the fixture', api='api1', created=0,
                 state='USERACK'),
        _message('a0000000-0000-4000-8000-000000000002', 0, 'A reply quoting it', outbox=1, api='api2', created=1,
                 quoted='api1', state='READ', deliveredAtUtc=T0 + 61000, readAtUtc=T0 + 62000),
        _message('a0000000-0000-4000-8000-000000000003', 4,
                 json.dumps([47.0, 8.0, 12.5, 'Invented street 1, Nowhere', None]), created=2),
        _message(PHOTO_UID, 8, photo_body, outbox=1, created=3, state='READ'),
        _message('a0000000-0000-4000-8000-000000000005', 9, json.dumps([1, {'status': 2, 'duration': 42}]),
                 outbox=1, created=4),
        _message('a0000000-0000-4000-8000-000000000006', 12,
                 json.dumps([3, {'status': 3, 'quantity': 0, 'staticText': None}]), created=5, status=1),
        _message('a0000000-0000-4000-8000-000000000007', 3, json.dumps([7, True, '00' * 16, '11' * 16]), created=6),
        _message('a0000000-0000-4000-8000-000000000008', 1, json.dumps([True, '', '', '']),
                 caption='An old image message', created=7),
        _message('a0000000-0000-4000-8000-000000000009', 0, 'Edited and then deleted', outbox=1, created=8,
                 editedAtUtc=T0 + 9 * 60000, deletedAtUtc=T0 + 10 * 60000),
    ]


def group_messages():
    return [
        _message('b0000000-0000-4000-8000-000000000001', 0, 'Group created.', identity=None, created=20, status=1,
                 groupId=1),
        _message('b0000000-0000-4000-8000-000000000002', 0, 'Hi group', identity=NICK_ONLY, api='gapi1', created=21,
                 groupId=1),
        _message('b0000000-0000-4000-8000-000000000003', 0, 'Hi back', identity=None, outbox=1, created=22,
                 quoted='gapi1', groupId=1),
    ]


def database():
    """The bytes of threema4.db, written through SQLCipher with the client's key and settings."""
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, 'threema4.db')
    con = sqlcipher.connect(path)  # pylint: disable=no-member
    # The client's passphrase is the text x"<hex>", not SQLCipher's raw key
    # syntax x'<hex>', derived with a single iteration (DatabaseExtensions.kt).
    con.execute(f"PRAGMA key = 'x\"{MASTER_KEY.hex()}\"'")
    con.execute('PRAGMA kdf_iter = 1')
    for statement in SCHEMA:
        con.execute(statement)
    con.execute('PRAGMA user_version = 114')
    con.executemany('INSERT INTO contacts (identity, firstName, lastName, publicNickName, verificationLevel, '
                    'dateCreated, acquaintanceLevel, isArchived) VALUES (?,?,?,?,?,?,?,?)', [
                        (CONTACT, 'Fixture', 'Contact', 'fixture', 2, T0 - 86400000, 0, 0),
                        (NICK_ONLY, None, None, 'Nick Only', 1, T0 - 3600000, 0, 1),
                        (GROUP_ONLY, None, None, 'Group Member', 0, T0 - 60000, 1, 0)])
    for table, rows in (('message', messages()), ('m_group_message', group_messages())):
        for row in rows:
            con.execute(f'INSERT INTO {table} ({", ".join(row)}) VALUES ({", ".join("?" * len(row))})',
                        list(row.values()))
    con.execute("INSERT INTO m_group (id, apiGroupId, name, creatorIdentity) VALUES (1, 'g1', 'Fixture group', ?)",
                (OWN,))
    con.execute("INSERT INTO contact_reactions VALUES (2, ?, '❤️', ?)", (CONTACT, T0 + 5 * 60000))
    con.execute("INSERT INTO group_reactions VALUES (2, ?, '\U0001F44D', ?)", (OWN, T0 + 23 * 60000))
    con.commit()
    con.close()
    with open(path, 'rb') as handle:
        data = handle.read()
    os.remove(path)
    os.rmdir(folder)
    return data


def files():
    """(path in the extraction, bytes) of the constructed install."""
    photo = _jpeg((200, 80, 40), (32, 24))
    stem = '.' + PHOTO_UID.replace('-', '')
    return [
        (f'{APP}/files/master_key.dat', master_key_dat()),
        (f'{APP}/databases/threema4.db', database()),
        (f'{APP}/shared_prefs/ch.threema.app_preferences.xml', preferences()),
        (f'{EXTERNAL}/{stem}', _encrypt(photo, 1)),
        (f'{EXTERNAL}/{stem}_T', _encrypt(_jpeg((200, 80, 40), (8, 6)), 2)),
        # A message file whose message is not in the database.
        (f'{EXTERNAL}/.{ORPHAN_UID.replace("-", "")}', _encrypt(_jpeg((40, 80, 200), (8, 8)), 3)),
        (f'{EXTERNAL}/.avatar/{_picture_name(".c-", OWN)}.nomedia', _encrypt(_jpeg((10, 10, 10), (8, 8)), 4)),
        (f'{EXTERNAL}/.avatar/{_picture_name(".p-", CONTACT)}.nomedia', _encrypt(_jpeg((90, 90, 90), (8, 8)), 5)),
        # Not a user file name of the client, and not encrypted: not reported.
        (f'{EXTERNAL}/.nomedia', b''),
        # Gallery copies: the photo as copyMediaFileToGallery writes it (decrypted, under the
        # message's file name), and a picture no message is tied to.
        (f'{GALLERY}/fixture-photo.jpg', photo),
        (f'{GALLERY}/unrelated.jpg', _jpeg((5, 5, 5), (8, 8))),
    ]


def write_case(repo_root='.'):
    """Write the zips and the case of testdata.Threema.json under repo_root."""
    from scripts.artifacts import Threema  # pylint: disable=import-outside-toplevel
    members = files()
    folder = os.path.join(repo_root, 'admin', 'test', 'cases', 'data', 'Threema')
    case = {'description': 'Constructed Threema install with an unprotected version 2 master_key.dat, built by '
                           'admin/test/scripts/threema_fixture.py, in the file layout, key file layers and table '
                           'definitions of schema version 114. Invented values, contains no real evidence.',
            'maker': 'synthetic',
            'make_data': {'input_data_path': 'threema_fixture.py', 'os': 'any',
                          'timestamp': '2026-11-15T12:00:00.000000',
                          'last_commit': {'hash': 'Uncommitted', 'author_name': 'N/A', 'author_email': 'N/A',
                                          'date': '2026-11-15T12:00:00.000000',
                                          'message': 'File not yet committed to git'}},
            'artifacts': {}}
    for artifact, block in Threema.__artifacts_v2__.items():
        patterns = list(block['paths'])
        matched = [(name, data) for name, data in members
                   if any(fnmatch.fnmatchcase('root/' + name, pattern) for pattern in patterns)]
        base.write_zip(os.path.join(folder, f'testdata.Threema.{artifact}.{CASE}.zip'), matched)
        case['artifacts'][artifact] = {'search_patterns': patterns, 'file_count': len(matched),
                                       'expected_output': {'headers': [], 'data': []}}
    path = os.path.join(repo_root, 'admin', 'test', 'cases', 'testdata.Threema.json')
    with open(path, encoding='utf-8') as handle:
        cases = json.load(handle)
    cases[CASE] = case
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        json.dump(cases, handle, indent=2, ensure_ascii=False)
        handle.write('\n')
    for artifact, entry in case['artifacts'].items():
        print(artifact, entry['file_count'], 'files')


if __name__ == '__main__':
    write_case()
