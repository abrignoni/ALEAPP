__artifacts_v2__ = {
    "samsung_health_weight": {
        "name": "Samsung Health - Weight and Height (Preferences)",
        "description": "The weight and height values Samsung Health keeps in its own preferences file, with "
                       "the time stored beside them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Health",
        "notes": (
            'One row per Samsung Health container whose shared_prefs/temporary_sharedpreferences_main.xml '
            'holds tracker_weight_weight or tracker_weight_height. Values are read with an XML parser and '
            'shown as the stored text. Timestamp is tracker_weight_timestamp read as Unix milliseconds; Time '
            'Offset (ms, as stored) is tracker_weight_timeoffset, -18000000 (UTC-5) on the known-data image. '
            'Weight Unit Setting is tracker_weight_profile_unit from permanent_sharedpreferences_main.xml in '
            'the same container; whether the stored weight follows that setting is not established, since '
            "only kg was exercised. No height unit key was found in the app's shared_prefs on the known-data "
            'image. On samsung_a166u_a16_known_20261116 the profile was saved at 17:10:01 UTC with 170.0 cm '
            'and 70.0 kg (units switched to cm and kg), and the file held weight 70.0, height 170.0, unit kg '
            'and a Timestamp of 17:09:57.954 UTC, about 3 s before the logged save. The file holds one set of '
            'values, not a weight history: one row per container. Fat (as stored) and Skeletal Muscle Mass '
            '(as stored) held -1.0 and Weight Change (as stored) 0.0 on the known-data image, where none of '
            'them was entered; what -1.0 stands for is not established. tracker_weight_last_timestamp (the '
            'same value as Timestamp there) and tracker_weight_fatchange are not reported. The keys were '
            'absent from the same file on anne_a15, cookbook_a11, sharon_a13 and sharon_a14. Rows from '
            'several Android users are reported together and no column names the user. SecureHealthData.db, '
            'HealthFramework.db, HealthSharing.db, HealthSharingLogs.db, Permission.db, SdkPolicy.db and '
            'SportTracker.db have no SQLite header and byte entropy of 7.99 to 8.00 bits per byte on the '
            'known-data image, each with a <name>-se file beside it. SecureHealthData.db-wal has a WAL header '
            'and entropy of 8.00. None of them is read. No database key was identified: '
            'permanent_sharedpreferences_main.xml holds two AndroidX security-crypto keyset entries and '
            'files/ holds aks, aks_verify and aks_verify_iv, and what they protect is not established. The '
            'profile nickname and the text of the walking workout note made in the known-data session were '
            "not found by a byte search (UTF-8 and UTF-16) of the app's files outside those seven databases "
            'on the known-data image; whether the note was saved was not checked. Other plaintext stores hold '
            'values from the known-data session and are not reported: shared_prefs/sleep_card_cache.xml holds '
            'a period marked MANUAL from 04:00 to 12:00 UTC on 2026-11-16, and '
            'files/caches/preferences/sleep.watch_summary.*.pref (gzip) holds the same start and end; these '
            'match the manual sleep entry made in the session (11:00 PM to 7:00 AM local); '
            'shared_prefs/tracker_sport_recently_retrieved_workout_result_pref.xml holds a workout result of '
            'exercise type 1001 with times 17:00:37 and 17:01:07 UTC, which fits the walking workout ended at '
            "about 17:01:10 UTC; and the app's text logs (files/logs/m_*.txt and r_*.txt, app debug lines "
            'with local times and no zone) include exercise session lines. The other readable databases, '
            'shared_prefs files and files/caches/preferences files are not reported.'
        ),
        "paths": (
            '*/com.sec.android.app.shealth/shared_prefs/temporary_sharedpreferences_main.xml',
            '*/com.sec.android.app.shealth/shared_prefs/permanent_sharedpreferences_main.xml',
        ),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.shealth 6.30.3.011 | 1 row",
            "anne_a15": "Android 15 | com.sec.android.app.shealth | 0 rows",
            "cookbook_a11": "Android 11 | com.sec.android.app.shealth | 0 rows",
            "sharon_a13": "Android 13 | com.sec.android.app.shealth | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.shealth | 0 rows",
        },
    },
    "samsung_health_daily_steps": {
        "name": "Samsung Health - Daily Step Summary",
        "description": "The one-day step summary Samsung Health keeps in pedometer_setting.db.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Health",
        "notes": (
            'One row per pedometer_setting.db whose tracker_pedometer_temp_step_data key holds a JSON step '
            'summary, read with a JSON parser. The mStepCount, mWalkStepCount and mRunStepCount values are '
            'shown under their stored names; mDistance, mCalorie and mTotalActiveTime are as stored and their '
            'units are not established. Day Start is mStartTime read as Unix milliseconds, and Day is that '
            'instant as a calendar date in Time Zone, the tracker_pedometer_last_timezone value; on the '
            'known-data image Day Start was 05:00 UTC, local midnight in America/New_York. Last Step Logging '
            'Time is tracker_pedometer_last_allstep_logging_time read as Unix milliseconds; what event sets '
            'it is not established. This is a summary of one day, not a step history. On '
            'samsung_a166u_a16_known_20261116 it held 32 steps for 2026-11-16. That count is not confirmed by '
            'known data: the phone was carried for a short walk at about 17:02 to 17:04 UTC, and the app '
            'showed 0 steps at 17:04:45 and 17:10 UTC. The tracker_pedometer_temp_step_binning row in the '
            'same table holds 144 ten-minute bins for that day; two hold 16 steps each, starting 17:30 and '
            '17:40 UTC, after the walk (see the Step Bins artifact). Last Step Logging Time was 18:16:42 UTC, '
            '2 s after the Date value in the UFED .ufd (18:16:40 UTC); the .ufd EndTime is 18:54:19 UTC. When '
            'the summary itself was written is not established. The key step_allstep_last_count held the same '
            '32 and is not reported. pedometer_setting.db on anne_a15 and sharon_a14 did not hold the key. '
            'The other pedometer_setting rows are not reported; they include a data source list, sync, '
            'workout and update times, and settings. The goal_activity table (6 rows) is not reported. Rows '
            'from several Android users are reported together and no column names the user. '
            'SecureHealthData.db, HealthFramework.db, HealthSharing.db, HealthSharingLogs.db, Permission.db, '
            'SdkPolicy.db and SportTracker.db have no SQLite header and byte entropy of 7.99 to 8.00 bits per '
            'byte on the known-data image, each with a <name>-se file beside it. SecureHealthData.db-wal has '
            'a WAL header and entropy of 8.00. None of them is read. No database key was identified: '
            'permanent_sharedpreferences_main.xml holds two AndroidX security-crypto keyset entries and '
            'files/ holds aks, aks_verify and aks_verify_iv, and what they protect is not established. The '
            'profile nickname and the text of the walking workout note made in the known-data session were '
            "not found by a byte search (UTF-8 and UTF-16) of the app's files outside those seven databases "
            'on the known-data image; whether the note was saved was not checked. Other plaintext stores hold '
            'values from the known-data session and are not reported: shared_prefs/sleep_card_cache.xml holds '
            'a period marked MANUAL from 04:00 to 12:00 UTC on 2026-11-16, and '
            'files/caches/preferences/sleep.watch_summary.*.pref (gzip) holds the same start and end; these '
            'match the manual sleep entry made in the session (11:00 PM to 7:00 AM local); '
            'shared_prefs/tracker_sport_recently_retrieved_workout_result_pref.xml holds a workout result of '
            'exercise type 1001 with times 17:00:37 and 17:01:07 UTC, which fits the walking workout ended at '
            "about 17:01:10 UTC; and the app's text logs (files/logs/m_*.txt and r_*.txt, app debug lines "
            'with local times and no zone) include exercise session lines. The other readable databases, '
            'shared_prefs files and files/caches/preferences files are not reported.'
        ),
        "paths": ('*/com.sec.android.app.shealth/databases/pedometer_setting.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.shealth 6.30.3.011 | 1 row",
            "anne_a15": "Android 15 | com.sec.android.app.shealth | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.shealth | 0 rows",
        },
    },
    "samsung_health_step_bins": {
        "name": "Samsung Health - Step Bins",
        "description": "The time bins with steps in the one-day step list Samsung Health keeps in "
                       "pedometer_setting.db.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Health",
        "notes": (
            'One row per bin with a non-zero mStepCount in the JSON list stored under '
            'tracker_pedometer_temp_step_binning in pedometer_setting.db, read with a JSON parser; bins with '
            "no steps are in the list but are not reported. Bin Start is the bin's mStartTime read as Unix "
            'milliseconds and mTimeUnit (ms, as stored) is the bin length (600000, 10 minutes, on every bin '
            'of the known-data image). mTotalActiveTime and mSpeed are not reported. The step values are '
            'shown under their stored names; mDistance and mCalorie are as stored and their units are not '
            'established. On samsung_a166u_a16_known_20261116 the list held 144 bins starting 05:00 UTC '
            '(local midnight), and two held steps: 16 each at 17:30 and 17:40 UTC, which add up to the 32 in '
            'the Daily Step Summary. The phone was carried for a short walk at about 17:02 to 17:04 UTC, and '
            'the bins covering it hold 0; what the steps at 17:30 and 17:40 record is not established. The '
            'list covers one day and is not a step history. pedometer_setting.db on anne_a15 and sharon_a14 '
            'did not hold the key. Rows from several Android users are reported together and no column names '
            'the user. SecureHealthData.db, HealthFramework.db, HealthSharing.db, HealthSharingLogs.db, '
            'Permission.db, SdkPolicy.db and SportTracker.db have no SQLite header and byte entropy of 7.99 '
            'to 8.00 bits per byte on the known-data image, each with a <name>-se file beside it. '
            'SecureHealthData.db-wal has a WAL header and entropy of 8.00. None of them is read. No database '
            'key was identified: permanent_sharedpreferences_main.xml holds two AndroidX security-crypto '
            'keyset entries and files/ holds aks, aks_verify and aks_verify_iv, and what they protect is not '
            'established. The profile nickname and the text of the walking workout note made in the '
            "known-data session were not found by a byte search (UTF-8 and UTF-16) of the app's files outside "
            'those seven databases on the known-data image; whether the note was saved was not checked. Other '
            'plaintext stores hold values from the known-data session and are not reported: '
            'shared_prefs/sleep_card_cache.xml holds a period marked MANUAL from 04:00 to 12:00 UTC on '
            '2026-11-16, and files/caches/preferences/sleep.watch_summary.*.pref (gzip) holds the same start '
            'and end; these match the manual sleep entry made in the session (11:00 PM to 7:00 AM local); '
            'shared_prefs/tracker_sport_recently_retrieved_workout_result_pref.xml holds a workout result of '
            'exercise type 1001 with times 17:00:37 and 17:01:07 UTC, which fits the walking workout ended at '
            "about 17:01:10 UTC; and the app's text logs (files/logs/m_*.txt and r_*.txt, app debug lines "
            'with local times and no zone) include exercise session lines. The other readable databases, '
            'shared_prefs files and files/caches/preferences files are not reported.'
        ),
        "paths": ('*/com.sec.android.app.shealth/databases/pedometer_setting.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.shealth 6.30.3.011 | 2 rows",
            "anne_a15": "Android 15 | com.sec.android.app.shealth | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.shealth | 0 rows",
        },
    },
}

