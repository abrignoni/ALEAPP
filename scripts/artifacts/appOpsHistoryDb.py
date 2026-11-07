__artifacts_v2__ = {
    "appops_history_db": {
        "name": "App Ops Access History (Database)",
        "description": "Rows of the app_op_accesses table in the App Ops history databases under system/appops, "
                       "with the package, the op, the first access time of each aggregation window, the process "
                       "state, the flags and the access and reject counts.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Permissions",
        "notes": "One row per row of the app_op_accesses table in the App Ops history databases under system/appops, "
                 "read with the write-ahead log applied. Three layouts are read, told apart by file name: "
                 "app_op_history_short_interval.db and app_op_history_long_interval.db (aggregated, shown in Interval "
                 "as Short and Long) and app_op_history.db (one row per access, shown as Not aggregated). Interval is "
                 "taken from the file name and separates the short database from the long one exactly as Source File "
                 "does, which is why both are kept. The databases are in system, not in a "
                 "per-user folder, and hold every Android user's accesses: Android User is the uid divided by 100000 "
                 "(UserHandle.PER_USER_RANGE), so uid 15010101 is user 150, app id 10101. Android User held 0 on every "
                 "row of two of the five tested images and 150 on 777 rows of the other three; no other user id "
                 "occurred.\n"
                 "Evidence tiers. Proven on real data: the two aggregated databases, read from five Android 16 Samsung "
                 "(One UI 8.x) full file system images, 328,519 rows in all (2,940; 8,587; 286,819; 23,269 and 6,904 "
                 "per image, short and long together), each count re-derived with an independent sqlite query. Of the "
                 "3,180 access times in appops_accesses.xml that fall inside the time span of the database on the same "
                 "image, 1,717 equal an Access Time of the same package and op to the millisecond, which confirms the "
                 "unit and the epoch; the rest are not explained by this check, since that XML holds the last access "
                 "of a key and this table the first access of a window. Source-verified, not shown on a real image: "
                 "the meaning of the columns (AOSP AppOpHistoryTable, AppOpHistoryHelper and HistoricalRegistry at "
                 "android16-qpr1-release) and the names of ops 156 to 169 (AOSP AppOpsManager at "
                 "android16-qpr2-release). Code-present, never run on a real image: the app_op_history.db layout of "
                 "the Android 16.0 release, which has no Total Duration, Access Count or Reject Count and never a NULL "
                 "device id, built from AOSP DiscreteOpsTable at android-16.0.0_r1 and tested on a constructed "
                 "database only. On two corpus Google Pixel 8 Pro images (hc_pixel8pro_a16, Android 16, and hc_pixel8pro_a17, Android 17) the two aggregated databases, each with a -wal, gave 90,420 and 62,102 rows, equal to app_op_accesses with the -wal applied, counted without ALEAPP. Not examined: any other device or Android version. "
                 "The one Android 14 image checked held none of these files. Releases before Android 16 keep this "
                 "information in other forms that this artifact does not read: appops_accesses.xml (App Ops Recent "
                 "Accesses), appops.xml (App Ops Permission Modes) and appops/discrete (DiscreteNative); the XML files in "
                 "appops/history are read by none of the App Ops artifacts.\n"
                 "Access Time is milliseconds since the Unix epoch, shown in UTC; the stored integer, or text, is in "
                 "Access Time (ms As Stored), and a stored value that is text SQLite cannot read as a number, is below zero or is beyond the years Python's datetime holds leaves Access Time empty; a stored decimal is truncated to a whole millisecond. By the AOSP source it is the actual time of the first access the platform recorded in an "
                 "aggregation window, so a row stands for Access Count accesses and Reject Count rejected attempts "
                 "grouped under the same uid, package, device, op, attribution tag, process state, flags, chain and duration bucket within one window, and the other accesses of the window have no time of their own. The default windows are 1 "
                 "minute for the short database and 15 minutes for the long one, are configurable, and the window a "
                 "device used is not stored. A row records that the platform noted an op for a package; it does not "
                 "say what the app did with it, whether anything was captured, or whether the user knew.\n"
                 "Which ops go to which database is platform configuration. The AOSP default for the short database is "
                 "the camera, microphone and location ops and a few security-relevant ones; everything else goes to "
                 "the long database. On the five images camera (26), microphone (27), coarse location (0) and fine "
                 "location (1) were in the short databases only, 2,936, 573, 22,430 and 75,860 rows, and in none of "
                 "the long ones. A missing row is not evidence that an app did not use an op: records are kept for a "
                 "retention period only (AOSP default 7 days, at most 30), and the observed spans were 3.6 to 8.8 days on eight of the ten Samsung databases, 37.9 days on both databases of one Samsung image, 43.5 days on both databases of hc_pixel8pro_a17 and 104.4 days on both of hc_pixel8pro_a16, so the AOSP figures did not describe three of the seven images.\n"
                 "Access Duration (ms) is, by the AOSP source, -1 for an access noted without a duration, 0 for a "
                 "start or resume of the op, and a positive number of milliseconds on the row recorded when the op "
                 "finished or paused; Total Duration (ms) is the sum of the durations grouped into the row. On the "
                 "five images 193,538 rows held -1, 67,545 held 0 and 67,436 held a positive number. The 67,319 rows "
                 "with Access Count and Reject Count both 0 are exactly the rows with a positive Access Duration and "
                 "Total Duration; 117 further rows had a positive Access Duration, a Total Duration of 0 and a "
                 "non-zero Access Count, which the source reading does not explain. A duration does not by itself say "
                 "that audio, video or location was captured.\n"
                 "App State At Access is uid_state, named from AppOpsManager UID_STATE_*: PERSISTENT 100, TOP 200, "
                 "FOREGROUND_SERVICE_LOCATION 300, FOREGROUND_SERVICE 400, FOREGROUND 500, BACKGROUND 600, CACHED 700 "
                 "and NONEXISTENT 2147483647. Every state except FOREGROUND_SERVICE_LOCATION occurred on the five "
                 "images, NONEXISTENT on one row of one image; a value outside the list is shown as stored. Access "
                 "Flag is the op_flags mask (SELF 1, TRUSTED_PROXY 2, UNTRUSTED_PROXY 4, TRUSTED_PROXIED 8, "
                 "UNTRUSTED_PROXIED 16), something other than SELF alone on 7,920 rows, and SELF on every row of two "
                 "of the five images. Attribution Flags is the attribution_flags mask (ACCESSOR 1, INTERMEDIARY 2, "
                 "RECEIVER 4, TRUSTED 8, NONE for 0): NONE on every row of four of the five images, and 9 or 12 "
                 "(ACCESSOR | TRUSTED, RECEIVER | TRUSTED) on 28 rows of the fifth. Attribution Chain ID is chain_id "
                 "as stored, -1 meaning no chain, which it held on every row of one image; 573 rows across the five "
                 "carried a chain id of 0 or more. Neither the chain id nor the flags have been shown to link rows of "
                 "different packages here.\n"
                 "Device ID is empty where the platform stored NULL, which is what it stores for the default device, "
                 "and it was empty on every row of the five images; in the app_op_history.db layout the default device "
                 "is stored as default:0 and is shown as stored. Package Name is as stored, NULL shown empty. A uid "
                 "can have more than one package name (55 uids in the ten databases did, shared uids), so use Package "
                 "Name and UID together. Op Code is the stored number and Permission its AOSP short name from "
                 "AppOpsManager sAppOpInfos, where the array index is the op code: codes 0 to 155 are the table the "
                 "other App Ops artifacts use, 156 to 169 are added here from android16-qpr2-release "
                 "(android16-qpr1-release gives the same names for 156 to 166). Codes 163 "
                 "(POST_PROMOTED_NOTIFICATIONS, 166 rows, one package, one image) and 166 (READ_CELL_INFO, 3 rows, one "
                 "system package, two images) occurred on the tested images (on the two Pixel 8 Pro images codes 163, 164, 166 and 169 also occurred, and hc_pixel8pro_a17 held 112 rows of code 176, which this table does not name); their names are the AOSP names and were "
                 "not confirmed on a device, and a vendor can use a code that AOSP does not define. Code 96 is a "
                 "retired placeholder and any code above 169 is left unnamed, with the number in Op Code.\n"
                 "The path pattern is tolerant, so a second copy of these files in an extraction adds its rows again, "
                 "and Source File names the file each row came from. A database without the app_op_accesses table logs "
                 "the error and gives no rows; an empty table gives none either. The largest pair of databases tested "
                 "produced 286,819 rows, more than the 50,000 the framework puts on an HTML page, and an output "
                 "folder of about 360 MB. The file-only companion artifact lists rows that are in the database file but not in the log-applied view, or that differ from it.\n"
                 "References: AOSP AppOpHistoryTable (columns), "
                 "https://android.googlesource.com/platform/frameworks/base/+/33b96ce8a122757002e5040ac59824bd7a262e00/services/core/java/com/android/server/appop/AppOpHistoryTable.java#76 "
                 "; AppOpHistoryHelper (duration values -1 and 0, first-event time, window discretization), "
                 "https://android.googlesource.com/platform/frameworks/base/+/33b96ce8a122757002e5040ac59824bd7a262e00/services/core/java/com/android/server/appop/AppOpHistoryHelper.java#132 "
                 "; HistoricalRegistry (file names, 1 and 15 minute windows, 7 and 30 day retention, short-interval "
                 "ops), "
                 "https://android.googlesource.com/platform/frameworks/base/+/33b96ce8a122757002e5040ac59824bd7a262e00/services/core/java/com/android/server/appop/HistoricalRegistry.java#112 "
                 "; AppOpsManager (op names, uid state, op flags, attribution flags), "
                 "https://android.googlesource.com/platform/frameworks/base/+/45034f0663f960d9ee5fb0a101a4732b71f6e2f4/core/java/android/app/AppOpsManager.java#2881 "
                 "; the Android 16.0 release table, "
                 "https://android.googlesource.com/platform/frameworks/base/+/99b01a65cc4c104933788b3143285ab6bae65827/services/core/java/com/android/server/appop/DiscreteOpsTable.java#24 "
                 ".",
        "paths": ('*/system/appops/app_op_history*.db*',),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | 90,420 rows",
            "hc_pixel8pro_a17": "Android 17 | 62,102 rows",
        },
    },
    "appops_history_db_file_only": {
        "name": "App Ops Access History (Database File Only)",
        "description": "Rows that are in the main App Ops history database file but are absent or different once "
                       "its write-ahead log is applied, read from system/appops/app_op_history*.db.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Permissions",
        "notes": "Rows that are in the main App Ops history database file but are not in the database as SQLite reads "
                 "it with the write-ahead log applied, or are there with different values, from the same files as App "
                 "Ops Access History (Database) and with the same columns. Row Status says which: Not in the database "
                 "once the -wal is applied, or Different once the -wal is applied (the row shown has the values stored "
                 "in the database file). The two reads are matched by Row ID. Nothing is reported for a database with "
                 "no -wal beside it, or with an empty one, because then the two reads are the same. Interval is taken "
                 "from the file name and separates the files exactly as Source File does; Row Status held one value on every row of the two Samsung images that had rows.\n"
                 "Evidence tier: proven on real data for the rows reported, not for their cause. Of the five tested Android 16 Samsung images all five carried a -wal for both databases; two had rows in this artifact, 703 (691 short, 12 long) and 238 (17 short, 221 long). On the two corpus Pixel 8 Pro images (Android 16 and 17) both databases also carried a -wal and no row of the main file was missing once it was applied, counted without ALEAPP, so this artifact reports none there. All were Not in the database once the -wal is "
                 "applied; no row differed in value. In each of those database files the Access Time of every such row "
                 "is earlier than the oldest row left in the log-applied view, which is what deleting the oldest "
                 "records would give; the database does not record why a row was removed. The rows can be older than "
                 "the oldest row of the log-applied view by up to 16 days (one short database), so they can show "
                 "accesses that the live view no longer holds.\n"
                 "Not covered: pages freed inside the database file, earlier -wal frames that a checkpoint has already "
                 "folded in, and the -wal's own frames beyond what SQLite applies. A -wal and its database copied at "
                 "different moments can disagree for reasons unrelated to the device. On the two Samsung images that had rows, Android User held 0 on every row, Access Flag held SELF, Attribution Flags held NONE and Device ID was empty. Attribution "
                 "Chain ID held -1 on every row of one image and -1 or 136 on the other, and Reject Count held 0 on every "
                 "row of the 703-row image. See App Ops Access History (Database) for what the other columns mean and "
                 "for the references.",
        "paths": ('*/system/appops/app_op_history*.db*',),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
        },
    },
}

