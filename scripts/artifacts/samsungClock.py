"""Samsung Clock (com.sec.android.app.clockpackage): alarms and world clock cities."""

__artifacts_v2__ = {
    "samsungClockAlarms": {
        "name": "Samsung Clock - Alarms",
        "description": (
            "Alarms in the Samsung Clock app's alarm.db: name, the stored create time, the alarm time, the "
            "repeat days, the stored active value, alarm type flags and the stored alert time."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Samsung Clock",
        "notes": (
            "Read from the alarm table of com.sec.android.app.clockpackage/databases/alarm.db with "
            "its -wal. On the 11 tested images the file is in the app's device-encrypted (user_de) "
            "folder. samsunga53_a14 also holds the same file under data_mirror/data_de, and it is "
            "read once. Field meanings come from the code of Clock 12.5.07.16 (the version in the "
            "manifest of the base.apk on samsung_a166u_a16_known_20261117), decompiled with jadx. The "
            "session record logged 12.5.07.13 for the 2026-11-16 actions. The other nine tested "
            "images have an alarm table without the alarm_group_id column, and the code of the "
            "versions that wrote them was not read. The time, repeat and active fields are compared "
            "with the known data below. Create Time is createtime and Alert Time is alerttime, both read by the shared converter and shown in UTC. The converter picks the unit from the value's size: 10,000,000,000 up to 10,000,000,000,000 is read as milliseconds since the Unix epoch, and a smaller value as seconds. Every tested value has 13 digits, so it was read as milliseconds. A stored 0, negative value or non-number is blank. In the code createtime is set to the "
            "current time when an alarm is saved from the edit screen, including when an existing "
            "alarm is edited and saved (not tested), and also when an alarm is created by a SET_ALARM "
            "intent, by Bixby, by the bedtime screens or as the preset alarm. On the known data it "
            "was the logged save time for two alarms and 2 seconds before the logged time for the one "
            "created by intent, and it did not change when an alarm was turned off. Alert Time is "
            "alerttime: on the three known-data alarms it was the next time the alarm was due. What it records on other alarms was not tested. The code path for an alarm with a selected date is described below. Every alarm on the other nine tested images is off. On cookbook_a11 and galaxys10_a10 Alert Time is earlier than Create Time. Alarm Time is alarmtime, stored as hours times 100 plus minutes in the phone's local time, and shown as HH:MM. A value that does not give hours 0 to 23 and minutes 0 to 59 is shown as the stored number, and a non-number is blank. No tested row was in either state. Active is the stored active value: 1 was "
            "on and 0 off on the known data. The code also sets and tests 2, beside log text that "
            "reads ALARM_SNOOZE (AlarmItem). No tested row held 2. Repeat is decoded from repeattype "
            "(shown as stored in Repeat Type): in AlarmItemBase the low four bits are 1 for a "
            "one-time alarm (isOneTimeAlarm) and 5 for a weekly one (isWeeklyAlarm), and each of the "
            "next seven four-bit groups is one day, Saturday in the lowest through Sunday in the "
            "highest (clearRepeatDay). A weekly alarm lists its days; on the known data the one day "
            "set on a one-time alarm was the day it was due to ring. Another low value is shown as "
            "Other with the days; no tested row had one. Alarm Flags names the bits of dailybrief "
            "(shown as stored in Daily Brief) that AlarmItemBase defines as specific date (1), "
            "holiday (4), working day (8), bedtime (131072) and wake-up time (262144); other bits "
            "defined there (sound, voice and briefing options, substitute holiday, pre-dismissed, "
            "sleep schedule) are not named. In the edit screen code an alarm saved with a selected "
            "date gets the specific date bit and its alerttime is set to that date "
            "(AlarmEditActivity.saveDetailChange); no tested row had this bit. On the tested images "
            "only one anne_a15 row had a named bit (bedtime). On samsung_a166u_a16_known_20261117 "
            "Alarm Flags was empty and Daily Brief held 0 on every row, and Name was empty on every "
            "row of the images other than the two known-data ones. Known data "
            "(samsung_a166u_a16_known_20261117 and samsung_a166u_a16_known_20261116): an alarm named "
            "KD was created by a SET_ALARM intent for 4:44 AM one time at 15:31:39 UTC on 2026-11-16 "
            "and turned off; KD_weekday_alarm (7:30 AM, Monday to Friday, then turned off) and "
            "KD_onetime_alarm (2:30 PM that day, left on) were saved at 06:15:43 and 06:16:33 UTC on "
            "2026-11-17, per the session record. Create Time was 15:31:37, 06:15:43 and 06:16:33 for "
            "the three, Alarm Time 04:44, 07:30 and 14:30, KD_onetime_alarm had Active 1 and Alert "
            "Time 19:30 UTC, and both one-time alarms showed Tuesday, the day each was due. KD and KD_weekday_alarm, both turned off, had Active 0, and KD_weekday_alarm showed Weekly: Mon, Tue, Wed, Thu, Fri. Every "
            "tested image holds an unnamed 06:00 Monday to Friday alarm that is off; on the known "
            "data its createtime is 2026-02-13, before the session. That code creates a preset 06:00 "
            "weekday alarm when the alarm table is empty (AlarmMainDbRepo.setPresetAlarm), so this "
            "row need not come from the user. anne_a15 holds one more unnamed weekly alarm, off. Not "
            "reported: the sound, volume, vibration, snooze, background, group, notitype, sbd, "
            "bedalarmtime and map columns (map holds the alarm's UUID in the 12.5.07.16 code), and "
            "locationactive, latitude, longitude and locationtext: the first three held 0 on every "
            "tested row, and in that code their values are set on an alarm only when a row is read "
            "from the database, and the insert and update statements write them back; that code uses "
            "locationtext for a Spotify music path; it was empty on every tested row. The groupAlarm "
            "table is present only on the two samsung_a166u images and is empty there. Other Clock "
            "databases are named in the World Clock Cities notes. Android User is the user of the app "
            "data folder the file is in, taken from its path (data/data and user_de/0 are user 0). "
            "Android User held 0 on every row of the tested images. A row with the same user, _id, "
            "createtime and name in a second copy of the database is shown once, from the copy read "
            "first; this was not exercised on a corpus image."
        ),
        "paths": ("*/com.sec.android.app.clockpackage/databases/alarm.db*",),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.clockpackage | 4 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.clockpackage | 2 rows",
            "anne_a15": "Android 15 | com.sec.android.app.clockpackage | 2 rows",
            "cookbook_a11": "Android 11 | com.sec.android.app.clockpackage | 1 row",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.clockpackage | 1 row",
            "galaxys10_a10": "Android 10 | com.sec.android.app.clockpackage | 1 row",
            "s20fe_a13": "Android 13 | com.sec.android.app.clockpackage | 1 row",
            "samsunga53_a14": "Android 14 | com.sec.android.app.clockpackage | 1 row (file also under data_mirror/data_de)",
            "samsungs20_a13": "Android 13 | com.sec.android.app.clockpackage | 1 row",
            "sharon_a13": "Android 13 | com.sec.android.app.clockpackage | 1 row",
            "sharon_a14": "Android 14 | com.sec.android.app.clockpackage | 1 row",
        },
    },
    "samsungClockWorldClock": {
        "name": "Samsung Clock - World Clock Cities",
        "description": (
            "Cities in the Samsung Clock app's worldclock.db and dualclock databases, with the stored "
            "time zone value."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Samsung Clock",
        "notes": (
            "Read from two tables in com.sec.android.app.clockpackage/databases/: worldclock in "
            "worldclock.db and dualclock in dualclock. The worldclock table holds the Clock app's "
            "World clock list. The dualclock table is served by the content provider in "
            "com.sec.android.widgetapp.dualclockdigital; the app's code writes it from the dual clock "
            "widget, and also names the AOD screen, the cover screen and a watch as places a city is "
            "picked from; which one wrote the tested rows was not established. One row per stored row of each table, so a city held in both tables is shown once per table. A row with the same Android user, table, Row ID and city as one already read from another copy of the database is not repeated. Store names the table. Field meanings come from the code of Clock 12.5.07.16 (the "
            "version in the manifest of the base.apk on samsung_a166u_a16_known_20261117), decompiled "
            "with jadx. The session record logged 12.5.07.13 for the 2026-11-16 actions. The code of "
            "the Clock versions on the other tested images was not read. City and Time Zone are city "
            "and gmt as stored: on the known data worldclock held a time zone name in gmt, and "
            "dualclock held a number that fits an offset from UTC in milliseconds (-18000000 for New "
            "York in November); the row writer stores City.getOffsetMillis, which returns the offset "
            "in force when it is called, so the value reflects the date the row was written; whether "
            "the app rewrites it when daylight saving changes was not established. Row ID is _id; on "
            "the known data the app listed the cities in a different order. Known data "
            "(samsung_a166u_a16_known_20261117, compared with samsung_a166u_a16_known_20261116): "
            "before the 2026-11-17 Clock actions the World clock tab showed London and New York, and "
            "the earlier image held those two cities only in dualclock, with no worldclock.db. "
            "Whether these two cities were added by a person was not established; London has the "
            "unique id that the code names DEFAULT_CITY (44). After Tokyo was added at 06:18:02 UTC "
            "on 2026-11-17 (per the session record), worldclock held New York, London and Tokyo and "
            "dualclock was unchanged. The rows hold no time of when a city was added. On the other "
            "nine tested images dualclock was absent, 0 bytes, had no dualclock table, or held no "
            "rows, and worldclock.db was absent or empty. Not reported from the Clock app: the "
            "timerlife table of timer.db (the same three unnamed 10, 15 and 30 minute timers on the "
            "nine tested images that hold timer.db), and the MultiTimer and timerWidget tables of "
            "timer.db, lapHistory in Stopwatch.db, watchinfo.db, alertbg.db, spotifydb and "
            "celebvoicepkgs.db, all empty where present on the tested images. Android User is the "
            "user of the app data folder the file is in, taken from its path. Android User held 0 on "
            "every row of the tested images."
        ),
        "paths": (
            "*/com.sec.android.app.clockpackage/databases/worldclock.db*",
            "*/com.sec.android.app.clockpackage/databases/dualclock*",
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.clockpackage | 5 rows (worldclock 3, dualclock 2)",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.clockpackage | 2 rows (dualclock 2)",
            "galaxys10_a10": "Android 10 | com.sec.android.app.clockpackage | worldclock and dualclock empty | 0 rows",
        },
    },
}


from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
)