import datetime
import json
import os
import sqlite3
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import canonical_path, unique_files

_UTC = datetime.timezone.utc


def _ms_to_utc(value):
    if isinstance(value, str) and value.strip().lstrip('-').isdigit():
        value = int(value)
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=_UTC) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return ''


def _container(context, file_found):
    """The app container a file belongs to: storage class, Android user and package path."""
    key, _rank = canonical_path(context.get_relative_path(file_found))
    marker = '/com.sec.android.app.shealth/'
    return key.split(marker, 1)[0] if marker in key else key


def _read_prefs(path):
    """{name: (tag, value)} of an Android shared_prefs XML file, or None when unreadable."""
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Samsung Health: could not read {path}: {ex}')
        return None
    values = {}
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        values[name] = element.get('value') if element.get('value') is not None else (element.text or '')
    return values


def _number(value):
    """The stored text of a preferences value, unchanged."""
    return '' if value is None else value


@artifact_processor
def samsung_health_weight(context):
    temporary, permanent = {}, {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        name = os.path.basename(file_found)
        if name == 'temporary_sharedpreferences_main.xml':
            temporary[_container(context, file_found)] = file_found
        elif name == 'permanent_sharedpreferences_main.xml':
            permanent[_container(context, file_found)] = file_found

    data_list = []
    source_paths = []
    for container, path in temporary.items():
        values = _read_prefs(path)
        if values is None:
            continue
        source_paths.append(path)
        if 'tracker_weight_weight' not in values and 'tracker_weight_height' not in values:
            continue
        unit = ''
        if container in permanent:
            permanent_values = _read_prefs(permanent[container]) or {}
            unit = permanent_values.get('tracker_weight_profile_unit', '')
            source_paths.append(permanent[container])
        offset = values.get('tracker_weight_timeoffset', '')
        data_list.append((
            _ms_to_utc(values.get('tracker_weight_timestamp')),
            _number(values.get('tracker_weight_weight')),
            unit,
            _number(values.get('tracker_weight_height')),
            _number(values.get('tracker_weight_weightchange')),
            _number(values.get('tracker_weight_fat')),
            _number(values.get('tracker_weight_skeletal_muscle_mass')),
            int(offset) if isinstance(offset, str) and offset.lstrip('-').isdigit() else offset,
        ))

    data_headers = (('Timestamp', 'datetime'), 'Weight (as stored)', 'Weight Unit Setting',
                    'Height (as stored)', 'Weight Change (as stored)', 'Fat (as stored)',
                    'Skeletal Muscle Mass (as stored)', 'Time Offset (ms, as stored)')
    return data_headers, data_list, '\n'.join(source_paths)


_PEDOMETER_KEYS = ('tracker_pedometer_temp_step_data', 'tracker_pedometer_last_timezone',
                   'tracker_pedometer_last_allstep_logging_time')


def _local_day(start_ms, zone_name):
    """The calendar day a day summary starts on, in the zone the app recorded."""
    start = _ms_to_utc(start_ms)
    if not start or not zone_name:
        return ''
    try:
        return start.astimezone(ZoneInfo(zone_name)).date()
    except (ZoneInfoNotFoundError, ValueError):
        return ''


@artifact_processor
def samsung_health_daily_steps(context):
    data_list = []
    source_paths = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.endswith('pedometer_setting.db') or os.path.isdir(file_found):
            continue
        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        source_paths.append(file_found)
        try:
            marks = ','.join('?' * len(_PEDOMETER_KEYS))
            values = dict(db.execute(f'SELECT key, value FROM pedometer_setting WHERE key IN ({marks})',
                                     _PEDOMETER_KEYS).fetchall())
        except sqlite3.Error as ex:
            logfunc(f'Samsung Health: could not read {file_found}: {ex}')
            continue
        finally:
            db.close()
        raw = values.get('tracker_pedometer_temp_step_data')
        if not raw:
            continue
        try:
            summary = json.loads(raw)
        except ValueError as ex:
            logfunc(f'Samsung Health: step summary not parsed in {file_found}: {ex}')
            continue
        if not isinstance(summary, dict):
            continue
        zone_name = values.get('tracker_pedometer_last_timezone', '')
        data_list.append((
            _local_day(summary.get('mStartTime'), zone_name),
            _ms_to_utc(summary.get('mStartTime')),
            _ms_to_utc(values.get('tracker_pedometer_last_allstep_logging_time')),
            summary.get('mStepCount', ''),
            summary.get('mWalkStepCount', ''),
            summary.get('mRunStepCount', ''),
            summary.get('mDistance', ''),
            summary.get('mCalorie', ''),
            summary.get('mTotalActiveTime', ''),
            summary.get('mDeviceName', ''),
            zone_name,
        ))

    data_headers = (('Day', 'date'), ('Day Start', 'datetime'), ('Last Step Logging Time', 'datetime'),
                    'mStepCount', 'mWalkStepCount', 'mRunStepCount', 'mDistance (as stored)',
                    'mCalorie (as stored)', 'mTotalActiveTime (as stored)', 'Device Name', 'Time Zone')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def samsung_health_step_bins(context):
    data_list = []
    source_paths = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.endswith('pedometer_setting.db') or os.path.isdir(file_found):
            continue
        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        source_paths.append(file_found)
        try:
            row = db.execute("SELECT value FROM pedometer_setting WHERE key = 'tracker_pedometer_temp_step_binning'"
                             ).fetchone()
        except sqlite3.Error as ex:
            logfunc(f'Samsung Health: could not read {file_found}: {ex}')
            continue
        finally:
            db.close()
        if not row or not row[0]:
            continue
        try:
            bins = json.loads(row[0])
        except ValueError as ex:
            logfunc(f'Samsung Health: step bins not parsed in {file_found}: {ex}')
            continue
        if not isinstance(bins, list):
            continue
        for entry in bins:
            if not isinstance(entry, dict) or not entry.get('mStepCount'):
                continue
            unit = entry.get('mTimeUnit')
            data_list.append((
                _ms_to_utc(entry.get('mStartTime')),
                unit,
                entry.get('mStepCount', ''),
                entry.get('mWalkStepCount', ''),
                entry.get('mRunStepCount', ''),
                entry.get('mDistance', ''),
                entry.get('mCalorie', ''),
            ))

    data_headers = (('Bin Start', 'datetime'), 'mTimeUnit (ms, as stored)', 'mStepCount', 'mWalkStepCount',
                    'mRunStepCount', 'mDistance (as stored)', 'mCalorie (as stored)')
    return data_headers, data_list, '\n'.join(source_paths)
