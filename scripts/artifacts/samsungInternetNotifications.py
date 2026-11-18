"""Samsung Internet (com.sec.android.app.sbrowser): web notifications and notification permissions.

Samsung Internet keeps the notifications websites posted in databases/webNotificationDB.db
(notifications) and the per-site notification permissions in the Chromium profile's
app_sbrowser/Default/Preferences (profile.content_settings.exceptions.notifications).
"""

__artifacts_v2__ = {
    "get_samsung_internet_web_notifications": {
        "name": "Samsung Internet - Web Notifications",
        "description": (
            "Parses the notifications table of Samsung Internet's webNotificationDB.db: each "
            "notification row with its time, title, text, site, notification id and the "
            "stored read, clicked and seen values."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            "Read from the notifications table of "
            "com.sec.android.app.sbrowser/databases/webNotificationDB.db with its -wal. "
            "Time is the time column, milliseconds since the Unix epoch converted to UTC in "
            "whole seconds. Title, Text (the descreption column, spelled that way in the "
            "schema), Domain and URL are stored text. Notification ID (as stored) is "
            "the persid column. Read, Clicked and Seen are shown as stored and not decoded; the "
            "tag column was empty and is not shown, and the icon blob is not shown. "
            "Known data (samsung_a166u_a16_known_20261117, Samsung Internet 30.0.5.27, "
            "actions logged during the session): notifications were allowed for a public "
            "notification test site at 06:36:52 to 06:37:01 UTC and one notification was "
            "displayed at 06:37:13. The one row is that notification, at 06:37:14, with "
            "Read 1, Clicked 0 and Seen 0. Whether a row stays after the notification is "
            "dismissed is not established. On the 11 other registered images whose listing "
            "holds webNotificationDB.db the table is empty."
        ),
        "paths": ("*/com.sec.android.app.sbrowser/databases/webNotificationDB.db*",),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.sbrowser 30.0.5.27 | 1 row",
            "adams_ss135dl_a13": "Android 13 | notifications empty | 0 rows",
            "anne_a15": "Android 15 | notifications empty | 0 rows",
            "cookbook_a11": "Android 11 | notifications empty | 0 rows",
            "falken_a326u_a13": "Android 13 | notifications empty | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | notifications empty | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | notifications empty | 0 rows",
            "s20fe_a13": "Android 13 | notifications empty | 0 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | notifications empty | 0 rows",
            "samsunga53_a14": "Android 14 | notifications empty | 0 rows",
            "sharon_a13": "Android 13 | notifications empty | 0 rows",
            "sharon_a14": "Android 14 | notifications empty | 0 rows",
        },
    },
    "get_samsung_internet_notification_permissions": {
        "name": "Samsung Internet - Notification Permissions",
        "description": (
            "Parses the per-site notification permissions in Samsung Internet's Chromium "
            "Preferences file (profile.content_settings.exceptions.notifications): one row "
            "per site pattern with the stored setting value."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            "Read from the profile.content_settings.exceptions.notifications object of "
            "com.sec.android.app.sbrowser/app_sbrowser/Default/Preferences, a JSON file. "
            "One row per site pattern. Setting (as stored) is the stored setting value and "
            "is not decoded; Samsung's file held no last_modified value for the entry. "
            "Known data (samsung_a166u_a16_known_20261117, Samsung Internet 30.0.5.27, "
            "actions logged during the session): notifications were allowed for a public "
            "notification test site at 06:36:52 to 06:37:01 UTC and one notification was "
            "displayed at 06:37:13. The one row is that site's pattern with setting 1. "
            "On the 10 other registered images whose listing holds this Preferences file "
            "the object is empty. "
            "Not found in the browser's stores on the known data: the tab lock applied to "
            "one tab (pintab.db stayed empty and no other database or preference read here "
            "holds it) and the Secret mode tab, which was not restored after the app was "
            "force-stopped."
        ),
        "paths": ("*/com.sec.android.app.sbrowser/app_sbrowser/Default/Preferences",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.sbrowser 30.0.5.27 | 1 row",
            "anne_a15": "Android 15 | no notification permission entry | 0 rows",
            "cookbook_a11": "Android 11 | no notification permission entry | 0 rows",
            "falken_a326u_a13": "Android 13 | no notification permission entry | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | no notification permission entry | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | no notification permission entry | 0 rows",
            "s20fe_a13": "Android 13 | no notification permission entry | 0 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | no notification permission entry | 0 rows",
            "samsunga53_a14": "Android 14 | no notification permission entry | 0 rows",
            "sharon_a13": "Android 13 | no notification permission entry | 0 rows",
            "sharon_a14": "Android 14 | no notification permission entry | 0 rows",
            "adams_ss135dl_a13": "Android 13 | no Preferences file | 0 rows",
        },
    },
}

