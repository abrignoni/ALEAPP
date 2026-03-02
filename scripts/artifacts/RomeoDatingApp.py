# Android Romeo - Gay Dating App (com.planetromeo.android.app)

# Tested Version: 3.40.0


__artifacts_v2__ = {
    'romeo_dating_messages': {
        'name': 'Romeo Dating App Messages',
        'description': 'Parses Romeo Dating App Messages',
        'author': 'Marco Neumann {kalinko@be-binary.de}',
        'version': '0.0.1',
        'creation_date': '2026-02-25',
        'last_update_date': '2026-02-25',
        'requirements': '',
        'category': 'Chats',
        'notes': '',
        'paths': (
            '*/com.planetromeo.android.app/databases/planetromeo-room.db.*' 
            ),
        'output_types': 'standard',
        'artifact_icon': 'message-square'
    },
    'romeo_dating_contacts': {
        'name': 'Romeo Dating App Contacts',
        'description': 'Parses Romeo Dating App Contacts',
        'author': 'Marco Neumann {kalinko@be-binary.de}',
        'version': '0.0.1',
        'creation_date': '2026-02-25',
        'last_update_date': '2026-02-25',
        'requirements': '',
        'category': 'Contacts',
        'notes': '',
        'paths': (
            '*/com.planetromeo.android.app/databases/planetromeo-room.db.*'
            ),
        'output_types': 'standard',
        'artifact_icon': 'users'
    },
    'romeo_dating_accounts': {
        'name': 'Romeo Dating App Accounts',
        'description': 'Parses Romeo Dating App Contacts',
        'author': 'Marco Neumann {kalinko@be-binary.de}',
        'version': '0.0.1',
        'creation_date': '2026-02-25',
        'last_update_date': '2026-02-25',
        'requirements': '',
        'category': 'Accounts',
        'notes': '',
        'paths': (
            '*/com.planetromeo.android.app/databases/accounts.db'
            ),
        'output_types': 'standard',
        'artifact_icon': 'user'
    }
}


from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records

