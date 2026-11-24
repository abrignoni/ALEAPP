"""Samsung Health medications (com.sec.android.app.shealth).

The Samsung Health app keeps the medications a person adds in databases/medication.db
(medication_schedule) and the doses logged against them in
databases/medication_local_<n>_<n>.db (medication_log_local_cache). Both are plain SQLite,
unlike SecureHealthData.db.
"""

__artifacts_v2__ = {
    "get_samsung_health_medications": {
        "name": "Samsung Health - Medication Schedule",
        "description": (
            "One row per medication_schedule row of Samsung Health's medication.db: "
            "medicine name, nickname, strength, dose date and time, scheduled time and "
            "reminder values."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": (
            "Read from the medication_schedule table of "
            "com.sec.android.app.shealth/databases/medication.db with its -wal. Known data "
            "(samsung_a166u_a16_known_20261117): one made-up medication was added in "
            "Samsung Health and one dose marked as taken on 2026-11-17 between 14:09 and "
            "14:15 UTC, per the session record. Scheduled Time is scheduled_time, "
            "milliseconds since the Unix epoch converted to UTC to whole seconds; on the "
            "known data it was 14:00 UTC on 2026-11-18, the day after the logged dose. It "
            "is a planned time, not a recorded event, and on the known data it is later "
            "than the extraction, so this artifact is not sent to the timeline. Dose Date "
            "is dosage_date. On the known data both stored values are milliseconds that "
            "fall on midnight UTC, so it is shown as the UTC date of the stored value. The "
            "known data does not separate a UTC date from a phone-local date. Dose Time is "
            "dosage_time. It held 540 on the known data and is shown as minutes after "
            "midnight (09:00). On the known data scheduled_time was 14:00 UTC, which is "
            "09:00 in the phone's zone (UTC-5), so 540 reads as a local clock time. One "
            "row; the dose time set in the app was not recorded. Strength Unit, Unit, Type, "
            "Shape, Reminder State and Reminder Style are shown as stored and not decoded. Nickname was empty on the known data. "
            "The stored name matches the made-up name planned for the session except for "
            "letter case. What was typed was not recorded. Not reported: product_id, "
            "ingredient_strength, color_left, color_right, sound_uri, alert_time (equal to "
            "scheduled_time on the known data), snooze_count and _id. Left out: the "
            "medication_medicine_<country>_<n>_<date>_<time>.db file beside it on "
            "samsung_a166u_a16_known_20261117, a drug catalogue of more than 100 MB with "
            "tables such as product_combined and drug_interaction. It is on "
            "samsung_a166u_a16_known_20261117 only. It is absent from "
            "samsung_a166u_a16_known_20261116 and anne_a15, and the date and time in its "
            "name fall in the session in which the medication was added. Its tables hold "
            "product and interaction reference data, not the medications added, so its rows "
            "are not reported. samsung_a166u_a16_known_20261116 and anne_a15 hold "
            "medication.db with no medication_schedule row. No other registered image "
            "scanned holds it (64 of 83 scanned; the 19 not scanned are emulator images). "
            "The water and weight entries made in the same session are not in medication.db "
            "or medication_local_<n>_<n>.db. Where they are stored is not established on "
            "this image. SecureHealthData.db is encrypted and no current artifact reports "
            "water intake or weight from it. On samsung_a166u_a16_known_20261117 the "
            "extraction's Secrets/secrets.json has no SecureHealthData entry for Android "
            "user 0, so SecureHealthData.db stays encrypted there."
        ),
        "paths": ("*/com.sec.android.app.shealth/databases/medication.db*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "activity",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.shealth | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | medication_schedule empty | 0 rows",
            "anne_a15": "Android 15 | medication_schedule empty | 0 rows",
        },
    },
    "get_samsung_health_medication_log": {
        "name": "Samsung Health - Medication Log",
        "description": (
            "One row per medication_log_local_cache row of Samsung Health's "
            "medication_local_<n>_<n>.db: action time (action_date), dose date and time, "
            "quantity and action value, and the medication name from medication.db where "
            "the same medication_uuid is there."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Health & Fitness",
        "notes": (
            "Read from the medication_log_local_cache table of "
            "com.sec.android.app.shealth/databases/medication_local_<n>_<n>.db with its "
            "-wal. Medicine Name comes from medication.db in the same Android user's "
            "container where its medication_uuid equals the log row's; otherwise it is "
            "blank. The blank case and a second Android user are not exercised. Known data "
            "(samsung_a166u_a16_known_20261117): one made-up medication was added in "
            "Samsung Health and one dose marked as taken on 2026-11-17 between 14:09 and "
            "14:15 UTC, per the session record. Action Time is action_date, milliseconds "
            "since the Unix epoch converted to UTC to whole seconds. On the known data it "
            "was 14:12:34 UTC on 2026-11-17, inside the window the session record gives for "
            "the dose. The known data does not show whether it is the time of the tap or a "
            "time the person can set. Dose Date is dosage_date. On the known data both "
            "stored values are milliseconds that fall on midnight UTC, so it is shown as "
            "the UTC date of the stored value. The known data does not separate a UTC date "
            "from a phone-local date. Dose Time is dosage_time. It held 540 on the known "
            "data and is shown as minutes after midnight (09:00). On the known data the "
            "scheduled_time of the same medication in medication.db was 14:00 UTC, which is "
            "09:00 in the phone's zone (UTC-5), so 540 reads as a local clock time. One "
            "row. Action (as stored) is action_type; it held 1 on the one dose, which was "
            "marked as taken. Every value is shown as stored and none is decoded. Only the "
            "value 1 is exercised. Unit is shown as stored. Note is the stored note (empty "
            "on the known data). _id is not reported. samsung_a166u_a16_known_20261116 "
            "holds the file with no log row. No other registered image scanned holds it (64 "
            "of 83 scanned; the 19 not scanned are emulator images)."
        ),
        "paths": (
            "*/com.sec.android.app.shealth/databases/medication_local_*.db*",
            "*/com.sec.android.app.shealth/databases/medication.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.shealth | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | medication_log_local_cache empty | 0 rows",
        },
    },
}

import re
from datetime import datetime, timezone

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
)

