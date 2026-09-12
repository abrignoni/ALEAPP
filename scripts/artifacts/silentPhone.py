__artifacts_v2__ = {
    "silentphone_zrtp_peers": {
        "name": "Silent Phone - ZRTP Peer Identities",
        "description": "Rows from the ZRTP identity store, pairing this device's own ZID with "
                       "each remote party it has established a secure media session with, and "
                       "the name recorded for that party",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Silent Phone",
        "notes": "com.silentcircle.silentphone keeps its messages in encrypted "
                 "databases that this artifact does not open. Those are repo_store_enc.db, a "
                 "per-account file ending _axo_store_enc.db, message_indexes.db and "
                 "sc_keystore.db, all in the package databases directory, and none carries a "
                 "readable SQLite header. The scheme is SQLCipher, which the application's own "
                 "dialer preference file records in an entry named sqlcipher_db_version. The "
                 "passphrase is not present in any readable store in the package: every entry "
                 "of all six preference files the application writes was read and none holds "
                 "key material, and there is no fixed key to try. The contents of those four "
                 "files were therefore not recovered, which is a boundary of this artifact "
                 "rather than a property of the data; closing it would need an extraction "
                 "carrying the key material. files/zids_sqlite.db, which this artifact does "
                 "read, is plain SQLite. "
                 "ZRTP is "
                 "the key agreement used for the app's media sessions, and each party is "
                 "identified by a ZID. zrtpIdOwn holds this device's ZID, zrtpIdRemote holds one "
                 "row per remote ZID it has cached retained secrets for, and zrtpNames maps a "
                 "remote ZID to a name. The three are joined here on the remote and local ZID "
                 "pair, so a row records that this device holds ZRTP state for that party. "
                 "Secure Since and Last Update are Unix seconds. Peer Name is the string the app "
                 "stored: on one corpus below it was a bare account name and on the other a SIP "
                 "address in angle brackets, and both are reported as stored. RS1, RS2 and MITM "
                 "Key hold 32 byte retained secrets; the artifact reports only whether each is "
                 "present and non-zero rather than the bytes, since the values are key material "
                 "and their presence is what indicates a prior session. Flags and Presh Counter "
                 "are reported as stored, no source for their meanings having been located. One "
                 "remote party was present on each of the two corpora below.",
        "paths": ('*/com.silentcircle.silentphone/files/zids_sqlite.db*',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.silentcircle.silentphone | 1 row",
            "pixel7a_a14": "Android 14 | com.silentcircle.silentphone | 1 row",
        },
    },
    "silentphone_account": {
        "name": "Silent Phone - Account and Settings",
        "description": "Entries from the application's own preference files, holding the "
                       "provisioned account, its assigned number, the subscription state, the "
                       "provider's data retention flags and the registered device identifiers",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Silent Phone",
        "notes": "Every entry from the preference files the application itself writes is "
                 "reported, so entries added by later versions still appear and nothing is "
                 "filtered on a guess at which names matter. Those are the files named "
                 "com.silentcircle.* together with uuid_store.xml; the package's other "
                 "shared_prefs file belongs to Google Play services and is not read. The "
                 "provisioning file carries the account identity, including a user id, a display "
                 "name, an assigned telephone number where one is present, the subscription "
                 "state and expiry, and a set of entries whose names begin DATA_RETENTION_, "
                 "which record what the service provider retains for that account rather than "
                 "what is on the device. Those flags are reported as stored and their individual "
                 "meanings are not expanded, no source for the code list having been located. "
                 "spa_device_id_prod ends in thirteen digits consistent with a Unix millisecond "
                 "value, but what event it records is not established, so it is reported as "
                 "stored and no date is derived from it. Store names the file each row came "
                 "from.",
        "paths": ('*/com.silentcircle.silentphone/shared_prefs/*.xml',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.silentcircle.silentphone | 63 rows",
            "pixel7a_a14": "Android 14 | com.silentcircle.silentphone | 69 rows",
        },
    },
    "silentphone_conversation_objects": {
        "name": "Silent Phone - Conversation Objects",
        "description": "Files cached under the app's object store, whose path names the two "
                       "parties to a conversation and the identifier of the item the object "
                       "belongs to",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Silent Phone",
        "notes": "The app caches conversation attachments under cache/objects in a directory "
                 "named for the two parties joined by an underscore, three colons and an underscore, "
                 "then a directory named "
                 "for an identifier, then the object itself. The object bytes are encrypted and "
                 "carry no recognised signature, so no media is checked in and nothing is "
                 "decoded here; what the artifact reports is the path, which names the "
                 "correspondents and survives even though the message store does not open. "
                 "Participant 1 and Participant 2 are the two names in the directory as stored, "
                 "split on that separator. The seeker replaces a colon when it stages a file, so the "
                 "same directory reaches this artifact as five underscores and both "
                 "spellings are matched. On both corpora below Participant 1 matched the "
                 "user id "
                 "in the account preference file of the same extraction, so the first name is "
                 "the local account on those images; that is an observation about two images "
                 "rather than an established rule, which is why the columns are numbered rather "
                 "than labelled local and remote. Size is the object byte size. Item Identifier "
                 "and Conversation Folder (as stored) each held one value across the rows of a "
                 "corpus below, because each image carried a single conversation holding a single "
                 "item; both are kept because they are what separates conversations and items on a "
                 "device holding more than one. Three objects "
                 "in one conversation were present on one corpus and two in one conversation on "
                 "the other.",
        "paths": ('*/com.silentcircle.silentphone/cache/objects/*',),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.silentcircle.silentphone | 3 rows",
            "pixel7a_a14": "Android 14 | com.silentcircle.silentphone | 2 rows",
        },
    },
}