@artifact_processor
def romeo_dating_messages(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    main_db = ''
    data_list = []

    query = '''
            SELECT me.date [Timestamp],
            me.chatPartnerId [Contact ID],
            cpe.name [Contact Name],
            me.text [Message Text],
            me.transmissionStatus [Status],
            me.saved [Saved?],
            me.unread [Unread?],
            me.messageId [Message ID],
            CASE WHEN iae.imageId IS NOT NULL
            THEN
                "Yes"
            ELSE
                "No"
            END [Image Contained?]
            FROM MessageEntity me
            INNER JOIN ChatPartnerEntity cpe ON cpe.profileId = me.chatPartnerId
            LEFT JOIN ImageAttachmentEntity iae ON me.messageId = iae.parentMessageId
            '''

    for file_found in files_found:
        main_db = str(file_found)



        db_records = get_sqlite_db_records(main_db, query)


        for row in db_records:
            timestamp = row[0]
            contact_id = row[1]
            contact_name = row[2]
            text = row[3]
            status = row[4]
            saved = row[5]
            unread = row[6]
            message_id = row[7]
            image_contained = row[8]



            data_list.append((  timestamp,
                                contact_id,
                                contact_name,
                                text,
                                status,
                                saved,
                                unread,
                                message_id,
                                image_contained,
                                main_db
                            ))
        
        data_headers = (    ('Timestamp', 'datetime'),
                            'Contact ID',
                            'Contact Username',
                            'Text', 
                            'Status',
                            'Saved?',
                            'Unread?',
                            'Message ID',
                            'Image Contained?',
                            'Source Database'
                        )
        # On android we only know if an Image was part of the message,
        # content isn't on the phone anymore- so just "image contained?"

    return data_headers, data_list, 'See Table for Source DB'


@artifact_processor
def romeo_dating_contacts(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]


    main_db = ''
    data_list = []

    query = '''
            SELECT 
            CASE WHEN cpe.fetchDate IS NOT NULL
                THEN
                cpe.fetchDate
                ELSE
                0
            END [Last Fetched Date],
            CASE WHEN cpe.deletionDate IS NOT NULL
                THEN
                cpe.deletionDate
                ELSE
                0
            END [Deletion Date],
            ce.userId [UserID],
            cpe.name [Name],
            cpe.headline [Headline],
            ce.contactNote [Notes],
            ce.linkStatus [Status],
            cpe.age [Age],
            cpe.weight [Weight],
            cpe.height [Height],
            cpe.locationName [City],
            cpe.country [Country],

            cpe.isDeactivated [Deactivated?],
            cpe.isBLocked [Blocked?]
            FROM ContactEntity ce
            INNER JOIN ChatPartnerEntity cpe ON ce.userID = cpe.profileId
            '''

    for file_found in files_found:
        main_db = str(file_found)

        db_records = get_sqlite_db_records(main_db, query)

        for row in db_records:
            fetch_timestamp = convert_unix_ts_to_utc(int(row[0]) / 1000)
            delete_timestamp = convert_unix_ts_to_utc(int(row[1]) / 1000)
            contact_id = row[2]
            contact_name = row[3]
            headline = row[4]
            notes = row[5]
            status = row[6]
            age = row[7]
            weight = row[8]
            height = row[9]
            city = row[10]
            country = row[11]
            deactivated = row[12]
            blocked = row[13]


            data_list.append((  fetch_timestamp,
                                delete_timestamp,
                                contact_id,
                                contact_name,
                                headline,
                                notes,
                                status,
                                age,
                                weight,
                                height,
                                city,
                                country,
                                deactivated,
                                blocked,
                                main_db
                            ))
    
    data_headers = (    ('Last Fetched', 'datetime'),
                        ('Deleted', 'datetime'),
                        'Contact ID',
                        'Contact Name',
                        'Headline',
                        'Notes',
                        'Status',
                        'Age',
                        'Weight',
                        'Height',
                        'City',
                        'Country',
                        'Deactivated?',
                        'Blocked?',
                        'Source Database'
                    )

    return data_headers, data_list, 'See Table for Source DB'


@artifact_processor
def romeo_dating_accounts(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    main_db = ''

    for file_found in files_found:
        main_db = str(file_found)
        

    query = '''
            SELECT 
            _id [ID],
            username [Username],
            email [E-Mail],
            json_extract(location, '$.address.address') [Address],
            json_extract(location, '$.name') [City],
            json_extract(location, '$.lat') [Latitude],
            json_extract(location, '$.long') [Longitude],
			json_extract(profile, '$.headline') [Headline],
			json_extract(profile, '$.personal.profile_text') [Profile Text],
			json_extract(profile, '$.creation_date') [Creation Date],
			json_extract(profile, '$.last_login') [Last Login],
			json_extract(profile, '$.personal.age') [Age],
			json_extract(profile, '$.personal.birthdate') [Birthdate]
            FROM accounts
            '''

    db_records = get_sqlite_db_records(main_db, query)
    data_list = []

    for row in db_records:
        account_id = row[0]
        username = row[1]
        email = row[2]
        address = row[3]
        city = row[4]
        latitude = row[5]
        longitude = row[6]
        headline = row[7]
        profile_text = row[8]
        creation_date = row[9]
        last_login_date = row[10]
        age = row[11]
        birthdate = row[12]


        data_list.append((  account_id,
                            username,
                            email,
                            address,
                            city,
                            latitude,
                            longitude,
                            headline,
                            profile_text,
                            creation_date,
                            last_login_date,
                            age,
                            birthdate
                        ))
    
    data_headers = (    'Account ID',
                        'Username',
                        'E-Mail',
                        'Address',
                        'City',
                        'Latitude',
                        'Longitude',
                        'Headline',
                        'Profile Text',
                        ('Creation Date', 'datetime'),
                        ('Last Login Date', 'datetime'),
                        'Age',
                        'Birthdate'
                    )

    return data_headers, data_list, main_db
