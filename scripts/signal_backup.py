"""Signal on-device backup: the recovery key for this run, and the reader of a snapshot.

The key is held in this process only. It is never written to a profile, case data file,
log, report or history entry, and no message raised here carries it.

Format from Signal-Android tag v8.35.4 (commit b330f4efcf49a0cec87807d18504f07f5df12bf2)
and libsignal tag v0.106.1 (commit 904c8dc8216073b078a5f2f5090e3da8382e6a92). _SCHEMA below
names only the field numbers and types read here (lib/archive/src/main/protowire/Backup.proto
and LocalArchive.proto); a field not named is ignored by the protobuf parser.
"""
# pylint: disable=no-member  # protobuf and PyCryptodome build these names at run time
import hashlib
import hmac
import os
import re
import zlib

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
from google.protobuf.message import DecodeError

KEY_LENGTH = 64  # AccountEntropyPool.LENGTH (core/util-jvm/.../AccountEntropyPool.kt L21)
_FORWARD_SECRECY_MAGIC = b'SBACKUP\x01'  # EncryptedBackupWriter.MAGIC_NUMBER
_CHUNK = 1024 * 1024
_MAC_SIZE = 32
_IV_SIZE = 16

_recovery_key = None


class BackupKeyError(Exception):
    """The key does not open this snapshot: its HMAC did not verify."""


class BackupFormatError(Exception):
    """The snapshot is damaged or uses a layout this reader does not handle."""


def normalise_recovery_key(text):
    """The key in the form Signal derives from (AccountEntropyPool.kt L17, L29-32, L49).

    Raises ValueError, with no part of the value in its message, when it is not 64 letters
    and digits once separators are removed.
    """
    stripped = re.sub(r'[^0-9a-zA-Z]', '', text.replace('#', 'O').replace('=', '0')).lower()
    if len(stripped) != KEY_LENGTH:
        raise ValueError(f'A Signal recovery key has {KEY_LENGTH} letters and digits; '
                         f'this value has {len(stripped)}.')
    return stripped


def key_from_file(path):
    """The normalised key read from a text file."""
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            return normalise_recovery_key(handle.read(4096))
    except (OSError, UnicodeDecodeError) as error:
        raise ValueError(f'Could not read the Signal recovery key file: {type(error).__name__}') from None


def key_from_env(name):
    """The normalised key read from an environment variable."""
    value = os.environ.get(name)
    if not value:
        raise ValueError(f'The environment variable {name} is not set.')
    return normalise_recovery_key(value)


def set_recovery_key(key):
    """Hold the normalised key for this run, or clear it with None."""
    global _recovery_key  # pylint: disable=global-statement
    _recovery_key = key


def get_recovery_key():
    """The key held for this run, or None."""
    return _recovery_key


