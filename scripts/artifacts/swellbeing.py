__artifacts_v2__ = {
    "samsung_wellbeing": {
        "name": "Samsung Digital Wellbeing",
        "description": "Parses Samsung Digital Wellbeing usage events from the usageEvents table of dwbCommon.db (timestamp, event ID, package and event type).",
        "author": "@abrignoni, @Adam-Hachem",
        "creation_date": "2020-05-21",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Device Activity",
        "notes": (
            "Timestamp is usageEvents.timeStamp read as Unix milliseconds and shown in UTC; that unit is not sourced from the app's code. Event-type labels are taken from the AOSP UsageEvents.Event constant names "
            "(reference: AOSP, UsageEvents.java at tag android-14.0.0_r1, "
            "https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/core/java/android/app/usage/UsageEvents.java#104) "
            "and applied to the stored codes. The labels for codes 1 and 2 each show two constant "
            "names, which that file defines with the same value. "
            "No Samsung source for these codes was used, and they are not verified to match those constants, so the labels are unverified. An event type with no matching label "
            "is shown as stored. Package Name is read from the pkgName column of usageEvents where "
            "the database has one, and otherwise joined from foundPackages on pkgId. The pkgName column was reported by @Adam-Hachem. samsung_a166u_a16_known_20261117 (Android 16) has it in the databases of Android users 0 and 150 (4,561 and 62 rows, and no row is in both), and every row there has a Package Name. samsung_a166u_a16_known_20261116 (Android 16) has pkgId. "
            "An event whose package id has no row in "
            "foundPackages is reported with a blank Package Name; no event on galaxys10_a10, samsungs20_a13 or samsung_a166u_a16_known_20261116 was in that state. A database present under several storage paths "
            "(data/data, data/user/0, data_mirror) is read once. "
            "Android User is the user number in the path of the database: n under data/user/<n>, data/user_de/<n>, userdata/user/<n>, userdata/user_de/<n>, data_mirror/data_ce/<volume>/<n> or data_mirror/data_de/<volume>/<n>, and 0 under data/data or userdata/data. It is blank for any other path. That includes a rollback copy under data/misc_ce/<n>/rollback. A rollback copy is read unless the live database was also found and the two files and their -wal and -journal match. No sample_data image had a rollback copy of dwbCommon.db, so the blank case is unexercised. samsung_a166u_a16_known_20261117 has users 0 and 150. The other six sample_data images have 0 on every row. "
            "A label names a recorded transition and does not by itself establish a user "
            "action."
        ),
        "paths": ('*/com.samsung.android.forest/databases/dwbCommon.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.forest | 2410 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.forest | 11382 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.forest | 2307 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.forest | 554 rows",
            "sharon_a14": "Android 14 | com.samsung.android.forest vc 510200008 | 3187 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.forest | 3689 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.forest | 4623 rows",
        },
    },
    "samsung_wellbeing_timezone": {
        "name": "Samsung Digital Wellbeing - Timezone Changes",
        "description": "Timezone changes Samsung Digital Wellbeing logged in dwbCommon.db under the UsageDataManager::timeZoneChanged() key.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-03",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Device Activity",
        "notes": "Reads Logging rows whose key contains UsageDataManager::timeZoneChanged() from the first dwbCommon.db found, with the previous and new timezone split from the value. A change logged under another key is not reported: on samsungs20_a13 one Logging row holds a previous and new timezone under a different key, and this artifact reports no rows. An empty result does not show that no timezone change happened. Timestamp is Logging.timeStamp, converted by a shared helper that picks the unit from the value's size, and shown in UTC.",
        "paths": ('*/com.samsung.android.forest/databases/dwbCommon.db*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "galaxys10_a10": "1 row",
            "sharon_a14": "1 row",
        },
    },
    "samsung_wellbeing_app_timers": {
        "name": "Samsung Digital Wellbeing - App Timers",
        "description": "App timers (daily usage limits) set in Samsung Digital Wellbeing: timer name, the "
                       "packages it covers, the daily limit and the stored days and state, from dwbCommon.db.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Device Activity",
        "notes": "One row per app timer and schedule row: apptimer_table of com.samsung.android.forest/"
                 "databases/dwbCommon.db joined to apptimer_schedule_table on observer_id. A timer with more "
                 "than one schedule row would give one row per schedule; the known-data image has one "
                 "schedule per timer. A timer with no schedule row is still reported, and a schedule row "
                 "whose observer_id names no timer is not; both paths are in the code and were not run "
                 "against real data. Timer Name and Packages are apptimer_table.timer_name and package_name "
                 "as stored; on the known-data image the timer covering two apps stored them separated by a "
                 "comma and a space. Daily Limit (minutes) is apptimer_schedule_table.time_limit. Schedule Days (as stored) is its enable_days value; how that value maps to weekdays is not established. Known data on samsung_a166u_a16_known_20261116 ties the values to the "
                 "settings made on the phone: a timer set for 1 minute every day stored time_limit 1 and "
                 "enable_days 127, and one set for 30 minutes Monday to Friday stored 30 and 62 (bits 1 to "
                 "5). The Logging table records the same allowances as remainingUsage 60000 and 1800000 "
                 "milliseconds (see the App Timer Log artifact). Suspended (as stored) is is_suspended; it "
                 "held 1 on the 1-minute timer, whose app was in front for about 80 s from 15:17:57 UTC in "
                 "the known-data session, and 0 on the other; what clears it is not established. Schedule "
                 "Enabled (as stored) held 1 on both rows. Extended Time Limit (as stored) held 0 on both "
                 "rows; no time extension was made in the known-data session. Extended Time Stamp is "
                 "extended_time_stamp read as Unix milliseconds, the only time the table stores; it is not "
                 "a creation time, and what writes it is not established. On the known-data image the first "
                 "timer's value was 15:16:37 UTC, 26 s after that timer's first Logging row and within 1 s "
                 "of its second. The second timer's value was within 1 s of a Logging row and of the "
                 "LAST_TIMER_INIT value in persistentMapDb.db (all 18:16:32 UTC), 13 s after a "
                 "BOOT_COMPLETED log row and 8 s before the Date value in the UFED .ufd (18:16:40 UTC). That "
                 "value is later than every action in the known-data session, so on that image it does not "
                 "record an action taken on the timer. apptimer_table also has time_limit and enable_days "
                 "columns; they were empty on both rows and are not read. Nine of the ten other images "
                 "checked have no apptimer_schedule_table and no timers, so where a timer's limit is stored "
                 "on those builds is not established, and such a timer would be reported with a blank Daily "
                 "Limit and Schedule Days. Android User is the user number in the path of the database: n under data/user/<n>, data/user_de/<n>, userdata/user/<n>, userdata/user_de/<n>, data_mirror/data_ce/<volume>/<n> or data_mirror/data_de/<volume>/<n>, and 0 under data/data or userdata/data. It is blank for any other path. That includes a rollback copy under data/misc_ce/<n>/rollback. A rollback copy is read unless the live database was also found and the two files and their -wal and -journal match. No sample_data image had a rollback copy of dwbCommon.db, so the blank case is unexercised. The 2 rows on samsung_a166u_a16_known_20261116, the only sample_data image with rows, have Android User 0. A non-zero value is unexercised for this artifact. Observer ID "
                 "and Schedule ID held the same values on both rows of the known-data image; they are "
                 "separate keys (apptimer_table.observer_id and apptimer_schedule_table.scheduleId). Not "
                 "reported: appTimerWidget, focusModeHistory, DailyBedTimeSchedule, drivingCustomizedApp, "
                 "FocusTargetApps, installedPkgs, notiSummary, promovenceScreenTime, promovenceUnlock, "
                 "settingsExcludedApp and widgetsSetting (0 rows on the known-data image), focusMode (2 rows "
                 "with usageCount 0 and start and end 0), device (1 row of device and sync identifiers), "
                 "persistentMapDb.db (key and value settings), dwb_category_data.xml, the WorkManager and "
                 "datatransport databases and the shared_prefs files. apptimer_table held 0 rows on the ten "
                 "other images checked.",
        "paths": ('*/com.samsung.android.forest/databases/dwbCommon.db*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.forest 6.1.01.27 | 2 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
        },
    },
    "samsung_wellbeing_app_timer_log": {
        "name": "Samsung Digital Wellbeing - App Timer Log",
        "description": "Rows of the Samsung Digital Wellbeing Logging table in dwbCommon.db that record an app "
                       "timer's remaining usage or a usage limit being reached.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Device Activity",
        "notes": "Rows of the Logging table of com.samsung.android.forest/databases/dwbCommon.db whose "
                 "value names an app timer's packages followed by timeUsedUdm, timeVisibleUsm, usedInMin "
                 "and remainingUsage, or contains APP_USAGE_LIMIT_REACHED. Every other Logging row (boot "
                 "times, time and timezone changes, lines of the form '--> package: n to n' whose meaning is "
                 "not established, and other app log lines) is left out. The Timezone Changes artifact reads "
                 "Logging rows by a key that the known-data image does not use, so that image's timezone "
                 "line is not reported by either artifact. Timestamp is Logging.timeStamp read as Unix "
                 "milliseconds. Packages, Remaining Usage and usedInMin are parsed from the value text, which "
                 "is shown in full in Log Value (as stored); no source for the format of these log lines was used. Remaining Usage is in milliseconds: the 1-minute and 30-minute "
                 "timers of the known-data image logged 60000 and 1800000. usedInMin was 0 on every row, so "
                 "its unit is taken from the field name only. On samsung_a166u_a16_known_20261116 the rows "
                 "fall at the times timers were created (15:16:11 and 15:17:45 UTC, within 2 s of the mint "
                 "log's 15:16:13 and 15:17:47), at 15:16:37 for the first timer again (26 s after its first "
                 "row), at 15:18:59 for the APP_USAGE_LIMIT_REACHED row (the 1-minute timer's app had been "
                 "brought to the front at 15:17:57), and at 18:16:32 for the second timer, 13 s after a "
                 "BOOT_COMPLETED row and 8 s before the Date value in the UFED .ufd (18:16:40 UTC). The "
                 "APP_USAGE_LIMIT_REACHED row does not name a package. A row does not by itself show that a "
                 "person set or met a limit. Android User is the user number in the path of the database: n under data/user/<n>, data/user_de/<n>, userdata/user/<n>, userdata/user_de/<n>, data_mirror/data_ce/<volume>/<n> or data_mirror/data_de/<volume>/<n>, and 0 under data/data or userdata/data. It is blank for any other path. That includes a rollback copy under data/misc_ce/<n>/rollback. A rollback copy is read unless the live database was also found and the two files and their -wal and -journal match. No sample_data image had a rollback copy of dwbCommon.db, so the blank case is unexercised. The 5 rows on samsung_a166u_a16_known_20261116, the only sample_data image with rows, have Android User 0. A non-zero value is unexercised for this artifact. No Logging row on the ten other images checked matched either "
                 "shape.",
        "paths": ('*/com.samsung.android.forest/databases/dwbCommon.db*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.forest 6.1.01.27 | 5 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
        },
    },
}

