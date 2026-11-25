__artifacts_v2__ = {
    "telephony_analytics_calls": {
        "name": "Telephony Analytics - Calls",
        "description": "Daily counts of calls by type, outcome and SIM slot that the Android "
                       "phone process kept in telephony_analytics.db. Failed calls are also "
                       "split by radio technology and failure reason.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Read from user_de/<user>/com.android.phone/databases/telephony_analytics.db"
                 " with the table and column names AOSP's telephony analytics providers "
                 "create (frameworks/opt/telephony "
                 "src/java/com/android/internal/telephony/analytics at android-16.0.0_r1; the"
                 " same files at android-15.0.0_r1 except TelephonyAnalytics.java). 'Date' is"
                 " LogDate, a yyyy-MM-dd date in the time zone the phone process had when it "
                 "started (TelephonyAnalyticsDatabase.java DATE_FORMAT); it can differ from "
                 "the device's zone on that day if the zone changed while the process ran. It"
                 " is the day the provider wrote or updated the row, a date with no time, and"
                 " is not converted. When a provider writes, at most once per day, it deletes"
                 " rows dated more than two calendar months before that day and trims the "
                 "table to the 1,000 rows with the newest dates (TelephonyAnalyticsUtil.java "
                 "CUTOFF_MONTHS and MAX_ENTRIES_LIMIT); nothing is trimmed while nothing is "
                 "written, and the row cap was not reached on the test images. A missing day "
                 "does not show that nothing happened. 'Release Version' is the build's "
                 "incremental version string (Build.VERSION.INCREMENTAL) the provider stores "
                 "on each row. When more than one database is found, a Source File column "
                 "names the database of each row; no test image had more than one. Successful"
                 " calls: one row per date, call type and SIM slot; 'Radio Technology', "
                 "'Failure Reason' and 'Release Version' on that row are those of the last "
                 "call counted, and 'Failure Reason' holds its disconnect cause, not a "
                 "failure. Failed calls: one row per date, call type, radio technology, SIM "
                 "slot, failure reason and release version. 'Count' is how many calls ended "
                 "on that date for the row (CallAnalyticsProvider.java). The table holds no "
                 "phone numbers, contacts or call times. On dragna_pixel9a_a16 'Call Type' "
                 "held Normal Call, 'Call Status' held Success, 'SIM Slot' held 0 and "
                 "'Release Version' held one value on every row.",
        "paths": ('*/user_de/*/com.android.phone/databases/telephony_analytics.db*',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.android.phone | 15 rows",
            "anne_a15": "Android 15 | com.android.phone | 1 row",
            "emu_a15_oss2_v3": "Android 15 | com.android.phone | 0 rows",
            "emu_a15_oss_v17": "Android 15 | com.android.phone | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.phone | 6 rows",
            "hc_pixel8pro_a17": "Android 17 | com.android.phone | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.phone | 8 rows",
        },
    },
    "telephony_analytics_sms": {
        "name": "Telephony Analytics - SMS and MMS",
        "description": "Daily counts of SMS messages by type, outcome and SIM slot that the "
                       "Android phone process kept in telephony_analytics.db. Failed messages"
                       " are also split by radio technology and failure reason.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Read from user_de/<user>/com.android.phone/databases/telephony_analytics.db"
                 " with the table and column names AOSP's telephony analytics providers "
                 "create (frameworks/opt/telephony "
                 "src/java/com/android/internal/telephony/analytics at android-16.0.0_r1; the"
                 " same files at android-15.0.0_r1 except TelephonyAnalytics.java). 'Date' is"
                 " LogDate, a yyyy-MM-dd date in the time zone the phone process had when it "
                 "started (TelephonyAnalyticsDatabase.java DATE_FORMAT); it can differ from "
                 "the device's zone on that day if the zone changed while the process ran. It"
                 " is the day the provider wrote or updated the row, a date with no time, and"
                 " is not converted. When a provider writes, at most once per day, it deletes"
                 " rows dated more than two calendar months before that day and trims the "
                 "table to the 1,000 rows with the newest dates (TelephonyAnalyticsUtil.java "
                 "CUTOFF_MONTHS and MAX_ENTRIES_LIMIT); nothing is trimmed while nothing is "
                 "written, and the row cap was not reached on the test images. A missing day "
                 "does not show that nothing happened. 'Release Version' is the build's "
                 "incremental version string (Build.VERSION.INCREMENTAL) the provider stores "
                 "on each row. When more than one database is found, a Source File column "
                 "names the database of each row; no test image had more than one. Successful"
                 " messages: one row per date, message type and SIM slot; 'Radio Technology' "
                 "and 'Release Version' on that row are those of the last message counted. "
                 "Failed messages: one row per date, message type, radio technology, SIM "
                 "slot, failure reason and release version. 'Count' is how many messages the "
                 "provider counted for the row (SmsMmsAnalyticsProvider.java). The table can "
                 "also name MMS types; none appeared on the seven test images. The table "
                 "holds no phone numbers, contacts or message content. On dragna_pixel9a_a16 "
                 "'Status' held Success, 'Failure Reason' held NA, 'SIM Slot' held 0 and "
                 "'Release Version' held one value on every row.",
        "paths": ('*/user_de/*/com.android.phone/databases/telephony_analytics.db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.android.phone | 101 rows",
            "anne_a15": "Android 15 | com.android.phone | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | com.android.phone | 0 rows",
            "emu_a15_oss_v17": "Android 15 | com.android.phone | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.phone | 30 rows",
            "hc_pixel8pro_a17": "Android 17 | com.android.phone | 35 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.phone | 115 rows",
        },
    },
    "telephony_analytics_service_state": {
        "name": "Telephony Analytics - Service State",
        "description": "Accumulated time the Android phone process recorded for each SIM slot"
                       " in each device status (IN_SERVICE, NO_NETWORK_COVERAGE, APM and "
                       "others) and radio technology, logged under the date each interval was"
                       " written, kept in telephony_analytics.db.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Read from user_de/<user>/com.android.phone/databases/telephony_analytics.db"
                 " with the table and column names AOSP's telephony analytics providers "
                 "create (frameworks/opt/telephony "
                 "src/java/com/android/internal/telephony/analytics at android-16.0.0_r1; the"
                 " same files at android-15.0.0_r1 except TelephonyAnalytics.java). 'Date' is"
                 " LogDate, a yyyy-MM-dd date in the time zone the phone process had when it "
                 "started (TelephonyAnalyticsDatabase.java DATE_FORMAT); it can differ from "
                 "the device's zone on that day if the zone changed while the process ran. It"
                 " is the day the provider wrote or updated the row, a date with no time, and"
                 " is not converted. When a provider writes, at most once per day, it deletes"
                 " rows dated more than two calendar months before that day and trims the "
                 "table to the 1,000 rows with the newest dates (TelephonyAnalyticsUtil.java "
                 "CUTOFF_MONTHS and MAX_ENTRIES_LIMIT); nothing is trimmed while nothing is "
                 "written, and the row cap was not reached on the test images. A missing day "
                 "does not show that nothing happened. 'Release Version' is the build's "
                 "incremental version string (Build.VERSION.INCREMENTAL) the provider stores "
                 "on each row. When more than one database is found, a Source File column "
                 "names the database of each row; no test image had more than one. One row "
                 "per date, device status (for example IN_SERVICE, CELLULAR_OOS_WITH_IWLAN, "
                 "NO_NETWORK_COVERAGE, APM), radio technology, SIM slot and release version. "
                 "The status is assigned by logServiceState (TelephonyAnalytics.java); for "
                 "example APM is recorded when airplane mode is on and Wi-Fi calling data is "
                 "not in service. 'Duration (ms)' is the accumulated time in that state, "
                 "measured with SystemClock.elapsedRealtime (TelephonyAnalytics.java "
                 "getTimeMillis), and 'Duration (minutes)' is that value divided by 60,000 "
                 "and rounded to one decimal. Intervals shorter than 10 seconds are not "
                 "recorded, and the state in force at extraction is not written until it "
                 "changes. A state interval is added whole to the date on which the provider "
                 "wrote it, which is when the state changed or a dump ran, so one date can "
                 "show more than 24 hours: on dragna_pixel9a_a16, 18 of 98 rows exceed 1,440 "
                 "minutes, for example one APM row of 1,588.7. On dragna_pixel9a_a16 'SIM "
                 "Slot' held 0 and 'Release Version' held one value on every row.",
        "paths": ('*/user_de/*/com.android.phone/databases/telephony_analytics.db*',),
        "output_types": "standard",
        "artifact_icon": "radio",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.android.phone | 98 rows",
            "anne_a15": "Android 15 | com.android.phone | 11 rows",
            "emu_a15_oss2_v3": "Android 15 | com.android.phone | 3 rows",
            "emu_a15_oss_v17": "Android 15 | com.android.phone | 6 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.phone | 30 rows",
            "hc_pixel8pro_a17": "Android 17 | com.android.phone | 37 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.phone | 144 rows",
        },
    },
}

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, get_sqlite_db_records