# name: {field: (number, type or message name[, 'repeated'])}
_SCHEMA = {
    'Metadata': {'version': (1, 'uint64'), 'backupId': (2, 'EncryptedBackupId')},
    'EncryptedBackupId': {'iv': (1, 'bytes'), 'encryptedId': (2, 'bytes')},
    'FilesFrame': {'mediaName': (1, 'string')},
    'BackupInfo': {'version': (1, 'uint64'), 'backupTimeMs': (2, 'uint64'),
                   'currentAppVersion': (4, 'string'), 'firstAppVersion': (5, 'string')},
    'Frame': {'account': (1, 'AccountData'), 'recipient': (2, 'Recipient'), 'chat': (3, 'Chat'),
              'chatItem': (4, 'ChatItem'), 'installedStickerPack': (5, 'Unread'),
              'adHocCall': (6, 'Unread'), 'notificationProfile': (7, 'Unread'),
              'chatFolder': (8, 'Unread'), 'hiddenStickerPack': (9, 'Unread'),
              'favoriteStickerList': (10, 'Unread')},
    'Unread': {},
    'AccountData': {'username': (2, 'string'), 'givenName': (4, 'string'), 'familyName': (5, 'string'),
                    'svrPin': (11, 'string'), 'bioText': (13, 'string'), 'bioEmoji': (14, 'string')},
    'Recipient': {'id': (1, 'uint64'), 'contact': (2, 'Contact'), 'group': (3, 'Group'),
                  'distributionList': (4, 'DistributionListItem'), 'self': (5, 'Unread'),
                  'releaseNotes': (6, 'Unread'), 'callLink': (7, 'Unread')},
    'Name': {'given': (1, 'string'), 'family': (2, 'string')},
    'NotRegistered': {'unregisteredTimestamp': (1, 'uint64')},
    'Contact': {'aci': (1, 'bytes'), 'pni': (2, 'bytes'), 'username': (3, 'string'), 'e164': (4, 'uint64'),
                'blocked': (5, 'bool'), 'visibility': (6, 'int32'), 'notRegistered': (8, 'NotRegistered'),
                'profileGivenName': (11, 'string'), 'profileFamilyName': (12, 'string'),
                'nickname': (16, 'Name'), 'note': (17, 'string'), 'systemGivenName': (18, 'string'),
                'systemFamilyName': (19, 'string'), 'systemNickname': (20, 'string'),
                'blockedAtTimestamp': (23, 'uint64')},
    'Group': {'snapshot': (5, 'GroupSnapshot'), 'blocked': (6, 'bool'), 'blockedAtTimestamp': (8, 'uint64')},
    'GroupSnapshot': {'title': (2, 'GroupAttributeBlob'), 'members': (7, 'GroupMember', 'repeated'),
                      'description': (11, 'GroupAttributeBlob')},
    'GroupAttributeBlob': {'title': (1, 'string'), 'descriptionText': (4, 'string')},
    'GroupMember': {'userId': (1, 'bytes')},
    'DistributionListItem': {'deletionTimestamp': (2, 'uint64'), 'distributionList': (3, 'DistributionList')},
    'DistributionList': {'name': (1, 'string'), 'memberRecipientIds': (4, 'uint64', 'repeated')},
    'Chat': {'id': (1, 'uint64'), 'recipientId': (2, 'uint64'), 'archived': (3, 'bool'),
             'pinnedOrder': (4, 'uint32'), 'expirationTimerMs': (5, 'uint64'), 'muteUntilMs': (6, 'uint64'),
             'markedUnread': (7, 'bool')},
    'ChatItem': {'chatId': (1, 'uint64'), 'authorId': (2, 'uint64'), 'dateSent': (3, 'uint64'),
                 'expireStartDate': (4, 'uint64'), 'expiresInMs': (5, 'uint64'),
                 'revisions': (6, 'ChatItem', 'repeated'), 'sms': (7, 'bool'),
                 'incoming': (8, 'IncomingMessageDetails'), 'outgoing': (9, 'OutgoingMessageDetails'),
                 'directionless': (10, 'Unread'), 'standardMessage': (11, 'StandardMessage'),
                 'contactMessage': (12, 'ReactionsOnly2'), 'stickerMessage': (13, 'StickerMessage'),
                 'remoteDeletedMessage': (14, 'Unread'), 'updateMessage': (15, 'ChatUpdateMessage'),
                 'paymentNotification': (16, 'Unread'), 'giftBadge': (17, 'Unread'),
                 'viewOnceMessage': (18, 'ViewOnceMessage'),
                 'directStoryReplyMessage': (19, 'DirectStoryReplyMessage'), 'poll': (20, 'Poll'),
                 'adminDeletedMessage': (22, 'Unread')},
    'IncomingMessageDetails': {'dateReceived': (1, 'uint64'), 'dateServerSent': (2, 'uint64'),
                               'read': (3, 'bool'), 'sealedSender': (4, 'bool')},
    'OutgoingMessageDetails': {'sendStatus': (1, 'SendStatus', 'repeated'), 'dateReceived': (2, 'uint64')},
    'SendStatus': {'recipientId': (1, 'uint64'), 'timestamp': (2, 'uint64'), 'pending': (3, 'Unread'),
                   'sent': (4, 'Unread'), 'delivered': (5, 'Unread'), 'read': (6, 'Unread'),
                   'viewed': (7, 'Unread'), 'skipped': (8, 'Unread'), 'failed': (9, 'Unread')},
    'Text': {'body': (1, 'string')},
    'StandardMessage': {'quote': (1, 'Quote'), 'text': (2, 'Text'),
                        'attachments': (3, 'MessageAttachment', 'repeated'),
                        'linkPreview': (4, 'LinkPreview', 'repeated'), 'longText': (5, 'FilePointer'),
                        'reactions': (6, 'Reaction', 'repeated')},
    'ReactionsOnly2': {'reactions': (2, 'Reaction', 'repeated')},
    'StickerMessage': {'sticker': (1, 'Sticker'), 'reactions': (2, 'Reaction', 'repeated')},
    'Sticker': {'emoji': (4, 'string'), 'data': (5, 'FilePointer')},
    'ViewOnceMessage': {'attachment': (1, 'MessageAttachment'), 'reactions': (2, 'Reaction', 'repeated')},
    'DirectStoryReplyMessage': {'textReply': (1, 'TextReply'), 'emoji': (2, 'string'),
                                'reactions': (3, 'Reaction', 'repeated')},
    'TextReply': {'text': (1, 'Text'), 'longText': (2, 'FilePointer')},
    'Poll': {'question': (1, 'string'), 'options': (3, 'PollOption', 'repeated'),
             'reactions': (5, 'Reaction', 'repeated')},
    'PollOption': {'option': (1, 'string')},
    'LinkPreview': {'url': (1, 'string'), 'title': (2, 'string'), 'image': (3, 'FilePointer')},
    'MessageAttachment': {'pointer': (1, 'FilePointer'), 'flag': (2, 'int32')},
    'FilePointer': {'contentType': (4, 'string'), 'fileName': (7, 'string'), 'caption': (10, 'string'),
                    'locatorInfo': (13, 'LocatorInfo')},
    'LocatorInfo': {'size': (3, 'uint32'), 'localKey': (9, 'bytes'), 'plaintextHash': (10, 'bytes')},
    'Quote': {'targetSentTimestamp': (1, 'uint64'), 'authorId': (2, 'uint64'), 'text': (3, 'Text')},
    'Reaction': {'emoji': (1, 'string'), 'authorId': (2, 'uint64'), 'sentTimestamp': (3, 'uint64')},
    'ChatUpdateMessage': {'simpleUpdate': (1, 'SimpleChatUpdate'), 'groupChange': (2, 'Unread'),
                          'expirationTimerChange': (3, 'Unread'), 'profileChange': (4, 'Unread'),
                          'threadMerge': (5, 'Unread'), 'sessionSwitchover': (6, 'Unread'),
                          'individualCall': (7, 'IndividualCall'), 'groupCall': (8, 'Unread'),
                          'learnedProfileChange': (9, 'Unread'), 'pollTerminate': (10, 'Unread'),
                          'pinMessage': (11, 'Unread')},
    'SimpleChatUpdate': {'type': (1, 'int32')},
    'IndividualCall': {'type': (2, 'int32'), 'direction': (3, 'int32'), 'state': (4, 'int32'),
                       'startedCallTimestamp': (5, 'uint64')},
}