import datetime
import re
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_unix_ts_to_utc, get_sqlite_db_records, get_file_path, logfunc
from scripts.artifacts.storagePathViews import android_user, unique_files


@artifact_processor
def samsung_wellbeing(context):
    data_list = []
    source_paths = []
    # unique_files collapses the data/data, data/user/0 and data_mirror views of one
    # database, which otherwise report every event once per view.
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.endswith('dwbCommon.db'):
            continue  # Skip all other files

        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        cursor = db.cursor()
        columns = {row[1] for row in cursor.execute('PRAGMA table_info(usageEvents)')}
        if 'pkgName' in columns:
            # samsung_a166u_a16_known_20261117 stores the package name on the event row.
            package_column = 'usageEvents.pkgName'
            package_join = ''
        elif 'pkgId' in columns:
            package_column = 'foundPackages.name'
            package_join = 'LEFT JOIN foundPackages ON usageEvents.pkgId=foundPackages.pkgId'
        else:
            logfunc(f'samsung_wellbeing: usageEvents has neither pkgName nor pkgId in {file_found}')
            db.close()
            continue
        # event types pulled from:
        # https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/core/java/android/app/usage/UsageEvents.java#104
        cursor.execute(f'''
        SELECT
        usageEvents.timeStamp,
        usageEvents.eventId,
        {package_column},
        usageEvents.eventType,
        CASE
        when usageEvents.eventType=1 THEN 'ACTIVITY_RESUMED / MOVE_TO_FOREGROUND'
        when usageEvents.eventType=2 THEN 'ACTIVITY_PAUSED / MOVE_TO_BACKGROUND'
		when usageEvents.eventType=3 THEN 'END_OF_DAY'
		when usageEvents.eventType=4 THEN 'CONTINUE_PREVIOUS_DAY'
        when usageEvents.eventType=5 THEN 'CONFIGURATION_CHANGE'
		when usageEvents.eventType=6 THEN 'SYSTEM_INTERACTION'
        when usageEvents.eventType=7 THEN 'USER_INTERACTION'
		when usageEvents.eventType=8 THEN 'SHORTCUT_INVOCATION'
		when usageEvents.eventType=9 THEN 'CHOOSER_ACTION'
        when usageEvents.eventType=10 THEN 'NOTIFICATION_SEEN'
        when usageEvents.eventType=11 THEN 'STANDBY_BUCKET_CHANGED'
        when usageEvents.eventType=12 THEN 'NOTIFICATION_INTERRUPTION'
		when usageEvents.eventType=13 THEN 'SLICE_PINNED_PRIV'
		when usageEvents.eventType=14 THEN 'SLICE_PINNED'
        when usageEvents.eventType=15 THEN 'SCREEN_INTERACTIVE'
        when usageEvents.eventType=16 THEN 'SCREEN_NON_INTERACTIVE'
        when usageEvents.eventType=17 THEN 'KEYGUARD_SHOWN'
        when usageEvents.eventType=18 THEN 'KEYGUARD_HIDDEN'
        when usageEvents.eventType=19 THEN 'FOREGROUND_SERVICE_START'
        when usageEvents.eventType=20 THEN 'FOREGROUND_SERVICE_STOP'
		when usageEvents.eventType=21 THEN 'CONTINUING_FOREGROUND_SERVICE'
		when usageEvents.eventType=22 THEN 'ROLLOVER_FOREGROUND_SERVICE'
        when usageEvents.eventType=23 THEN 'ACTIVITY_STOPPED'
		when usageEvents.eventType=24 THEN 'ACTIVITY_DESTROYED'
		when usageEvents.eventType=25 THEN 'FLUSH_TO_DISK'
        when usageEvents.eventType=26 THEN 'DEVICE_SHUTDOWN'
        when usageEvents.eventType=27 THEN 'DEVICE_STARTUP'
        when usageEvents.eventType=28 THEN 'USER_UNLOCKED'
		when usageEvents.eventType=29 THEN 'USER_STOPPED'
		when usageEvents.eventType=30 THEN 'LOCUS_ID_SET'
		when usageEvents.eventType=31 THEN 'APP_COMPONENT_USED'
        else usageEvents.eventType
        END as eventTypeDescription
        FROM usageEvents
        {package_join}
        ''')
        all_rows = cursor.fetchall()
        db.close()
        source_paths.append(file_found)
        user = android_user(context.get_relative_path(file_found))

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((timestamp, row[1], row[2], row[3], row[4], user))

    data_headers = (('Timestamp', 'datetime'), 'Event ID', 'Package Name', 'Event Type', 'Event Type Description',
                    'Android User')
    return data_headers, data_list, '\n'.join(source_paths)