import datetime
import os
import sqlite3

from scripts.artifacts.appOpsAccesses import APP_OP_NAMES, OP_FLAGS, UID_STATES
from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_path,
    get_sqlite_db_records,
    logfunc,
    null_absent_columns,
)

# AppOpsManager.sAppOpInfos at the android16-qpr2-release branch, commit
# 45034f0663f960d9ee5fb0a101a4732b71f6e2f4, codes 156 to 169. The table shared with the XML artifacts
# stops at 155. The first 156 entries of this table are identical to it, and the android16-qpr1-release
# branch (commit 33b96ce8a122757002e5040ac59824bd7a262e00, codes up to 166) gives the same names for
# 156 to 166.
EXTRA_OP_NAMES = {
    156: "EYE_TRACKING_COARSE", 157: "EYE_TRACKING_FINE", 158: "FACE_TRACKING",
    159: "HAND_TRACKING", 160: "HEAD_TRACKING", 161: "SCENE_UNDERSTANDING_COARSE",
    162: "SCENE_UNDERSTANDING_FINE", 163: "POST_PROMOTED_NOTIFICATIONS", 164: "SYSTEM_APPLICATION_OVERLAY",
    165: "READ_CELL_IDENTITY", 166: "READ_CELL_INFO", 167: "COMPUTER_CONTROL",
    168: "READ_OTP_SMS", 169: "ACCESS_LOCAL_NETWORK",
}

