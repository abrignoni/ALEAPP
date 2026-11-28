__artifacts_v2__ = {
    'zangichats': {
        'name': 'Zangi Chats',
        'description': 'Parses messages from the Zangi message table. isIncoming is reported as stored, with names joined from user_profile without assigning local-user ownership. Messages are retained when chatWith is empty or NULL. Timestamps are read as Unix milliseconds.',
        'author': '@C_Peter, @AlexisBrignoni, Codex',
        'version': '0.0.1',
        'date': '2025-11-20',
        'creation_date': '2025-11-20',
        'last_update_date': '2026-10-09',
        'requirements': 'none',
        'category': 'Messaging',
        'notes': 'Every matched .db file other than settings.db that holds a message table is '
                 'read, one copy per storage view of the app directory, and the Source File '
                 'column names the database each row was read from. Where a '
                 'message\'s attachment value holds no package path, the attachment is looked up '
                 'by the name pattern files/zangi/Zangi Files/<msgId>.*, which is a name match '
                 'and not a link the store records. isIncoming is reported as stored; From Name '
                 'and To Name are joined profile names. Direction meaning and local-account '
                 'ownership are not established, so the conversation direction view is '
                 'unconfigured.',
        'paths': (
            '*/data/com.beint.zangi/databases/*',
            '*/data/com.beint.zangi/files/zangi/*'),
        'output_types': 'standard',
        'artifact_icon': 'message',
    },
    'zangi_calls': {
        'name': 'Zangi Calls',
        'description': 'Call history rows from the Zangi recents table.',
        'author': '@AlexisBrignoni, Claude',
        'creation_date': '2026-11-16',
        'last_update_date': '2026-11-16',
        'requirements': 'none',
        'category': 'Messaging',
        'notes': (
            "One row per row of the recents table in each .db file under com.beint.zangi/databases that "
            "holds one (files ending in settings.db are skipped; on the tested image the file name is a "
            "number). Start Time and End Time are startTime and endTime read as Unix milliseconds; a "
            "stored 0, a NULL, a negative or a non-integer value is shown blank, and only the 0 case "
            "occurred in the tested data. Duration (s, computed) is End Time minus Start Time and is "
            "blank when either is blank or when endTime is earlier than startTime. status and "
            "call_traffic are shown as stored; their meanings are not established. On "
            "samsung_a166u_a16_known_20261116, the known-data session had two incoming audio calls from "
            "one test contact. The first rang on the calling phone from about 17:22:50 to 17:23:53 UTC "
            "and was not answered; its row had status 5, startTime 17:23:09 UTC and endTime 0. The "
            "second was answered at about 17:27:29 UTC and hung up at 17:27:55 UTC; its row had status "
            "1, startTime 17:27:28.968 and endTime 17:27:53.897 UTC, a computed 24.929 s. Whether "
            "status 5 and 1 stand for missed and answered calls in general is not established. Email "
            "and Network Call Name had no value on both rows. Number and e164number (as stored) are "
            "shown as stored; a NULL is shown blank. Rows from several Android users are reported "
            "together and no column names the user. Only Zangi 6.6.4 was exercised. When this artifact "
            "was written (2026-11-16), of the 62 registered Android images whose member lists were "
            "read, this was the only one with a com.beint.zangi databases folder."),
        'paths': ('*/com.beint.zangi/databases/*',),
        'output_types': 'standard',
        'artifact_icon': 'phone',
        'sample_data': {
            'samsung_a166u_a16_known_20261116': 'Android 16 | com.beint.zangi 6.6.4 | 2 rows',
        },
    },
    'zangi_groups': {
        'name': 'Zangi Groups',
        'description': 'Groups from the Zangi t_group table with their members from t_chat_members.',
        'author': '@AlexisBrignoni, Claude',
        'creation_date': '2026-11-16',
        'last_update_date': '2026-11-28',
        'requirements': 'none',
        'category': 'Messaging',
        'notes': (
            "One row per row of t_group in each Zangi account database, with its member rows from "
            "t_chat_members (m_member_group_id equal to g_group_id) listed as m_chatjid with "
            "m_memberrole; Member Rows counts them. On samsung_a166u_a16_known_20261116 the join was "
            "exercised on one group. Rows of t_chat_members whose m_member_group_id is 0 or NULL are "
            "not listed; the tested image had one, and its m_chatjid equals the group's g_uid. "
            "Conversation Last Update is t_conversation.c_last_update_date for the conversation whose "
            "c_group_id is the group, read as Unix milliseconds. g_state, g_type, g_is_accepted and "
            "m_memberrole are shown as stored; their meanings are not established. When t_group has no "
            "g_is_accepted column, the g_is_accepted (as stored) column is blank, and that blank is not "
            "a stored value; the samsung_a166u_a16_known_20261116 database (user_version 127) has the "
            "column. Group UID is g_uid as stored. On samsung_a166u_a16_known_20261116 the one group "
            "was created by the other test phone at about 17:29:12 UTC and was seen in this phone's "
            "chat list at 17:29:17 UTC, where the app showed it as accepted without a tap; its row held "
            "the group name given there, 2 member rows (roles 3 and 1), g_is_accepted 2, and a "
            "Conversation Last Update of 17:30:23.755 UTC, equal to the date of the reply message row "
            "and about 2 s before the 17:30:26 UTC the mint log records for that reply. Messages whose "
            "Chat-ID in the Zangi Chats artifact equals Group UID belong to the group's chat (5 rows on "
            "the tested image). Rows from several Android users are reported together and no column "
            "names the user. Not reported from the account database: numbers, contacts2, bucket and box "
            "tables, message_info, message_live_duration, security_key, Pending, t_c_size, "
            "t_member_configuration, t_msg_status, tableUser, emoji_us and the rest of t_conversation; "
            "user_profile is used only for name joins in Zangi Chats; blocked_numbers and the other "
            "zero-row tables held no rows. The settings database and zangi_common (users and a "
            "countries list) are not read. When this artifact was written (2026-11-16), of the 62 "
            "registered Android images whose member lists were read, this was the only one with a "
            "com.beint.zangi databases folder."),
        'paths': ('*/com.beint.zangi/databases/*',),
        'output_types': 'standard',
        'artifact_icon': 'users',
        'sample_data': {
            'samsung_a166u_a16_known_20261116': 'Android 16 | com.beint.zangi 6.6.4 | 1 row',
        },
    }
}