import json
import re

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
    logfunc,
)

PACKAGE = "com.sec.android.app.sbrowser"
_USER_RE = re.compile(r"/(?:user|user_de|data_mirror/data_(?:ce|de)/[^/]+)/(\d+)/")


def _container(path, marker):
    """(android user, storage area) of the sbrowser container a path sits in, or None."""
    norm = str(path).replace("\\", "/")
    idx = norm.find(f"/{PACKAGE}/{marker}")
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


WANTED = ("time", "title", "descreption", "domain", "url", "tag", "persid", "read", "clicked",
          "seen", "_id")


@artifact_processor
def get_samsung_internet_web_notifications(context):
    data_list = []
    source_paths = set()
    seen_rows = set()
    for path in context.get_files_found():
        path = str(path)
        if is_sqlite_sidecar(path) or not path.endswith("webNotificationDB.db"):
            continue
        container = _container(path, "databases/")
        if container is None:
            continue
        source_paths.add(path)
        if not does_table_exist_in_db(path, "notifications"):
            continue
        present = {row[1] for row in get_sqlite_db_records(path, "PRAGMA table_info(notifications)")}
        select = ", ".join(c if c in present else f"NULL AS {c}" for c in WANTED)
        for row in get_sqlite_db_records(path, f"SELECT {select} FROM notifications ORDER BY time, _id"):
            (stamp, title, text, domain, url, _tag, persid, read, clicked, seen, row_id) = row
            key = (container[0], row_id, stamp, persid)
            if key in seen_rows:
                continue
            seen_rows.add(key)
            data_list.append((
                _ms(stamp), title or "", text or "", domain or "", url or "",
                persid or "", read, clicked, seen, row_id, container[0],
            ))

    data_headers = (
        ("Time", "datetime"),
        "Title",
        "Text",
        "Domain",
        "URL",
        "Notification ID (as stored)",
        "Read (as stored)",
        "Clicked (as stored)",
        "Seen (as stored)",
        "Row ID",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(source_paths))


@artifact_processor
def get_samsung_internet_notification_permissions(context):
    data_list = []
    source_paths = set()
    seen_rows = set()
    for path in context.get_files_found():
        path = str(path)
        if not path.replace("\\", "/").endswith("/app_sbrowser/Default/Preferences"):
            continue
        container = _container(path, "app_sbrowser/")
        if container is None:
            continue
        source_paths.add(path)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                prefs = json.load(handle)
        except (OSError, ValueError) as error:
            logfunc(f"Samsung Internet Preferences not read: {path}: {error}")
            continue
        exceptions = prefs.get("profile", {}).get("content_settings", {}).get("exceptions", {})
        notifications = exceptions.get("notifications", {}) if isinstance(exceptions, dict) else {}
        if not isinstance(notifications, dict):
            continue
        for pattern, entry in sorted(notifications.items()):
            entry = entry if isinstance(entry, dict) else {}
            key = (container[0], pattern)
            if key in seen_rows:
                continue
            seen_rows.add(key)
            data_list.append((
                pattern, "" if entry.get("setting") is None else entry.get("setting"),
                container[0],
            ))

    data_headers = (
        "Site Pattern",
        "Setting (as stored)",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(source_paths))
