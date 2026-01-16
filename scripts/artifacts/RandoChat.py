# Android RandoChat App (com.random.chat.app)

# Tested Version: 6.3.3


__artifacts_v2__ = {
    'randochat_messages': {
        'name': 'RandoChat Messages',
        'description': 'Parses RandoChat App Messages',
        'author': 'Marco Neumann {kalinko@be-binary.de}',
        'version': '0.0.1',
        'creation_date': '2026-01-15',
        'last_update_date': '2026-01-15',
        'requirements': 'os, path',
        'category': 'Chats',
        'notes': '',
        'paths': (
            '*/data/com.random.chat.app/databases/ramdochatV2.db*',
            '*/Android/data/com.random.chat.app/files/Pictures/RandoChat/*',
            '*/Android/data/com.random.chat.app/files/images/*',
            '*/Android/data/com.random.chat.app/files/Music/RandoChat/*'
            ),
        'output_types': 'standard',
        'artifact_icon': 'message-square',
        "html_columns": ["Media File"]
    },
    'randochat_account': {
        'name': 'RandoChat Accounts',
        'description': 'Parses RandoChat App Accounts',
        'author': 'Marco Neumann {kalinko@be-binary.de}',
        'version': '0.0.1',
        'creation_date': '2026-01-15',
        'last_update_date': '2026-01-15',
        'requirements': '',
        'category': 'Accounts',
        'notes': '',
        'paths': (
            '*/data/com.random.chat.app/databases/ramdochatV2.db*'
            ),
        'output_types': 'standard',
        'artifact_icon': 'user'
    },
    'randochat_contacts': {
        'name': 'RandoChat Contacts',
        'description': 'Parses RandoChat App Contacts',
        'author': 'Marco Neumann {kalinko@be-binary.de}',
        'version': '0.0.1',
        'creation_date': '2026-01-15',
        'last_update_date': '2026-01-15',
        'requirements': '',
        'category': 'Contacts',
        'notes': '',
        'paths': (
            '*/data/com.random.chat.app/databases/ramdochatV2.db*'
            ),
        'output_types': 'standard',
        'artifact_icon': 'user'
    }
}

import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, media_to_html

@artifact_processor
def randochat_messages(files_found, report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]   


    # Get the different files found and store their pathes in corresponding lists to work with them
    main_db = ''
    attachments = []

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('ramdochatV2.db'):
            main_db = file_found

        if 'files' in os.path.dirname(file_found):
            attachments.append(file_found)
        

    query = '''
            SELECT 
            m.hora [Timestamp],
            m.mensagem [Message Content],
            c.apelido [Contact Username],
            m.minha [Sent?], -- 1 = sent, 2 = received 
            m.url [Media File],
            m.id_talk_server [Conversation ID],
            m.id_servidor [Message ID]
            FROM mensagens m
            LEFT JOIN conversa c ON c.id_server = m.id_talk_server
            '''

    db_records = get_sqlite_db_records(main_db, query)
    data_list = []

    for row in db_records:
        timestamp = convert_unix_ts_to_utc(int(row[0])/1000)
        content = row[1]
        contact_name = row[2]
        direction = row[3]
        media_file = row[4]
        conv_id = row[5]
        message_id = row[6]

        # Handling attachments
        if media_file is None:
            attachment = 0
        else:
            attachment = ''
            for att_path in attachments:
                if os.path.basename(media_file) in os.path.basename(att_path):
                    attachment = media_to_html(os.path.basename(att_path), attachments, report_folder)

        data_list.append((timestamp, content, contact_name, direction, attachment, conv_id, message_id))
    
    data_headers = ('Timestamp', 'Content', 'Contact Username', 'Sent?',  'Media File', 'Conversation ID', 'Message ID')

    return data_headers, data_list, main_db


@artifact_processor
def randochat_account(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]   


    # Get the different files found and store their pathes in corresponding lists to work with them
    main_db = ''

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('ramdochatV2.db'):
            main_db = file_found
        

    query = '''
            SELECT 
            MAX(CASE WHEN name LIKE 'apelido' THEN value END) [Username],
            MAX(CASE WHEN name LIKE 'sexo' THEN (CASE WHEN value = 'H' THEN 'Male' WHEN value = 'M' THEN 'Female' END) END) [User Sex],
            MAX(CASE WHEN name LIKE 'idade' THEN value END) [User Age],
            MAX(CASE WHEN name LIKE 'language' THEN value END) [Language],
            MAX(CASE WHEN name LIKE 'device_id' THEN value END) [Device ID],
            MAX(CASE WHEN name LIKE 'idade_de' THEN value END) [Preferred Age From],
            MAX(CASE WHEN name LIKE 'idade_ate' THEN value END) [Preferred Age To],
            MAX(CASE WHEN name LIKE 'sexo_search' THEN (CASE WHEN value = 'H' THEN 'Male' WHEN value = 'M' THEN 'Female' END) END) [Preferred Sex]
            FROM configuracao
            '''

    db_records = get_sqlite_db_records(main_db, query)
    data_list = []

    for row in db_records:
        username = row[0]
        sex = row[1]
        age = row[2]
        language = row[3]
        device_id = row[4]
        age_from = row[5]
        age_to = row[6]
        preferred_sex = row[7]


        data_list.append((username, sex, age, language, device_id, age_from, age_to, preferred_sex))
    
    data_headers = ('Username', 'User Sex', 'User Age', 'Language',  'Device ID', 'Preferred Age From', 'Preferred Age To', 'Preferred Sex')

    return data_headers, data_list, main_db


@artifact_processor
def randochat_contacts(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]   
    main_db = ''

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('ramdochatV2.db'):
            main_db = file_found
        

    query = '''
            SELECT
            c.id_pessoa [Account ID],
            c.apelido [Username],
            c.idade [Age],
            CASE
                WHEN c.sexo = 'M' THEN 'Female' -- From Mulher
                WHEN c.sexo = 'H' THEN 'Male'  -- From Homem
            END	[Sex],
            CASE
                WHEN c.favorite = 1 THEN 'Yes'
                WHEN c.favorite = 0 THEN 'No'
            END [Favorite?],
            CASE
                WHEN c.bloqueado = 1 THEN 'Yes'
                WHEN c.bloqueado = 0 THEN 'No'
            END [Blocked?],
            CASE WHEN
                c.images = '' THEN 'n/a'
            ELSE
                json_extract(c.images, "$[0].img")
            END [Link Profile Pic]
            FROM conversa c
            '''

    db_records = get_sqlite_db_records(main_db, query)
    data_list = []

    for row in db_records:
        account_id = row[0]
        username = row[1]
        age = row[2]
        sex = row[3]
        favorite = row[4]
        blocked = row[5]
        profile_pic = row[6]


        data_list.append((account_id, username, age, sex, favorite, blocked, profile_pic))
    
    data_headers = ('Account ID', 'Username', 'Age', 'Sex', 'Favorite?', 'Blocked?', 'Link Profile Pic')

    return data_headers, data_list, main_db