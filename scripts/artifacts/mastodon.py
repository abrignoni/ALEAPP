# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_mastodon": {
        "name": "Mastodon - Hashtag Searches",
        "description": "Parses Mastodon hashtag searches",
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2022-12-07",
        "last_update_date": "2022-12-07",
        "requirements": "BeautifulSoup",
        "category": "Mastodon",
        "notes": "",
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
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2022-12-07",
        "last_update_date": "2022-12-07",
        "requirements": "BeautifulSoup",
        "category": "Mastodon",
        "notes": "",
        "paths": ('*/org.joinmastodon.android/databases/*.db*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.joinmastodon.android vc 93 | 1 row",
        },
    },
    "get_mastodon_notifications": {
        "name": "Mastodon - Notifications",
        "description": "Parses Mastodon notifications",
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2022-12-07",
        "last_update_date": "2022-12-07",
        "requirements": "BeautifulSoup",
        "category": "Mastodon",
        "notes": "",
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
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2022-12-07",
        "last_update_date": "2022-12-07",
        "requirements": "BeautifulSoup",
        "category": "Mastodon",
        "notes": "",
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
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2022-12-07",
        "last_update_date": "2022-12-07",
        "requirements": "BeautifulSoup",
        "category": "Mastodon",
        "notes": "",
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
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2022-12-07",
        "last_update_date": "2022-12-07",
        "requirements": "BeautifulSoup",
        "category": "Mastodon",
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


def _mastodon_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.lower().endswith('.db'):
            return file_found
    return ''


def _query(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except Exception as e:
        logfunc(str(e))
        rows = []
    db.close()
    return rows


@artifact_processor
def get_mastodon(files_found, report_folder, seeker, wrap_text):
    source_path = _mastodon_db(files_found)
    rows = _query(source_path, '''
        select time,
        json_extract(recent_searches.json, '$.hashtag.name'),
        json_extract(recent_searches.json, '$.hashtag.url')
        from recent_searches where id like 'tag%'
    ''')
    data_list = [(_sec_to_utc(r[0]), r[1], r[2]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Hashtag Name', 'Hashtag URL')
    return data_headers, data_list, source_path


@artifact_processor
def get_mastodon_account_searches(files_found, report_folder, seeker, wrap_text):
    source_path = _mastodon_db(files_found)
    rows = _query(source_path, '''
        select time,
        json_extract(recent_searches.json, '$.account.username'),
        json_extract(recent_searches.json, '$.account.display_name'),
        json_extract(recent_searches.json, '$.account.url'),
        json_extract(recent_searches.json, '$.account.id')
        from recent_searches where id like 'acc%'
    ''')
    data_list = [(_sec_to_utc(r[0]), r[1], r[2], r[3], r[4]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Username', 'Display Name', 'URL', 'ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_mastodon_notifications(files_found, report_folder, seeker, wrap_text):
    source_path = _mastodon_db(files_found)
    rows = _query(source_path, '''
        select
        json_extract(notifications_all.json, '$.created_at'),
        json_extract(notifications_all.json, '$.account.acct'),
        case type when 0 then "Follow" when 2 then "Mention" when 3 then "Boost" when 4 then "Favorite" end,
        json_extract(notifications_all.json, '$.status.url'),
        json_extract(notifications_all.json, '$.status.content'),
        json_extract(notifications_all.json, '$.status.visibility'),
        json_extract(notifications_all.json, '$.status.created_at'),
        id
        from notifications_all
    ''')
    data_list = [(_iso_to_utc(r[0]), r[1], r[2], r[3], _strip_html(r[4]), r[5], _iso_to_utc(r[6]), r[7]) for r in rows]
    data_headers = (('Notification Created Timestamp', 'datetime'), 'Notification From', 'Notification Type', 'Reference URL', 'Text Content', 'Visibility', ('Status Created Timestamp', 'datetime'), 'ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_mastodon_timeline(files_found, report_folder, seeker, wrap_text):
    source_path = _mastodon_db(files_found)
    rows = _query(source_path, '''
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
    for r in rows:
        attachments = ''
        try:
            attachments = '\n'.join(x.get('url', '') for x in json.loads(r[13]).get('media_attachments', []))
        except (ValueError, TypeError):
            pass
        data_list.append((_iso_to_utc(r[0]), r[1], r[2], _strip_html(r[3]), attachments, r[4], r[5],
                          _strip_html(r[6]), r[7], r[8], r[9], r[10], r[11], r[12]))
    data_headers = (('Timestamp', 'datetime'), 'Account Name', 'App Name', 'Text Content', 'Attachment URL', 'URL', 'Boosted Account Name', 'Boosted Content', 'Boosted URL', 'Replies Count', 'Boosted Count', 'Favorites Count', 'Visibility', 'ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_mastodon_accounts(files_found, report_folder, seeker, wrap_text):
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

    data_headers = (('Created Timestamp', 'datetime'), 'Name', 'User Name', 'Display Name', 'URL', 'ID', 'Followers Count', 'Following Count', 'Bio', 'Avatar URL', 'Instance Name', 'Favorite Alerts', 'Follow Alerts', 'Mention Alerts', 'Poll Alerts', 'Boost Alerts', 'Is Bot', 'Is Discoverable', 'Is Locked', 'Is Suspended')
    return data_headers, data_list, source_path


@artifact_processor
def get_mastodon_instance(files_found, report_folder, seeker, wrap_text):
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
