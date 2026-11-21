"""Signal on-device backup reader and content artifacts, on a backup written here with a made-up key."""
# pylint: disable=protected-access
import gzip
import hashlib
import hmac
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Crypto.Cipher import AES

from scripts import signal_backup as sb
from scripts.artifacts import signalLocalBackups as slb

KEY = 'abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz01'
OTHER_KEY = 'b' + KEY[1:]
PIN = '4821'
LOCAL_KEY = bytes(range(64))
IMAGE = b'\xff\xd8\xff\xe0' + b'made-up image' * 8
LONG_TEXT = 'the whole long message'.encode()


def varint(value):
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def pad(data):
    count = 16 - len(data) % 16
    return data + bytes([count]) * count


def encrypt_blob(plain, key=LOCAL_KEY):
    iv = b'\x07' * 16
    body = iv + AES.new(key[:32], AES.MODE_CBC, iv=iv).encrypt(pad(plain))
    return body + hmac.new(key[32:], body, hashlib.sha256).digest()


def pointer(target, plain, name='photo.jpg'):
    target.contentType = 'image/jpeg'
    target.fileName = name
    target.locatorInfo.size = len(plain)
    target.locatorInfo.localKey = LOCAL_KEY
    target.locatorInfo.plaintextHash = hashlib.sha256(plain).digest()


def frames():
    out = []
    frame = sb.parse('Frame', b'')
    frame.account.givenName = 'Test'
    frame.account.svrPin = PIN
    out.append(frame)
    for rid, setter in ((1, lambda r: r.self.SetInParent()),
                        (2, lambda r: setattr(r.contact, 'profileGivenName', 'Pat')),
                        (3, lambda r: setattr(r.group.snapshot.title, 'title', 'Team'))):
        frame = sb.parse('Frame', b'')
        frame.recipient.id = rid
        setter(frame.recipient)
        out.append(frame)
    frame = sb.parse('Frame', b'')
    frame.chat.id = 9
    frame.chat.recipientId = 2
    out.append(frame)

    frame = sb.parse('Frame', b'')
    item = frame.chatItem
    item.chatId, item.authorId, item.dateSent = 9, 2, 1700000000000
    item.incoming.dateReceived = 1700000001000
    item.incoming.read = True
    item.standardMessage.text.body = 'hello'
    pointer(item.standardMessage.attachments.add().pointer, IMAGE)
    reaction = item.standardMessage.reactions.add()
    reaction.emoji, reaction.authorId, reaction.sentTimestamp = 'ok', 1, 1700000002000
    earlier = item.revisions.add()
    earlier.chatId, earlier.authorId, earlier.dateSent = 9, 2, 1699999999000
    earlier.incoming.dateReceived = 1699999999500
    earlier.standardMessage.text.body = 'helo'
    out.append(frame)

    frame = sb.parse('Frame', b'')
    item = frame.chatItem
    item.chatId, item.authorId, item.dateSent = 9, 1, 1700000003000
    status = item.outgoing.sendStatus.add()
    status.recipientId, status.timestamp = 2, 1700000004000
    status.read.SetInParent()
    item.standardMessage.text.body = 'the whole'
    pointer(item.standardMessage.longText, LONG_TEXT, name='')
    out.append(frame)

    frame = sb.parse('Frame', b'')
    item = frame.chatItem
    item.chatId, item.authorId, item.dateSent = 9, 2, 1700000005000
    item.directionless.SetInParent()
    item.updateMessage.individualCall.type = 2
    item.updateMessage.individualCall.direction = 1
    item.updateMessage.individualCall.state = 3
    out.append(frame)

    # a kind this reader does not report
    frame = sb.parse('Frame', b'')
    frame.installedStickerPack.SetInParent()
    out.append(frame)
    return out


