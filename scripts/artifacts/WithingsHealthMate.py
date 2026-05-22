# Withings Health Mate App (com.withings.wiscale2)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.2
# 
# Tested with the following versions:
# 2020-10-09: Android 6, App: 5.1.4
# 2024-04-20: Android 13, App: 6.3.1

# Requirements:  datetime

__artifacts_v2__ = {

    
    "healthmate_accounts": {
        "name": "Health Mate - Accounts",
        "description": "Health Mate Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.1",
        "creation_date": "2024-04-20",
        "last_update_date": "2026-05-14",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "healthmate_trackings": {
        "name": "Health Mate - Trackings",
        "description": "Health Mate Trackings",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.1",
        "creation_date": "2024-04-20",
        "last_update_date": "2026-05-14",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-2.html",
        "paths": (  '*/com.withings.wiscale2/databases/room-healthmate*',
                    '*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "healthmate_locations": {
        "name": "Health Mate - Locations",
        "description": "Health Mate Locations",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.1",
        "creation_date": "2024-04-20",
        "last_update_date": "2026-05-14",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-3-heart.html",
        "paths": ('*/com.withings.wiscale2/databases/room-healthmate*'),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    },
    "healthmate_messages": {
        "name": "Health Mate - Messages",
        "description": "Health Mate Messages",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.1",
        "creation_date": "2024-04-20",
        "last_update_date": "2026-05-14",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "output_types": "standard",
        "artifact_icon": "message-square"
    },
    "healthmate_contacts": {
        "name": "Health Mate - Contacts",
        "description": "Health Mate Contacts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.1",
        "creation_date": "2024-04-21",
        "last_update_date": "2026-05-14",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html",
        "paths": ('*/com.withings.wiscale2/databases/room-healthmate*'),
        "output_types": "message-square",
        "artifact_icon": "users"
    },
    "healthmate_measurements": {
        "name": "Health Mate - Measurements",
        "description": "Health Mate Measurements",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.1",
        "creation_date": "2024-04-21",
        "last_update_date": "2026-05-14",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-3-heart.html",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "healthmate_devices": {
        "name": "Health Mate - Devices",
        "description": "Health Mate Devices",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.1",
        "creation_date": "2024-04-21",
        "last_update_date": "2026-05-14",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records

@artifact_processor
def healthmate_accounts(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])

    query =('''
        SELECT
        id [User ID],
        lastname [Last Name],
        firstname [First Name],
        shortname [Short Name],
        gender [Gender],
        pronoun [Pronoun],
        birthdate [Birthdate],
        fatmethod [Fat Method],
        email [E-Mail],
        creationdate [Creation Date],
        modifieddate [Modified Date],
        bodymodel [Body Model]
        FROM users
    ''')
    
    db_records = get_sqlite_db_records(file_found, query)

    data_list = []

    for row in db_records:
        user_id = row[0]
        lastname = row[1]
        firstname = row[2]
        shortname = row[3]
        gender = row[4]
        pronoun = row[5]
        if row[6] > 0:
            birthdate = convert_unix_ts_to_utc(row[6]/1000)
        else:
            birthdate = 0
        fatmethod = row[7]
        email = row[8]
        creationdate = convert_unix_ts_to_utc(row[9]/1000)
        modifieddate = convert_unix_ts_to_utc(row[10]/1000)
        bodymodel = row[11]


        data_list.append(   (
                            creationdate,
                            user_id,
                            lastname,
                            firstname,
                            shortname,
                            gender,
                            pronoun,
                            birthdate,
                            fatmethod,
                            email,
                            modifieddate,
                            bodymodel)
                        )

    data_headers = (    ('Creation Date', 'datetime'),
                        'User ID',
                        'Last Name',
                        'First Name',
                        'Short Name',
                        'Gender',
                        'Pronoun',
                        ('Birthdate', 'datetime'),
                        'Fat Method',
                        'E-Mail',
                        ('Modified Date', 'datetime'),
                        'Body Model',
                    )

    return data_headers, data_list, file_found

@artifact_processor
def healthmate_trackings(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    room_db = next((str(f) for f in files_found if 'room-healthmate' in str(f).lower()), None)
    wiscale_db = next((str(f) for f in files_found if 'withings-scale' in str(f).lower()), None)

    wiscale_query = ('''
        SELECT id, name
        FROM activityCategory
    ''')

    db_records_wiscale_db = get_sqlite_db_records(wiscale_db, wiscale_query)

    activity_categories = {}
    if len(db_records_wiscale_db) > 0:
        for category in db_records_wiscale_db:
            activity_categories[category[0]] = category[1]
            # add activity categories that are not part of the listing but were recognizable by manual analysis
        activity_categories[37] = 'Sleeping'
        activity_categories[272] = 'Activity Tracking started manually'

    # get activities from database room-healthmate*
    room_query = ('''
        SELECT *
        FROM Track;
    ''')

    db_records_room_db = get_sqlite_db_records(room_db, room_query)

    data_list = []

    for row in db_records_room_db:
        entry_id = row[0]
        wsid = row[1]
        userid = row[2]
        starttime = convert_unix_ts_to_utc(row[3]/1000)
        endtime = convert_unix_ts_to_utc(row[4]/1000)
        modifiedtime = convert_unix_ts_to_utc(row[7]/1000)
        device_id = row[9]
        device_modell = row[10]
        category_id = row[12]
        try:
            category_name = activity_categories[category_id]
        except KeyError:
            category_name = "Not listed - Unknown"
        datajson = row[13]

        data_list.append((  starttime, 
                            endtime,
                            modifiedtime,
                            entry_id,
                            wsid,
                            userid,
                            device_id,
                            device_modell,
                            category_id,
                            category_name,
                            datajson))


    data_headers = (    ('Start Time', 'datetime'),
                        ('End Time', 'datetime'),
                        ('Modified Time', 'datetime'),
                        'ID',
                        'wsId',
                        'UserID',
                        'Device ID',
                        'Device Model',
                        'Activity Category ID',
                        'Activity Category Name',
                        'Tracking Data'
                    )

    return data_headers, data_list, room_db

@artifact_processor
def healthmate_locations(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    query = ('''
        SELECT *
        FROM WorkoutLocation;
    ''')
    db_records = get_sqlite_db_records(file_found, query)

    data_list = []

    for row in db_records:
        row_id = row[0]
        userid = row[1]
        date = convert_unix_ts_to_utc(row[2]/1000)
        speed = row[3]
        h_accuracy = row[4]
        altitude = row[5]
        v_accuracy = row[6]
        lat = row[7]
        lon = row[8]            

        data_list.append(   (date,
                            row_id,
                            userid,
                            speed,
                            h_accuracy,
                            altitude,
                            v_accuracy,
                            lat,
                            lon)
                        )

    data_headers = (    ('Timestamp', 'datetime'), 
                        'ID',
                        'User ID',
                        'Speed',
                        'Horizontal Accuracy',
                        'Altitude',
                        'Vertical Accuracy',
                        'Latitude',
                        'Longitude')

    return data_headers, data_list, file_found
@artifact_processor
def healthmate_messages(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    query = ('''
        SELECT *
        FROM chat;
    ''')
    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        row_id = row[0]
        senderid = row[1]
        receiverid = row[2]
        date = convert_unix_ts_to_utc(row[3]/1000)
        message = row[4]
        message_type = row[6]
            
        data_list.append(   (date,
                            row_id,
                            senderid,
                            receiverid,
                            message,
                            message_type)
                        )

    data_headers = (    ('Timestamp', 'datetime'),
                        'Message ID',
                        'Sender ID',
                        'Receiver ID',
                        'Message',
                        'Type'
                    )

    return data_headers, data_list, files_found[0]

@artifact_processor
def healthmate_contacts(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    query = ('''
        SELECT *
        FROM leaderboard;
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        modified = convert_unix_ts_to_utc(row[7]/1000)
        row_id = row[0]
        date = row[1]
        userid = row[2]
        score = row[3]
        firstname = row[4]
        lastname = row[5]
        imageurl = row[6]
        

        data_list.append(   (modified,
                            date,
                            row_id,
                            userid,
                            score,
                            firstname,
                            lastname,
                            imageurl
                            )
                        )
    
    data_headers = (    ('Modified Timestamp', 'datetime'),
                        'ID',
                        'Date',
                        'User ID',
                        'Score',
                        'First Name',
                        'Last Name',
                        'Image URL',
                    )
    return data_headers, data_list, files_found[0]

@artifact_processor
def healthmate_measurements(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    query = ('''
        Select *
        from vasistas;
    ''')
    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        row_id = row[0]
        category_id = row[24]
        match category_id:
            case -22:
                category = 'Core Temperature'
            case -19:
                category = 'SPO2'
            case -16:
                category = 'Heart Rate'
            case 16:
                category = 'Steps'
            case _:
                category = 'Unknown Category ID'
        timestamp = datetime.datetime.fromtimestamp(row[4]/1000).strftime('%Y-%m-%d %H:%M:%S')
        userid = row[1]
        duration = row[5]
        steps = row[11]
        distance = row[12]
        ascent = row[13]
        descent = row[14]
        heartrate =row[18]
        spo2 = row[32]
        spo2_quality = row[33]
        swim_laps = row[23]
        swim_movements = row[22]
        temperature = row[42]
        

        data_list.append(   (timestamp,
                            row_id,
                            category_id,
                            category,
                            userid,
                            duration,
                            steps,
                            distance,
                            ascent,
                            descent,
                            heartrate,
                            spo2,
                            spo2_quality,
                            swim_laps,
                            swim_movements,
                            temperature))

    data_headers = (    ('Timestamp', 'datetime'),
                        'ID',
                        'Category ID',
                        'Category',
                        'User ID',
                        'Duration',
                        'Steps',
                        'Distance',
                        'Ascent',
                        'Descent',
                        'Heartrate',
                        'SPO2',
                        'SPO2 Quality',
                        'Swim Laps',
                        'Swim Movements',
                        'Core Temperature'
                    )

    return data_headers, data_list, files_found[0]

@artifact_processor
def healthmate_devices(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    query = ('''
        SELECT *
        FROM devices;
    ''')
    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        row_id = row[0]
        userid = row[1]
        assdate = convert_unix_ts_to_utc(row[2]/1000)
        lastdate = convert_unix_ts_to_utc(row[3]/1000)
        moddate = convert_unix_ts_to_utc(row[4]/1000)
        mac = row[5]
        firmware = row[6]
        lat = row[8]
        lon = row[9]  
        dev_type = row[14]  
        dev_modell = row[15]      

        data_list.append(   (assdate,
                            lastdate,
                            moddate,
                            row_id,
                            userid,
                            mac,
                            firmware,
                            lat,
                            lon,
                            dev_type,
                            dev_modell)
                        )

    data_headers = (    ('Association Timestamp', 'datetime'),
                        ('Last Used Timestamp', 'datetime'),
                        ('Modified Timestamp', 'datetime'),
                        'ID',
                        'User ID',
                        'MAC',
                        'Firmware',
                        'Latitude',
                        'Longitude',
                        'Device Type',
                        'Device Model'
                    )
    return data_headers, data_list, files_found[0]