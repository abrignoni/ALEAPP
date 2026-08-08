__artifacts_v2__ = {
    "slack_messages": {
        "name": "Slack - Messages",
        "description": "Messages and thread replies from the Slack workspace store, with the "
                       "message text, the sending user, the conversation and any shared file "
                       "recovered from the app's image cache",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Slack",
        "notes": "Read from the messages and message_threads tables of the per-workspace store "
                 "databases/org_<team id>. Both tables are reported here, distinguished by the "
                 "Record Source column, so a thread reply appears alongside the message it "
                 "replies to.\n"
                 "The message text is taken from the text field of the message_json (or "
                 "message_blob) document on the row; the column itself holds the whole message as "
                 "returned by the server. Slack writes user mentions into that text as raw "
                 "<@Uxxxxxxxx> tokens; they are reported as stored rather than substituted, and "
                 "the Slack - Users artifact maps those ids to names.\n"
                 "Sender is resolved through users.id, and the conversation name through "
                 "conversation.conversation_id. Timestamps are the ts column, which is Unix epoch "
                 "seconds with a fractional part, held as text.\n"
                 "Subtype is reported as stored. Rows whose subtype is CHANNEL_JOIN and similar "
                 "are events the client recorded in the same table as ordinary messages, not "
                 "text the user typed.\n"
                 "Attachments are linked by recorded identity, not by correlation. Slack's image "
                 "cache is a DiskLruCache whose entry key is the SHA-256 of the requested URL, so "
                 "each URL held on the file record is hashed and looked up directly; the matching "
                 "cache body file is checked in as media. A file with no match means no cached "
                 "copy was found in the extraction, which does not establish that the file was "
                 "never on the device.",
        "paths": ('*/com.Slack/databases/org_*',
                  '*/com.Slack/cache/slack_image_cache/*/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Slack | 33 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation",
                "textColumn": "Message",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
                "mediaColumn": "Attachment",
            }
        },
    },
    "slack_conversations": {
        "name": "Slack - Conversations",
        "description": "Channels and direct message conversations in the Slack workspace store, "
                       "with the name, the kind, the membership flags and the last read marker",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Slack",
        "notes": "Read from the conversation table of databases/org_<team id>. The Kind column is "
                 "the stored type value, observed as PUBLIC and DM in the tested corpus.\n"
                 "Two column meanings come from the developers' own comments in the CREATE TABLE "
                 "text of this database: is_member is documented there as being set to NULL for "
                 "DMs and group DMs, so an empty Is Member on a DM row is the documented state "
                 "rather than missing data; and name_normalized_no_delimiter is documented as the "
                 "conversation name without delimiters such as - or _.\n"
                 "Last Read is the stored lastRead marker, a Slack message timestamp rather than "
                 "a wall-clock read time, and is reported converted from that value.",
        "paths": ('*/com.Slack/databases/org_*',),
        "output_types": "standard",
        "artifact_icon": "hash",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Slack | 8 rows",
        },
    },
    "slack_users": {
        "name": "Slack - Users",
        "description": "Members of the Slack workspace, with the handle, real name, email address, "
                       "time zone and the administrator, owner and bot flags",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Slack",
        "notes": "Read from the users table of databases/org_<team id>. Slack stores the profile "
                 "flattened into profile_ prefixed columns on this table, so the name, email, "
                 "title and phone are read directly rather than out of a JSON blob.\n"
                 "These are the workspace members the client had cached, which is not necessarily "
                 "every member of the workspace. The user ids reported here are the ones the "
                 "Slack - Messages artifact resolves senders and <@Uxxxxxxxx> mention tokens "
                 "against.",
        "paths": ('*/com.Slack/databases/org_*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Slack | 5 rows",
        },
    },
    "slack_files": {
        "name": "Slack - Files",
        "description": "Files shared in the Slack workspace, with the name, type, size, the "
                       "uploading user and the cached copy where one is present in the extraction",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Slack",
        "notes": "Read from the files table of databases/org_<team id>. Each row carries the "
                 "server's file record as JSON in file_blob, and the name, type, size and "
                 "timestamps are read from it.\n"
                 "The cached copy is linked by recorded identity rather than by correlation. The "
                 "app's image cache is a DiskLruCache whose entry key is the SHA-256 of the "
                 "requested URL, which is stated by the cache's own journal format and confirmed "
                 "against this corpus: every URL on the file record is hashed and looked up, and "
                 "the cache body file at that key is checked in as media. In the tested corpus "
                 "three files matched on the full-size url_private and one only on its thumb_720 "
                 "thumbnail, so the Matched On column records which URL produced the hit and "
                 "therefore whether the checked-in image is the full file or a thumbnail.\n"
                 "No match means no cached copy was found in the extraction. It does not "
                 "establish that the file was never on the device.",
        "paths": ('*/com.Slack/databases/org_*',
                  '*/com.Slack/cache/slack_image_cache/*/*'),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Slack | 4 rows",
        },
    },
    "slack_account": {
        "name": "Slack - Account",
        "description": "The signed-in Slack account and workspace, with the user id, the email "
                       "address, the team name and domain and the last accessed time",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Slack",
        "notes": "Read from the accounts table of databases/account_manager.\n"
                 "That table also holds token_encrypted and token_encrypted_ext1 columns. Those "
                 "are session credentials for the account, so they are deliberately not reported "
                 "by this artifact; reporting them into a case file would put a usable "
                 "authentication secret into the report.",
        "paths": ('*/com.Slack/databases/account_manager*',),
        "output_types": "standard",
        "artifact_icon": "user-check",
        "sample_data": {
            "pixel7a_a14": "Android 14 | Slack | 1 row",
        },
    },
}