import datetime
import os
from pathlib import Path
from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, \
    get_sqlite_db_records, \
    does_table_exist_in_db, \
    check_in_media

def _append_rows(data_list, db_records, relative_source):
    for record in db_records:
        m_time = datetime.datetime.fromtimestamp(record[0]/1000, tz=datetime.timezone.utc)
        chat_name = record[1]
        chat_id = record[2]
        message_id = record[3]
        msgId = record[4]
        message = record[5]
        media = record[6]
        media_path = ""
        if media != None and media != "":
            if "com.beint.zangi" in media:
                parts = media.split("com.beint.zangi/")
                if len(parts) > 1:
                    media_path = parts[1]
                else:
                    media_path = None
            else:
                media_path = f"files/zangi/Zangi Files/{msgId}.*"
            try:
                attach_file_name = Path(media_path).name
                attach_file = check_in_media(media_path, attach_file_name)
            except TypeError:
                attach_file = ""
        else:
            attach_file = ""
        sender = record[7]
        sender_id = record[8]
        receiver = record[9]
        receiver_id = record[10]
        incoming = record[11]
        data_list.append((m_time, incoming, sender, chat_name, message, attach_file, chat_id, message_id, sender_id, receiver, receiver_id, relative_source))


@artifact_processor
def zangichats(context):
    data_list = []
    source_files = []
    # Every matched database that holds a message table is read, once per storage view.
    databases = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.endswith(".db") or file_found.endswith("settings.db"):
            continue
        if os.path.isdir(file_found) or not does_table_exist_in_db(file_found, 'message'):
            continue
        databases.append(file_found)

    #user_query = '''
    #    SELECT
    #        CASE
    #            WHEN tableUserLastName IS NULL OR tableUserLastName = '' THEN tableUserName
    #            ELSE tableUserName || ' ' || tableUserLastName
    #        END AS user
    #    FROM tableUser
    #    '''

    chat_query = '''
        SELECT     
            m."date",
            CASE 
                WHEN cn.last_name IS NULL OR cn.last_name = '' THEN cn.first_name
                ELSE cn.first_name || ' ' || cn.last_name
            END AS chat,
            m.chatWith,
            m.message_id,
            m.msgId,
            m.message_msg,
            m.extra,
            CASE 
                WHEN uf.last_name IS NULL OR uf.last_name = '' THEN uf.first_name
                ELSE uf.first_name || ' ' || uf.last_name
            END AS from_name,
            m.msgFrom,
            CASE 
                WHEN ut.last_name IS NULL OR ut.last_name = '' THEN ut.first_name
                ELSE ut.first_name || ' ' || ut.last_name
            END AS to_name,
            m.msgTo,
            m.isIncoming
        FROM message m
        LEFT JOIN user_profile uf 
            ON m.msgFrom = uf.id
        LEFT JOIN user_profile ut 
            ON m.msgTo = ut.id
        LEFT JOIN user_profile cn 
            ON m.chatWith = cn.id;
            '''
    for source_path in databases:
        db_records = get_sqlite_db_records(source_path, chat_query)
        source_files.append(source_path)
        relative_source = str(context.get_relative_path(source_path))
        _append_rows(data_list, db_records, relative_source)

    data_headers = (
        ('Timestamp', 'datetime'),
        'isIncoming (as stored)',
        'From Name (joined)',
        'Chat',
        'Message',
        ('Attachment File', 'media'),
        'Chat-ID',
        'Message-ID',
        'From ID',
        'To Name (joined)',
        'To ID',
        'Source File',
    )

    return data_headers, data_list, '\n'.join(source_files)


