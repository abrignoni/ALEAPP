"""Samsung Reminder (com.samsung.android.app.reminder): reminders and reminder search.

The app keeps its items in databases/reminder.db, a Room database. Live reminders are in
reminder, with their time trigger in alarm_event, their place trigger in location_event and
their text in contents. reminder_trash and the *_trash tables hold the copies the app moves
to reminder_trash and its sibling *_trash tables.
"""

__artifacts_v2__ = {
    "get_samsung_reminders": {
        "name": "Samsung Reminder - Reminders",
        "description": (
            "Parses Samsung Reminder items from the reminder and reminder_trash tables of "
            "reminder.db, one row per reminder row and one per reminder_trash row, with the "
            "creation, modification, completion and trash-row times, the time trigger, the "
            "place trigger (place name, address, coordinates, radius and the time a place "
            "notification was recorded), the title and text, and the stored "
            "cloud_synced_account value."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Reminder",
        "notes": (
            "Read from com.samsung.android.app.reminder/databases/reminder.db with its "
            "-wal. Live items come from reminder, joined on reminder_uuid to alarm_event "
            "(time trigger), location_event (place trigger) and contents (text, joined with "
            "' | ' when an item has several; no registered image has an item with more than "
            "one text row, so the join is not exercised). Trash items come from "
            "reminder_trash with alarm_time_trash, alarm_place_trash and contents_trash, "
            "the same way. Record says which. "
            "Observed on known data (samsung_a166u_a16_known_20261117, Reminder app actions "
            "logged with times during the session; samsung_a166u_a16_known_20261116 for the "
            "first reminder): all four logged reminders appear. The four Created times, the "
            "one logged completion and the one logged deletion are within two seconds of "
            "the logged times; times are shown to the whole second. "
            "On samsung_a166u_a16_known_20261117 item_status was 1 on the items not "
            "completed and 2 on the completed ones, shown as Active and Completed. On "
            "samsung_a166u_a16_known_20261116 the one reminder, not completed, held 0, "
            "shown as 0; the same reminder held 1 a day later, and what separates 0 from 1 "
            "is not established. event_type was 4 on time reminders and 5 on the place "
            "reminder, shown as Trigger Time or Place; transition_type was 2 on the place "
            "reminder set to fire when leaving, shown as Leaving. Any other item_status or "
            "event_type value is shown as stored. Place Transition is blank when no "
            "coordinate is stored. "
            "On the known data, completing a reminder kept it in reminder with Status "
            "Completed and also wrote a copy to reminder_trash with deleted_from "
            "REMINDER_COMP and trash_type 1, holding the item as it was before completion "
            "(Status Active) (two items, one of them logged). On the known data (one item), "
            "deleting a reminder removed it from reminder and left one reminder_trash row "
            "with deleted_from REMINDER and trash_type 0. The two rows with Trash Origin "
            "REMINDER_COMP were copies of completed reminders that were still in reminder, "
            "not deleted reminders; these two values are the only ones observed, and they "
            "are shown as stored. Whether the app shows REMINDER_COMP rows in its Trash "
            "screen is not established. "
            "Created, Last Modified, Completed, Trash Row Written "
            "(reminder_trash.inserted_time), Remind At (alarm remind_time) and Place "
            "Notification (the place trigger's notification_time) are milliseconds since "
            "the Unix epoch converted to UTC; 0 is shown blank. On the known data the place "
            "reminder's live row held notification_time 0 (shown blank), and its trash "
            "copy, written when it was completed, held a notification_time 99 seconds "
            "before the completion; neither that notification nor the completion is in the "
            "session log, which ends before the phone was carried away, so what each "
            "records is not established. "
            "Place Name is place_of_interest and Address is address; on the known data both "
            "held the street address the app resolved for 'Current location'. Latitude, "
            "Longitude and Radius (as stored) are filled only when a coordinate is stored, "
            "and the unit of radius (1.0 on the known data) is not established. Output "
            "includes KML for rows with coordinates. "
            "Cloud Synced Account (as stored) is cloud_synced_account, an email-shaped "
            "value; what sets it is not established (the first reminder was made before the "
            "logged Samsung account sign-in and carries it). It held one value on every row "
            "of the known data. "
            "Left out: condition_preset (the same eight time presets on every registered "
            "image that holds reminder.db, read here as shipped defaults; plus, on "
            "samsung_a166u_a16_known_20261117, two more rows that hold a place and were "
            "absent the day before, one repeating the place reminder's address and "
            "coordinates, the other with a short place name, no address and different "
            "coordinates), space_category (the default local category), sync_dirty_field "
            "and sync_dirty_trash (per-item 0/1 columns, not decoded), "
            "alarm_event.notification_time and alert_time, and the empty attached_file, "
            "card_data, group_share, occasion_event, dates and due_date tables, their trash "
            "copies, alarm_occasion_trash and space_category_trash. Those tables are empty "
            "on every registered image, so what they hold is not exercised; repeating "
            "reminders are not exercised either. Other stores in the package (smp.db, "
            "kmx_sdk.db, shared_prefs) are not read. "
            "Only the known data holds reminders: on every other registered image that "
            "holds reminder.db the reminder and reminder_trash tables are empty "
            "(galaxys10_a10 and cookbook_a11 have no reminder_trash table, and "
            "galaxys10_a10 no completed_time column; a missing column is read as blank). "
            "The user 150 (Secure Folder) reminder.db on samsung_a166u_a16_known_20261117 "
            "holds no reminders, only the eight presets and the category row. On "
            "samsung_a166u_a16_known_20261117 Cloud Synced Account (as stored) held one "
            "value and Android User held 0 on all six rows; Title and Text were identical "
            "on all six rows (each item holds one text line equal to its title), and Place "
            "Name and Address were identical on all six rows (blank on the time reminders, "
            "the same street address on the place reminder and its trash copy)."
        ),
        "paths": ("*/com.samsung.android.app.reminder/databases/reminder.db*",),
        "output_types": "all",
        "artifact_icon": "bell",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.reminder | 6 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.app.reminder 12.7.02.2 | 1 row",
            "adams_ss135dl_a13": "Android 13 | reminder and reminder_trash empty | 0 rows",
            "anne_a15": "Android 15 | reminder and reminder_trash empty | 0 rows",
            "cookbook_a11": "Android 11 | reminder empty, no reminder_trash table | 0 rows",
            "falken_a326u_a13": "Android 13 | reminder and reminder_trash empty | 0 rows",
            "galaxys10_a10": "Android 10 | reminder empty, no reminder_trash table | 0 rows",
            "s20fe_a13": "Android 13 | reminder and reminder_trash empty | 0 rows",
            "samsunga53_a14": "Android 14 | reminder and reminder_trash empty | 0 rows",
            "samsungs20_a13": "Android 13 | reminder and reminder_trash empty | 0 rows",
            "sharon_a13": "Android 13 | reminder and reminder_trash empty | 0 rows",
            "sharon_a14": "Android 14 | reminder and reminder_trash empty | 0 rows",
        },
    },
    "get_samsung_reminder_search": {
        "name": "Samsung Reminder - Search History",
        "description": (
            "Parses the search_history table of Samsung Reminder's reminder.db: each "
            "keyword with its update_time."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Reminder",
        "notes": (
            "Read from the search_history table of "
            "com.samsung.android.app.reminder/databases/reminder.db. Updated is "
            "update_time, milliseconds since the Unix epoch converted to UTC. On "
            "samsung_a166u_a16_known_20261117 the one row matches the one logged search, at "
            "the same second; Type (as stored) held 1 and is not decoded. Whether the app "
            "keeps every search or only recent ones, and whether a repeated search updates "
            "the time, is not established; only one search is in the known data. No other "
            "registered image holds a row."
        ),
        "paths": ("*/com.samsung.android.app.reminder/databases/reminder.db*",),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.reminder | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | search_history empty | 0 rows",
            "adams_ss135dl_a13": "Android 13 | search_history empty | 0 rows",
            "anne_a15": "Android 15 | search_history empty | 0 rows",
            "cookbook_a11": "Android 11 | search_history empty | 0 rows",
            "falken_a326u_a13": "Android 13 | search_history empty | 0 rows",
            "galaxys10_a10": "Android 10 | search_history empty | 0 rows",
            "s20fe_a13": "Android 13 | search_history empty | 0 rows",
            "samsunga53_a14": "Android 14 | search_history empty | 0 rows",
            "samsungs20_a13": "Android 13 | search_history empty | 0 rows",
            "sharon_a13": "Android 13 | search_history empty | 0 rows",
            "sharon_a14": "Android 14 | search_history empty | 0 rows",
        },
    },
}

