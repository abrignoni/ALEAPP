__artifacts_v2__ = {
    "healthmate_accounts": {
        "name": "Health Mate - Accounts",
        "description": "Health Mate Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
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
        "description": "Tracking records with stored activity category IDs and names from a paired local lookup.",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2024-04-20",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-2.html "
                 "Columns of the Track table are read by position; the mapping was written "
                 "against app versions 5.1.4 (Android 6) and 6.3.1 (Android 13), the versions "
                 "recorded in the module's comment header, and may not hold on other versions. "
                 "Stored Activity Category Name is read without interpretation from id and name "
                 "in activityCategory of the unique Withings-WiScale main in the same physical "
                 "and evidence-relative app databases folder as the selected room-healthmate main. "
                 "Only the first eligible room main is read. Missing, conflicting or unreadable "
                 "lookups retain the tracking row and Activity Category ID, with Category Lookup "
                 "Status explaining why no stored name is supplied. The artifact source indicator "
                 "includes the lookup only when its table was successfully consulted. NULL and "
                 "empty stored names have separate statuses. IDs and names are matched by stored "
                 "type and value; conflicting names for an ID are not selected. "
                 "The cited post proposes 37 = Sleeping and 272 = Activity started on watch "
                 "without explaining their derivation. The prior parser labelled 272 Activity "
                 "Tracking started manually. These remain unverified research interpretations, "
                 "not stored lookup names, and never override activityCategory values.",
        "paths": ('*/com.withings.wiscale2/databases/room-healthmate*',
                  '*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "healthmate_locations": {
        "name": "Health Mate - Locations",
        "description": "Health Mate Locations",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-04-20",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-3-heart.html "
                 "Columns of the WorkoutLocation table, including Latitude and Longitude, are read by "
                 "position; the mapping was written against app versions 5.1.4 (Android 6) and "
                 "6.3.1 (Android 13), the versions recorded in the module's comment header, and "
                 "may not hold on other versions.",
        "paths": ('*/com.withings.wiscale2/databases/room-healthmate*'),
        "output_types": "standard",
        "artifact_icon": "map-pin"
    },
    "healthmate_messages": {
        "name": "Health Mate - Messages",
        "description": "Health Mate Messages",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-04-20",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html "
                 "Columns of the chat table are read by position (the cited post, written against "
                 "app 5.1.4, names the table chats); the mapping was written "
                 "against app versions 5.1.4 (Android 6) and 6.3.1 (Android 13), the versions "
                 "recorded in the module's comment header, and may not hold on other versions.",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "output_types": "standard",
        "artifact_icon": "message"
    },
    "healthmate_contacts": {
        "name": "Health Mate - Leaderboard",
        "description": "Health Mate leaderboard entries (leaderboard table)",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-04-21",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html "
                 "Columns of the leaderboard table of the room-healthmate database are read by "
                 "position (the cited post, written against app 5.1.4, found the table in "
                 "Withings-WiScale); the mapping was written "
                 "against app versions 5.1.4 (Android 6) and 6.3.1 (Android 13), the versions "
                 "recorded in the module's comment header, and may not hold on other "
                 "versions.",
        "paths": ('*/com.withings.wiscale2/databases/room-healthmate*'),
        "output_types": "standard",
        "artifact_icon": "users"
    },
    "healthmate_measurements": {
        "name": "Health Mate - Measurements",
        "description": "Health Mate Measurements",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2024-04-21",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on "
                 "https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-3-heart.html "
                 "The Category names for -16 (Heart Rate) and 16 (Steps) come from that post; the "
                 "meanings of -19 and -22 are not established, so these values receive no "
                 "mapped name and use the Unknown Category ID label. Category ID is retained "
                 "as stored. "
                 "Columns of the vasistas table, including the values reported as SPO2 and Core "
                 "Temperature, are read by position; the mapping was written against app "
                 "versions 5.1.4 (Android 6) and 6.3.1 (Android 13), the versions recorded in "
                 "the module's comment header, and may not hold on other versions.",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    },
    "healthmate_devices": {
        "name": "Health Mate - Devices",
        "description": "Health Mate Devices",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-04-21",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html "
                 "Columns of the devices table, including the value reported as the Last Used "
                 "Timestamp and the Latitude/Longitude pair, are read by position; the mapping was "
                 "written against app versions 5.1.4 (Android 6) and 6.3.1 (Android 13), the "
                 "versions recorded in the module's comment header, and may not "
                 "hold on other versions.",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "output_types": "standard",
        "artifact_icon": "activity"
    }
}

# Withings Health Mate App (com.withings.wiscale2)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.2
#
# Tested with the following versions:
# 2020-10-09: Android 6, App: 5.1.4
# 2024-04-20: Android 13, App: 6.3.1

# Requirements:  none
import sqlite3
from pathlib import Path, PurePosixPath

from scripts.ilapfuncs import (artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records,
                              get_sqlite_db_path, logfunc)


@artifact_processor
def healthmate_accounts(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
    file_found = str(files_found[0])

    query = '''
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
    '''

    db_records = get_sqlite_db_records(file_found, query)

    data_list = []

    for row in db_records:
        user_id = row[0]
        lastname = row[1]
        firstname = row[2]
        shortname = row[3]
        gender = row[4]
        pronoun = row[5]
        # Tested against the value, not against zero: a birth date before 1970 is stored
        # negative, and comparing it away reported the field as 0 rather than as a date.
        if row[6]:
            birthdate = convert_unix_ts_to_utc(row[6]/1000)
        else:
            birthdate = 0
        fatmethod = row[7]
        email = row[8]
        creationdate = convert_unix_ts_to_utc(row[9]/1000)
        modifieddate = convert_unix_ts_to_utc(row[10]/1000)
        bodymodel = row[11]

        data_list.append((
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

    data_headers = ((
        'Creation Date', 'datetime'),
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


def _tracking_mains(context, basename):
    """Exact supplied mains, retaining their physical and evidence namespace."""
    mains = []
    seen = set()
    for candidate in context.get_files_found():
        path = str(candidate)
        if (path in seen or not Path(path).is_file() or Path(path).is_symlink()
                or Path(path).name != basename):
            continue
        relative = PurePosixPath(context.get_relative_path(path).replace('\\', '/'))
        if (relative.name != basename or relative.parent.name != 'databases'
                or relative.parent.parent.name != 'com.withings.wiscale2'):
            continue
        seen.add(path)
        mains.append((path, relative))
    return mains


def _tracking_categories(context, room_db, room_relative):
    """An optional exact sibling lookup; failures cannot discard tracking rows."""
    candidates = [item for item in _tracking_mains(context, 'Withings-WiScale')
                  if item[1].parent == room_relative.parent]
    if not candidates:
        logfunc(f'Withings Trackings: missing lookup for {room_relative}')
        return {}, 'missing-lookup', ''
    if len(candidates) != 1 or Path(candidates[0][0]).parent != Path(room_db).parent:
        logfunc(f'Withings Trackings: ambiguous lookup namespace for {room_relative}')
        return {}, 'ambiguous-lookup', ''
    wiscale_db, relative = candidates[0]
    db = None
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(wiscale_db)}?mode=ro', uri=True)
        wiscale_query = '''
        SELECT id, name
        FROM activityCategory
    '''

        categories = {}
        for category_id, name in db.execute(wiscale_query):
            if category_id is not None:
                categories.setdefault((type(category_id), category_id), set()).add((type(name), name))
        return categories, 'ready', wiscale_db
    except sqlite3.Error as error:
        status = ('unsupported-lookup-schema' if 'no such table' in str(error)
                  or 'no such column' in str(error) else 'unreadable-lookup')
        logfunc(f'Withings Trackings: {status} in {relative}')
        return {}, status, ''
    finally:
        if db is not None:
            db.close()


def _tracking_category_name(category_id, categories, lookup_status):
    """Keep NULL, empty and conflicting stored names distinct from absence."""
    if category_id is None:
        return '', 'missing-category-ID'
    if lookup_status != 'ready':
        return '', lookup_status
    names = categories.get((type(category_id), category_id))
    if not names:
        return '', 'category-not-listed'
    if len(names) != 1:
        return '', 'ambiguous-category'
    name = next(iter(names))[1]
    return name, ('matched-NULL-name' if name is None else 'matched-empty-name' if name == ''
                  else 'matched-name')


@artifact_processor
def healthmate_trackings(context):
    room_mains = _tracking_mains(context, 'room-healthmate')
    room_db = room_mains[0][0] if room_mains else ''
    activity_categories, lookup_status, wiscale_db = (
        _tracking_categories(context, *room_mains[0]) if room_mains else ({}, 'missing-lookup', ''))
    if len(room_mains) > 1:
        logfunc('Withings Trackings: first eligible room main only; other room states are not read')

    # get activities from database room-healthmate*
    room_query = ('''
        SELECT *
        FROM Track;
    ''')

    db_records_room_db = get_sqlite_db_records(room_db, room_query)

    data_list = []
    logged = set()

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
        category_name, category_status = _tracking_category_name(
            category_id, activity_categories, lookup_status)
        if category_status == 'ambiguous-category' and (type(category_id), category_id) not in logged:
            logfunc(f'Withings Trackings: ambiguous category {repr(category_id)[:80]} in '
                    f'{context.get_relative_path(wiscale_db)}')
            logged.add((type(category_id), category_id))
        datajson = row[13]

        data_list.append((
            starttime,
            endtime,
            modifiedtime,
            entry_id,
            wsid,
            userid,
            device_id,
            device_modell,
            category_id,
            category_name,
            datajson,
            category_status))

    if isinstance(db_records_room_db, sqlite3.Cursor):
        db_records_room_db.connection.close()

    data_headers = (
        ('Start Time', 'datetime'),
        ('End Time', 'datetime'),
        ('Modified Time', 'datetime'),
        'ID',
        'wsId',
        'UserID',
        'Device ID',
        'Device Model',
        'Activity Category ID',
        'Stored Activity Category Name',
        'Tracking Data',
        'Category Lookup Status'
    )

    return data_headers, data_list, '\n'.join(path for path in (room_db, wiscale_db) if path)


@artifact_processor
def healthmate_locations(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]

    file_found = str(files_found[0])
    query = '''
        SELECT *
        FROM WorkoutLocation;
    '''
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

        data_list.append(
            (date,
             row_id,
             userid,
             speed,
             h_accuracy,
             altitude,
             v_accuracy,
             lat,
             lon)
        )

    data_headers = (
        ('Timestamp', 'datetime'),
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
def healthmate_messages(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]

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

        data_list.append(
            (date,
             row_id,
             senderid,
             receiverid,
             message,
             message_type)
        )

    data_headers = (
        ('Timestamp', 'datetime'),
        'Message ID',
        'Sender ID',
        'Receiver ID',
        'Message',
        'Type'
    )

    return data_headers, data_list, files_found[0]


@artifact_processor
def healthmate_contacts(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]

    query = '''
        SELECT *
        FROM leaderboard;
    '''

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

        data_list.append(
            (modified,
             row_id,
             date,
             userid,
             score,
             firstname,
             lastname,
             imageurl
             )
        )

    data_headers = (
        ('Modified Timestamp', 'datetime'),
        'ID',
        'Date',
        'User ID',
        'Score',
        'First Name',
        'Last Name',
        'Image URL',)
    return data_headers, data_list, files_found[0]


@artifact_processor
def healthmate_measurements(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]

    query = '''
        Select *
        from vasistas;
    '''
    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        row_id = row[0]
        category_id = row[24]
        match category_id:
            case -16:
                category = 'Heart Rate'
            case 16:
                category = 'Steps'
            case _:
                category = 'Unknown Category ID'
        timestamp = convert_unix_ts_to_utc(row[4]/1000)
        userid = row[1]
        duration = row[5]
        steps = row[11]
        distance = row[12]
        ascent = row[13]
        descent = row[14]
        heartrate = row[18]
        spo2 = row[32]
        spo2_quality = row[33]
        swim_laps = row[23]
        swim_movements = row[22]
        temperature = row[42]

        data_list.append(
            (timestamp,
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

    data_headers = (
        ('Timestamp', 'datetime'),
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
        'Core Temperature')

    return data_headers, data_list, files_found[0]


@artifact_processor
def healthmate_devices(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]

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

        data_list.append(
            (assdate,
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

    data_headers = (
        ('Association Timestamp', 'datetime'),
        ('Last Used Timestamp', 'datetime'),
        ('Modified Timestamp', 'datetime'),
        'ID',
        'User ID',
        'MAC',
        'Firmware',
        'Latitude',
        'Longitude',
        'Device Type',
        'Device Model')

    return data_headers, data_list, files_found[0]
