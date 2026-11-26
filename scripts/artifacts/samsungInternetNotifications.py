"""Samsung Internet (com.sec.android.app.sbrowser): web notifications.

Samsung Internet records notifications websites posted in databases/webNotificationDB.db
(notifications). The Chromium Platform Notifications LevelDB and the Preferences file of the
same profile are read by the Chromium Web Notifications and Chromium Site Permissions artifacts.
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
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Browsers",
        "notes": (
            "Read from the notifications table of "
            "com.sec.android.app.sbrowser/databases/webNotificationDB.db with its -wal. Time is "
            "the time column. On the known data it is a 13-digit integer that reads as "
            "milliseconds since the Unix epoch and falls one second after the logged action. It "
            "is shown in UTC, cut to whole seconds. A zero or negative value is shown blank. "
            "Title, Text (the descreption column, spelled that way in the schema), Domain and "
            "URL are stored text. Notification ID (as stored) is the persid column. Read, "
            "Clicked and Seen are shown as stored and not decoded. Row ID is the _id column. "
            "Android User is taken from the container path (/data/data is user 0). It is not a "
            "stored value. A row found under more than one path of the same user is shown once. "
            "The tag column held an empty string on the one known-data row. It is not shown. "
            "The icon blob is not shown. Known data (samsung_a166u_a16_known_20261117, Samsung "
            "Internet 30.0.5.27 per the session record): on 2026-11-17 the permission request "
            "of a public notification test site was tapped at 06:36:52 UTC and Allow was tapped "
            "at 06:37:01. The page's display button was tapped at 06:37:13 and one notification "
            "was posted. The one row is that notification, at 06:37:14, with Read 1, Clicked 0 "
            "and Seen 0. Whether a row stays after the notification is dismissed is not "
            "established. The Chromium Web Notifications artifact reads the Platform "
            "Notifications LevelDB in app_sbrowser/Default. On the known data it held one "
            "record for the same notification: its key ends with this row's persid and its "
            "Created time falls in the same second as this row's Time. That artifact does not "
            "show the notification id, so match the two on Site, Title and Created. The record "
            "held click counts of 0, no click or close time and Closed Reason Unknown. The "
            "Chromium Site Permissions artifact reads the site's notification permission from "
            "the Preferences file. On the 11 other corpus images where webNotificationDB.db was "
            "found the notifications table is empty. Images with no member listing were not "
            "scanned."
        ),
        "paths": ("*/com.sec.android.app.sbrowser/databases/webNotificationDB.db*",),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.sbrowser | 1 row",
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
}

import re

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
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
