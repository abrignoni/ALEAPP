"""Samsung Clock (com.sec.android.app.clockpackage): alarms and world clock cities."""

__artifacts_v2__ = {
    "samsungClockAlarms": {
        "name": "Samsung Clock - Alarms",
        "description": (
            "Alarms in the Samsung Clock app's alarm.db: name, when the alarm was created, its time, the "
            "repeat days, whether it is on, the next alert time and any stored location."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Samsung Clock",
        "notes": (
            "Read from the alarm table of com.sec.android.app.clockpackage/databases/alarm.db with "
            "its -wal; on the tested images the file is in the app's device-encrypted (user_de) "
            "folder, and samsunga53_a14 also holds one in the credential-encrypted folder. Field "
            "meanings come from the Clock app's own code, decompiled with jadx from the base.apk on "
            "samsung_a166u_a16_known_20261117 (com.sec.android.app.clockpackage 12.5.07.13 per the "
            "session record), and are checked against the known data below. Created is createtime and "
            "Alert Time is alerttime, both milliseconds since the Unix epoch shown in UTC. Alert Time "
            "is the next time the app computed for the alarm to ring; it is kept on alarms that are "
            "off. Alarm Time is alarmtime, stored as hours times 100 plus minutes in the phone's "
            "local time, and shown as HH:MM. Active is the stored active value: 1 was on and 0 off on "
            "the known data. Repeat is decoded from repeattype (shown as stored in Repeat Type): in "
            "AlarmItemBase the low four bits are 1 for a one-time alarm (isOneTimeAlarm) and 5 for a "
            "weekly one (isWeeklyAlarm), and each of the next seven four-bit groups is one day, "
            "Saturday in the lowest through Sunday in the highest (clearRepeatDay). A weekly alarm "
            "lists its days; on the known data the one day set on a one-time alarm was the day it was "
            "due to ring. Another low value is shown as Other with the days. Location Alarm is "
            "locationactive as stored, and Latitude, Longitude and Location Text are the stored "
            "values; no tested alarm had a location set, so those columns were 0 or empty on every "
            "row and the path is not exercised. Known data (samsung_a166u_a16_known_20261117 and "
            "samsung_a166u_a16_known_20261116): an alarm named KD was saved for 4:44 AM one time at "
            "15:31:39 UTC on 2026-11-16 and turned off; KD_weekday_alarm (7:30 AM, Monday to Friday, "
            "then turned off) and KD_onetime_alarm (2:30 PM that day, left on) were saved at 06:15:43 "
            "and 06:16:33 UTC on 2026-11-17, per the session record. Created was 15:31:37, 06:15:43 "
            "and 06:16:33 for the three, Alarm Time 04:44, 07:30 and 14:30, KD_onetime_alarm had "
            "Active 1 and Alert Time 19:30 UTC, and both one-time alarms showed Tuesday, the day each "
            "was due. The fourth row is an unnamed 6:00 weekday alarm that was on the phone before "
            "the session, created on 2026-02-13. The other tested images each hold one or two unnamed "
            "weekly alarms, all off. Not reported: the sound, volume, vibration, snooze, briefing, "
            "background and group columns, and the groupAlarm table (empty on the tested images). "
            "Other Clock databases are named in the World Clock Cities notes. Android User is the "
            "user of the app data folder the file is in, taken from its path (data/data and user_de/0 "
            "are user 0). Rows found in more than one copy of the same user's database are shown "
            "once. On every row of the tested images Location Alarm (as stored), Latitude and "
            "Longitude held 0, Location Text was empty, and Android User held 0."
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
            "samsunga53_a14": "Android 14 | com.sec.android.app.clockpackage | 1 row (same alarm in both folders)",
            "samsungs20_a13": "Android 13 | com.sec.android.app.clockpackage | 1 row",
            "sharon_a13": "Android 13 | com.sec.android.app.clockpackage | 1 row",
            "sharon_a14": "Android 14 | com.sec.android.app.clockpackage | 1 row",
        },
    },
    "samsungClockWorldClock": {
        "name": "Samsung Clock - World Clock Cities",
        "description": (
            "Cities in the Samsung Clock app's world clock list (worldclock.db) and dual clock widget "
            "(dualclock), with the stored time zone."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Samsung Clock",
        "notes": (
            "Read from two tables in com.sec.android.app.clockpackage/databases/: worldclock in "
            "worldclock.db (the Clock app's World clock list) and dualclock in dualclock (in the "
            "app's code, the data of the dual clock widget, "
            "com.sec.android.widgetapp.dualclockdigital). One row per city; Store names the table. "
            "Field meanings come from the Clock app's own code, decompiled with jadx from the "
            "base.apk on samsung_a166u_a16_known_20261117 (com.sec.android.app.clockpackage "
            "12.5.07.13 per the session record), and are checked against the known data below. City "
            "and Time Zone are city and gmt as stored: on the known data worldclock held a time zone "
            "name in gmt and dualclock held an offset in milliseconds. Order is _id. Known data "
            "(samsung_a166u_a16_known_20261117, compared with samsung_a166u_a16_known_20261116): "
            "before the session the World clock tab showed London and New York, and the earlier image "
            "held those two cities only in dualclock, with no worldclock.db. After Tokyo was added at "
            "06:18:02 UTC on 2026-11-17 (per the session record), worldclock held New York, London "
            "and Tokyo and dualclock was unchanged. The rows hold no time of when a city was added. "
            "On the other tested images dualclock held no rows and worldclock was absent or empty. "
            "Not reported from the Clock app: the timerlife table of timer.db (the same three preset "
            "timers on every tested image), the MultiTimer and timerWidget tables of timer.db, "
            "lapHistory in Stopwatch.db, watchinfo.db, alertbg.db, spotifydb and celebvoicepkgs.db, "
            "all empty on the tested images. Android User is the user of the app data folder the file "
            "is in, taken from its path. Android User held 0 on every row of the tested images."
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
                 "locationactive", "latitude", "longitude", "locationtext")


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
            (row_id, active, created, alert, alarm_time, repeat, name, location_active, latitude,
             longitude, location_text) = row
            key = (user, row_id, created, name)
            if key in seen:
                continue
            seen.add(key)
            data_list.append((
                _ms(created), _ms(alert), _clock(alarm_time), name or "", _repeat(repeat), active,
                location_active, latitude, longitude, location_text or "", repeat, user,
            ))
    data_headers = (
        ("Created", "datetime"),
        ("Alert Time", "datetime"),
        "Alarm Time (local)",
        "Name",
        "Repeat",
        "Active (as stored)",
        "Location Alarm (as stored)",
        "Latitude",
        "Longitude",
        "Location Text",
        "Repeat Type (as stored)",
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
    data_headers = ("City", "Time Zone (as stored)", "Order", "Store", "Android User")
    return data_headers, data_list, "\n".join(source_paths)
