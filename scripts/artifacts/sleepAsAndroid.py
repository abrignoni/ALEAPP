__artifacts_v2__ = {
    "sleepasandroid_records": {
        "name": "Sleep as Android - Sleep Records",
        "description": "Rows from the records table of sleep-track.db, each a tracked sleep "
                       "session with its start and end, the timezone the record carries and the "
                       "measures the application scored for it",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Sleep as Android",
        "notes": "com.urbandroid.sleep tracks sleep sessions, so a row bounds a period the "
                 "application recorded as sleep for the device it ran on. startTime and toTime "
                 "are Unix milliseconds and are reported in UTC. The record also stores its own "
                 "IANA timezone name, so Start and End are given again in that zone rather than "
                 "in one assumed by this parser, and the zone itself is in its own column so the "
                 "conversion can be redone. Latest To Time is a third stored time whose relation "
                 "to the other two is not established, so it is reported without interpretation. "
                 "Quality, Rating, Cycles, Snore and Noise Level are the application's own "
                 "measures; Snore and Noise Level held -1 on every row of the corpus below, "
                 "which is the value the columns carry when nothing was recorded rather than a "
                 "measurement of zero, and Rating held 0.0 on every row. Comment is a free text "
                 "field and held a tag on every row below. The geo column, which would carry a "
                 "location for the session, was empty on every row below, so no location was "
                 "recorded there. The recordData, recordFullData and recordNoiseData columns "
                 "hold the raw movement and sound series as binary and are not reported, being "
                 "large and not readable as evidence without the application; their presence is "
                 "reported as a byte length instead. Several columns were uniform across the "
                 "single corpus below and are kept because they separate sessions on an "
                 "extraction holding more than one device or setting: Stored Timezone held "
                 "one zone throughout, Finished held 1 on every row, Length Adjust held 0, "
                 "and Frame Rate held one value. Record Full Data Bytes was empty and Record "
                 "Noise Data Bytes held 0 on every row, meaning the application stored only "
                 "the first of its three raw series on that device.",
        "paths": ('*/com.urbandroid.sleep/databases/sleep-track.db*',),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.urbandroid.sleep | 7 rows",
        },
    },
    "sleepasandroid_alarms": {
        "name": "Sleep as Android - Alarms",
        "description": "Rows from the alarms table of alarms.db, each an alarm configured in "
                       "the application with its time, the days it repeats and its label",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Sleep as Android",
        "notes": "An alarm row records a configured wake time rather than an event that "
                 "happened. Hour and Minutes are the configured time of day as stored, in "
                 "whatever zone the device was set to, and carry no date. Days Of Week (as "
                 "stored) is the schema's own integer and is not expanded into day names, no "
                 "source for its bit layout having been located; on the corpus below it held 31 "
                 "and 96. Alarm Time is stored as a Unix millisecond value and was empty on both "
                 "rows below, so no next firing time was recorded. Enabled held 0 on both rows "
                 "there, so neither alarm was recorded as enabled, and Message and Alert were "
                 "empty, so neither carried a label or a chosen sound. Those columns are kept "
                 "because a populated value on another extraction is the point of the "
                 "artifact.",
        "paths": ('*/com.urbandroid.sleep/databases/alarms.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.urbandroid.sleep | 2 rows",
        },
    },
}

import os

import pytz

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    convert_utc_human_to_timezone,
    get_sqlite_db_records,
    logfunc,
)

SIDECARS = ('-wal', '-shm', '-journal')


def _databases(context, name):
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or file_found.endswith(SIDECARS):
            continue
        if os.path.basename(file_found) == name:
            found.append(file_found)
    return found


def _in_zone(utc_value, zone_name):
    """The same instant in the zone the record itself names, or '' if it cannot be."""
    if not utc_value or not zone_name:
        return ''
    try:
        return convert_utc_human_to_timezone(utc_value, zone_name)
    except (pytz.exceptions.UnknownTimeZoneError, ValueError, TypeError) as error:
        logfunc(f'Sleep as Android: could not apply the stored timezone {zone_name!r}: {error}')
        return ''


@artifact_processor
def sleepasandroid_records(context):
    data_list = []
    source_paths = []

    for db_path in _databases(context, 'sleep-track.db'):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT startTime, toTime, latestToTime, timezone, quality, rating, comment,
                   cycles, snore, noiseLevel, finished, lenAdjust, framerate, geo,
                   length(recordData), length(recordFullData), length(recordNoiseData), _id
            FROM records ORDER BY startTime
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            (start, end, latest, zone, quality, rating, comment, cycles, snore, noise,
             finished, adjust, framerate, geo, raw_len, full_len, noise_len, row_id) = row
            start_utc = convert_unix_ts_to_utc(start / 1000) if start else ''
            end_utc = convert_unix_ts_to_utc(end / 1000) if end else ''
            data_list.append((
                start_utc,
                end_utc,
                _in_zone(start_utc, zone),
                _in_zone(end_utc, zone),
                zone or '',
                convert_unix_ts_to_utc(latest / 1000) if latest else '',
                quality if quality is not None else '',
                rating if rating is not None else '',
                comment or '',
                cycles if cycles is not None else '',
                snore if snore is not None else '',
                noise if noise is not None else '',
                finished if finished is not None else '',
                geo or '',
                adjust if adjust is not None else '',
                framerate if framerate is not None else '',
                raw_len if raw_len is not None else '',
                full_len if full_len is not None else '',
                noise_len if noise_len is not None else '',
                row_id if row_id is not None else '',
            ))

    data_headers = (
        ('Start', 'datetime'),
        ('End', 'datetime'),
        'Start In Stored Timezone',
        'End In Stored Timezone',
        'Stored Timezone',
        ('Latest To Time', 'datetime'),
        'Quality',
        'Rating',
        'Comment',
        'Cycles',
        'Snore',
        'Noise Level',
        'Finished',
        'Geo',
        'Length Adjust',
        'Frame Rate',
        'Record Data Bytes',
        'Record Full Data Bytes',
        'Record Noise Data Bytes',
        'Record ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def sleepasandroid_alarms(context):
    data_list = []
    source_paths = []

    for db_path in _databases(context, 'alarms.db'):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT hour, minutes, daysofweek, enabled, alarmtime, message, alert, vibrate,
                   suspendtime, ndswakeupwindow, captcha, _id
            FROM alarms ORDER BY hour, minutes
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            (hour, minutes, days, enabled, alarm_time, message, alert, vibrate,
             suspend, window, captcha, row_id) = row
            data_list.append((
                convert_unix_ts_to_utc(alarm_time / 1000) if alarm_time else '',
                hour if hour is not None else '',
                minutes if minutes is not None else '',
                days if days is not None else '',
                enabled if enabled is not None else '',
                message or '',
                alert or '',
                vibrate if vibrate is not None else '',
                suspend if suspend is not None else '',
                window if window is not None else '',
                captcha if captcha is not None else '',
                row_id if row_id is not None else '',
            ))

    data_headers = (
        ('Alarm Time', 'datetime'),
        'Hour',
        'Minutes',
        'Days Of Week (as stored)',
        'Enabled',
        'Message',
        'Alert',
        'Vibrate',
        'Suspend Time (as stored)',
        'Wakeup Window',
        'Captcha (as stored)',
        'Row ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)
