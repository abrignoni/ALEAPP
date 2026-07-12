# pylint: disable=W0613
__artifacts_v2__ = {
    "get_nike_activMoments": {
        "name": "Nike - Activity Moments",
        "description": "Per-activity moments (pauses, resumes, splits, GPS signal events) from the Nike Run app database (com.nike.nrc.room)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-03-18",
        "last_update_date": "2023-03-18",
        "requirements": "none",
        "category": "Nike-Run",
        "notes": "Interactive JS timeline replaced with a structured table (one row per activity moment); "
                 "run start/end and summary metrics are covered by the 'Nike - Activities' artifact.",
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


def _db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if 'com.nike.nrc.room' in file_found and not file_found.endswith(('wal', 'shm', '-journal')):
            return file_found
    return ''


def _q(cursor, sql, params=()):
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    except sqlite3.Error:
        return []


def _moment_desc(mtype, mvalue):
    if mtype == 'halt':
        if mvalue in ('auto_pause', 'pause'):
            return 'Run paused'
        if mvalue in ('auto_resume', 'resume'):
            return 'Run resumed'
    elif mtype in ('split_km', 'lap'):
        return f'Split KM - {mvalue}'
    elif mtype == 'split_mile':
        return f'Split Mile - {mvalue}'
    elif mtype == 'gps_signal':
        if mvalue == 'lost':
            return 'GPS signal lost'
        if mvalue == 'found':
            return 'GPS signal found'
    return ''


@artifact_processor
def get_nike_activMoments(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        moments = _q(cursor, '''SELECT as2_m_activity_id, as2_m_timestamp_utc_ms, as2_m_type, as2_m_value
            FROM activity_moment ORDER BY as2_m_activity_id, as2_m_timestamp_utc_ms''')
        for row in moments:
            data_list.append((row[0], _ms_to_utc(row[1]), row[2], row[3], _moment_desc(row[2], row[3])))
        db.close()

    data_headers = ('Activity ID', ('Timestamp', 'datetime'), 'Moment Type', 'Value', 'Description')
    return data_headers, data_list, source_path