@artifact_processor
def samsung_wellbeing_timezone(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = get_file_path(files_found, "dwbCommon.db")
    
    query  = '''
    SELECT
    timeStamp,
    Value
    from Logging
    where key like '%UsageDataManager::timeZoneChanged()%'
    '''
    
    db_records = get_sqlite_db_records(source_path, query)
    
    for record in db_records:
        time = convert_unix_ts_to_utc(record[0])
        pre_timezone = record[1].split(', ')[0].replace('prevTimezone( ','')[:-1]
        new_timezone = record[1].split(', ')[1].replace('newTimezone( ','')[:-1]
        
        data_list.append((time, pre_timezone, new_timezone))
                            
    data_headers = (('Timestamp', 'datetime'),'Previous Timezone','New Timezone')
    return data_headers, data_list, source_path

_TIMER_COLUMNS = ('observer_id', 'timer_name', 'package_name', 'extended_time_limit',
                  'extended_time_stamp', 'is_suspended')
_SCHEDULE_COLUMNS = ('scheduleId', 'observer_id', 'time_limit', 'enabled', 'enable_days')


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return ''


def _select(db, table, wanted):
    """Rows of table as dicts, with None for any wanted column this schema lacks."""
    present = {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
    columns = ', '.join(f'"{name}"' if name in present else f'NULL AS "{name}"' for name in wanted)
    cursor = db.execute(f'SELECT {columns} FROM "{table}"')
    return [dict(zip(wanted, row)) for row in cursor.fetchall()]


def _dwb_databases(context):
    for file_found in unique_files(context):
        file_found = str(file_found)
        if file_found.endswith('dwbCommon.db'):
            yield file_found


@artifact_processor
def samsung_wellbeing_app_timers(context):
    data_list = []
    source_paths = []
    for file_found in _dwb_databases(context):
        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        source_paths.append(file_found)
        try:
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if 'apptimer_table' not in tables:
                continue
            timers = _select(db, 'apptimer_table', _TIMER_COLUMNS)
            schedules = {}
            if 'apptimer_schedule_table' in tables:
                for schedule in _select(db, 'apptimer_schedule_table', _SCHEDULE_COLUMNS):
                    schedules.setdefault(schedule['observer_id'], []).append(schedule)
        except sqlite3.Error as ex:
            logfunc(f'samsung_wellbeing_app_timers: could not read {file_found}: {ex}')
            continue
        finally:
            db.close()

        user = android_user(context.get_relative_path(file_found))
        for timer in sorted(timers, key=lambda t: (t['observer_id'] is None, t['observer_id'])):
            # a timer with no schedule row still gets its own row
            for schedule in schedules.get(timer['observer_id']) or [{}]:
                data_list.append((
                    _ms_to_utc(timer['extended_time_stamp']),
                    timer['timer_name'] or '',
                    timer['package_name'] or '',
                    schedule.get('time_limit'),
                    schedule.get('enable_days'),
                    schedule.get('enabled'),
                    timer['is_suspended'],
                    timer['extended_time_limit'],
                    timer['observer_id'],
                    schedule.get('scheduleId'),
                    user,
                ))

    data_headers = (('Extended Time Stamp', 'datetime'), 'Timer Name', 'Packages',
                    'Daily Limit (minutes)', 'Schedule Days (as stored)', 'Schedule Enabled (as stored)',
                    'Suspended (as stored)', 'Extended Time Limit (as stored)', 'Observer ID', 'Schedule ID',
                    'Android User')
    return data_headers, data_list, '\n'.join(source_paths)


_TIMER_LOG = re.compile(r'^(?P<packages>.+?) timeUsedUdm\s*:\s*(?P<used_udm>-?\d+),\s*timeVisibleUsm\s*:\s*'
                        r'(?P<visible>-?\d+)\s+usedInMin\s*:\s*(?P<used_min>-?\d+),\s*remainingUsage\s*:\s*'
                        r'(?P<remaining>-?\d+)')
_LIMIT_REACHED = 'APP_USAGE_LIMIT_REACHED'


@artifact_processor
def samsung_wellbeing_app_timer_log(context):
    data_list = []
    source_paths = []
    for file_found in _dwb_databases(context):
        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        source_paths.append(file_found)
        try:
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            rows = db.execute('SELECT id, timeStamp, key, value FROM Logging ORDER BY timeStamp, id').fetchall() \
                if 'Logging' in tables else []
        except sqlite3.Error as ex:
            logfunc(f'samsung_wellbeing_app_timer_log: could not read {file_found}: {ex}')
            rows = []
        finally:
            db.close()

        user = android_user(context.get_relative_path(file_found))
        for row_id, timestamp, _key, value in rows:
            value = value or ''
            match = _TIMER_LOG.match(value)
            if match:
                data_list.append((_ms_to_utc(timestamp), match['packages'], int(match['remaining']),
                                  int(match['used_min']), value, row_id, user))
            elif _LIMIT_REACHED in value:
                data_list.append((_ms_to_utc(timestamp), '', '', '', value, row_id, user))

    data_headers = (('Timestamp', 'datetime'), 'Packages', 'Remaining Usage (ms, parsed)',
                    'usedInMin (parsed)', 'Log Value (as stored)', 'Log ID', 'Android User')
    return data_headers, data_list, '\n'.join(source_paths)