PACKAGE = "com.sec.android.app.shealth"
_USER_RE = re.compile(r"/(?:user|user_de|data_mirror/data_(?:ce|de)/[^/]+)/(\d+)/")
_LOCAL_RE = re.compile(r"medication_local_\d+_\d+\.db$")


def _container(path):
    """(android user, storage area) of the shealth container a path sits in, or None."""
    norm = str(path).replace("\\", "/")
    idx = norm.find(f"/{PACKAGE}/databases/")
    if idx < 0:
        return None
    head = norm[:idx + 1]
    area = "de" if ("/user_de/" in head or "/data_mirror/data_de/" in head) else "ce"
    match = None
    for match in _USER_RE.finditer(head):
        pass
    if match and head.endswith(f"/{match.group(1)}/"):
        return int(match.group(1)), area
    if head.rstrip("/").rsplit("/", 1)[-1] == "data":
        # /data/data/<pkg>, and layouts such as userdata/data/<pkg> that keep user 0 there
        return 0, area
    return None


def _ms(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    return convert_unix_ts_to_utc(value) if value > 0 else ""


def _date(value):
    """UTC date of a millisecond value (dosage_date fell on midnight UTC on the known data)."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    if value <= 0:
        return ""
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def _clock(minutes):
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        return ""
    if not 0 <= minutes < 24 * 60:
        return str(minutes)
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _columns(path, table):
    return {row[1] for row in get_sqlite_db_records(path, f"PRAGMA table_info({table})")}


def _select(path, table, wanted):
    present = _columns(path, table)
    return ", ".join(c if c in present else f"NULL AS {c}" for c in wanted)


SCHEDULE = ("medicine_name", "nickname", "medication_uuid", "strength", "strength_unit", "type",
            "shape", "reminder_state", "reminder_style", "dosage_date", "dosage_time",
            "scheduled_time", "quantity", "unit", "_id")


def _schedules(files_found):
    """[(path, container, row dict)] from every medication.db."""
    found = []
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not path.replace("\\", "/").endswith("/medication.db"):
            continue
        container = _container(path)
        if container is None or not does_table_exist_in_db(path, "medication_schedule"):
            continue
        query = f"SELECT {_select(path, 'medication_schedule', SCHEDULE)} FROM medication_schedule"
        for row in get_sqlite_db_records(path, query):
            found.append((path, container, dict(zip(SCHEDULE, row))))
    return found


@artifact_processor
def get_samsung_health_medications(context):
    data_list = []
    source_paths = set()
    seen = set()
    for path, container, row in _schedules(context.get_files_found()):
        source_paths.add(path)
        key = (container, row["medication_uuid"], row["_id"])
        if key in seen:
            continue
        seen.add(key)
        data_list.append((
            _ms(row["scheduled_time"]), _date(row["dosage_date"]), _clock(row["dosage_time"]),
            row["medicine_name"] or "", row["nickname"] or "", row["strength"],
            row["strength_unit"], row["quantity"], row["unit"], row["type"], row["shape"],
            row["reminder_state"], row["reminder_style"], row["medication_uuid"] or "",
            container[0],
        ))

    data_headers = (
        ("Scheduled Time", "datetime"),
        "Dose Date (UTC date of stored value)",
        "Dose Time (stored minutes as clock time)",
        "Medicine Name",
        "Nickname",
        "Strength",
        "Strength Unit (as stored)",
        "Quantity",
        "Unit (as stored)",
        "Type (as stored)",
        "Shape (as stored)",
        "Reminder State (as stored)",
        "Reminder Style (as stored)",
        ("Medication UUID", "hash"),
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(source_paths))


LOG = ("action_date", "medication_uuid", "dosage_date", "dosage_time", "quantity", "unit",
       "action_type", "note", "_id")


@artifact_processor
def get_samsung_health_medication_log(context):
    files_found = context.get_files_found()
    names = {}
    for path, container, row in _schedules(files_found):
        names.setdefault((container[0], row["medication_uuid"]), (row["medicine_name"] or "", path))
    data_list = []
    source_paths = set()
    seen = set()
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not _LOCAL_RE.search(path.replace("\\", "/")):
            continue
        container = _container(path)
        if container is None or not does_table_exist_in_db(path, "medication_log_local_cache"):
            continue
        source_paths.add(path)
        query = (f"SELECT {_select(path, 'medication_log_local_cache', LOG)} "
                 "FROM medication_log_local_cache ORDER BY action_date, _id")
        for row in get_sqlite_db_records(path, query):
            row = dict(zip(LOG, row))
            key = (container, row["_id"], row["medication_uuid"], row["action_date"])
            if key in seen:
                continue
            seen.add(key)
            name, name_path = names.get((container[0], row["medication_uuid"]), ("", ""))
            if name_path:
                source_paths.add(name_path)
            data_list.append((
                _ms(row["action_date"]), _date(row["dosage_date"]), _clock(row["dosage_time"]),
                name, row["quantity"], row["unit"], row["action_type"],
                row["note"] or "", row["medication_uuid"] or "", container[0],
            ))

    data_headers = (
        ("Action Time", "datetime"),
        "Dose Date (UTC date of stored value)",
        "Dose Time (stored minutes as clock time)",
        "Medicine Name",
        "Quantity",
        "Unit (as stored)",
        "Action (as stored)",
        "Note",
        ("Medication UUID", "hash"),
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(source_paths))
