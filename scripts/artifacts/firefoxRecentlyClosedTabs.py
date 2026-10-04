__artifacts_v2__ = {
    "get_firefoxRecentlyClosedTabs": {
        "name": "Firefox - Recently Closed Tabs",
        "description": "Parses Firefox recently closed tabs (the created_at time as stored, title and URL) from the recently_closed_tabs database.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-01-12",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Firefox",
        "notes": (
            "Created At is the created_at column of the recently_closed_tabs table, stored as "
            "milliseconds since 1970 UTC and shown here as UTC. The column name does not say what "
            "the time marks. In Mozilla's android-components source the row is built with "
            "createdAt = lastAccess "
            "(https://github.com/mozilla-mobile/firefox-android/blob/fe8a71cd70ad5674abe1824fe11dc78372b736c2/"
            "android-components/components/feature/recentlyclosed/src/main/java/mozilla/components/"
            "feature/recentlyclosed/db/RecentlyClosedTabEntity.kt#L45-L52), and lastAccess is "
            "documented there as the last time the tab was selected "
            "(https://github.com/mozilla-mobile/firefox-android/blob/fe8a71cd70ad5674abe1824fe11dc78372b736c2/"
            "android-components/components/browser/state/src/main/java/mozilla/components/browser/"
            "state/state/recover/TabState.kt#L31). That commit is from June 2024; other app "
            "versions were not read. That source does not describe the value as the time the tab was closed "
            "or opened. On pixel7a_a14 the one row's Created At is 100.7 seconds after the only "
            "history visit places.sqlite holds for the same URL; one row cannot show what the "
            "time marks."
        ),
        "paths": ('*/org.mozilla.firefox/databases/recently_closed_tabs*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 1 row",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_firefoxRecentlyClosedTabs(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'recently_closed_tabs':  # skip -journal and other files
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(created_at/1000,'unixepoch') AS CreatedDate,
        title as Title,
        url as URL
        FROM recently_closed_tabs
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2]))

        db.close()

    data_headers = (
        ('Created At', 'datetime'),
        'Title',
        'URL',
    )
    return data_headers, data_list, source_path