_PACKAGE = 'leapp.signalbackup'
_SCALARS = {
    'uint64': descriptor_pb2.FieldDescriptorProto.TYPE_UINT64,
    'uint32': descriptor_pb2.FieldDescriptorProto.TYPE_UINT32,
    'int32': descriptor_pb2.FieldDescriptorProto.TYPE_INT32,
    'bool': descriptor_pb2.FieldDescriptorProto.TYPE_BOOL,
    'string': descriptor_pb2.FieldDescriptorProto.TYPE_STRING,
    'bytes': descriptor_pb2.FieldDescriptorProto.TYPE_BYTES,
}


def _build_messages():
    source = descriptor_pb2.FileDescriptorProto(
        name='leapp_signal_backup_subset.proto', package=_PACKAGE, syntax='proto2')
    for message_name, fields in _SCHEMA.items():
        message = source.message_type.add(name=message_name)
        for field_name, spec in fields.items():
            field = message.field.add(name=field_name, number=spec[0])
            field.label = (descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED if len(spec) > 2
                           else descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL)
            if spec[1] in _SCALARS:
                field.type = _SCALARS[spec[1]]
            else:
                field.type = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
                field.type_name = f'.{_PACKAGE}.{spec[1]}'
    pool = descriptor_pool.DescriptorPool()
    pool.Add(source)
    return {name: message_factory.GetMessageClass(pool.FindMessageTypeByName(f'{_PACKAGE}.{name}'))
            for name in _SCHEMA}


