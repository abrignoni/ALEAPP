__artifacts_v2__ = {
    "wechat_messages": {
        "name": "WeChat - Messages",
        "description": "Rows from the message table of the decrypted EnMicroMsg.db, each a "
                       "message with its conversation, direction, time and content",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "sqlcipher3",
        "category": "WeChat",
        "notes": "com.tencent.mm stores its messages in EnMicroMsg.db, a SQLCipher database. The "
                 "key is the first seven characters of the lowercase MD5 of the device IMEI "
                 "joined to the account uin, which is the scheme this application has long used "
                 "and is documented across forensic references. The uin is read from the "
                 "application's own auth_info_key_prefs.xml, and the account directory name under "
                 "MicroMsg is the MD5 of the literal mm joined to that uin, which this artifact "
                 "checks so it opens each account's database with that account's key. The IMEI "
                 "is taken from the application's WLOGIN_DEVICE_INFO.xml, and the literal "
                 "1234567890ABCDEF is also tried, which is the value the application substitutes "
                 "for the IMEI on releases that can no longer read it; on the corpus below the "
                 "database opened with the literal rather than the stored IMEI. The database is "
                 "opened with the SQLCipher parameter set this application uses, page size 1024, "
                 "4000 KDF iterations and HMAC off, and a database that does not open with the "
                 "derived key fails outright rather than returning wrong rows. createTime is "
                 "Unix milliseconds. Is Send is the isSend column, 1 for a message the account "
                 "sent; the sender of a received message is the Talker, which is the other "
                 "party's WeChat id for a one to one conversation and the group id for a group. "
                 "Message Type (as stored) is the type column and is reported as stored, no "
                 "authoritative source for its full code list having been located; on the "
                 "corpus below type 1 was text and the other values carried XML documents. "
                 "Message is the readable form of the content column: for a plain text row it is "
                 "that text unchanged, and for a row holding a document it is the document's own "
                 "title and des elements, with Link taken from its url element. Those are the "
                 "document's own element names, read from it rather than inferred. Content "
                 "Element names the first element inside the root, so a document carrying no "
                 "title still says what kind it is. Content (as stored) keeps the raw value in "
                 "every case, so nothing the summary omits is lost. On the corpus below 587 of "
                 "602 rows produced a readable Message and 461 carried a Link; the 15 that "
                 "produced neither were the rows whose Content Element is img, which hold an "
                 "image reference and no text, so Message is empty on those by design rather "
                 "than through a failure to parse. A document that does not parse is logged and "
                 "leaves Message, Content Element and Link empty, with the stored column as the "
                 "only record for the row. "
                 "Media, Attachment File, Attachment Format and Attachment Size are resolved "
                 "from names the database itself recorded for the row, never by matching a file "
                 "on size or time. An image row points at its thumbnail through the imgPath "
                 "column, a voice row is joined to voiceinfo on the message id to get its file "
                 "name, and a sticker row names its file directly; each name is then looked for "
                 "only inside that row's own account container, so two accounts holding a file "
                 "of the same name cannot be confused. Media is checked in only where the "
                 "resolved thumbnail is a real image by its leading bytes. On the corpus below "
                 "all 15 image rows resolved to a thumbnail and every one was a plain JPEG, so "
                 "15 rows carry a rendered image; 21 rows resolved an attachment. Attachment "
                 "Format is read from the file's leading bytes, and the values seen were the "
                 "reason the other files are not rendered: the full size images are a wxgf "
                 "container, the voice files carry a SILK header despite their amr extension, "
                 "and the two sticker files matched no known signature. Those three are reported "
                 "by name, format and size so an examiner knows the file exists and where, "
                 "without this artifact claiming to have decoded it. Image Path (as stored) "
                 "keeps the raw imgPath token."
                 "points to where it has one.",
        "paths": ('*/com.tencent.mm/MicroMsg/*/EnMicroMsg.db*',
                  '*/com.tencent.mm/shared_prefs/auth_info_key_prefs.xml',
                  '*/com.tencent.mm/shared_prefs/WLOGIN_DEVICE_INFO.xml',
                  '*/com.tencent.mm/MicroMsg/*/image2/*',
                  '*/com.tencent.mm/MicroMsg/*/voice2/*',
                  '*/com.tencent.mm/MicroMsg/*/emoji/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Talker",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Time",
                "senderColumn": "Talker",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Media",
            }
        },
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | com.tencent.mm | 602 rows",
        },
    },
    "wechat_contacts": {
        "name": "WeChat - Contacts",
        "description": "Rows from the rcontact table of the decrypted EnMicroMsg.db, each a "
                       "contact the account holds, with the WeChat id, nickname and any remark",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "sqlcipher3",
        "category": "WeChat",
        "notes": "rcontact holds every contact record the account keeps, which includes the contacts added on "
                 "the device and also the service and official accounts the application ships. Type (as "
                 "stored) and Verify Flag (as stored) are the columns that separate those, and both are "
                 "reported as stored so the distinction is preserved rather than asserted: no authoritative "
                 "source for their full code lists was located, and on the corpus below most rows carried a "
                 "type value that the service and official accounts share. WeChat ID is the username column, "
                 "Alias is the id the user set for themselves where present, Nickname is the display name and "
                 "Remark is the name this account gave the contact. conRemark being populated is a sign the "
                 "user interacted with that contact deliberately. createTime is Unix milliseconds where "
                 "present.",
        "paths": ('*/com.tencent.mm/MicroMsg/*/EnMicroMsg.db*',
                  '*/com.tencent.mm/shared_prefs/auth_info_key_prefs.xml',
                  '*/com.tencent.mm/shared_prefs/WLOGIN_DEVICE_INFO.xml'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | com.tencent.mm | 32 rows",
        },
    },
    "wechat_conversations": {
        "name": "WeChat - Conversations",
        "description": "Rows from the rconversation table of the decrypted EnMicroMsg.db, each a "
                       "conversation the account holds, with its message count and the time and "
                       "digest of its last message",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "sqlcipher3",
        "category": "WeChat",
        "notes": "rconversation is one row per conversation. Username is the other party's "
                 "WeChat id or the group id, Message Count is the count the application records "
                 "for that conversation, Unread Count is what it recorded as unread, and Last "
                 "Message Time is conversationTime as Unix milliseconds. Digest is the preview "
                 "text of the last message the application stored for the conversation list, so "
                 "it can hold the text of a message that the message table also carries. Which "
                 "conversations have the highest message counts is the quickest guide to where "
                 "the activity is.",
        "paths": ('*/com.tencent.mm/MicroMsg/*/EnMicroMsg.db*',
                  '*/com.tencent.mm/shared_prefs/auth_info_key_prefs.xml',
                  '*/com.tencent.mm/shared_prefs/WLOGIN_DEVICE_INFO.xml'),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | com.tencent.mm | 7 rows",
        },
    },
    "wechat_account": {
        "name": "WeChat - Account",
        "description": "The signed-in account, read from the userinfo table of the decrypted "
                       "EnMicroMsg.db and the account's own preference files",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "sqlcipher3",
        "category": "WeChat",
        "notes": "userinfo is a key and value table holding the signed-in account's own record. "
                 "The rows are reported with the numeric id the table uses and the value as "
                 "stored: on the corpus below id 2 held the account's WeChat id, id 4 the "
                 "display name and id 6 the bound telephone number, which are the fields an "
                 "examiner would want, but the id to field mapping is the application's own and "
                 "is not expanded here beyond reporting the id, since no authoritative source "
                 "for the full list was located. The account uin, taken from "
                 "auth_info_key_prefs.xml, is reported alongside so the record can be tied to "
                 "the database directory it came from.",
        "paths": ('*/com.tencent.mm/MicroMsg/*/EnMicroMsg.db*',
                  '*/com.tencent.mm/shared_prefs/auth_info_key_prefs.xml',
                  '*/com.tencent.mm/shared_prefs/WLOGIN_DEVICE_INFO.xml'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | com.tencent.mm | 97 rows",
        },
    },
}

