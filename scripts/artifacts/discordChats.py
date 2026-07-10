# pylint: disable=W0612,W0613,W0631
__artifacts_v2__ = {
    "get_discordChats": {
        "name": "discordChats",
        "description": "Parses Discord chat messages from the kv-storage key-value store",
        "author": "",
        "creation_date": "2023-09-18",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Discord Chats",
        "notes": "",
        "paths": ('*/data/com.discord/files/kv-storage/*/a*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.discord vc 333012 | 7 rows",
            "pixel7a_a14": "Android 14 | com.discord vc 239015 | 47 rows",
            "samsungs20_a13": "Android 13 | com.discord vc 310011 | 1 row",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Channel ID",
                "textColumn": "Content",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Username"
            }
        },
    }
}

import re
import sys
import json

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_discordChats(files_found, report_folder, seeker, wrap_text):

    # build a table mapping all non-printable characters to None
    NOPRINT_TRANS_TABLE = {
        i: None for i in range(0, sys.maxunicode + 1) if not chr(i).isprintable()
    }

    def make_printable(s):
        """Replace non-printable characters in a string."""

        # the translate method on str removes characters
        # that map to None from the string
        return s.translate(NOPRINT_TRANS_TABLE)

    for file_found in files_found:
        file_name = str(file_found)
        if file_found.endswith('a'):
            break # Skip all other files

    source_path = str(file_found)
    # local account id is part of the kv-storage path
    account_match = re.search(r'@account\.(\d+)', source_path)
    account_id = account_match.group(1) if account_match else ''
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
        SELECT
        *
        from messages0
    ''')

    all_rows = cursor.fetchall()
    data_list = []
    for row in all_rows:
        data = (row[6].decode())

        jsontext = make_printable(data)

        data = json.loads(jsontext)
        datatimestamp = (data['message']['timestamp'])
        channelid = (data['channelId'])
        dataid = (data['id'])
        username = (data['message']['author']['username'])
        sender_id = str(data['message']['author'].get('id', ''))
        content = (data['message']['content'])
        attachments = (data['message']['attachments'])
        if len(attachments) > 0:
            attachementfilename = (attachments[0]['filename'])
            attachementurl = (attachments[0]['url'])
            attachmentproxyurl = (attachments[0]['proxy_url'])
        else:
            attachementfilename = attachementurl = attachmentproxyurl = ''
        mentions = (data['message']['mentions'])
        mentionroles = (data['message']['mention_roles'])
        pinned = (data['message']['pinned'])
        avatar = (data['message']['author']['avatar'])
        editedtimestamp = (data['message']['edited_timestamp'])

        if account_id and sender_id:
            direction = 'Outgoing' if sender_id == account_id else 'Incoming'
        else:
            direction = ''
        data_list.append((datatimestamp,channelid,dataid,username,content,attachementfilename,attachementurl,attachmentproxyurl,mentions,mentionroles,pinned,avatar,editedtimestamp,sender_id,account_id,direction))

    db.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        'Channel ID',
        'ID',
        'Username',
        'Content',
        'Attachment Filename',
        'Attachment URL',
        'Attachment Proxy URL',
        'Mentions',
        'Mention Roles',
        'Pinned',
        'Avatar',
        ('Edited Timestamp', 'datetime'),
        'Sender ID',
        'Account ID',
        'Direction',
    )
    return data_headers, data_list, source_path
