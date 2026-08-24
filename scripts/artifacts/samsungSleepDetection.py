__artifacts_v2__ = {
    "samsungSleepScreenData": {
        "name": "Samsung Sleep Detection Screen Data",
        "description": "Screen state changes logged by the Samsung Continuity Service sleep "
                       "detection (SleepDetection.db, screen_data table), with the user "
                       "present and keyguard flags. State values are stored as raw integers "
                       "and are reported as-is.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Samsung Continuity Service",
        "notes": "The Time Text column is the device-local time string as stored.",
        "paths": ('*/com.samsung.android.mcfds/databases/SleepDetection.db*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.mcfds | 86 rows",
        },
    },
    "samsungSleepTime": {
        "name": "Samsung Sleep Detection Sleep Times",
        "description": "Sleep windows computed by the Samsung Continuity Service sleep "
                       "detection (SleepDetection.db, sleep_time table): the recorded start "
                       "and end of each window and when the record was written.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Samsung Continuity Service",
        "notes": "The *Text columns are the device-local time strings as stored.",
        "paths": ('*/com.samsung.android.mcfds/databases/SleepDetection.db*',),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.mcfds | 5 rows",
        },
    },
}

import re

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc


def _unique_db_files(context, name_suffix):
    '''Database files matching the suffix, without -journal/-wal/-shm sidecars and
    without the duplicates extractions carry for the same file (data_mirror, and
    /data/data next to /data/user/0).

    The dedupe key is the evidence-relative path, not the extracted path: the report's own
    data folder ends in /data, so a raw-path replace can rewrite the harness boundary
    instead of the evidence path on archives whose members start with data/.'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(name_suffix):
            continue
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if 'data_mirror' in relative:
            continue
        normalized = re.sub(r'(^|/)data/data/', r'\1data/user/0/', relative)
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(file_found)
    return result


@artifact_processor
def samsungSleepScreenData(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'SleepDetection.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT time, timeText, screenState, userPresent, useKeyGuard
            FROM screen_data
            ORDER BY time DESC
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                row[1],
                row[2],
                row[3],
                row[4],
            ))

    data_headers = (
        ('Time', 'datetime'),
        'Time Text (Device Local)',
        'Screen State',
        'User Present',
        'Use Keyguard',
    )
    return data_headers, data_list, source_path


@artifact_processor
def samsungSleepTime(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'SleepDetection.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT startTime, startTimeText, endTime, endTimeText, time, timeText,
                   ignoreSleep
            FROM sleep_time
            ORDER BY startTime DESC
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                row[1],
                convert_unix_ts_to_utc(row[2]),
                row[3],
                convert_unix_ts_to_utc(row[4]),
                row[5],
                row[6],
            ))

    data_headers = (
        ('Sleep Start', 'datetime'),
        'Sleep Start Text (Device Local)',
        ('Sleep End', 'datetime'),
        'Sleep End Text (Device Local)',
        ('Recorded', 'datetime'),
        'Recorded Text (Device Local)',
        'Ignore Sleep',
    )
    return data_headers, data_list, source_path
