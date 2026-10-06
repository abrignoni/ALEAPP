__artifacts_v2__ = {
    "get_nike_activMoments": {
        "name": "Nike - Activity Moments",
        "description": "Rows of the activity_moment table in the Nike Run Club app database "
                       "(com.nike.nrc.room), with the stored moment type and value",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}, @AlexisBrignoni, Codex",
        "creation_date": "2023-03-18",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Nike-Run",
        "notes": "One row per activity_moment row, ordered by activity and stored timestamp. "
                 "Moment Type and Value are as stored; their app meanings and units are "
                 "unverified, so no derived action or distance label is added. Timestamp "
                 "retains the existing Unix-millisecond conversion. The registered samples "
                 "recorded zero rows; positive genuine coverage remains unavailable. Only "
                 "the first database found is read. Run summaries are in Nike - Activities.",
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


@artifact_processor
def get_nike_activMoments(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        moments = _q(cursor, '''SELECT as2_m_activity_id, as2_m_timestamp_utc_ms, as2_m_type, as2_m_value
            FROM activity_moment ORDER BY as2_m_activity_id, as2_m_timestamp_utc_ms''')
        for row in moments:
            data_list.append((_ms_to_utc(row[1]), row[0], row[2], row[3]))
        db.close()

    data_headers = (('Timestamp', 'datetime'), 'Activity ID', 'Moment Type', 'Value')
    return data_headers, data_list, source_path