# AppOpsManager.UID_STATE_NONEXISTENT is Integer.MAX_VALUE; the shared table stops at CACHED.
UID_STATE_NONEXISTENT = 2147483647

# AppOpsManager.ATTRIBUTION_FLAG_* bit mask.
ATTRIBUTION_FLAGS = (
    (0x1, 'ACCESSOR'),
    (0x2, 'INTERMEDIARY'),
    (0x4, 'RECEIVER'),
    (0x8, 'TRUSTED'),
)

# android.os.UserHandle.PER_USER_RANGE: uid = user id * 100000 + app id.
PER_USER_RANGE = 100000

# Which database each file name is, per HistoricalRegistry (aggregated, two windows) and the
# DiscreteOpsDbHelper database of Android 16.0 (one row per access).
INTERVALS = {
    'app_op_history_short_interval.db': 'Short',
    'app_op_history_long_interval.db': 'Long',
    'app_op_history.db': 'Not aggregated',
}

QUERY = '''
SELECT
id,
uid,
package_name,
device_id,
op_code,
attribution_tag,
uid_state,
op_flags,
attribution_flags,
chain_id,
access_time,
access_duration,
total_duration,
access_count,
reject_count
FROM app_op_accesses;
'''

COMMON_HEADERS = (
    ('Access Time', 'datetime'),
    'Package Name',
    'UID',
    'Android User',
    'Permission',
    'Op Code',
    'Attribution Tag',
    'App State At Access',
    'Access Flag',
    'Attribution Flags',
    'Attribution Chain ID',
    'Access Duration (ms)',
    'Total Duration (ms)',
    'Access Count',
    'Reject Count',
    'Device ID',
    'Interval',
    'Access Time (ms As Stored)',
    'Row ID',
)


