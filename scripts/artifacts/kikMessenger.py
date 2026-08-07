__artifacts_v2__ = {
    "kik_messages": {
        "name": "Kik Messages",
        "description": "Messages from the Kik messagesTable, with the conversation partner, the "
                       "body, and the attachment metadata held against the message content id",
        "author": "",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "Kik",
        "notes": "Recent versions name the databases with the account core id, for example "
                 "<core id>.kikDatabase.db, so the paths allow for a prefix. Direction is taken "
                 "from the was_me column, which published Kik research describes as marking the "
                 "party that sent the message. Read state is reported as the stored integer.",
        "paths": ('*/kik.android/databases/*kikDatabase.db*',
                  '*/kik.android/databases/kikCoreDatabase.db*',
                  '*/kik.android/*/cache/chatPics*/*',
                  '*/[Dd][Cc][Ii][Mm]/Kik/*',
                  '*/Android/data/kik.android/cache/temp/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "pixel7a_a14": "Android 14 | kik.android | 17 rows",
            "hc_pixel8pro_a17": "Android 17 | kik.android | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat ID",
                "textColumn": "Body",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender",
                "mediaColumn": "Attachment",
            }
        },
    },
    "kik_users": {
        "name": "Kik Users",
        "description": "Entries in the Kik contacts table, covering individual users and groups "
                       "with their display name, user name and roster flags",
        "author": "",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('*/kik.android/databases/*kikDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | kik.android | 5 rows",
            "hc_pixel8pro_a17": "Android 17 | kik.android | 0 rows",
        },
    },
    "kik_attachments": {
        "name": "Kik Attachments",
        "description": "Attachment properties from the Kik content table, pivoted so each content "
                       "id gives one row with its file name, size, source app and URLs",
        "author": "",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "Kik",
        "notes": "KIKContentTable stores one row per property, keyed by content id; this artifact "
                 "pivots those rows and adds the platform URIs from KIKContentURITable. Property "
                 "names are reported as the app wrote them. Files kept on the device under "
                 "DCIM/Kik or the chatPics caches are matched to a content id by file name and "
                 "checked in; files in those locations with no matching content id are listed as "
                 "rows of their own so they are not lost.",
        "paths": ('*/kik.android/databases/*kikDatabase.db*',
                  '*/kik.android/*/cache/chatPics*/*',
                  '*/[Dd][Cc][Ii][Mm]/Kik/*',
                  '*/Android/data/kik.android/cache/temp/*'),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "sample_data": {
            "pixel7a_a14": "Android 14 | kik.android | 3 rows",
            "hc_pixel8pro_a17": "Android 17 | kik.android | 0 rows",
        },
    },
    "kik_chat_metadata": {
        "name": "Kik Chat Metadata",
        "description": "Rows from chatMetaInfTable, including the chat end time and the flags Kik "
                       "keeps for anonymously matched chats",
        "author": "",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('*/kik.android/databases/*kikDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "info",
        "sample_data": {
            "pixel7a_a14": "Android 14 | kik.android | 1 row",
            "hc_pixel8pro_a17": "Android 17 | kik.android | 0 rows",
        },
    },
    "kik_local_account": {
        "name": "Kik Local Account",
        "description": "Account rows from kikCoreDatabase, giving the core id used to name the "
                       "other databases and the user name held against it",
        "author": "",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "Kik",
        "notes": "",
        "paths": ('*/kik.android/databases/kikCoreDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | kik.android | 1 row",
            "hc_pixel8pro_a17": "Android 17 | kik.android | 1 row",
        },
    },
    "kik_roster": {
        "name": "Kik Roster and Contact Profiles",
        "description": "Bare JIDs held in the user roster and contact profile databases, with the "
                       "profile update time where the app records one",
        "author": "",
        "creation_date": "2026-08-06",
        "last_update_date": "2026-08-06",
        "requirements": "none",
        "category": "Kik",
        "notes": "Both tables keep the profile itself in a protobuf blob that this artifact does "
                 "not decode; the JIDs are reported so roster membership can be compared against "
                 "the Kik Users artifact. These databases are also named with the account core id.",
        "paths": ('*/kik.android/databases/*userRosterEntries.db*',
                  '*/kik.android/databases/*contactProfileEntries.db*'),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "pixel7a_a14": "Android 14 | kik.android | 5 rows",
            "hc_pixel8pro_a17": "Android 17 | kik.android | 4 rows",
        },
    },
}

import os

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    get_sqlite_db_records,
)