import hashlib
import os
import xml.etree.ElementTree as ET

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    logfunc,
)

try:
    from sqlcipher3 import dbapi2 as sqlcipher
    _SQLCIPHER_AVAILABLE = True
except ImportError as _sqlcipher_import_error:
    # Guarded so a missing sqlcipher3 install disables only these artifacts rather
    # than aborting the import of every ALEAPP artifact, the pattern threema.py uses.
    _SQLCIPHER_AVAILABLE = False
    logfunc(f'WeChat: sqlcipher3 not available, encrypted-database artifacts '
            f'disabled: {_sqlcipher_import_error}')

SIDECARS = ('-wal', '-shm', '-journal')

# The parameter set this application's EnMicroMsg.db uses.
_CIPHER_PRAGMAS = (
    'PRAGMA cipher_page_size = 1024;',
    'PRAGMA kdf_iter = 4000;',
    'PRAGMA cipher_use_hmac = OFF;',
    'PRAGMA cipher_hmac_algorithm = HMAC_SHA1;',
    'PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1;',
)

# Substituted for the device IMEI by releases that can no longer read it.
_FALLBACK_IMEI = '1234567890ABCDEF'


def _pref_value(files_found, filename, name):
    """A named string entry from one of the app's preference files."""
    for file_found in files_found:
        if os.path.basename(str(file_found)) != filename:
            continue
        try:
            root = ET.parse(str(file_found)).getroot()
        except (OSError, ET.ParseError) as error:
            logfunc(f'WeChat: could not parse {file_found}: {error}')
            continue
        for entry in root:
            if entry.get('name') == name:
                return entry.text if entry.tag == 'string' else entry.get('value', '')
    return ''


