# pylint: disable=W0718
__artifacts_v2__ = {
    "get_mastodon": {
        "name": "Mastodon - Hashtag Searches",
        "description": "Rows of the recent_searches table whose id begins with tag, from the Mastodon databases",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-12-07",
        "last_update_date": "2026-11-26",
        "requirements": "BeautifulSoup",
        "category": "Social Media",
        "notes": "Each file ending in .db that the search returned is read once, even when it appears under several storage views. A rollback snapshot that is identical to its live copy is not read. A database without the recent_searches table is passed over. Source File names the database a row came from. Timestamp is recent_searches.time read as Unix seconds. The app sets it when it saves a search result to its recent searches and replaces the row when the same result is saved again, so it is the latest save of that result (CacheController.java putRecentSearch at release v2.5.0, versionCode 93: https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/api/CacheController.java#L250-L257). Later app versions keep only the 20 newest rows (https://github.com/mastodon/mastodon-android/blob/24d8c5d9d012858e8928ab465b455ad52805a9ee/mastodon/src/main/java/org/joinmastodon/android/api/CacheController.java#L364). The app builds an id that begins with post for post results (https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/model/SearchResult.java#L63-L65), but at both commits read, the code that saves a recent search skips post results (https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/fragments/discover/SearchFragment.java#L106-L107). Only rows whose id begins with tag or acc are reported, one kind per artifact.",
        "paths": ('*/org.joinmastodon.android/databases/*.db*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.joinmastodon.android vc 93 | 0 rows",
        },
    },
    "get_mastodon_account_searches": {
        "name": "Mastodon - Account Searches",
        "description": "Parses Mastodon account searches",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-12-07",
        "last_update_date": "2026-11-26",
        "requirements": "BeautifulSoup",
        "category": "Social Media",
        "notes": "Each file ending in .db that the search returned is read once, even when it appears under several storage views. A rollback snapshot that is identical to its live copy is not read. A database without the recent_searches table is passed over. Source File names the database a row came from. Timestamp is recent_searches.time read as Unix seconds. The app sets it when it saves a search result to its recent searches and replaces the row when the same result is saved again, so it is the latest save of that result (CacheController.java putRecentSearch at release v2.5.0, versionCode 93: https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/api/CacheController.java#L250-L257). Later app versions keep only the 20 newest rows (https://github.com/mastodon/mastodon-android/blob/24d8c5d9d012858e8928ab465b455ad52805a9ee/mastodon/src/main/java/org/joinmastodon/android/api/CacheController.java#L364). The app builds an id that begins with post for post results (https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/model/SearchResult.java#L63-L65), but at both commits read, the code that saves a recent search skips post results (https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/fragments/discover/SearchFragment.java#L106-L107). Only rows whose id begins with tag or acc are reported, one kind per artifact.",
        "paths": ('*/org.joinmastodon.android/databases/*.db*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.joinmastodon.android vc 93 | 1 row",
        },
    },
    "get_mastodon_notifications": {
        "name": "Mastodon - Notifications",
        "description": "Rows of the notifications_all table of the Mastodon databases, with the notification type as stored and an interpretation of it. The notifications_mentions table is not read.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2022-12-07",
        "last_update_date": "2026-11-26",
        "requirements": "BeautifulSoup",
        "category": "Social Media",
        "notes": "Notification Type Interpretation is decoded from the stored integer type as 0 Follow, 2 Mention, 3 Boost and 4 Favorite. The app writes the enum position (ordinal) of the notification type to notifications_all.type (CacheController.java putNotifications at release v2.5.0, versionCode 93: https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/api/CacheController.java#L229). At that release the enum is Notification.Type (https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/model/Notification.java#L42-L52), and at a later commit it is NotificationType (https://github.com/mastodon/mastodon-android/blob/24d8c5d9d012858e8928ab465b455ad52805a9ee/mastodon/src/main/java/org/joinmastodon/android/model/NotificationType.java#L9-L17). Both have the same first five positions: FOLLOW, FOLLOW_REQUEST, MENTION, REBLOG and FAVORITE. Any other stored value, including 1 (FOLLOW_REQUEST), is shown blank in the interpretation. On pixel7a_a14 only stored values 0 and 2 occur. The enum position of a type can differ in an app version that was not checked. Type (As Stored) shows the number in notifications_all.type as read, whether or not the interpretation covers it. The report stores it as text. The columns were mapped on the layout of app versionCode 93, where each row holds one notification with its account and, when it has one, its status. Later app versions store grouped notifications and keep the accounts and statuses in the notifications_accounts_all and notifications_statuses_all tables (https://github.com/mastodon/mastodon-android/blob/24d8c5d9d012858e8928ab465b455ad52805a9ee/mastodon/src/main/java/org/joinmastodon/android/api/CacheController.java#L306-L341), which this artifact does not read. On those versions Notification Created Timestamp, Status Created Timestamp, Notification From, Reference URL, Text Content and Visibility are blank, and ID is the group key. Not tested on such a database. Text Content has its HTML tags removed. Each file ending in .db that the search returned is read once, even when it appears under several storage views. A rollback snapshot that is identical to its live copy is not read. A database without the notifications_all table is passed over. Source File names the database a row came from.",
        "paths": ('*/org.joinmastodon.android/databases/*.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.joinmastodon.android vc 93 | 6 rows",
        },
    },
    "get_mastodon_timeline": {
        "name": "Mastodon - Timeline",
        "description": "Parses Mastodon timeline",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-12-07",
        "last_update_date": "2026-11-26",
        "requirements": "BeautifulSoup",
        "category": "Social Media",
        "notes": "Each file ending in .db that the search returned is read once, even when it appears under several storage views. A rollback snapshot that is identical to its live copy is not read. A database without the home_timeline table is passed over. Source File names the database a row came from. Timestamp is the created_at of the row's status. Text Content and Boosted Content have their HTML tags removed. Attachment URL lists the media of the row's own status only. Media attached to a boosted post is not reported. No boost or attachment row was present on pixel7a_a14.",
        "paths": ('*/org.joinmastodon.android/databases/*.db*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.joinmastodon.android vc 93 | 2 rows",
        },
    },
    "get_mastodon_accounts": {
        "name": "Mastodon - Account Details",
        "description": "Parses Mastodon account details",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-12-07",
        "last_update_date": "2026-11-26",
        "requirements": "BeautifulSoup",
        "category": "Social Media",
        "notes": "Fields are read from the one-letter keys the app wrote at versionCode 93: b for the account, c for the instance domain and j for the push subscription. The letters follow the field order of AccountSession at release v2.5.0 (https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/api/session/AccountSession.java#L48-L57), and a later commit lists them as alternates of named keys (https://github.com/mastodon/mastodon-android/blob/24d8c5d9d012858e8928ab465b455ad52805a9ee/mastodon/src/main/java/org/joinmastodon/android/api/session/AccountSession.java#L63-L81). At a later commit (versionCode 190) the app keeps accounts in the accounts table of accounts.db. It moves an existing accounts.json into that table and deletes the file (https://github.com/mastodon/mastodon-android/blob/24d8c5d9d012858e8928ab465b455ad52805a9ee/mastodon/src/main/java/org/joinmastodon/android/api/session/AccountSessionManager.java#L843-L861). This artifact does not read accounts.db. An entry without the b, c and j keys gives a row with every column blank. Account (acct) is the acct field of the account. Bio has its HTML tags removed. The entry also holds the time the access token was generated (https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/model/Token.java#L23-L26) and two millisecond times: one the app sets when it adds the account and when it refreshes the account info (https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/api/session/AccountSession.java#L80 and https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/api/session/AccountSessionManager.java#L293), and one it sets when it refreshes the word filters (https://github.com/mastodon/mastodon-android/blob/1124bc48c253567a4b79a4fd0cab3a8a16f86bd8/mastodon/src/main/java/org/joinmastodon/android/api/session/AccountSessionManager.java#L311). This artifact does not report them.",
        "paths": ('*/org.joinmastodon.android/files/accounts.json',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.joinmastodon.android vc 93 | 1 row",
        },
    },
    "get_mastodon_instance": {
        "name": "Mastodon - Instance Details",
        "description": "Parses Mastodon instance details",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-12-07",
        "last_update_date": "2022-12-07",
        "requirements": "BeautifulSoup",
        "category": "Social Media",
        "notes": "",
        "paths": ('*/org.joinmastodon.android/files/instance*.json',),
        "output_types": "standard",
        "artifact_icon": "server",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.joinmastodon.android vc 93 | 1 row",
        },
    }
}