def _ms(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return ''


def _account_databases(context, table):
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.endswith('.db') or file_found.endswith('settings.db') or os.path.isdir(file_found):
            continue
        if does_table_exist_in_db(file_found, table):
            yield file_found


@artifact_processor
def zangi_calls(context):
    query = """
        SELECT startTime, endTime, status, number, e164number, email, call_traffic, call_id,
               network_call_name, id
        FROM recents ORDER BY startTime, id
    """
    data_list = []
    source_files = []
    for source_path in _account_databases(context, 'recents'):
        source_files.append(source_path)
        for row in get_sqlite_db_records(source_path, query):
            start, end = row[0], row[1]
            duration = ''
            if isinstance(start, int) and isinstance(end, int) and start > 0 and end >= start:
                duration = round((end - start) / 1000, 3)
            data_list.append((_ms(start), _ms(end), duration, row[2], row[3] or '', row[4] or '', row[5] or '',
                              row[6], row[7] or '', row[8] or '', row[9]))
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'Duration (s, computed)',
                    'status (as stored)', 'Number', 'e164number (as stored)', 'Email', 'call_traffic (as stored)', 'Call ID',
                    'Network Call Name', 'Row ID')
    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def zangi_groups(context):
    member_query = """
        SELECT m_member_group_id, m_chatjid, m_memberrole FROM t_chat_members
        WHERE m_member_group_id > 0 ORDER BY m_member_group_id, m_id
    """
    conversation_query = """
        SELECT c_group_id, c_last_update_date FROM t_conversation WHERE c_group_id > 0
    """
    data_list = []
    source_files = []
    for source_path in _account_databases(context, 't_group'):
        source_files.append(source_path)
        members = {}
        for group_id, jid, role in get_sqlite_db_records(source_path, member_query):
            members.setdefault(group_id, []).append(f'{jid} (role {role})')
        updated = {group_id: last for group_id, last in get_sqlite_db_records(source_path, conversation_query)}
        # g_is_accepted is missing from t_group in some databases. The column is then blank.
        columns = {row[1] for row in get_sqlite_db_records(source_path, 'PRAGMA table_info(t_group)')}
        accepted = 'g_is_accepted' if 'g_is_accepted' in columns else "''"
        group_query = (f'SELECT g_group_id, g_name, g_uid, g_state, g_type, {accepted} '
                       'FROM t_group ORDER BY g_group_id')
        for row in get_sqlite_db_records(source_path, group_query):
            group_members = members.get(row[0], [])
            data_list.append((_ms(updated.get(row[0])), row[1] or '', row[2] or '', len(group_members),
                              '; '.join(group_members), row[3], row[4], row[5], row[0]))
    data_headers = (('Conversation Last Update', 'datetime'), 'Group Name', 'Group UID', 'Member Rows',
                    'Members (as stored, with m_memberrole)', 'g_state (as stored)', 'g_type (as stored)',
                    'g_is_accepted (as stored)', 'Group ID')
    return data_headers, data_list, '\n'.join(source_files)