def _db_key(imei, uin):
    """The EnMicroMsg.db key: first 7 chars of lowercase md5(imei + uin)."""
    return hashlib.md5(f'{imei}{uin}'.encode()).hexdigest()[:7]


def _open_database(db_path, uin, imeis):
    """Open EnMicroMsg.db with the key derived for this account, or None."""
    directory_ok = os.path.basename(os.path.dirname(db_path)) == \
        hashlib.md5(f'mm{uin}'.encode()).hexdigest()
    if not directory_ok:
        logfunc(f'WeChat: {db_path} is not the directory for uin {uin}, skipping')
        return None
    for imei in imeis:
        if not imei:
            continue
        connection = None
        try:
            connection = sqlcipher.connect(  # pylint: disable=no-member
                f'file:{db_path}?mode=ro', uri=True)
            cursor = connection.cursor()
            cursor.execute(f"PRAGMA key = '{_db_key(imei, uin)}';")
            for pragma in _CIPHER_PRAGMAS:
                cursor.execute(pragma)
            cursor.execute('SELECT count(*) FROM sqlite_master;').fetchone()
            return connection
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'WeChat: {os.path.basename(db_path)} did not open with the key '
                    f'from IMEI {imei!r}: {error}')
            if connection is not None:
                try:
                    connection.close()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
    return None


def _connections(context):
    """Yield (connection, uin, db path) for each account database opened."""
    files_found = [str(f) for f in unique_files(context)]
    if not _SQLCIPHER_AVAILABLE:
        return
    uin = _pref_value(files_found, 'auth_info_key_prefs.xml', '_auth_uin')
    if not uin:
        uin = _pref_value(files_found, 'system_config_prefs.xml', 'default_uin')
    imei = _pref_value(files_found, 'WLOGIN_DEVICE_INFO.xml', 'imei')
    imeis = [imei, _FALLBACK_IMEI]
    if not uin:
        logfunc('WeChat: no account uin found in the preference files, cannot derive a key')
        return
    for db_path in files_found:
        if os.path.basename(db_path) != 'EnMicroMsg.db':
            continue
        connection = _open_database(db_path, uin, imeis)
        if connection is not None:
            yield connection, uin, db_path


def _read_head(path, length=16):
    try:
        with open(path, 'rb') as handle:
            return handle.read(length)
    except OSError as error:
        logfunc(f'WeChat: could not read {path}: {error}')
        return b''