def _rows(context, table, query):
    """(rows, sources) from every telephony_analytics.db found, a Source File column added
    when there is more than one."""
    dbs = [str(f) for f in unique_files(context)
           if os.path.basename(str(f)) == 'telephony_analytics.db']
    rows = []
    for db in dbs:
        if not does_table_exist_in_db(db, table):
            continue
        for row in get_sqlite_db_records(db, query):
            row = tuple('' if value is None else value for value in row)
            rows.append(row + ((context.get_relative_path(db),) if len(dbs) > 1 else ()))
    return dbs, rows


def _headers(headers, dbs):
    return headers + (('Source File',) if len(dbs) > 1 else ())


@artifact_processor
def telephony_analytics_calls(context):
    dbs, rows = _rows(context, 'CallDataLogs',
                      'SELECT LogDate, CallType, CallStatus, Count, RAT, SlotID, FailureReason, '
                      'ReleaseVersion FROM CallDataLogs ORDER BY LogDate, _id')
    headers = (('Date', 'date'), 'Call Type', 'Call Status', ('Count', 'number'), 'Radio Technology',
               'SIM Slot', 'Failure Reason', 'Release Version')
    return _headers(headers, dbs), rows, '\n'.join(dbs)


@artifact_processor
def telephony_analytics_sms(context):
    dbs, rows = _rows(context, 'SmsMmsDataLogs',
                      'SELECT LogDate, SmsMmsType, SmsMmsStatus, Count, RAT, SlotID, '
                      'FailureReason, ReleaseVersion FROM SmsMmsDataLogs ORDER BY LogDate, _id')
    headers = (('Date', 'date'), 'Type', 'Status', ('Count', 'number'), 'Radio Technology', 'SIM Slot',
               'Failure Reason', 'Release Version')
    return _headers(headers, dbs), rows, '\n'.join(dbs)


@artifact_processor
def telephony_analytics_service_state(context):
    dbs, rows = _rows(context, 'ServiceStateLogs',
                      'SELECT LogDate, DeviceStatus, TimeDuration, '
                      'round(TimeDuration / 60000.0, 1), RAT, SlotID, ReleaseVersion '
                      'FROM ServiceStateLogs ORDER BY LogDate, _id')
    headers = (('Date', 'date'), 'Device Status', ('Duration (ms)', 'number'), ('Duration (minutes)', 'number'),
               'Radio Technology', 'SIM Slot', 'Release Version')
    return _headers(headers, dbs), rows, '\n'.join(dbs)