def _ms(value):
    """Kik stores epoch milliseconds; zero and empty values stay blank."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    return convert_unix_ts_to_utc(value)


def _table_exists(db_path, table):
    # get_sqlite_db_records returns a cursor, so the rows have to be pulled out of it.
    rows = list(get_sqlite_db_records(
        db_path, f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
    return len(rows) > 0


def _query(db_path, table, query):
    if not db_path or not _table_exists(db_path, table):
        return []
    return get_sqlite_db_records(db_path, query)


def _main_db(files_found):
    """The databases carry the account core id as a prefix, so match on the suffix."""
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('kikDatabase.db'):
            return file_found
    return ''


def _db_ending_with(files_found, suffix):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(suffix):
            return file_found
    return ''


def _local_username(files_found):
    core_db = _db_ending_with(files_found, 'kikCoreDatabase.db')
    for record in _query(core_db, 'CoreTable',
                         'SELECT username FROM CoreTable ORDER BY is_active DESC'):
        if record[0]:
            return record[0]
    return ''


def _media_index(files_found):
    """Map content ids to files kept on the device, keeping unmatched media aside.

    Kik writes received pictures to DCIM/Kik and caches chat pictures under the account
    folder, both named after the content id. The temp folder keeps a working copy that
    carries no content id at all.
    """
    by_content_id = {}
    unmatched = []
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue
        lowered = file_found.lower()
        if not ('/dcim/kik/' in lowered or '/cache/chatpics' in lowered
                or '/kik.android/cache/temp/' in lowered):
            continue
        stem = os.path.splitext(os.path.basename(file_found))[0]
        if len(stem) == 36 and stem.count('-') == 4:
            by_content_id.setdefault(stem, []).append(file_found)
        else:
            unmatched.append(file_found)
    return by_content_id, unmatched


def _check_in(paths):
    references = [check_in_media(path, os.path.basename(path)) for path in paths]
    references = [reference for reference in references if reference]
    if len(references) == 1:
        return references[0]
    return references if references else ''


def _attachment_properties(db_path):
    """Pivot KIKContentTable into {content_id: {property: value}}."""
    pivot = {}
    for record in _query(db_path, 'KIKContentTable',
                         'SELECT content_id, content_name, content_string FROM KIKContentTable'):
        pivot.setdefault(record[0], {})[record[1]] = record[2]
    return pivot


@artifact_processor
def kik_messages(context):
    files_found = context.get_files_found()
    source_path = _main_db(files_found)
    data_list = []

    local_user = _local_username(files_found)
    attachments = _attachment_properties(source_path)
    media_by_content_id, _ = _media_index(files_found)

    query = '''
    SELECT messagesTable.timestamp, messagesTable.was_me, messagesTable.partner_jid,
           KIKcontactsTable.display_name, messagesTable.body, messagesTable.read_state,
           messagesTable.bin_id, messagesTable.content_id, messagesTable.app_id,
           messagesTable.uid, KIKcontactsTable.is_group, messagesTable.stat_msg,
           messagesTable.sys_msg
    FROM messagesTable
    LEFT JOIN KIKcontactsTable ON messagesTable.partner_jid = KIKcontactsTable.jid
    ORDER BY messagesTable.timestamp
    '''
    for record in _query(source_path, 'messagesTable', query):
        outgoing = record[1] == 1
        partner = record[3] or record[2]
        properties = attachments.get(record[7], {}) if record[7] else {}
        data_list.append((
            _ms(record[0]),
            'Outgoing' if outgoing else 'Incoming',
            local_user if outgoing else partner,
            record[2],
            record[3],
            record[4],
            _check_in(media_by_content_id.get(record[7], [])) if record[7] else '',
            properties.get('file-name', ''),
            properties.get('file-size', ''),
            properties.get('file-url', ''),
            properties.get('app-name', ''),
            record[5],
            'Yes' if record[10] else 'No',
            record[6],
            record[11],
            record[12],
            record[7],
            record[8],
            record[9],
        ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Sender',
        'Partner JID',
        'Partner Display Name',
        'Body',
        ('Attachment', 'media'),
        'Attachment File Name',
        'Attachment File Size',
        ('Attachment URL', 'url'),
        'Attachment Source App',
        'Read State Value',
        'Group Chat',
        'Chat ID',
        'Status Message',
        'System Message',
        'Content ID',
        'App ID',
        'Message UID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def kik_users(context):
    source_path = _main_db(context.get_files_found())
    data_list = []
    query = '''
    SELECT jid, display_name, user_name, local_name, is_group, group_size, group_hashtag,
           in_roster, is_blocked, is_ignored, is_stub, verified, user_type,
           user_permission_level, is_user_admin, is_user_removed, description, photo_url,
           photo_timestamp
    FROM KIKcontactsTable
    ORDER BY display_name
    '''
    for record in _query(source_path, 'KIKcontactsTable', query):
        data_list.append((
            record[0], record[1], record[2], record[3], 'Yes' if record[4] else 'No', record[5],
            record[6], 'Yes' if record[7] else 'No', 'Yes' if record[8] else 'No',
            'Yes' if record[9] else 'No', 'Yes' if record[10] else 'No',
            'Yes' if record[11] else 'No', record[12], record[13],
            'Yes' if record[14] else 'No', 'Yes' if record[15] else 'No', record[16],
            record[17], _ms(record[18]),
        ))

    data_headers = (
        'JID',
        'Display Name',
        'User Name',
        'Local Name',
        'Group',
        'Group Size',
        'Group Hashtag',
        'In Roster',
        'Blocked',
        'Ignored',
        'Stub Entry',
        'Verified',
        'User Type',
        'Permission Level',
        'Admin',
        'Removed',
        'Description',
        ('Photo URL', 'url'),
        ('Photo Timestamp', 'datetime'),
    )
    return data_headers, data_list, source_path


@artifact_processor
def kik_attachments(context):
    files_found = context.get_files_found()
    source_path = _main_db(files_found)
    data_list = []
    pivot = _attachment_properties(source_path)
    media_by_content_id, unmatched_media = _media_index(files_found)

    uris = {}
    for record in _query(source_path, 'KIKContentURITable',
                         '''SELECT content_id, content_uri, type, platform, file_content_type
                            FROM KIKContentURITable'''):
        uris.setdefault(record[0], []).append(record)

    for content_id, properties in pivot.items():
        uri_rows = uris.get(content_id, [])
        data_list.append((
            _check_in(media_by_content_id.get(content_id, [])),
            properties.get('file-name', ''),
            properties.get('file-size', ''),
            properties.get('app-name', ''),
            properties.get('layout', ''),
            properties.get('file-url', ''),
            uri_rows[0][1] if uri_rows else '',
            uri_rows[0][4] if uri_rows else '',
            properties.get('allow-forward', ''),
            properties.get('preview', ''),
            properties.get('icon', ''),
            content_id,
            context.get_relative_path(media_by_content_id.get(content_id, [''])[0])
            if media_by_content_id.get(content_id) else '',
        ))

    for path in unmatched_media:
        name = os.path.basename(path)
        size = os.path.getsize(path)
        if name.startswith('.') or size == 0:
            continue
        data_list.append((
            _check_in([path]), name, size, '', '', '', '', '', '', '', '', '',
            context.get_relative_path(path),
        ))

    data_headers = (
        ('Media', 'media'),
        'File Name',
        'File Size',
        'Source App',
        'Layout',
        ('File URL', 'url'),
        ('Platform URI', 'url'),
        'File Content Type',
        'Allow Forward',
        'Preview Reference',
        'Icon Reference',
        'Content ID',
        'Local File Path',
    )
    return data_headers, data_list, source_path


@artifact_processor
def kik_chat_metadata(context):
    source_path = _main_db(context.get_files_found())
    data_list = []
    query = '''
    SELECT chat_end_time, bin_id, retained, show_when_empty, is_anonymously_matched,
           anon_chat_session_uuid, anon_has_been_reported, anon_chat_has_been_rated,
           anon_friending_initiated, sort_order
    FROM chatMetaInfTable
    ORDER BY chat_end_time
    '''
    for record in _query(source_path, 'chatMetaInfTable', query):
        data_list.append((
            _ms(record[0]), record[1], 'Yes' if record[2] else 'No',
            'Yes' if record[3] else 'No', 'Yes' if record[4] else 'No', record[5],
            'Yes' if record[6] else 'No', 'Yes' if record[7] else 'No',
            'Yes' if record[8] else 'No', record[9],
        ))

    data_headers = (
        ('Chat End Time', 'datetime'),
        'Chat ID',
        'Retained',
        'Show When Empty',
        'Anonymously Matched',
        'Anonymous Session UUID',
        'Anonymous Chat Reported',
        'Anonymous Chat Rated',
        'Anonymous Friending Started',
        'Sort Order',
    )
    return data_headers, data_list, source_path


@artifact_processor
def kik_local_account(context):
    source_path = _db_ending_with(context.get_files_found(), 'kikCoreDatabase.db')
    data_list = []
    for record in _query(source_path, 'CoreTable',
                         'SELECT username, core_id, is_active FROM CoreTable'):
        data_list.append((record[0], record[1], 'Yes' if record[2] else 'No'))

    data_headers = ('User Name', 'Core ID', 'Active')
    return data_headers, data_list, source_path


@artifact_processor
def kik_roster(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('userRosterEntries.db'):
            sources.append(file_found)
            for record in _query(file_found, 'UserRosterEntries',
                                 'SELECT bare_jid FROM UserRosterEntries ORDER BY bare_jid'):
                data_list.append(('', record[0], 'User roster',
                                  os.path.basename(file_found).split('.')[0]))
        elif file_found.endswith('contactProfileEntries.db'):
            sources.append(file_found)
            for record in _query(file_found, 'ContactProfileEntries',
                                 '''SELECT bare_jid, last_update_timestamp
                                    FROM ContactProfileEntries ORDER BY bare_jid'''):
                data_list.append((_ms(record[1]), record[0], 'Contact profile',
                                  os.path.basename(file_found).split('.')[0]))

    data_headers = (
        ('Profile Update Time', 'datetime'),
        'Bare JID',
        'Held In',
        'Account Core ID',
    )
    return data_headers, data_list, '\n'.join(sources)
