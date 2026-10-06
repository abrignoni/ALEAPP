# Android RandoChat App (com.random.chat.app)

# Tested Version: 6.3.3


__artifacts_v2__ = {
    'randochat_messages': {
        'name': 'RandoChat Messages',
        'description': 'Parses the mensagens table of the RandoChat database.',
        'author': 'Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex',
        'version': '0.0.1',
        'creation_date': '2026-01-15',
        'last_update_date': '2026-10-06',
        'requirements': 'os, path',
        'category': 'Chats',
        'notes': 'Timestamp is the hora column read as Unix milliseconds. '
                 'Sent? is the minha column as stored; a comment in the '
                 'module reads 1 as sent and 2 as received, and no source for '
                 'those values is recorded. Stored Media URL retains url as stored. '
                 'A local media candidate requires an exact, nonempty basename match '
                 'using the stored value without URL decoding. This is a filename '
                 'candidate, not a proven path or ownership association. Candidate count and '
                 'sorted evidence-relative paths retain every distinct input path. Only '
                 'a unique candidate is exported; ambiguous matches attach nothing. Repeated '
                 'identical paths collapse, while aliases remain candidates. Namespace '
                 'ownership and last-main database selection remain unresolved.',
        'paths': (
            '*/data/com.random.chat.app/databases/ramdochatV2.db*',
            '*/Android/data/com.random.chat.app/files/Pictures/RandoChat/*',
            '*/Android/data/com.random.chat.app/files/images/*',
            '*/Android/data/com.random.chat.app/files/Music/RandoChat/*'
            ),
        'output_types': 'standard',
        'artifact_icon': 'message',
        "html_columns": ["Media File"]
    },
    'randochat_account': {
        'name': 'RandoChat Accounts',
        'description': 'Parses the configuracao table of the RandoChat database.',
        'author': 'Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex',
        'version': '0.0.1',
        'creation_date': '2026-01-15',
        'last_update_date': '2026-10-06',
        'requirements': '',
        'category': 'Accounts',
        'notes': 'Stored Sex and Stored Sex Search Value retain the values under sexo and sexo_search. '
                 'Existing SQLite MAX aggregates and name LIKE predicates are preserved, so duplicate '
                 'keys are not a chronology claim. The H/M vendor meanings are unverified. Only the last '
                 'matched main database is read.',
        'paths': (
            '*/data/com.random.chat.app/databases/ramdochatV2.db*'
            ),
        'output_types': 'standard',
        'artifact_icon': 'user'
    },
    'randochat_contacts': {
        'name': 'RandoChat Contacts',
        'description': 'Parses the conversa table of the RandoChat database, one row per conversation record.',
        'author': 'Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex',
        'version': '0.0.1',
        'creation_date': '2026-01-15',
        'last_update_date': '2026-10-06',
        'requirements': '',
        'category': 'Contacts',
        'notes': 'Stored Sex is c.sexo as stored, including unknown values and NULL. H/M vendor meanings '
                 'are unverified. Stored Person ID is c.id_pessoa without asserting an account '
                 'relationship. Only the last matched main database is read.',
        'paths': (
            '*/data/com.random.chat.app/databases/ramdochatV2.db*'
            ),
        'output_types': 'standard',
        'artifact_icon': 'user'
    }
}

import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, check_in_media

@artifact_processor
def randochat_messages(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]   


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

        # A filename match identifies candidates, not ownership.
        filename = os.path.basename(media_file) if media_file is not None else ''
        candidates = sorted(
            {path for path in attachments if filename and filename == os.path.basename(path)},
            key=lambda path: (context.get_relative_path(path), path),
        )
        candidate_paths = '\n'.join(context.get_relative_path(path) for path in candidates)
        attachment = 0 if media_file is None else ''
        if len(candidates) == 1:
            attachment = check_in_media(candidates[0], os.path.basename(candidates[0]))

        data_list.append((timestamp, content, contact_name, direction, attachment, media_file, len(candidates), candidate_paths, conv_id, message_id))
    
    data_headers = (
                        ('Timestamp', 'datetime'),
                        'Content', 
                        'Contact Username',
                        'Sent?',
                        ('Media File', 'media'),
                        'Stored Media URL',
                        'Media Filename Candidate Count',
                        'Media Filename Candidate Paths',
                        'Conversation ID',
                        'Message ID'
                    )

    return data_headers, data_list, main_db


@artifact_processor
def randochat_account(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]   


    # Get the different files found and store their pathes in corresponding lists to work with them
    main_db = ''

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('ramdochatV2.db'):
            main_db = file_found
        

    query = '''
            SELECT 
            MAX(CASE WHEN name LIKE 'apelido' THEN value END) [Username],
            MAX(CASE WHEN name LIKE 'sexo' THEN value END) [Stored Sex],
            MAX(CASE WHEN name LIKE 'idade' THEN value END) [User Age],
            MAX(CASE WHEN name LIKE 'language' THEN value END) [Language],
            MAX(CASE WHEN name LIKE 'device_id' THEN value END) [Device ID],
            MAX(CASE WHEN name LIKE 'idade_de' THEN value END) [Preferred Age From],
            MAX(CASE WHEN name LIKE 'idade_ate' THEN value END) [Preferred Age To],
            MAX(CASE WHEN name LIKE 'sexo_search' THEN value END) [Stored Sex Search Value]
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
    
    data_headers = (
                        'Username',
                        'Stored Sex',
                        'User Age',
                        'Language',
                        'Device ID',
                        'Preferred Age From',
                        'Preferred Age To',
                        'Stored Sex Search Value'
                    )

    return data_headers, data_list, main_db


@artifact_processor
def randochat_contacts(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]   
    main_db = ''

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('ramdochatV2.db'):
            main_db = file_found
        

    query = '''
            SELECT
            c.id_pessoa [Stored Person ID],
            c.apelido [Username],
            c.idade [Age],
            c.sexo [Stored Sex],
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
    
    data_headers = ('Stored Person ID', 'Username', 'Age', 'Stored Sex', 'Favorite?', 'Blocked?', 'Link Profile Pic')

    return data_headers, data_list, main_db