def _query(context, sql, keep_path=False):
    """(rows, source paths) from every account database, closing each after.

    With keep_path the database each row came from is carried alongside it, so a
    caller resolving media can look only inside that row's own account container.
    """
    data_rows, source_paths = [], []
    for connection, uin, db_path in _connections(context):
        try:
            rows = connection.cursor().execute(sql).fetchall()
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'WeChat: query failed on {db_path}: {error}')
            rows = []
        finally:
            connection.close()
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            data_rows.append((row, uin, db_path) if keep_path else (row, uin))
    return data_rows, source_paths



# Leading-byte signatures, checked because the name a message points to does not
# establish the format of the bytes behind it.
_SIGNATURES = (
    (b'\xff\xd8\xff', 'JPEG'),
    (b'\x89PNG\r\n\x1a\n', 'PNG'),
    (b'GIF87a', 'GIF'),
    (b'GIF89a', 'GIF'),
    (b'RIFF', 'RIFF container'),
    (b'wxgf', 'wxgf (WeChat image container)'),
    (b'\x02#!SILK_V3', 'SILK audio'),
    (b'#!SILK_V3', 'SILK audio'),
    (b'#!AMR', 'AMR audio'),
)


def _sniff(head):
    """A format label read from a file's leading bytes, or '' if unrecognised."""
    for magic, label in _SIGNATURES:
        if head.startswith(magic):
            return label
    return ''


def _media_index(files_found):
    """{(container, basename): path} for the media the seeker returned.

    Keyed on the account container as well as the name, so two accounts holding a
    file of the same name are never confused for one another.
    """
    index = {}
    for file_found in files_found:
        if os.path.isdir(file_found):
            continue
        parts = file_found.replace('\\', '/').split('/')
        container = ''
        for position in range(len(parts) - 1, -1, -1):
            if parts[position] == 'com.tencent.mm':
                container = '/'.join(parts[:position + 1])
                break
        index.setdefault((container, os.path.basename(file_found)), file_found)
    return index


def _container_of(path):
    parts = str(path).replace('\\', '/').split('/')
    for position in range(len(parts) - 1, -1, -1):
        if parts[position] == 'com.tencent.mm':
            return '/'.join(parts[:position + 1])
    return ''

def _readable_content(content):
    """(readable text, content element, link) for a message's content column.

    A plain text message is returned unchanged. Where the column holds a document,
    the values are read from that document's own element names rather than being
    inferred: title and des for the readable text, url for the link, and the name
    of the first element inside the root for the content element, so a document
    with no title still says what kind of document it is. A document that does not
    parse yields empty values and is logged, leaving the stored column as the only
    record for that row.
    """
    if not content:
        return '', '', ''
    stripped = content.lstrip()
    if not stripped.startswith('<'):
        return content, '', ''
    try:
        root = ET.fromstring(stripped)
    except ET.ParseError as error:
        logfunc(f'WeChat: message content did not parse as XML: {error}')
        return '', '', ''
    first = next(iter(root), None)
    element = first.tag if first is not None else root.tag

    def value(tag):
        node = root.find(f'./{element}/{tag}')
        if node is None:
            node = root.find(f'.//{tag}')
        return (node.text or '').strip() if node is not None and node.text else ''

    title, description, link = value('title'), value('des'), value('url')
    if title and description:
        readable = f'{title} - {description}'
    else:
        readable = title or description
    return readable, element, link