import datetime
import json
import os

from bs4 import BeautifulSoup

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import unique_files


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _iso_to_utc(value):
    if not value:
        return ''
    try:
        dt = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt.astimezone(datetime.timezone.utc)
    except (ValueError, TypeError):
        return value


def _strip_html(value):
    if not value:
        return value
    return BeautifulSoup(value, 'html.parser').get_text()


def _mastodon_dbs(context):
    """Every database file the search returned, one storage view of each."""
    return [f for f in unique_files(context) if f.lower().endswith('.db')]


def _query(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except Exception as e:
        logfunc(f'Mastodon: {os.path.basename(source_path)}: {e}')
        rows = []
    db.close()
    return rows


def _query_all(context, table, sql):
    """Run sql on every database that holds table; return (rows, relative path) pairs and the files read."""
    results = []
    sources = []
    for source_path in _mastodon_dbs(context):
        if not _query(source_path, "select 1 from sqlite_master where type='table' and name='" + table + "'"):
            continue
        sources.append(source_path)
        relative = context.get_relative_path(source_path)
        for row in _query(source_path, sql):
            results.append((row, relative))
    return results, '\n'.join(sources)


@artifact_processor
def get_mastodon(context):
    rows, source_path = _query_all(context, 'recent_searches', '''
        select time,
        json_extract(recent_searches.json, '$.hashtag.name'),
        json_extract(recent_searches.json, '$.hashtag.url')
        from recent_searches where id like 'tag%'
    ''')
    data_list = [(_sec_to_utc(r[0]), r[1], r[2], src) for r, src in rows]
    data_headers = (('Timestamp', 'datetime'), 'Hashtag Name', 'Hashtag URL', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_mastodon_account_searches(context):
    rows, source_path = _query_all(context, 'recent_searches', '''
        select time,
        json_extract(recent_searches.json, '$.account.username'),
        json_extract(recent_searches.json, '$.account.display_name'),
        json_extract(recent_searches.json, '$.account.url'),
        json_extract(recent_searches.json, '$.account.id')
        from recent_searches where id like 'acc%'
    ''')
    data_list = [(_sec_to_utc(r[0]), r[1], r[2], r[3], r[4], src) for r, src in rows]
    data_headers = (('Timestamp', 'datetime'), 'Username', 'Display Name', 'URL', 'ID', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_mastodon_notifications(context):
    rows, source_path = _query_all(context, 'notifications_all', '''
        select
        json_extract(notifications_all.json, '$.created_at'),
        json_extract(notifications_all.json, '$.account.acct'),
        case type when 0 then "Follow" when 2 then "Mention" when 3 then "Boost" when 4 then "Favorite" end,
        json_extract(notifications_all.json, '$.status.url'),
        json_extract(notifications_all.json, '$.status.content'),
        json_extract(notifications_all.json, '$.status.visibility'),
        json_extract(notifications_all.json, '$.status.created_at'),
        id,
        notifications_all.type
        from notifications_all
    ''')
    data_list = [(_iso_to_utc(r[0]), _iso_to_utc(r[6]), r[1], r[2], r[8], r[3], _strip_html(r[4]), r[5], r[7], src) for r, src in rows]
    data_headers = (('Notification Created Timestamp', 'datetime'), ('Status Created Timestamp', 'datetime'), 'Notification From', 'Notification Type Interpretation', 'Type (As Stored)', 'Reference URL', 'Text Content', 'Visibility', 'ID', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_mastodon_timeline(context):
    rows, source_path = _query_all(context, 'home_timeline', '''
        select
        json_extract(home_timeline.json, '$.created_at'),
        json_extract(home_timeline.json, '$.account.acct'),
        json_extract(home_timeline.json, '$.application.name'),
        json_extract(home_timeline.json, '$.content'),
        json_extract(home_timeline.json, '$.url'),
        json_extract(home_timeline.json, '$.reblog.account.acct'),
        json_extract(home_timeline.json, '$.reblog.content'),
        json_extract(home_timeline.json, '$.reblog.url'),
        json_extract(home_timeline.json, '$.replies_count'),
        json_extract(home_timeline.json, '$.reblogs_count'),
        json_extract(home_timeline.json, '$.favourites_count'),
        json_extract(home_timeline.json, '$.visibility'),
        id, json
        from home_timeline
    ''')
    data_list = []
    for r, src in rows:
        attachments = ''
        try:
            attachments = '\n'.join(x.get('url', '') for x in json.loads(r[13]).get('media_attachments', []))
        except (ValueError, TypeError):
            pass
        data_list.append((_iso_to_utc(r[0]), r[1], r[2], _strip_html(r[3]), attachments, r[4], r[5],
                          _strip_html(r[6]), r[7], r[8], r[9], r[10], r[11], r[12], src))
    data_headers = (('Timestamp', 'datetime'), 'Account Name', 'App Name', 'Text Content', 'Attachment URL', 'URL', 'Boosted Account Name', 'Boosted Content', 'Boosted URL', 'Replies Count', 'Boosted Count', 'Favorites Count', 'Visibility', 'ID', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_mastodon_accounts(context):
    files_found = context.get_files_found()
    source_path = ''
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.lower().endswith('accounts.json'):
            continue
        source_path = file_found
        with open(file_found, encoding='utf-8') as f:
            data = json.loads(f.read())
        for x in data.get('accounts', []):
            b = x.get('b', {})
            alerts = x.get('j', {}).get('alerts', {})
            data_list.append((
                _iso_to_utc(b.get('created_at', '')), b.get('acct', ''), b.get('username', ''), b.get('display_name', ''),
                b.get('url', ''), b.get('id', ''), b.get('followers_count', ''), b.get('following_count', ''),
                _strip_html(b.get('note', '')), b.get('avatar', ''), x.get('c', ''),
                str(alerts.get('favourite', '')).title(), str(alerts.get('follow', '')).title(),
                str(alerts.get('mention', '')).title(), str(alerts.get('poll', '')).title(), str(alerts.get('reblog', '')).title(),
                str(b.get('bot', '')).title(), str(b.get('discoverable', '')).title(),
                str(b.get('locked', '')).title(), str(b.get('suspended', '')).title()))

    data_headers = (('Created Timestamp', 'datetime'), 'Account (acct)', 'User Name', 'Display Name', 'URL', 'ID', 'Followers Count', 'Following Count', 'Bio', 'Avatar URL', 'Instance Domain', 'Favorite Alerts', 'Follow Alerts', 'Mention Alerts', 'Poll Alerts', 'Boost Alerts', 'Is Bot', 'Is Discoverable', 'Is Locked', 'Is Suspended')
    return data_headers, data_list, source_path


@artifact_processor
def get_mastodon_instance(context):
    files_found = context.get_files_found()
    source_path = ''
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if not (file_found.lower().endswith('.json') and os.path.basename(file_found).lower().startswith('instance')):
            continue
        source_path = file_found
        with open(file_found, encoding='utf-8') as f:
            data = json.loads(f.read())
        instance = data.get('instance', {})
        stats = instance.get('stats', {})
        data_list.append((
            _ms_to_utc(data.get('last_updated', '')), instance.get('uri', ''), instance.get('title', ''),
            instance.get('description', ''), instance.get('version', ''), stats.get('user_count', ''),
            stats.get('status_count', ''), str(instance.get('invites_enabled', '')).title(),
            str(instance.get('registrations', '')).title(), instance.get('email', ''),
            instance.get('contact_account', {}).get('url', ''), instance.get('thumbnail', '')))

    data_headers = (('Last Updated Timestamp', 'datetime'), 'URI', 'Title', 'Description', 'Version', 'User Count', 'Status Count', 'Invites Enable', 'Registrations Enabled', 'Admin Contact Email', 'Owner', 'Thumbnail')
    return data_headers, data_list, source_path