def write_backup(root, key=KEY):
    """A snapshot folder written the way the app writes one. Returns the member paths."""
    backup_key = sb._hkdf(key.encode(), b'20240801_SIGNAL_BACKUP_KEY', 32)
    metadata_key = sb._hkdf(backup_key, b'20241011_SIGNAL_LOCAL_BACKUP_METADATA_KEY', 32)
    backup_id = b'\x11' * 16
    meta = sb.parse('Metadata', b'')
    meta.version = 1
    meta.backupId.iv = b'\x22' * 12
    meta.backupId.encryptedId = AES.new(metadata_key, AES.MODE_CTR, nonce=meta.backupId.iv,
                                        initial_value=0).encrypt(backup_id)
    keys = sb._hkdf(backup_key, b'20241007_SIGNAL_BACKUP_ENCRYPT_MESSAGE_BACKUP:' + backup_id, 64)
    info = sb.parse('BackupInfo', b'')
    info.version, info.backupTimeMs = 1, 1700000100000
    plain = b''
    for message in [info] + frames():
        data = message.SerializeToString()
        plain += varint(len(data)) + data
    iv = b'\x33' * 16
    body = iv + AES.new(keys[32:], AES.MODE_CBC, iv=iv).encrypt(pad(gzip.compress(plain)))
    main = body + hmac.new(keys[:32], body, hashlib.sha256).digest()

    names = [sb.media_file_name(hashlib.sha256(value).digest(), LOCAL_KEY) for value in (IMAGE, LONG_TEXT)]
    listed = names + ['f' * 64]
    files = b''
    for name in listed:
        frame = sb.parse('FilesFrame', b'')
        frame.mediaName = name
        data = frame.SerializeToString()
        files += varint(len(data)) + data
    snapshot = root / 'data/media/0/Picked/SignalBackups/signal-backup-2023-11-14-22-15-00'
    snapshot.mkdir(parents=True)
    (snapshot / 'main').write_bytes(main)
    (snapshot / 'metadata').write_bytes(meta.SerializeToString())
    (snapshot / 'files').write_bytes(files)
    for name, value in zip(names, (IMAGE, LONG_TEXT)):
        blob = snapshot.parent / 'files' / name[:2] / name
        blob.parent.mkdir(parents=True, exist_ok=True)
        blob.write_bytes(encrypt_blob(value))
    return [snapshot / 'main', snapshot / 'metadata', snapshot / 'files']


class Seeker:
    def __init__(self, root):
        self.root = root

    def search(self, _pattern):
        return [str(path) for path in self.root.rglob('*') if path.is_file() and path.parent.parent.name == 'files']


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = [str(path) for path in files]

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace(os.sep, '/')

    def get_seeker(self):
        return Seeker(self.root)


class KeyTests(unittest.TestCase):
    def test_normalise(self):
        spaced = ' '.join(KEY[i:i + 4] for i in range(0, 64, 4)).upper()
        self.assertEqual(sb.normalise_recovery_key(spaced), KEY)
        self.assertEqual(sb.normalise_recovery_key('#' + 'a' * 62 + '='), 'o' + 'a' * 62 + '0')

    def test_a_key_given_as_the_variable_name_is_not_in_the_error(self):
        with self.assertRaises(ValueError) as caught:
            sb.key_from_env(KEY)
        self.assertNotIn(KEY, str(caught.exception))

    def test_a_bad_value_is_not_in_the_error(self):
        with self.assertRaises(ValueError) as caught:
            sb.normalise_recovery_key('secretvalue123')
        self.assertNotIn('secretvalue', str(caught.exception))


