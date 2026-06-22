# pylint: disable=W0613
__artifacts_v2__ = {
    "get_nike_activities": {
        "name": "Nike - Activities",
        "description": "User activities from the Nike Run app database (com.nike.nrc.room)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-03-18",
        "last_update_date": "2023-03-18",
        "requirements": "none",
        "category": "Nike-Run",
        "notes": "",
        "paths": ('*/com.nike.plusgps/databases/com.nike.nrc.room*',),
        "output_types": "standard",
        "artifact_icon": "activity",
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _round(value):
    try:
        return round(float(value), 2)
    except (ValueError, TypeError):
        return value


def _db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if 'com.nike.nrc.room' in file_found and not file_found.endswith(('wal', 'shm', '-journal')):
            return file_found
    return ''


def _q(cursor, sql, params):
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    except sqlite3.Error:
        return []


@artifact_processor
def get_nike_activities(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        activities = _q(cursor, 'SELECT * FROM activity', ())
        for row in activities:
            act_id = row[0]
            duration = _round(row[5] / 60000) if row[5] else ''
            name = location = version = temperature = weather = None
            calories = max_speed = mean_speed = steps = distance = pace = cadence = None

            for tag in _q(cursor, 'SELECT * FROM activity_tag WHERE as2_t_activity_id = ?', (act_id,)):
                key = tag[2]
                if key == 'com.nike.name':
                    name = tag[3]
                elif key == 'location':
                    location = tag[3]
                elif key == 'com.nike.running.recordingappversion':
                    version = tag[3]
                elif key == 'com.nike.temperature':
                    temperature = tag[3]
                elif key == 'com.nike.weather':
                    weather = tag[3]

            for summ in _q(cursor, 'SELECT * FROM activity_summary WHERE as2_s_activity_id = ?', (act_id,)):
                metric, val = summ[3], summ[6]
                if metric == 'calories':
                    calories = _round(val)
                elif metric == 'speed' and summ[5] == 'max':
                    max_speed = _round(val)
                elif metric == 'speed' and summ[5] == 'mean':
                    mean_speed = _round(val)
                elif metric == 'steps':
                    steps = val
                elif metric == 'distance':
                    distance = _round(val)
                elif metric == 'pace':
                    pace = _round(val)
                elif metric == 'cadence':
                    cadence = _round(val)

            data_list.append((act_id, name, _ms_to_utc(row[3]), _ms_to_utc(row[4]), location, row[2],
                              version, temperature, weather, duration, calories, max_speed, mean_speed,
                              steps, distance, pace, cadence))
        db.close()

    data_headers = ('Activity ID', 'Name', ('Start Time UTC', 'datetime'), ('End Time UTC', 'datetime'),
                    'Location', 'Source', 'Version', 'Temperature', 'Weather', 'Duration (min)',
                    'Calories', 'Max Speed', 'Mean Speed', 'Steps', 'Distance', 'Pace', 'Cadence')
    return data_headers, data_list, source_path