_MESSAGES = _build_messages()


def parse(name, data):
    """A message of _SCHEMA parsed from bytes. Raises BackupFormatError when it does not decode."""
    message = _MESSAGES[name]()
    try:
        message.ParseFromString(data)
    except DecodeError:
        raise BackupFormatError(f'{name} did not decode') from None
    return message


def which(message, names):
    """The first of names that is set on message, or ''."""
    for name in names:
        if message.HasField(name):
            return name
    return ''


def frame_names():
    """The kinds of frame a backup can hold."""
    return tuple(_SCHEMA['Frame'])


def _hkdf(secret, info, length):
    # RFC 5869 with no salt, as libsignal's Hkdf::new(None, ikm) (rust/account-keys/src/backup.rs)
    return HKDF(secret, length, None, SHA256, context=info)


def _read_varint(data, pos):
    value = shift = 0
    while pos < len(data) and shift < 64:
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, pos
        shift += 7
    return None, pos


def message_keys(recovery_key, metadata):
    """(HMAC key, AES key) of a snapshot, from the recovery key and its metadata file's bytes.

    Backup key = HKDF(key, 20240801_SIGNAL_BACKUP_KEY); metadata key = HKDF(backup key,
    20241011_SIGNAL_LOCAL_BACKUP_METADATA_KEY) (libsignal rust/account-keys/src/backup.rs
    L46-49, L63-67). The backup ID is AES-256-CTR under the metadata key, and the message
    key is HKDF(backup key, 20241007_SIGNAL_BACKUP_ENCRYPT_MESSAGE_BACKUP: + backup ID, 64),
    HMAC key first (rust/message-backup/src/key.rs L37-51).
    """
    parsed = parse('Metadata', metadata)
    if len(parsed.backupId.iv) != 12 or not parsed.backupId.encryptedId:
        raise BackupFormatError('metadata has no 12-byte IV and encrypted backup ID')
    backup_key = _hkdf(recovery_key.encode('ascii'), b'20240801_SIGNAL_BACKUP_KEY', 32)
    metadata_key = _hkdf(backup_key, b'20241011_SIGNAL_LOCAL_BACKUP_METADATA_KEY', 32)
    backup_id = AES.new(metadata_key, AES.MODE_CTR, nonce=parsed.backupId.iv,
                        initial_value=0).decrypt(parsed.backupId.encryptedId)
    keys = _hkdf(backup_key, b'20241007_SIGNAL_BACKUP_ENCRYPT_MESSAGE_BACKUP:' + backup_id, 64)
    return keys[:32], keys[32:]


def _verify_mac(path, size, mac_key):
    digest = hmac.new(mac_key, digestmod=hashlib.sha256)
    with open(path, 'rb') as handle:
        remaining = size - _MAC_SIZE
        while remaining:
            chunk = handle.read(min(_CHUNK, remaining))
            if not chunk:
                raise BackupFormatError('main ended early')
            digest.update(chunk)
            remaining -= len(chunk)
        stored = handle.read(_MAC_SIZE)
    if not hmac.compare_digest(digest.digest(), stored):
        raise BackupKeyError('main did not verify')


