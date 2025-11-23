__artifacts_v2__ = {
    'zangichats': {
        'name': 'Zangi Chats',
        'description': 'Parses Zangi Chat database',
        'author': '@C_Peter',
        'version': '0.0.1',
        'date': '2025-11-20',
        'requirements': 'none',
        'category': 'Chats',
        'notes': '',
        'paths': (
            '*/data/com.beint.zangi/databases/*',
            '*/data/com.beint.zangi/files/zangi/*'),
        'output_types': 'standard',
        'artifact_icon': 'message-square',
        'data_views': {
            'conversation': {
                'conversationColumn': 'Chat-ID',
                'conversationLabelColumn': 'Chat',
                'textColumn': 'Message',
                'directionColumn': 'From Me',
                'directionSentValue': 1,
                'timeColumn': 'Timestamp',
                'senderColumn': 'Sender Name',
                'mediaColumn': 'Attachment File'
            }
        }
    }
}

import datetime
import inspect
from pathlib import Path
from scripts.ilapfuncs import artifact_processor, \
    get_sqlite_db_records, \
    check_in_media

@artifact_processor
def zangichats(files_found, _report_folder, _seeker, _wrap_text):
    artifact_info = inspect.stack()[0]
    source_path = ""
    data_list = []
    for file_found in files_found:
        if file_found.endswith(".db") and not file_found.endswith("settings.db"):
            source_path = file_found
            #db_name = os.path.basename(file_found)
            #uid = os.path.splitext(db_name)[0]

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
    #user_id =  get_sqlite_db_records(source_path, user_query)
    db_records = get_sqlite_db_records(source_path, chat_query)

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
                attach_file = check_in_media(artifact_info, _report_folder, _seeker, files_found, media_path, attach_file_name)
            except TypeError:
                attach_file = ""
        else:
            attach_file = ""
        sender = 'Local User' if record[11] == 0 else record[7]
        sender_id = record[8]
        receiver = record[9] if record[11] == 0 else 'Local User'
        receiver_id = record[10]
        incoming = record[11]
        if int(incoming) == 0:
            outgoing = 1
        else:
            outgoing = 0
        
        if chat_id == "" or chat_id == None:
            pass
        else:
            data_list.append((m_time, chat_name, chat_id, message_id, sender, sender_id, receiver, receiver_id, message, attach_file, outgoing))
    
    data_headers = (
        ('Timestamp', 'datetime'), 'Chat', 'Chat-ID', 'Message-ID', 'Sender Name', 'From ID', 'Receiver', 'To ID',
        'Message', ('Attachment File', 'media'), 'From Me')

    return data_headers, data_list, source_path