import hashlib
import json
import os

from scripts.ilapfuncs import (artifact_processor, check_in_media, convert_unix_ts_to_utc,
                               does_table_exist_in_db, get_file_path, get_sqlite_db_records)

# The workspace store is named after the team id, so it cannot be matched by a
# fixed name. These tables identify it.
ORG_DB_TABLES = ('messages', 'conversation', 'users')


def _org_db_path(files_found):
    """databases/org_<team id> carries the workspace. Confirm by its tables rather
    than by name, because the name contains the team id."""
    for file_found in files_found:
        file_found = str(file_found)
        if '/databases/' not in file_found.replace(os.sep, '/'):
            continue
        if os.path.basename(file_found).endswith(('-wal', '-shm', '-journal')):
            continue
        if all(does_table_exist_in_db(file_found, table) for table in ORG_DB_TABLES):
            return file_found
    return None


def _cache_by_key(files_found):
    """The image cache is a DiskLruCache: <sha256 of the url>.0 holds the response
    metadata and .1 the body. Index the body files by their key."""
    cache = {}
    for file_found in files_found:
        file_found = str(file_found)
        name = os.path.basename(file_found)
        if name.endswith('.1') and 'slack_image_cache' in file_found.replace(os.sep, '/'):
            cache[name[:-2]] = file_found
    return cache


# The URL fields Slack puts on a file record, most complete first, so a full size
# match is preferred over a thumbnail.
FILE_URL_FIELDS = ('url_private', 'url_private_download', 'permalink',
                   'thumb_1024', 'thumb_800', 'thumb_720', 'thumb_360', 'thumb_80', 'thumb_64')


def _match_cached_file(blob, cache):
    """Return (media, matched_on) for a file record by hashing each recorded URL and
    looking the digest up in the cache index."""
    for field in FILE_URL_FIELDS:
        url = blob.get(field)
        if not isinstance(url, str) or not url:
            continue
        key = hashlib.sha256(url.encode('utf-8')).hexdigest()
        path = cache.get(key)
        if not path:
            continue
        media = check_in_media(path, blob.get('name') or key,
                               force_type=blob.get('mimetype'),
                               force_extension=blob.get('filetype')) or ''
        return media, field
    return '', ''


def _slack_ts(value):
    """Slack timestamps are Unix epoch seconds with a fractional part, held as text."""
    if value in (None, '', '0000000000.000000'):
        return ''
    try:
        return convert_unix_ts_to_utc(float(value))
    except (TypeError, ValueError):
        return str(value)


def _json_or_empty(value):
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _lookups(path):
    """Build {user id: (name, real name)} and {conversation id: (name, kind)}.

    For a DM the conversation's name_or_user column holds the other party's user
    id rather than a name, so resolve it through the users table."""
    users = {}
    if does_table_exist_in_db(path, 'users'):
        for record in get_sqlite_db_records(
                path, 'SELECT id, name, profile_real_name FROM users'):
            users[record[0]] = (record[1] or '', record[2] or '')
    conversations = {}
    if does_table_exist_in_db(path, 'conversation'):
        for record in get_sqlite_db_records(
                path, 'SELECT conversation_id, name_or_user, type FROM conversation'):
            label = record[1] or ''
            if label in users:
                name, real_name = users[label]
                label = real_name or name or label
            conversations[record[0]] = (label, record[2] or '')
    return users, conversations