import os
import re
import xml.etree.ElementTree as ET

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    get_sqlite_db_records,
    logfunc,
)

SIDECARS = ('-wal', '-shm', '-journal')

# The two parties in an object cache directory are joined by an underscore, three
# colons and an underscore. The seeker replaces a colon when it stages a file, so
# the same directory reaches an artifact as five underscores; both spellings are
# matched here rather than only the one the evidence uses.
PARTICIPANT_SEPARATOR = re.compile(r'_(?::::|___)_')


def _files(context, keep):
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or file_found.endswith(SIDECARS):
            continue
        if keep(file_found):
            found.append(file_found)
    return found


def _present(value):
    """Whether a retained secret column holds bytes that are not all zero."""
    if not value:
        return 'No'
    if isinstance(value, (bytes, bytearray)):
        return 'Yes' if any(value) else 'No (all zero)'
    return 'Yes'


@artifact_processor
def silentphone_zrtp_peers(context):
    data_list = []
    source_paths = []

    for db_path in _files(context, lambda p: os.path.basename(p) == 'zids_sqlite.db'):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT r.secureSince, n.lastUpdate, n.name, r.remoteZid, r.localZid, r.flags,
                   r.rs1, r.rs2, r.mitmKey, r.preshCounter, o.accountInfo
            FROM zrtpIdRemote r
            LEFT JOIN zrtpNames n
                   ON n.remoteZid = r.remoteZid AND n.localZid = r.localZid
            LEFT JOIN zrtpIdOwn o ON o.localZid = r.localZid
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            (secure_since, last_update, name, remote_zid, local_zid, flags,
             rs1, rs2, mitm, presh, account_info) = row
            data_list.append((
                convert_unix_ts_to_utc(secure_since) if secure_since else '',
                convert_unix_ts_to_utc(last_update) if last_update else '',
                name or '',
                remote_zid or '',
                local_zid or '',
                account_info or '',
                _present(rs1),
                _present(rs2),
                _present(mitm),
                flags if flags is not None else '',
                presh if presh is not None else '',
            ))

    data_headers = (
        ('Secure Since', 'datetime'),
        ('Name Last Update', 'datetime'),
        'Peer Name (as stored)',
        'Remote ZID',
        'Local ZID',
        'Local Account Info',
        'RS1 Retained Secret Present',
        'RS2 Retained Secret Present',
        'MITM Key Present',
        'Flags (as stored)',
        'Presh Counter (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def silentphone_account(context):
    data_list = []
    source_paths = []

    def app_owned(path):
        name = os.path.basename(path)
        return name.startswith('com.silentcircle') or name == 'uuid_store.xml'

    for prefs_path in _files(context, app_owned):
        try:
            root = ET.parse(prefs_path).getroot()
        except (OSError, ET.ParseError) as error:
            logfunc(f'Silent Phone: could not parse {prefs_path}: {error}')
            continue
        source_paths.append(context.get_relative_path(prefs_path))
        store = os.path.basename(prefs_path)
        for entry in root:
            name = entry.get('name', '')
            if entry.tag == 'set':
                value = ', '.join((child.text or '') for child in entry)
            elif entry.tag == 'string':
                value = entry.text or ''
            else:
                value = entry.get('value', '')
            data_list.append((name, value, entry.tag, store))

    data_list.sort(key=lambda row: (row[3], row[0]))
    data_headers = ('Preference', 'Value (as stored)', 'Stored Type', 'Store')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def silentphone_conversation_objects(context):
    data_list = []
    source_paths = []

    for file_found in _files(context, lambda p: '/cache/objects/' in
                             str(p).replace('\\', '/')):
        relative = context.get_relative_path(file_found).replace('\\', '/')
        tail = relative.split('/cache/objects/', 1)
        if len(tail) != 2:
            continue
        parts = tail[1].split('/')
        folder = parts[0]
        halves = PARTICIPANT_SEPARATOR.split(folder, 1)
        first = halves[0]
        second = halves[1] if len(halves) > 1 else ''
        try:
            size = os.path.getsize(file_found)
        except OSError as error:
            logfunc(f'Silent Phone: could not size {file_found}: {error}')
            continue
        source_paths.append(relative)
        data_list.append((
            first,
            second,
            parts[1] if len(parts) > 2 else '',
            parts[-1],
            size,
            folder,
        ))

    data_list.sort(key=lambda row: (row[5], row[2], row[3]))
    data_headers = (
        'Participant 1',
        'Participant 2',
        'Item Identifier',
        'Object',
        'Size',
        'Conversation Folder (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)
