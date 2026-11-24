__artifacts_v2__ = {
    "tiktok_play_records": {
        "name": "TikTok - Play Records",
        "description": "TikTok post (aweme) ids the app recorded in its aweme_record database"
                       " after its feed player prepared a post, or when the current post of a"
                       " feed changed, with the time the app recorded. One play can give a "
                       "row in each table.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Social Media",
        "notes": "Read from the AWEME_READ_RECORD and FOLLOWING_READ_RECORD tables of "
                 "databases/aweme_record (a Room database, AwemeRecordDatabase in "
                 "com.ss.android.ugc.aweme.friendstab.db), with its write-ahead log when one "
                 "is beside it. Sources are the app's decompiled code (TikTok "
                 "com.zhiliaoapp.musically versionCode 2024701040 from packages.xml, the APK "
                 "installed on dragna_pixel9a_a16, decompiled with jadx; the code is "
                 "obfuscated and jadx reported 859 errors, so a writer in an undecompiled "
                 "method can be missed). Other app versions were not examined. "
                 "AWEME_READ_RECORD rows are written by three paths found in the code: "
                 "onAwemeRead of ISocial2TabRedDotService, onFriendsV3StoryDetailRead, and "
                 "the Friends feed panel (FriendsFeedFragmentPanel). The feed player's "
                 "onPlayPrepare leads to onAwemeRead when a user is logged in; the write runs"
                 " on a background executor and during app start can be held until start-up "
                 "finishes, so the stored time is when the write ran. Each row stores the "
                 "post id (AWEME_ID), the current time in Unix milliseconds as READ_TIME and "
                 "INSERT_TIME, the page type, the current user id and the aweme type. For "
                 "onAwemeRead rows, 'Page Type (as stored)' is 10000 when the string the "
                 "player passed is homepage_hot, and otherwise the page type the caller "
                 "passed; onAwemeRead does not write page type 31. Page type 31 is written by"
                 " onFriendsV3StoryDetailRead and by the Friends feed panel, and only when no"
                 " read row for that post is already stored. What other values mean was not "
                 "established. FOLLOWING_READ_RECORD rows are written when a feed's current "
                 "post changes (AwemeChangedComponent, onGlobalAwemeChanged), when the app's "
                 "FollowRealTimeReadExp setting is on, with the current time as INSERT_TIME; "
                 "those rows have no read time, so 'Recorded Time' is INSERT_TIME for them "
                 "and the two time columns are equal. On the three images with rows in both "
                 "tables, every AWEME_READ_RECORD post also had a FOLLOWING_READ_RECORD row, "
                 "so which feeds write it was not established. 'Recorded Time' is READ_TIME "
                 "for AWEME_READ_RECORD rows; a stored 0 is shown blank. Times are shown in "
                 "UTC. A row shows the app recorded the post as read or current at that time;"
                 " it does not establish how long it was watched. Each table keeps one row "
                 "per post (INSERT OR REPLACE on the post id), so a later play replaces the "
                 "earlier row, and one play can appear in both tables. The app deletes rows "
                 "whose time is at or before a cutoff (DELETE ... WHERE READ_TIME <= ? and "
                 "WHERE INSERT_TIME <= ?, with separate cutoffs for page types 31 and 195), "
                 "so an empty table does not show that nothing was played. 'Video ID' is the "
                 "TikTok aweme id as stored. 'Scene', 'Aweme Type' and 'Reported' are "
                 "reported as stored, blank where the table has no such column. The other "
                 "tables of the database (FRIENDS_UNREAD_RECORD, FRIENDS_RED_DOT_RECORD, "
                 "REPOST_DISLIKE_RECORD) are not read; on dragna_pixel9a_a16 they hold 1, 0 "
                 "and 0 rows. On dragna_pixel9a_a16 'Reported (as stored)' held 0 and 'User "
                 "ID' held one value on every row, AWEME_READ_RECORD page types were 10000 "
                 "(244 rows) and 2000 (1 row), and the 562 rows name 317 distinct posts. On "
                 "the 8 sample_data images with no rows, AWEME_READ_RECORD exists and is "
                 "empty, and FOLLOWING_READ_RECORD exists and is empty on 2 of them. Stores "
                 "at schema versions 1, 2 and 4 (7 of the 12 images) have no "
                 "FOLLOWING_READ_RECORD table, and versions 1 and 2 also lack some "
                 "AWEME_READ_RECORD columns, shown blank; no such store held rows, so that "
                 "path is unexercised. The com.ss.android.ugc.trill path is unexercised.",
        "paths": ('*/com.zhiliaoapp.musically/databases/aweme_record*',
                  '*/com.ss.android.ugc.trill/databases/aweme_record*'),
        "output_types": "standard",
        "artifact_icon": "play-circle",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.zhiliaoapp.musically versionCode 2024701040 | 562 rows",
            "anne_a15": "Android 15 | com.zhiliaoapp.musically | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.zhiliaoapp.musically | 453 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically | 1 row",
            "hickman_a13": "Android 13 | com.zhiliaoapp.musically | 0 rows",
            "russell_a14": "Android 14 | com.zhiliaoapp.musically | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.zhiliaoapp.musically | 0 rows",
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically | 0 rows",
            "samsunga53_a14": "Android 14 | com.zhiliaoapp.musically | 0 rows",
            "sharon_a13": "Android 13 | com.zhiliaoapp.musically | 0 rows",
            "userb2_a13": "Android 13 | com.zhiliaoapp.musically | 0 rows",
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically | 0 rows",
        },
    },
}

import os
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, get_sqlite_db_records

# (table, column holding the recorded time) read in this order.
_TABLES = (('AWEME_READ_RECORD', 'READ_TIME'), ('FOLLOWING_READ_RECORD', 'INSERT_TIME'))


def _utc_ms(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    try:
        return datetime.fromtimestamp(number / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _get(row, name):
    value = row.get(name)
    return '' if value is None else value


@artifact_processor
def tiktok_play_records(context):
    data_headers = (
        ('Recorded Time', 'datetime'), ('Insert Time', 'datetime'), 'Video ID', 'Table',
        'Page Type (as stored)', 'Scene (as stored)', 'Aweme Type (as stored)',
        'Reported (as stored)', 'User ID')
    data_list, sources = [], []
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.basename(path) != 'aweme_record':
            continue
        sources.append(path)
        for table, time_column in _TABLES:
            if not does_table_exist_in_db(path, table):
                continue
            records = get_sqlite_db_records(path, f'SELECT * FROM {table}')
            names = [column[0] for column in getattr(records, 'description', None) or ()]
            for values in records:
                row = dict(zip(names, values))
                data_list.append((
                    _utc_ms(_get(row, time_column)), _utc_ms(_get(row, 'INSERT_TIME')),
                    _get(row, 'AWEME_ID'), table, _get(row, 'PAGE_TYPE'), _get(row, 'SCENE'),
                    _get(row, 'AWEME_TYPE'), _get(row, 'REPORTED'), _get(row, 'USER_ID'),
                ))
    data_list.sort(key=lambda r: r[0] or datetime.min.replace(tzinfo=timezone.utc),
                   reverse=True)
    return data_headers, data_list, '\n'.join(sources)