def _resolve(users, value):
    """A stored user id shown on its own is not useful; give the name where known."""
    if value in users:
        name, real_name = users[value]
        return real_name or name or value
    return value or ''


@artifact_processor
def slack_messages(context):
    files_found = context.get_files_found()
    source_path = _org_db_path(files_found)
    data_list = []
    if not source_path:
        return _MESSAGE_HEADERS, data_list, ''

    users, conversations = _lookups(source_path)
    cache = _cache_by_key(files_found)

    files_by_id = {}
    if does_table_exist_in_db(source_path, 'files'):
        for record in get_sqlite_db_records(source_path, 'SELECT id, file_blob FROM files'):
            files_by_id[record[0]] = _json_or_empty(record[1])

    def emit(ts, channel_id, user_id, subtype, blob, thread_ts, origin):
        message = _json_or_empty(blob)
        name, real_name = users.get(user_id, ('', ''))
        conversation, kind = conversations.get(channel_id, ('', ''))
        attachment = ''
        attached_names = []
        for entry in message.get('files') or []:
            if not isinstance(entry, dict):
                continue
            record = files_by_id.get(entry.get('id')) or entry
            attached_names.append(record.get('name') or '')
            media, _ = _match_cached_file(record, cache)
            if media and not attachment:
                attachment = media
        reactions = message.get('reactions') or []
        data_list.append((
            _slack_ts(ts),
            conversation or channel_id,
            real_name or name or user_id,
            message.get('text', ''),
            attachment,
            ', '.join(n for n in attached_names if n),
            kind,
            subtype or message.get('subtype', '') or '',
            'Yes' if message.get('edited') else 'No',
            len(reactions),
            _slack_ts(thread_ts),
            origin,
            user_id or '',
            channel_id or '',
            ts or '',
        ))

    query = ('SELECT ts, channel_id, user_id, subtype, message_json, thread_ts '
             'FROM messages ORDER BY ts')
    for record in get_sqlite_db_records(source_path, query):
        emit(record[0], record[1], record[2], record[3], record[4], record[5], 'messages')

    if does_table_exist_in_db(source_path, 'message_threads'):
        query = ('SELECT ts, channel_id, event_sub_type, message_blob, thread_ts '
                 'FROM message_threads ORDER BY ts')
        for record in get_sqlite_db_records(source_path, query):
            message = _json_or_empty(record[3])
            emit(record[0], record[1], message.get('user'), record[2], record[3],
                 record[4], 'message_threads')

    data_list.sort(key=lambda row: str(row[0]))
    return _MESSAGE_HEADERS, data_list, source_path


_MESSAGE_HEADERS = (
    ('Timestamp', 'datetime'),
    'Conversation',
    'Sender Name',
    'Message',
    ('Attachment', 'media'),
    'Attachment Names',
    'Conversation Kind',
    'Subtype (as stored)',
    'Edited',
    'Reaction Count',
    ('Thread Parent Timestamp', 'datetime'),
    'Record Source',
    'Sender User ID',
    'Conversation ID',
    'Raw Timestamp (as stored)',
)


@artifact_processor
def slack_conversations(context):
    source_path = _org_db_path(context.get_files_found())
    data_list = []
    if not source_path:
        return _CONVERSATION_HEADERS, data_list, ''

    users, _ = _lookups(source_path)
    query = '''
    SELECT lastRead, name_or_user, type, is_member, is_open, is_starred, latest,
           name_normalized_no_delimiter, conversation_id, updated
    FROM conversation
    '''
    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            _slack_ts(record[0]),
            _resolve(users, record[1]),
            record[2],
            '' if record[3] is None else ('Yes' if record[3] else 'No'),
            'Yes' if record[4] else 'No',
            'Yes' if record[5] else 'No',
            _slack_ts(record[6]),
            record[7] or '',
            record[8],
            convert_unix_ts_to_utc(record[9]) if record[9] else '',
        ))

    return _CONVERSATION_HEADERS, data_list, source_path