def _plaintext_chunks(path, size, aes_key):
    with open(path, 'rb') as handle:
        iv = handle.read(_IV_SIZE)
        cipher = AES.new(aes_key, AES.MODE_CBC, iv=iv)
        remaining = size - _IV_SIZE - _MAC_SIZE
        if remaining <= 0 or remaining % 16:
            raise BackupFormatError('main is not a whole number of cipher blocks')
        while remaining:
            take = min(_CHUNK, remaining)
            data = handle.read(take)
            if len(data) != take:
                raise BackupFormatError('main ended early')
            remaining -= take
            block = cipher.decrypt(data)
            if not remaining:
                pad = block[-1]
                if not 1 <= pad <= 16 or block[-pad:] != bytes([pad]) * pad:
                    raise BackupFormatError('main has invalid padding')
                block = block[:-pad]
            yield block


def _frames(path, size, aes_key):
    inflater = zlib.decompressobj(wbits=31)
    buffer = bytearray()
    try:
        for chunk in _plaintext_chunks(path, size, aes_key):
            buffer += inflater.decompress(chunk)
            pos = 0
            while True:
                length, after = _read_varint(buffer, pos)
                if length is None or after + length > len(buffer):
                    break
                yield bytes(buffer[after:after + length])
                pos = after + length
            del buffer[:pos]
        buffer += inflater.flush()
    except zlib.error:
        raise BackupFormatError('main did not decompress') from None
    pos = 0
    while pos < len(buffer):
        length, after = _read_varint(buffer, pos)
        if length is None or after + length > len(buffer):
            raise BackupFormatError('main ends inside a frame')
        yield bytes(buffer[after:after + length])
        pos = after + length


def open_snapshot(main_path, metadata_path, recovery_key):
    """(BackupInfo, iterator of Frame) of a snapshot. The HMAC over main is checked first.

    Raises BackupKeyError when it does not verify and BackupFormatError when the snapshot
    cannot be read.
    """
    with open(metadata_path, 'rb') as handle:
        metadata = handle.read()
    mac_key, aes_key = message_keys(recovery_key, metadata)
    size = os.path.getsize(main_path)
    with open(main_path, 'rb') as handle:
        head = handle.read(len(_FORWARD_SECRECY_MAGIC))
    if head == _FORWARD_SECRECY_MAGIC:
        # Remote backups carry this prefix and need a token held by the server.
        raise BackupFormatError('main has a forward secrecy prefix')
    if size < _IV_SIZE + 16 + _MAC_SIZE:
        raise BackupFormatError('main is too short')
    _verify_mac(main_path, size, mac_key)
    frames = _frames(main_path, size, aes_key)
    first = next(frames, None)
    if first is None:
        raise BackupFormatError('main holds no frames')
    return parse('BackupInfo', first), (parse('Frame', data) for data in frames)


def media_file_name(plaintext_hash, local_key):
    """The file name of an attachment in the backup's files folder (MediaName.forLocalBackupFilename)."""
    return hashlib.sha256(plaintext_hash + local_key).hexdigest()


def decrypt_media(blob, local_key, size, plaintext_hash):
    """The attachment's bytes, or None unless its HMAC and plaintext SHA-256 both match.

    Blob = IV + AES-256-CBC + HMAC-SHA256; the 64-byte local key is the AES key then the HMAC
    key (AttachmentCipherOutputStream.kt L37-48). The plaintext is padded, so it is cut to the
    recorded size.
    """
    if len(local_key) != 64 or len(blob) < _IV_SIZE + 16 + _MAC_SIZE or (len(blob) - _IV_SIZE - _MAC_SIZE) % 16:
        return None
    expected = hmac.new(local_key[32:], blob[:-_MAC_SIZE], hashlib.sha256).digest()
    if not hmac.compare_digest(expected, blob[-_MAC_SIZE:]):
        return None
    plain = AES.new(local_key[:32], AES.MODE_CBC, iv=blob[:_IV_SIZE]).decrypt(blob[_IV_SIZE:-_MAC_SIZE])
    pad = plain[-1]
    if not 1 <= pad <= 16:
        return None
    plain = plain[:-pad][:size]
    return plain if hashlib.sha256(plain).digest() == plaintext_hash else None
