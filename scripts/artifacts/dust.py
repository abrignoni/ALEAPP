__artifacts_v2__ = {
    "dust_conversations": {
        "name": "Dust - Conversations",
        "description": "Rows from the Chat table of the app's room-db, each naming a "
                       "conversation, the account it belongs to, the other account in it and "
                       "the time the row was last updated",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Dust",
        "notes": "com.radicalapps.cyberdust is a messaging app whose messages are not retained "
                 "on the device: room-db has no message table, and its Blasts, Contacts and "
                 "messageKeyPairs tables held no rows on any of the three corpora below. What "
                 "the Chat table does keep is one row per conversation carrying the other "
                 "party's display name in title, that party's account identifier in "
                 "otherAccountId, and updatedDate, so a conversation and its participants "
                 "survive on the device even though its messages do not. updatedDate is Unix "
                 "milliseconds; what event sets it was not established, so the column is named "
                 "for the field rather than described as a last message time. Subtitle (as "
                 "stored) held the string 'all caught up' on every row of all three corpora, "
                 "which is the app's own status wording and not message content; it is reported "
                 "as stored so a row carrying something else is not hidden. Muted, Blocked and "
                 "Missed Message are the schema's own 0 or 1 columns and were 0 on every row "
                 "below. Type was 0 on every row below and no source for the code list was "
                 "located, so it is reported as stored. The whole database lives in its "
                 "write-ahead log on these extractions: read without room-db-wal the file "
                 "reports no tables at all, so the sidecars are matched by the path pattern and "
                 "are required.",
        "paths": ('*/com.radicalapps.cyberdust/databases/room-db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.radicalapps.cyberdust | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | com.radicalapps.cyberdust | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.radicalapps.cyberdust | 1 row",
        },
    },
    "dust_key_bundles": {
        "name": "Dust - Conversation Key Bundles",
        "description": "Rows from the KeyBundles table, each pairing an account and a "
                       "conversation with the device identifiers the stored key material names",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Dust",
        "notes": "recipientKeyModels is a JSON object whose keys are device identifiers and "
                 "whose values carry an accountId and a deviceId for each. Device Identifiers "
                 "lists those keys and Accounts In Bundle lists the distinct accountId values "
                 "inside, so a conversation's participating devices are readable without "
                 "reading the key material itself. Key Material (as stored) holds the whole "
                 "JSON, which includes the stored public key values; this artifact does not "
                 "interpret them and recovering message content from them was not attempted and "
                 "is not implied. One row was present on each of the three corpora below.",
        "paths": ('*/com.radicalapps.cyberdust/databases/room-db*',),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.radicalapps.cyberdust | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.radicalapps.cyberdust | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.radicalapps.cyberdust | 1 row",
        },
    },
    "dust_known_accounts": {
        "name": "Dust - Known Accounts",
        "description": "Rows from the UserPhotoUrls table, each an account identifier the app "
                       "held an avatar record for and the time that record was updated",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Dust",
        "notes": "The table records one row per account identifier the app kept an avatar entry "
                 "for, which on the corpora below included the signed-in account and the other "
                 "party of each conversation. It is reported separately from the Chat table "
                 "because it carries its own updatedTime and can name an account that no longer "
                 "has a conversation row. updatedTime is Unix milliseconds. Photo URL was an "
                 "empty string on every row of all three corpora, so no avatar address was "
                 "recorded and none is resolved to a file; the column is kept so a populated "
                 "value on another extraction is not dropped.",
        "paths": ('*/com.radicalapps.cyberdust/databases/room-db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.radicalapps.cyberdust | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | com.radicalapps.cyberdust | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.radicalapps.cyberdust | 1 row",
        },
    },
}

import json
import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, logfunc

SIDECARS = ('-wal', '-shm', '-journal')


def _databases(context):
    """The room-db files, storage views collapsed and sidecars dropped.

    The sidecars are matched by the path pattern so the seeker copies them and
    SQLite can apply the log, but they are never opened directly: on these
    extractions the database file alone reports no tables.
    """
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or file_found.endswith(SIDECARS):
            continue
        if os.path.basename(file_found) == 'room-db':
            found.append(file_found)
    return found


@artifact_processor
def dust_conversations(context):
    data_list = []
    source_paths = []

    for db_path in _databases(context):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT updatedDate, title, otherAccountId, accountId, conversationId, subtitle,
                   muted, isBlocked, missedMessage, count, type
            FROM Chat ORDER BY updatedDate DESC
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            (updated, title, other_account, account, conversation, subtitle,
             muted, blocked, missed, count, kind) = row
            data_list.append((
                convert_unix_ts_to_utc(updated / 1000) if updated else '',
                title or '',
                other_account or '',
                account or '',
                conversation or '',
                subtitle or '',
                muted if muted is not None else '',
                blocked if blocked is not None else '',
                missed if missed is not None else '',
                count if count is not None else '',
                kind if kind is not None else '',
            ))

    data_headers = (
        ('Updated Date', 'datetime'),
        'Other Party Display Name',
        'Other Account ID',
        'Account ID',
        'Conversation ID',
        'Subtitle (as stored)',
        'Muted',
        'Blocked',
        'Missed Message',
        'Count',
        'Type (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def dust_key_bundles(context):
    data_list = []
    source_paths = []

    for db_path in _databases(context):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT accountId, conversationId, recipientKeyModels FROM KeyBundles
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for account, conversation, material in rows:
            devices, accounts = [], []
            if material:
                try:
                    bundle = json.loads(material)
                except (TypeError, ValueError) as error:
                    logfunc(f'Dust: recipientKeyModels did not parse as JSON: {error}')
                    bundle = {}
                for device_id, entry in (bundle or {}).items():
                    devices.append(device_id)
                    if isinstance(entry, dict) and entry.get('accountId'):
                        accounts.append(entry['accountId'])
            data_list.append((
                account or '',
                conversation or '',
                ', '.join(devices),
                ', '.join(sorted(set(accounts))),
                material or '',
            ))

    data_headers = (
        'Account ID',
        'Conversation ID',
        'Device Identifiers',
        'Accounts In Bundle',
        'Key Material (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def dust_known_accounts(context):
    data_list = []
    source_paths = []

    for db_path in _databases(context):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT updatedTime, id, photoUrl FROM UserPhotoUrls ORDER BY updatedTime
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for updated, account_id, photo_url in rows:
            data_list.append((
                convert_unix_ts_to_utc(updated / 1000) if updated else '',
                account_id or '',
                photo_url or '',
            ))

    data_headers = (
        ('Updated Time', 'datetime'),
        'Account ID',
        'Photo URL',
    )
    return data_headers, data_list, '\n'.join(source_paths)
