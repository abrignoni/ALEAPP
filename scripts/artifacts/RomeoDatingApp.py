# Android Romeo - Gay Dating App (com.planetromeo.android.app)

# Tested Version: 3.40.0


__artifacts_v2__ = {
    'romeo_dating_messages': {
        'name': 'Romeo Dating App Messages',
        'description': 'Messages from the MessageEntity table of the Romeo Android app database, with the contact name from ChatPartnerEntity where a row for the chat partner exists.',
        'author': 'Marco Neumann {kalinko@be-binary.de}',
        'version': '0.0.1',
        'creation_date': '2026-02-25',
        'last_update_date': '2026-10-04',
        'requirements': '',
        'category': 'Chats',
        'notes': 'A message is reported whether or not ChatPartnerEntity holds a row for its chat '
                 'partner, and is not repeated for each image attached to it. Whether profileId is '
                 'unique in ChatPartnerEntity is not established; if it is not, a message appears once '
                 'per matching row. Contact Username is ChatPartnerEntity.name '
                 'for the row whose profileId equals the message chatPartnerId, and is blank when '
                 'no such row exists. Image Contained? is Yes when at least one ImageAttachmentEntity '
                 'row names the message in parentMessageId, and No otherwise; the number of images '
                 'is not reported. Timestamp is the MessageEntity date column as stored, with no '
                 'conversion; its stored format and time zone are not established, so the column '
                 'is reported as text and not as a date and time. Status is transmissionStatus as '
                 'stored. No direction column is reported; a separate Romeo parser by this '
                 "module's author treats a transmissionStatus that reads sent, in any letter case, "
                 'as outgoing and one that reads received as incoming (https://github.com/kalink0/bubbly/blob/'
                 '8770cbdb03ec13cfa83906d1126b01d638a22deb/parsers/romeo_android_db.py#L193-L198). '
                 'No registered test image holds this database, so none of the above was measured '
                 'on real data; the row handling was exercised on a constructed database only.',
        'paths': (
            '*/com.planetromeo.android.app/databases/planetromeo-room.db.*' 
            ),
        'output_types': 'standard',
        'artifact_icon': 'message'
    },
    'romeo_dating_contacts': {
        'name': 'Romeo Dating App Contacts',
        'description': 'Parses contacts from the ContactEntity table of the Romeo Android app database, joined to ChatPartnerEntity.',
        'author': 'Marco Neumann {kalinko@be-binary.de}',
        'version': '0.0.1',
        'creation_date': '2026-02-25',
        'last_update_date': '2026-10-04',
        'requirements': '',
        'category': 'Contacts',
        'notes': 'Last Fetched and Deleted are fetchDate and deletionDate read as Unix milliseconds, an '
                 'assumed unit: no source for the unit was found and no registered test image holds '
                 'this database. A stored value that is NULL or 0 is reported blank, so a blank '
                 'Deleted cell means no deletion date is stored on that row. A stored value that is '
                 'not a number is reported as stored. '
                 'A contact with no ChatPartnerEntity row is not reported. The blank handling was '
                 'exercised on a constructed database only.',
        'paths': (
            '*/com.planetromeo.android.app/databases/planetromeo-room.db.*'
            ),
        'output_types': 'standard',
        'artifact_icon': 'users'
    },
    'romeo_dating_accounts': {
        'name': 'Romeo Dating App Accounts',
        'description': 'Account records from the Romeo dating app accounts database, with location, headline, profile text and dates',
        'author': 'Marco Neumann {kalinko@be-binary.de}',
        'version': '0.0.1',
        'creation_date': '2026-02-25',
        'last_update_date': '2026-10-04',
        'requirements': '',
        'category': 'Accounts',
        'notes': 'Creation Date and Last Login Date are the creation_date and last_login values of '
                 'the profile JSON as stored, with no conversion. Their stored format and time zone '
                 'are not established, so both columns are reported as text and not as a date and '
                 'time. No registered test image holds this database.',
        'paths': (
            '*/com.planetromeo.android.app/databases/accounts.db*'
            ),
        'output_types': 'standard',
        'artifact_icon': 'user'
    }
}


from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records


def _ms_to_utc(value):
    # A NULL or zero stored value is no date: report it blank rather than as the epoch.
    if value is None:
        return ''
    try:
        millis = int(value)
    except (TypeError, ValueError):
        return value
    if millis == 0:
        return ''
    return convert_unix_ts_to_utc(millis / 1000)

@artifact_processor
def romeo_dating_messages(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]

    main_db = ''
    data_list = []
    source_paths = set()

    query = '''
            SELECT me.date [Timestamp],
            me.chatPartnerId [Contact ID],
            cpe.name [Contact Name],
            me.text [Message Text],
            me.transmissionStatus [Status],
            me.saved [Saved?],
            me.unread [Unread?],
            me.messageId [Message ID],
            CASE WHEN EXISTS (
                SELECT 1 FROM ImageAttachmentEntity iae
                WHERE iae.parentMessageId = me.messageId
            )
            THEN
                "Yes"
            ELSE
                "No"
            END [Image Contained?]
            FROM MessageEntity me
            LEFT JOIN ChatPartnerEntity cpe ON cpe.profileId = me.chatPartnerId
            '''

    data_headers = (    'Timestamp',
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

    for file_found in files_found:
        main_db = str(file_found)
        source_db = context.get_relative_path(main_db)
        source_paths.add(main_db)

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
                                source_db
                            ))
        
        # On android we only know if an Image was part of the message,
        # content isn't on the phone anymore- so just "image contained?"

    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def romeo_dating_contacts(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]


    main_db = ''
    data_list = []
    source_paths = set()

    query = '''
            SELECT 
            cpe.fetchDate [Last Fetched Date],
            cpe.deletionDate [Deletion Date],
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
        source_db = context.get_relative_path(main_db)
        source_paths.add(main_db)

        db_records = get_sqlite_db_records(main_db, query)

        for row in db_records:
            fetch_timestamp = _ms_to_utc(row[0])
            delete_timestamp = _ms_to_utc(row[1])
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
                                source_db
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

    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def romeo_dating_accounts(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
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
                        'Creation Date',
                        'Last Login Date',
                        'Age',
                        'Birthdate'
                    )

    return data_headers, data_list, main_db
