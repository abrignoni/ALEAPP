# pylint: disable=W0613
__artifacts_v2__ = {
    "get_tikTok": {
        "name": "TikTok - Messages",
        "description": "Parses TikTok direct messages (timestamp, user, nickname, message, links, read state and conversation) from the TikTok IM databases.",
        "author": "",
        "creation_date": "2021-03-02",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "TikTok",
        "notes": "",
        "paths": ('*_im.db*', '*db_im_xx*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.zhiliaoapp.musically vc 2024108030 | 11 rows",
            "galaxys10_a10": "Android 10 | com.zhiliaoapp.musically vc 2021809050 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.zhiliaoapp.musically vc 2024109030 | 0 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically vc 2023507030 | 10 rows",
            "samsunga53_a14": "Android 14 | com.bd.nproject vc 100203 | 0 rows",
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically vc 2024301040 | 0 rows",
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically vc 2023600040 | 2 rows",
            "russell_pixel6a_a13": "Android 13 | com.zhiliaoapp.musically vc 2023000030 | 0 rows",
            "userb2_a13": "Android 13 | com.zhiliaoapp.musically vc 2023705030 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Nickname"
            }
        },
    },
    "get_tikTok_contacts": {
        "name": "TikTok - Contacts",
        "description": "Parses TikTok contacts (UID, nickname, unique ID, avatar and follow status) from the TikTok IM databases.",
        "author": "",
        "creation_date": "2021-03-02",
        "last_update_date": "2021-03-02",
        "requirements": "none",
        "category": "TikTok",
        "notes": "",
        "paths": ('*_im.db*', '*db_im_xx*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.zhiliaoapp.musically vc 2024108030 | 24 rows",
            "galaxys10_a10": "Android 10 | com.zhiliaoapp.musically vc 2021809050 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.zhiliaoapp.musically vc 2024109030 | 94 rows",
            "pixel7a_a14": "Android 14 | com.zhiliaoapp.musically vc 2023507030 | 2 rows",
            "samsunga53_a14": "Android 14 | com.bd.nproject vc 100203 | 0 rows",
            "samsungs20_a13": "Android 13 | com.zhiliaoapp.musically vc 2024301040 | 2 rows",
            "sharon_a14": "Android 14 | com.zhiliaoapp.musically vc 2023600040 | 8 rows",
            "russell_pixel6a_a13": "Android 13 | com.zhiliaoapp.musically vc 2023000030 | 5 rows",
            "userb2_a13": "Android 13 | com.zhiliaoapp.musically vc 2023705030 | 1 row",
        },
    }
}

import datetime
import os
import re

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _tiktok_dbs(files_found):
    maindb = attachdb = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('_im.db'):
            maindb = file_found
        elif file_found.endswith('db_im_xx'):
            attachdb = file_found
    return maindb, attachdb


@artifact_processor
def get_tikTok(files_found, report_folder, seeker, wrap_text):
    data_list = []
    maindb, attachdb = _tiktok_dbs(files_found)
    source_path = maindb
    if maindb and attachdb:
        db = open_sqlite_db_readonly(maindb)
        cursor = db.cursor()
        cursor.execute(f"ATTACH DATABASE '{attachdb}' as db_im_xx;")
        cursor.execute('''
            select
            created_time,
            UID,
            UNIQUE_ID,
            NICK_NAME,
            json_extract(content, '$.text') as message,
            json_extract(content,'$.display_name') as links_gifs_display_name,
            json_extract(content, '$.url.url_list[0]') as links_gifs_urls,
            read_status,
            case when read_status = 0 then 'Not read'
                when read_status = 1 then 'Read'
                else read_status
            end local_info,
            conversation_id
            from db_im_xx.SIMPLE_USER, msg
            where UID = sender and json_valid(content) = 1 order by created_time
        ''')
        all_rows = cursor.fetchall()
        db.close()

        # local account uid is the filename prefix: <uid>_im.db
        uid_match = re.search(r'(\d+)_im\.db$', os.path.basename(maindb))
        account_uid = uid_match.group(1) if uid_match else ''
        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            if account_uid and row[1] is not None:
                direction = 'Outgoing' if str(row[1]) == account_uid else 'Incoming'
            else:
                direction = ''
            data_list.append((timestamp, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                              row[9], direction))

    data_headers = (('Timestamp', 'datetime'), 'UID', 'Unique ID', 'Nickname', 'Message', 'Link GIF Name',
                    'Link GIF URL', 'Read?', 'Local Info', 'Conversation ID', 'Direction')
    return data_headers, data_list, source_path


@artifact_processor
def get_tikTok_contacts(files_found, report_folder, seeker, wrap_text):
    data_list = []
    maindb, attachdb = _tiktok_dbs(files_found)
    source_path = maindb
    if maindb and attachdb:
        db = open_sqlite_db_readonly(maindb)
        cursor = db.cursor()
        cursor.execute(f"ATTACH DATABASE '{attachdb}' as db_im_xx;")
        cursor.execute('''
            select UID, NICK_NAME, UNIQUE_ID, INITIAL_LETTER,
            json_extract(AVATAR_THUMB, '$.url_list[0]') as avatarURL,
            FOLLOW_STATUS
            from db_im_xx.SIMPLE_USER
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

    data_headers = ('UID', 'Nickname', 'Unique ID', 'Initial Letter', 'Avatar URL', 'Follow Status')
    return data_headers, data_list, source_path