class ParserTests(unittest.TestCase):
    def test_a_float_field_not_named_here_does_not_fail_the_message(self):
        # FilePointer.audioDurationSeconds is field 15, a float (wire type 5)
        data = b'\x22\x03a/b' + varint((15 << 3) | 5) + b'\x00\x00\x80\x3f'
        self.assertEqual(sb.parse('FilePointer', data).contentType, 'a/b')


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.work)
        self.addCleanup(sb.set_recovery_key, None)
        self.files = write_backup(self.work)
        self.context = Context(self.work, self.files)
        patcher = mock.patch.object(slb, 'check_in_embedded_media',
                                    side_effect=lambda _path, data, name='': hashlib.sha1(data).hexdigest())
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def table(function, context):
        headers, rows, source = function.__wrapped__(context)
        names = [h if isinstance(h, str) else h[0] for h in headers]
        for row in rows:
            assert len(row) == len(names)
        return [dict(zip(names, row)) for row in rows], source

    def test_no_key_lists_and_reads_nothing(self):
        rows, _ = self.table(slb.signalLocalBackups, self.context)
        self.assertEqual(rows[0]['Recovery Key Result'], 'Not given')
        self.assertEqual(rows[0]['Backup Time'], '')
        self.assertEqual(self.table(slb.signalBackupMessages, self.context)[0], [])

    def test_wrong_key_gives_no_content(self):
        sb.set_recovery_key(OTHER_KEY)
        rows, _ = self.table(slb.signalLocalBackups, self.context)
        self.assertEqual(rows[0]['Recovery Key Result'], 'Did not open')
        self.assertEqual(self.table(slb.signalBackupMessages, self.context)[0], [])
        with self.assertRaises(sb.BackupKeyError):
            sb.open_snapshot(str(self.files[0]), str(self.files[1]), OTHER_KEY)

    def test_a_changed_byte_is_refused(self):
        data = bytearray(self.files[0].read_bytes())
        data[40] ^= 1
        self.files[0].write_bytes(data)
        with self.assertRaises(sb.BackupKeyError):
            sb.open_snapshot(str(self.files[0]), str(self.files[1]), KEY)

    def test_messages(self):
        sb.set_recovery_key(KEY)
        rows, _ = self.table(slb.signalBackupMessages, self.context)
        self.assertEqual(len(rows), 4)
        earlier, latest, outgoing, call = rows
        self.assertEqual((earlier['Message'], earlier['Revision']), ('helo', 'Earlier version 1 of 1'))
        self.assertEqual((latest['Message'], latest['Revision']), ('hello', 'Latest of 2'))
        self.assertEqual(latest['Attachments'], [hashlib.sha1(IMAGE).hexdigest()])
        self.assertEqual((latest['Sender'], latest['Conversation'], latest['Direction']), ('Pat', 'Pat', 'Incoming'))
        self.assertIn('ok Self', latest['Reactions'])
        self.assertEqual(outgoing['Message'], LONG_TEXT.decode())
        self.assertIn('Pat: read', outgoing['Send Status'])
        self.assertEqual(call['Message'], '[VIDEO_CALL, INCOMING, MISSED]')
        self.assertEqual(earlier['Attachments'], '')

    def test_attachments_and_a_damaged_blob(self):
        sb.set_recovery_key(KEY)
        rows, _ = self.table(slb.signalBackupAttachments, self.context)
        status = sorted(row['Status'] for row in rows)
        self.assertEqual(status, ['Listed, no pointer read', 'Verified', 'Verified'])
        name = sb.media_file_name(hashlib.sha256(IMAGE).digest(), LOCAL_KEY)
        blob = self.files[0].parent.parent / 'files' / name[:2] / name
        data = bytearray(blob.read_bytes())
        data[20] ^= 1
        blob.write_bytes(data)
        rows, _ = self.table(slb.signalBackupAttachments, self.context)
        damaged = [row for row in rows if row['File Name'] == 'photo.jpg'][0]
        self.assertEqual((damaged['Status'], damaged['Attachment']), ('Did not verify', None))

    def test_recipients_chats_account(self):
        sb.set_recovery_key(KEY)
        rows, _ = self.table(slb.signalBackupRecipients, self.context)
        self.assertEqual({row['Kind']: row['Display Name'] for row in rows},
                         {'self': 'Self', 'contact': 'Pat', 'group': 'Team'})
        self.assertEqual({row['Kind']: row['Blocked'] for row in rows}, {'self': '', 'contact': 'No', 'group': 'No'})
        rows, _ = self.table(slb.signalBackupChats, self.context)
        self.assertEqual((rows[0]['Conversation'], rows[0]['Items']), ('Pat', 3))
        rows, _ = self.table(slb.signalBackupAccount, self.context)
        self.assertEqual((rows[0]['Given Name'], rows[0]['PIN (as stored)']), ('Test', PIN))

    def test_the_key_is_in_no_row(self):
        sb.set_recovery_key(KEY)
        for function in (slb.signalLocalBackups, slb.signalBackupMessages, slb.signalBackupAttachments,
                         slb.signalBackupRecipients, slb.signalBackupChats, slb.signalBackupAccount):
            _headers, rows, source = function.__wrapped__(self.context)
            self.assertNotIn(KEY, repr(rows) + source)


if __name__ == '__main__':
    unittest.main()