import re

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
)

PACKAGE = "com.samsung.android.app.reminder"
_USER_RE = re.compile(r"/(?:user|user_de|data_mirror/data_(?:ce|de)/[^/]+)/(\d+)/")

STATUS = {1: "Active", 2: "Completed"}
TRIGGER = {4: "Time", 5: "Place"}
TRANSITION = {2: "Leaving"}


def _container(path):
    """(android user, storage area) of the reminder container a path sits in, or None."""
    norm = str(path).replace("\\", "/")
    idx = norm.find(f"/{PACKAGE}/")
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


def _databases(files_found):
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not path.endswith("reminder.db"):
            continue
        container = _container(path)
        if container is not None:
            yield path, container


def _ms(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    return convert_unix_ts_to_utc(value) if value > 0 else ""


def _columns(path, table):
    return {row[1] for row in get_sqlite_db_records(path, f"PRAGMA table_info({table})")}


def _col(present, table, column):
    return f"{table}.{column}" if column in present else "NULL"


def _label(mapping, value):
    if value is None:
        return ""
    return mapping.get(value, str(value))


def _reminder_query(path, live):
    """One query for the live tables or the trash tables; absent columns read as NULL."""
    if live:
        item, alarm, place, contents = "reminder", "alarm_event", "location_event", "contents"
    else:
        item, alarm, place, contents = ("reminder_trash", "alarm_time_trash",
                                        "alarm_place_trash", "contents_trash")
    item_cols = _columns(path, item)
    alarm_cols = _columns(path, alarm)
    place_cols = _columns(path, place)
    contents_cols = _columns(path, contents)
    select = [
        _col(item_cols, item, "time_created"),
        _col(item_cols, item, "last_modified_time"),
        _col(item_cols, item, "completed_time"),
        _col(item_cols, item, "inserted_time"),
        _col(alarm_cols, "a", "remind_time"),
        _col(place_cols, "p", "notification_time"),
        _col(item_cols, item, "title"),
        (f"(SELECT group_concat(c.text, ' | ') FROM {contents} c "
         f"WHERE c.reminder_uuid = {item}.uuid AND c.text IS NOT NULL)")
        if {"text", "reminder_uuid"} <= contents_cols else "NULL",
        _col(item_cols, item, "item_status"),
        _col(item_cols, item, "event_type"),
        _col(place_cols, "p", "transition_type"),
        _col(place_cols, "p", "place_of_interest"),
        _col(place_cols, "p", "address"),
        _col(place_cols, "p", "latitude"),
        _col(place_cols, "p", "longitude"),
        _col(place_cols, "p", "radius"),
        _col(item_cols, item, "deleted_from"),
        _col(item_cols, item, "trash_type"),
        _col(item_cols, item, "cloud_synced_account"),
        _col(item_cols, item, "uuid"),
        f"{item}._id",
    ]
    joins = ""
    if alarm_cols:
        joins += f" LEFT JOIN {alarm} a ON a.reminder_uuid = {item}.uuid"
    if place_cols:
        joins += f" LEFT JOIN {place} p ON p.reminder_uuid = {item}.uuid"
    return f"SELECT {', '.join(select)} FROM {item}{joins} ORDER BY {item}._id"


@artifact_processor
def get_samsung_reminders(context):
    data_list = []
    source_paths = []
    seen = set()
    for path, container in _databases(context.get_files_found()):
        source_paths.append(path)
        for live, table in ((True, "reminder"), (False, "reminder_trash")):
            if not does_table_exist_in_db(path, table) or "uuid" not in _columns(path, table):
                continue
            for row in get_sqlite_db_records(path, _reminder_query(path, live)):
                (created, modified, completed, trashed, remind_at, place_notified, title, text,
                 status, event_type, transition, place_name, address, latitude, longitude,
                 radius, deleted_from, trash_type, account, uuid, row_id) = row
                key = (container, live, uuid, row_id, remind_at, place_notified)
                if key in seen:
                    continue
                seen.add(key)
                has_place = latitude not in (None, 0, 0.0) or longitude not in (None, 0, 0.0)
                data_list.append((
                    _ms(created), _ms(modified), _ms(completed), _ms(trashed), _ms(remind_at),
                    _ms(place_notified), "Live" if live else "Trash", title or "", text or "",
                    _label(STATUS, status), _label(TRIGGER, event_type),
                    _label(TRANSITION, transition) if transition is not None and has_place
                    else "",
                    place_name or "", address or "",
                    latitude if has_place else "", longitude if has_place else "",
                    radius if has_place else "", deleted_from or "",
                    "" if trash_type is None else trash_type, account or "", uuid or "",
                    container[0],
                ))

    data_headers = (
        ("Created", "datetime"),
        ("Last Modified", "datetime"),
        ("Completed", "datetime"),
        ("Trash Row Written", "datetime"),
        ("Remind At", "datetime"),
        ("Place Notification", "datetime"),
        "Record",
        "Title",
        "Text",
        "Status",
        "Trigger",
        "Place Transition",
        "Place Name",
        "Address",
        ("Latitude", "latitude"),
        ("Longitude", "longitude"),
        "Radius (as stored)",
        "Trash Origin (as stored)",
        "Trash Type (as stored)",
        "Cloud Synced Account (as stored)",
        ("Reminder UUID", "hash"),
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))


@artifact_processor
def get_samsung_reminder_search(context):
    data_list = []
    source_paths = []
    seen = set()
    for path, container in _databases(context.get_files_found()):
        source_paths.append(path)
        if not does_table_exist_in_db(path, "search_history"):
            continue
        cols = _columns(path, "search_history")
        if "keyword" not in cols:
            continue
        query = ("SELECT " + _col(cols, "search_history", "update_time") + ", keyword, "
                 + _col(cols, "search_history", "type") + ", _id FROM search_history ORDER BY _id")
        for saved, keyword, kind, row_id in get_sqlite_db_records(path, query):
            key = (container, row_id, keyword, saved)
            if key in seen:
                continue
            seen.add(key)
            data_list.append((_ms(saved), keyword or "", "" if kind is None else kind,
                              container[0]))

    data_headers = (
        ("Updated", "datetime"),
        "Keyword",
        "Type (as stored)",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))
