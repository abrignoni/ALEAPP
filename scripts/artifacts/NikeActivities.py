__artifacts_v2__ = {
    "get_nike_activities": {
        "name": "Nike - Activities",
        "description": "User activities from the Nike Run app database (com.nike.nrc.room)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-03-18",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Nike-Run",
        "notes": "The activity id, start time, end time and duration are resolved by column name "
                 "(as2_sa_id, as2_sa_start_utc_ms, as2_sa_end_utc_ms, as2_sa_active_duration_ms), the "
                 "same names the Nike - Activity Route artifact selects, so a schema change fails "
                 "instead of relabelling another column. The value reported under 'Source', and the "
                 "columns read from activity_tag and activity_summary, are still read by position; "
                 "that mapping was established against the app version this parser was written for "
                 "and may not hold on other versions.",
        "paths": ('*/com.nike.plusgps/databases/com.nike.nrc.room*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsunga53_a14": "Android 14 | com.nike.plusgps vc 1717605525 | 0 rows",
            "userb2_a13": "Android 13 | com.nike.plusgps vc 1717303105 | 0 rows",
        },
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
def get_nike_activities(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        activities = _q(cursor, 'SELECT * FROM activity', ())
        # Resolve the id, timestamp and duration columns by name -- the names NikePolyline selects --
        # so a schema change raises here instead of relabelling another column as a start or end time.
        columns = [column[0] for column in cursor.description] if activities else []
        for row in activities:
            act_id = row[columns.index('as2_sa_id')]
            start_time = _ms_to_utc(row[columns.index('as2_sa_start_utc_ms')])
            end_time = _ms_to_utc(row[columns.index('as2_sa_end_utc_ms')])
            active_duration = row[columns.index('as2_sa_active_duration_ms')]
            duration = _round(active_duration / 60000) if active_duration else ''
            source = row[2]  # column name not established; read by position
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

            data_list.append((act_id, name, start_time, end_time, location, source,
                              version, temperature, weather, duration, calories, max_speed, mean_speed,
                              steps, distance, pace, cadence))
        db.close()

    data_headers = ('Activity ID', 'Name', ('Start Time UTC', 'datetime'), ('End Time UTC', 'datetime'),
                    'Location', 'Source', 'Version', 'Temperature', 'Weather', 'Duration (min)',
                    'Calories', 'Max Speed', 'Mean Speed', 'Steps', 'Distance', 'Pace', 'Cadence')
    return data_headers, data_list, source_path
