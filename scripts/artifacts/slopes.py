__artifacts_v2__ = {
    "get_slopes": {
        "name": "Slopes - Resort Details",
        "description": "Parses ski resort details (name, location, coordinates, contact numbers, altitudes and run counts) recorded by the Slopes app from slopes.db.",
        "author": "",
        "creation_date": "2022-04-27",
        "last_update_date": "2022-04-27",
        "requirements": "none",
        "category": "Slopes",
        "notes": "",
        "paths": ('*/com.consumedbycode.slopes/databases/slopes.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "map-pin",
    },
    "get_slopes_actions": {
        "name": "Slopes - Actions",
        "description": "Parses recorded ski and snowboard actions (start and end time, duration, type, distance, coordinates, speed and altitude) from the Slopes slopes.db.",
        "author": "",
        "creation_date": "2022-04-27",
        "last_update_date": "2022-04-27",
        "requirements": "none",
        "category": "Slopes",
        "notes": "",
        "paths": ('*/com.consumedbycode.slopes/databases/slopes.db*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    },
    "get_slopes_lift": {
        "name": "Slopes - Lift Details",
        "description": "Parses ski lift details (name, type, capacity, start and end coordinates and resort) from the Slopes slopes.db.",
        "author": "",
        "creation_date": "2022-04-27",
        "last_update_date": "2022-04-27",
        "requirements": "none",
        "category": "Slopes",
        "notes": "",
        "paths": ('*/com.consumedbycode.slopes/databases/slopes.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "map-pin",
    }
}

import datetime
import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


def _slopes_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == 'slopes.db':
            return file_found
    return ''


@artifact_processor
def get_slopes(context):
    files_found = context.get_files_found()
    source_path = _slopes_db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
            select name, locality, admin_area, country, coordinate_lat, coordinate_long, website,
            generalNumber, skiPatrolNumber, baseAltitude, summitAltitude, distance,
            veryEasyRuns, easyRuns, intermediateRuns, expertRuns,
            case has_lift_data when 0 then '' when 1 then 'Yes' end as 'Has Ski Lift'
            from resort
        ''')
        data_list = cursor.fetchall()
        db.close()

    data_headers = ('Resort Name', 'City', 'State', 'Country', 'Latitude', 'Longitude', 'Website', 'General Number', 'Ski Patrol Number', 'Base Altitude', 'Summit Altitude', 'Distance', 'Very Easy Runs', 'Easy Runs', 'Intermediate Runs', 'Expert Runs', 'Has Ski Lift')
    return data_headers, data_list, source_path


@artifact_processor
def get_slopes_actions(context):
    files_found = context.get_files_found()
    source_path = _slopes_db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
            select action.start, action.end,
            strftime('%H:%M:%S', duration, 'unixepoch'),
            action.type, action.distance, action.max_lat, action.max_long, action.min_lat, action.min_long,
            action.avg_speed, action.top_speed, action.max_alt, action.min_alt, activity.location_name
            from action
            left join activity on activity.id = action.activity
        ''')
        for r in cursor.fetchall():
            data_list.append((_sec_to_utc(r[0]), _sec_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13]))
        db.close()

    data_headers = (('Timestamp (Start)', 'datetime'), ('Timestamp (End)', 'datetime'), 'Duration', 'Type', 'Distance (M)', 'Max Latitude', 'Max Longitude', 'Min Latitude', 'Min Longitude', 'Average Speed', 'Top Speed', 'Max Altitude', 'Min Altitude', 'Resort Name')
    return data_headers, data_list, source_path


@artifact_processor
def get_slopes_lift(context):
    files_found = context.get_files_found()
    source_path = _slopes_db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
            select lift.name, lift.type, lift.capacity, lift.start_lat, lift.start_long, lift.end_lat, lift.end_long,
            lift.pivots, lift.id, resort.name, resort.locality, resort.admin_area, resort.country
            from lift
            left join resort on resort.id = lift.resort
        ''')
        data_list = cursor.fetchall()
        db.close()

    data_headers = ('Name', 'Type', 'Capacity', 'Start Latitude', 'Start Longitude', 'End Latitude', 'End Longitude', 'Pivots', 'ID', 'Resort Name', 'City', 'State', 'Country')
    return data_headers, data_list, source_path
