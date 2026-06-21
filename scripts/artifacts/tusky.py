# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_tusky": {
        "name": "Tusky - Timeline",
        "description": "Parses Tusky timeline",
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2022-12-12",
        "last_update_date": "2022-12-12",
        "requirements": "BeautifulSoup",
        "category": "Tusky",
        "notes": "",
        "paths": ('*/com.keylesspalace.tusky/databases/tuskyDB*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "get_tusky_accounts": {
        "name": "Tusky - Account Details",
        "description": "Parses Tusky account details",
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2022-12-12",
        "last_update_date": "2022-12-12",
        "requirements": "BeautifulSoup",
        "category": "Tusky",
        "notes": "",
        "paths": ('*/com.keylesspalace.tusky/databases/tuskyDB*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    }
}

import datetime
import json
import os

from bs4 import BeautifulSoup

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _tusky_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == 'tuskyDB':
            return file_found
    return ''


def _strip_html(value):
    if not value:
        return ''
    return BeautifulSoup(value, 'html.parser').get_text()


def _attachment_urls(value):
    urls = []
    try:
        for item in json.loads(value or '[]'):
            url = item.get('url')
            if url:
                urls.append(url)
    except (ValueError, TypeError):
        pass
    return '\n'.join(urls)


@artifact_processor
def get_tusky(files_found, report_folder, seeker, wrap_text):
    source_path = _tusky_db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                select
                TimelineStatusEntity.createdAt,
                TimelineAccountEntity.username,
                TimelineAccountEntity.displayName,
                TimelineStatusEntity.url,
                TimelineStatusEntity.content,
                TimelineStatusEntity.attachments,
                TimelineStatusEntity.reblogsCount,
                TimelineStatusEntity.favouritesCount,
                TimelineStatusEntity.repliesCount,
                case TimelineStatusEntity.reblogged when 0 then "" when 1 then "True" end,
                case TimelineStatusEntity.bookmarked when 0 then "" when 1 then "True" end,
                case TimelineStatusEntity.favourited when 0 then "" when 1 then "True" end,
                case TimelineStatusEntity.sensitive when 0 then "" when 1 then "True" end,
                case TimelineStatusEntity.visibility when 0 then "Unknown" when 1 then "Public" when 4 then "Direct" end as "Visibility",
                json_extract(TimelineStatusEntity.application, '$.name') as "Application"
                from TimelineStatusEntity
                left join TimelineAccountEntity on TimelineAccountEntity.serverId = TimelineStatusEntity.authorServerId
                where TimelineStatusEntity.createdAt > 0
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            data_list.append((_ms_to_utc(row[0]), row[1], row[2], row[3], _strip_html(row[4]), _attachment_urls(row[5]),
                              row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]))

    data_headers = (('Timestamp', 'datetime'), 'User Name', 'Display Name', 'URL', 'Text Content', 'Attachments', 'Boost Count', 'Favorite Count', 'Replies Count', 'User Boosted?', 'User Bookmarked?', 'User Favorited?', 'Sensitive', 'Visibility', 'Application')
    return data_headers, data_list, source_path


@artifact_processor
def get_tusky_accounts(files_found, report_folder, seeker, wrap_text):
    source_path = _tusky_db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                select accountId, displayName, username, domain, profilePictureUrl,
                case notificationsEnabled when 0 then "False" when 1 then "True" end,
                case notificationsMentioned when 0 then "False" when 1 then "True" end,
                case notificationsFollowed when 0 then "False" when 1 then "True" end,
                case notificationsFollowRequested when 0 then "False" when 1 then "True" end,
                case notificationsReblogged when 0 then "False" when 1 then "True" end,
                case notificationsFavorited when 0 then "False" when 1 then "True" end,
                case notificationsPolls when 0 then "False" when 1 then "True" end,
                tabPreferences, accessToken, clientId, clientSecret
                from AccountEntity
            ''')
            data_list = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
        db.close()

    data_headers = ('Account ID', 'Display Name', 'User Name', 'Instance', 'Avatar URL', 'Notifications Enabled', 'Mentioned Notifications', 'Followed Notifications', 'Follow Requested Notifications', 'Boost Notifications', 'Favorited Notifications', 'Polls Notifications', 'Tab Preferences', 'Access Token', 'Client ID', 'Client Secret')
    return data_headers, data_list, source_path