PACKAGE = "/com.sec.android.app.clockpackage/databases/"
# AlarmItemBase.clearRepeatDay: day group n (bits 4n..4n+3) is Calendar day 8 - n.
DAY_GROUPS = ((7, "Sun"), (6, "Mon"), (5, "Tue"), (4, "Wed"), (3, "Thu"), (2, "Fri"), (1, "Sat"))
ALARM_COLUMNS = ("_id", "active", "createtime", "alerttime", "alarmtime", "repeattype", "name",
                 "dailybrief")
# AlarmItemBase: dailybrief bits named here.
FLAG_BITS = ((1, "Specific date"), (4, "Holiday"), (8, "Working day"), (131072, "Bedtime"),
             (262144, "Wake-up time"))


def _user(context, path):
    key, _rank = canonical_path(context.get_relative_path(path))
    parts = key.split("\x00")
    return parts[1].rsplit(":", 1)[-1] if len(parts) >= 3 else ""


def _ms(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    return convert_unix_ts_to_utc(value) if value > 0 else ""


def _clock(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    hours, minutes = divmod(value, 100)
    if 0 <= hours < 24 and 0 <= minutes < 60:
        return f"{hours:02d}:{minutes:02d}"
    return str(value)


def _repeat(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    days = [name for group, name in DAY_GROUPS if (value >> (4 * group)) & 0xF]
    kind = value & 0xF
    label = {1: "One time", 5: "Weekly"}.get(kind, "Other")
    return f"{label}: {', '.join(days)}" if days else label


def _flags(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    return ", ".join(name for bit, name in FLAG_BITS if value & bit)


def _select(path, table, wanted):
    present = {row[1] for row in get_sqlite_db_records(path, f'PRAGMA table_info("{table}")')}
    return ", ".join(column if column in present else f"NULL AS {column}" for column in wanted)


@artifact_processor
def samsungClockAlarms(context):
    data_list = []
    source_paths = []
    seen = set()
    for path in unique_files(context):
        path = str(path)
        normalized = path.replace("\\", "/")
        if is_sqlite_sidecar(path) or not normalized.endswith(PACKAGE + "alarm.db"):
            continue
        if not does_table_exist_in_db(path, "alarm"):
            continue
        source_paths.append(path)
        user = _user(context, path)
        query = f"SELECT {_select(path, 'alarm', ALARM_COLUMNS)} FROM alarm ORDER BY createtime, _id"
        for row in get_sqlite_db_records(path, query):
            (row_id, active, created, alert, alarm_time, repeat, name, daily_brief) = row
            key = (user, row_id, created, name)
            if key in seen:
                continue
            seen.add(key)
            data_list.append((
                _ms(created), _ms(alert), _clock(alarm_time), name or "", _repeat(repeat), active,
                _flags(daily_brief), repeat, daily_brief, user,
            ))
    data_headers = (
        ("Create Time", "datetime"),
        ("Alert Time", "datetime"),
        "Alarm Time (local)",
        "Name",
        "Repeat",
        "Active (as stored)",
        "Alarm Flags",
        "Repeat Type (as stored)",
        "Daily Brief (as stored)",
        "Android User",
    )
    return data_headers, data_list, "\n".join(source_paths)


@artifact_processor
def samsungClockWorldClock(context):
    data_list = []
    source_paths = []
    seen = set()
    for path in unique_files(context):
        path = str(path)
        normalized = path.replace("\\", "/")
        if is_sqlite_sidecar(path) or PACKAGE not in normalized:
            continue
        name = normalized.rsplit("/", 1)[-1]
        table = {"worldclock.db": "worldclock", "dualclock": "dualclock"}.get(name)
        if table is None or not does_table_exist_in_db(path, table):
            continue
        source_paths.append(path)
        user = _user(context, path)
        query = f"SELECT {_select(path, table, ('_id', 'city', 'gmt'))} FROM {table} ORDER BY _id"
        for row_id, city, gmt in get_sqlite_db_records(path, query):
            key = (user, table, row_id, city)
            if key in seen:
                continue
            seen.add(key)
            data_list.append((city or "", "" if gmt is None else gmt, row_id, table, user))
    data_headers = ("City", "Time Zone (as stored)", "Row ID", "Store", "Android User")
    return data_headers, data_list, "\n".join(source_paths)