def _to_int(value):
    """The value as an int, or None when it is absent or not a whole number."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


def _epoch_ms(value):
    """A UTC datetime from milliseconds since the Unix epoch, or None when it cannot be read: not a
    whole number, below zero, or beyond the years datetime holds. The arithmetic does not go through
    fromtimestamp, whose handling of negative and very large values differs between platforms."""
    number = _to_int(value)
    if number is None or number < 0:
        return None
    try:
        return EPOCH + datetime.timedelta(milliseconds=number)
    except OverflowError:
        return None


def _op_name(code):
    number = _to_int(code)
    if number is None:
        return ''
    return APP_OP_NAMES.get(number) or EXTRA_OP_NAMES.get(number, '')


def _uid_state(value):
    """The AOSP name of the uid state, or the stored value when it is not one the tables name."""
    number = _to_int(value)
    if number is None:
        return '' if value is None else str(value)
    if number == UID_STATE_NONEXISTENT:
        return 'NONEXISTENT'
    return UID_STATES.get(number, str(number))


def _flag_names(value, table, none_name):
    """The names of the bits set in a flag mask, any bit the table lacks as its number, and
    none_name for a mask of zero."""
    number = _to_int(value)
    if number is None:
        return '' if value is None else str(value)
    if number == 0:
        return none_name
    names = [name for bit, name in table if number & bit]
    remainder = number & ~sum(bit for bit, _ in table)
    if remainder:
        names.append(str(remainder))
    return ' | '.join(names)


def _sort_key(record):
    """Oldest access first, then row id, whatever the types stored in the two columns. The order is
    made here, not by an ORDER BY: on a table with no index on access_time SQLite sorts in a
    temporary file, and a temporary folder that is missing or full then fails the whole read."""
    when = _to_int(record[10])
    row_id = _to_int(record[0])
    return (when is None, when or 0, row_id is None, row_id or 0)


def _text(value):
    return '' if value is None else value


def _history_files(context):
    """The history databases found, in a stable order. The -wal and -shm files that the glob also
    matches are not databases and are read through their database."""
    found = []
    for file_found in sorted(str(item) for item in context.get_files_found()):
        if os.path.isdir(file_found) or not file_found.endswith('.db'):
            continue
        if os.path.basename(file_found) not in INTERVALS:
            continue
        found.append(file_found)
    return found


def _output_row(record, interval, relative_path, extra=()):
    """One report row from a QUERY record. Unreadable times are left empty and kept as stored."""
    uid = _to_int(record[1])
    return (
        _epoch_ms(record[10]),
        _text(record[2]),
        record[1],
        '' if uid is None else uid // PER_USER_RANGE,
        _op_name(record[4]),
        record[4],
        _text(record[5]),
        _uid_state(record[6]),
        _flag_names(record[7], OP_FLAGS, '0'),
        _flag_names(record[8], ATTRIBUTION_FLAGS, 'NONE'),
        record[9],
        record[11],
        record[12],
        record[13],
        record[14],
        _text(record[3]),
        interval,
        record[10],
        record[0],
    ) + tuple(extra) + (relative_path,)


def _read_main_file_only(path, query):
    """The rows of the database file itself, ignoring any -wal beside it, as a list of records, or
    [] when it cannot be read. immutable=1 is what makes SQLite skip the log."""
    database = None
    try:
        database = sqlite3.connect(f"file:{get_sqlite_db_path(path)}?mode=ro&immutable=1", uri=True)
        return database.execute(query).fetchall()
    except sqlite3.Error as error:
        logfunc(f'App Ops history: could not read the database file alone, {os.path.basename(path)}: {error}')
        return []
    finally:
        if database is not None:
            database.close()


def _log_applied_records(path, query):
    """The rows SQLite returns for the database with its -wal applied, as a list, or None when they
    cannot be read. A file that is not a database (zeroed or encrypted in the extraction) or a -wal
    that does not belong to it raises a DatabaseError that get_sqlite_db_records does not catch, and
    that would otherwise end the artifact and lose the other databases found."""
    try:
        return [tuple(record) for record in get_sqlite_db_records(path, query)]
    except sqlite3.Error as error:
        logfunc(f'App Ops history: could not read {os.path.basename(path)}: {error}')
        return None


@artifact_processor
def appops_history_db(context):
    data_headers = COMMON_HEADERS + ('Source File',)
    data_list = []
    sources = []

    for file_found in _history_files(context):
        interval = INTERVALS[os.path.basename(file_found)]
        relative_path = context.get_relative_path(file_found)
        sources.append(file_found)
        query = null_absent_columns(file_found, QUERY)
        records = _log_applied_records(file_found, query)
        if records is None and os.path.isfile(file_found + '-wal'):
            logfunc(f'App Ops history: {os.path.basename(file_found)} could not be read with its -wal '
                    'applied; the rows below are those of the database file alone')
            records = _read_main_file_only(file_found, query)
        rows = 0
        unreadable_times = 0
        for record in sorted(records or (), key=_sort_key):
            row = _output_row(record, interval, relative_path)
            if row[0] is None and record[10] is not None:
                unreadable_times += 1
            data_list.append(row)
            rows += 1
        if unreadable_times:
            logfunc(f'App Ops history: {unreadable_times} of {rows} access times in '
                    f'{os.path.basename(file_found)} could not be read as milliseconds since the epoch; '
                    'the stored value is in the Access Time (ms As Stored) column')

    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def appops_history_db_file_only(context):
    data_headers = COMMON_HEADERS + ('Row Status', 'Source File')
    data_list = []
    sources = []

    for file_found in _history_files(context):
        log_file = file_found + '-wal'
        if not os.path.isfile(log_file) or os.path.getsize(log_file) == 0:
            continue
        interval = INTERVALS[os.path.basename(file_found)]
        relative_path = context.get_relative_path(file_found)
        query = null_absent_columns(file_found, QUERY)
        records = _log_applied_records(file_found, query)
        sources.append(file_found)
        if records is None:
            continue
        current = {record[0]: record for record in records}
        for record in sorted(_read_main_file_only(file_found, query), key=_sort_key):
            if record[0] not in current:
                status = 'Not in the database once the -wal is applied'
            elif tuple(record) != current[record[0]]:
                status = 'Different once the -wal is applied'
            else:
                continue
            data_list.append(_output_row(record, interval, relative_path, (status,)))

    return data_headers, data_list, '\n'.join(sources)
