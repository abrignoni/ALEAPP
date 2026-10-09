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
        'category': 'Chats',
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