@artifact_processor
def wechat_messages(context):
    data_list = []
    files_found = [str(f) for f in unique_files(context)]
    index = _media_index(files_found)
    voice_names = {}
    for connection, _, db_path in _connections(context):
        try:
            for local_id, file_name in connection.cursor().execute(
                    'SELECT MsgLocalId, FileName FROM voiceinfo'):
                voice_names[(_container_of(db_path), local_id)] = file_name
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'WeChat: could not read voiceinfo from {db_path}: {error}')
        finally:
            connection.close()

    rows, source_paths = _query(context, '''
        SELECT createTime, isSend, talker, type, content, imgPath, status, msgId
        FROM message ORDER BY createTime
    ''', keep_path=True)
    for row, _, db_path in rows:
        created, is_send, talker, kind, content, img_path, status, msg_id = row
        readable, element, link = _readable_content(content)
        container = _container_of(db_path)

        # Every lookup below uses a name the database itself recorded for the row,
        # never a match on size or time.
        thumb = full = attachment = ''
        token = (img_path or '').split('://')[-1]
        if kind == 3 and token:
            thumb = index.get((container, token), '')
            full = index.get((container, f"{token.replace('th_', '', 1)}.jpg"), '')
        elif kind == 47 and token:
            attachment = index.get((container, token), '')
        elif kind == 34:
            name = voice_names.get((container, msg_id))
            if name:
                attachment = index.get((container, f'msg_{name}.amr'), '')
        attachment = attachment or full

        media = ''
        if thumb:
            head = _read_head(thumb)
            if _sniff(head) in ('JPEG', 'PNG', 'GIF'):
                media = check_in_media(thumb, os.path.basename(thumb))

        if attachment:
            attach_name = os.path.basename(attachment)
            attach_format = _sniff(_read_head(attachment))
            try:
                attach_size = os.path.getsize(attachment)
            except OSError:
                attach_size = ''
        else:
            attach_name = attach_format = attach_size = ''

        data_list.append((
            convert_unix_ts_to_utc(created / 1000) if created else '',
            'Outgoing' if is_send == 1 else 'Incoming',
            talker or '',
            readable,
            media,
            is_send if is_send is not None else '',
            kind if kind is not None else '',
            element,
            link,
            attach_name,
            attach_format,
            attach_size,
            img_path or '',
            status if status is not None else '',
            msg_id if msg_id is not None else '',
            content or '',
        ))
    data_headers = (
        ('Message Time', 'datetime'),
        'Direction',
        'Talker',
        'Message',
        ('Media', 'media'),
        'Is Send',
        'Message Type (as stored)',
        'Content Element',
        'Link',
        'Attachment File',
        'Attachment Format',
        'Attachment Size',
        'Image Path (as stored)',
        'Status (as stored)',
        'Message ID',
        'Content (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def wechat_contacts(context):
    data_list = []
    rows, source_paths = _query(context, '''
        SELECT username, alias, nickname, conRemark, type, verifyFlag, createTime
        FROM rcontact ORDER BY nickname
    ''')
    for row, _ in rows:
        username, alias, nickname, remark, kind, verify, created = row
        data_list.append((
            username or '',
            alias or '',
            nickname or '',
            remark or '',
            kind if kind is not None else '',
            verify if verify is not None else '',
            convert_unix_ts_to_utc(created / 1000) if created else '',
        ))
    data_headers = (
        'WeChat ID',
        'Alias',
        'Nickname',
        'Remark',
        'Type (as stored)',
        'Verify Flag (as stored)',
        ('Created', 'datetime'),
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def wechat_conversations(context):
    data_list = []
    rows, source_paths = _query(context, '''
        SELECT conversationTime, username, msgCount, unReadCount, digest, digestUser, status
        FROM rconversation ORDER BY conversationTime DESC
    ''')
    for row, _ in rows:
        conv_time, username, count, unread, digest, digest_user, status = row
        data_list.append((
            convert_unix_ts_to_utc(conv_time / 1000) if conv_time else '',
            username or '',
            count if count is not None else '',
            unread if unread is not None else '',
            digest or '',
            digest_user or '',
            status if status is not None else '',
        ))
    data_headers = (
        ('Last Message Time', 'datetime'),
        'Username',
        'Message Count',
        'Unread Count',
        'Digest',
        'Digest User',
        'Status (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def wechat_account(context):
    data_list = []
    rows, source_paths = _query(context, 'SELECT id, value FROM userinfo ORDER BY id')
    for row, uin in rows:
        row_id, value = row
        data_list.append((
            row_id if row_id is not None else '',
            value or '',
            uin,
        ))
    data_headers = ('Field ID (as stored)', 'Value', 'Account UIN')
    return data_headers, data_list, '\n'.join(source_paths)
