__artifacts_v2__ = {
    "get_firefoxRecentlyClosedTabs": {
        "name": "Firefox - Recently Closed Tabs",
        "description": "Parses Firefox recently closed tabs (the created_at time, title, URL and Android user) from each recently_closed_tabs database.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Browsers",
        "notes": (
            "Created At is the created_at column of the recently_closed_tabs table. It is read as milliseconds since 1970 UTC and shown as UTC. In Mozilla's android-components source, the action that updates a tab's lastAccess takes System.currentTimeMillis as its default value (https://github.com/mozilla-mobile/firefox-android/blob/fe8a71cd70ad5674abe1824fe11dc78372b736c2/android-components/components/browser/state/src/main/java/mozilla/components/browser/state/action/BrowserAction.kt#L390-L394). The HTML report and the TSV keep the milliseconds, and LAVA keeps whole seconds. A value of 0 or less is shown blank. No row on the images run holds one. The 0 case was exercised only by a unit test with made-up values. A negative value was not exercised. Each recently_closed_tabs database is read once, however many storage views of it the extraction holds. A rollback snapshot is skipped only when the live copy is also found and the two are identical, including their -wal and -journal. Otherwise it is read. No image run holds a snapshot of this store. Android User comes from the store's path: 0 for data/data, the number in the path for data/user/<n> and the other per-user layouts (data_mirror, userdata, user_de), and blank for any other path, including a rollback snapshot. Only the data/data case occurred on the images run. The others were exercised by unit tests with made-up values: data/user/<n> through this module, the rest on the shared path helper. On the 39 images run, 7 hold the store. Six hold it empty, under three views each. One (pixel7a_a14) gave one row, for user 0. The column name does not say what the time marks. In the same source the row is built with createdAt = lastAccess (https://github.com/mozilla-mobile/firefox-android/blob/fe8a71cd70ad5674abe1824fe11dc78372b736c2/android-components/components/feature/recentlyclosed/src/main/java/mozilla/components/feature/recentlyclosed/db/RecentlyClosedTabEntity.kt#L45-L52), and lastAccess is documented there as the last time the tab was selected (https://github.com/mozilla-mobile/firefox-android/blob/fe8a71cd70ad5674abe1824fe11dc78372b736c2/android-components/components/browser/state/src/main/java/mozilla/components/browser/state/state/recover/RecoverableTab.kt#L31). The same file gives lastAccess a default of 0 (https://github.com/mozilla-mobile/firefox-android/blob/fe8a71cd70ad5674abe1824fe11dc78372b736c2/android-components/components/browser/state/src/main/java/mozilla/components/browser/state/state/recover/RecoverableTab.kt#L47), so a stored 0 can be that default and is not taken as a time. It is shown blank, not as 1970-01-01. No row on the images run holds a 0. That commit is from June 2024; other app versions were not read. The three files cited do not describe the value as the time the tab was closed or opened. On pixel7a_a14 the one row's Created At is 100.7 seconds after the only history visit places.sqlite holds for the same URL; one row cannot show what the time marks."
        ),
        "paths": ('*/org.mozilla.firefox/databases/recently_closed_tabs*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 1 row",
        },
    }
}

import datetime
import os

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    """created_at milliseconds as UTC, keeping the milliseconds; blank for 0, which is not a time."""
    try:
        ms = int(value)
    except (TypeError, ValueError):
        return ''
    if ms <= 0:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=ms)
    except OverflowError:
        return ''


@artifact_processor
def get_firefoxRecentlyClosedTabs(context):
    data_list = []
    source_paths = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'recently_closed_tabs':  # skip -journal and other files
            continue

        source_paths.append(file_found)
        user = android_user(context.get_relative_path(file_found))
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('SELECT created_at, title, url FROM recently_closed_tabs')
        for created_at, title, url in cursor.fetchall():
            data_list.append((_ms_to_utc(created_at), title, url, user))
        db.close()

    data_headers = (
        ('Created At', 'datetime'),
        'Title',
        'URL',
        'Android User',
    )
    return data_headers, data_list, '\n'.join(source_paths)