_CONVERSATION_HEADERS = (
    ('Last Read', 'datetime'),
    'Name',
    'Kind',
    'Is Member',
    'Is Open',
    'Is Starred',
    ('Latest Message', 'datetime'),
    'Name Without Delimiters',
    'Conversation ID',
    ('Updated', 'datetime'),
)


@artifact_processor
def slack_users(context):
    source_path = _org_db_path(context.get_files_found())
    data_list = []
    if not source_path:
        return _USER_HEADERS, data_list, ''

    query = '''
    SELECT name, profile_real_name, profile_email, profile_phone, profile_title,
           tz, tz_label, is_admin, is_owner, is_primary_owner, is_bot, is_restricted,
           deleted, is_suspended, id, team_id, updated
    FROM users
    '''
    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            record[0] or '',
            record[1] or '',
            record[2] or '',
            record[3] or '',
            record[4] or '',
            record[5] or '',
            record[6] or '',
            'Yes' if record[7] else 'No',
            'Yes' if record[8] else 'No',
            'Yes' if record[9] else 'No',
            'Yes' if record[10] else 'No',
            'Yes' if record[11] else 'No',
            'Yes' if record[12] else 'No',
            'Yes' if record[13] else 'No',
            record[14],
            record[15],
            convert_unix_ts_to_utc(record[16]) if record[16] else '',
        ))

    return _USER_HEADERS, data_list, source_path


_USER_HEADERS = (
    'Handle',
    'Real Name',
    'Email',
    'Phone',
    'Title',
    'Time Zone',
    'Time Zone Label',
    'Is Admin',
    'Is Owner',
    'Is Primary Owner',
    'Is Bot',
    'Is Restricted',
    'Deleted',
    'Is Suspended',
    'User ID',
    'Team ID',
    ('Updated', 'datetime'),
)


@artifact_processor
def slack_files(context):
    files_found = context.get_files_found()
    source_path = _org_db_path(files_found)
    data_list = []
    if not source_path or not does_table_exist_in_db(source_path, 'files'):
        return _FILE_HEADERS, data_list, source_path or ''

    users, conversations = _lookups(source_path)
    cache = _cache_by_key(files_found)

    query = 'SELECT id, file_blob, user, channels, title, deleted FROM files'
    for record in get_sqlite_db_records(source_path, query):
        blob = _json_or_empty(record[1])
        media, matched_on = _match_cached_file(blob, cache)
        name, real_name = users.get(record[2], ('', ''))
        conversation = conversations.get(record[3], ('', ''))[0]
        data_list.append((
            convert_unix_ts_to_utc(int(blob['created'])) if str(blob.get('created', '')).isdigit() else '',
            blob.get('name', ''),
            media,
            matched_on,
            real_name or name or record[2] or '',
            conversation or record[3] or '',
            blob.get('mimetype', ''),
            blob.get('size', ''),
            'Yes' if record[5] else 'No',
            record[0],
        ))

    return _FILE_HEADERS, data_list, source_path


_FILE_HEADERS = (
    ('Created', 'datetime'),
    'File Name',
    ('Cached Copy', 'media'),
    'Matched On',
    'Uploaded By',
    'Conversation',
    'MIME Type',
    'Size',
    'Deleted',
    'File ID',
)


@artifact_processor
def slack_account(context):
    source_path = get_file_path(context.get_files_found(), 'account_manager')
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'accounts'):
        # token_encrypted and token_encrypted_ext1 are session credentials and are
        # deliberately not selected.
        query = '''
        SELECT last_accessed, email, user_id, team_id, team_domain, enterprise_id,
               environment_variant, secondary_auth_enabled, is_logged_out, created_ts, team_json
        FROM accounts
        '''
        for record in get_sqlite_db_records(source_path, query):
            team = _json_or_empty(record[10])
            data_list.append((
                convert_unix_ts_to_utc(record[0]) if record[0] else '',
                record[1],
                record[2],
                team.get('name', ''),
                record[4],
                record[3],
                record[5],
                record[6],
                'Yes' if record[7] else 'No',
                'Yes' if record[8] else 'No',
                convert_unix_ts_to_utc(record[9]) if record[9] else '',
            ))

    data_headers = (
        ('Last Accessed', 'datetime'),
        'Email',
        'User ID',
        'Team Name',
        'Team Domain',
        'Team ID',
        'Enterprise ID',
        'Environment',
        'Secondary Auth Enabled',
        'Is Logged Out',
        ('Created', 'datetime'),
    )
    return data_headers, data_list, source_path
