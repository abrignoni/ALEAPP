# pylint: disable=W0613
__artifacts_v2__ = {
    "get_groupMe": {
        "name": "GroupMe - Group Information",
        "description": "GroupMe group information",
        "author": "Josh Hickman (josh@thebinaryhick.blog)",
        "creation_date": "2021-02-01",
        "last_update_date": "2021-02-01",
        "requirements": "None",
        "category": "GroupMe",
        "notes": "",
        "paths": ('*/com.groupme.android/databases/groupme.db',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.groupme.android vc 240460204 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.groupme.android vc 231500204 | 1 row",
        },
    },
    "get_groupMe_chat": {
        "name": "GroupMe - Chat Information",
        "description": "GroupMe chat information",
        "author": "Josh Hickman (josh@thebinaryhick.blog)",
        "creation_date": "2021-02-01",
        "last_update_date": "2021-02-01",
        "requirements": "None",
        "category": "GroupMe",
        "notes": "",
        "paths": ('*/com.groupme.android/databases/groupme.db',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.groupme.android vc 240460204 | 86 rows",
            "russell_pixel6a_a13": "Android 13 | com.groupme.android vc 231500204 | 1 row",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


@artifact_processor
def get_groupMe(files_found, report_folder, seeker, wrap_text):
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT
        groups.created_at,
        groups.name,
        groups.group_type,
        members.user_real_name,
        members.role,
        groups.message_count,
        groups.attachment_count,
        groups.last_message_created_at,
        groups.updated_at
        FROM groups
        JOIN members ON members.user_id=groups.creator_user_id
        ORDER BY groups.created_at ASC
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((_sec_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                          _sec_to_utc(row[7]), _sec_to_utc(row[8])))

    data_headers = (('Group Creation Time', 'datetime'), 'Group Name', 'Group Type', 'Group Creator', 'Creator Role',
                    'Total Message Count in Group', 'Total Attachment Count in Group',
                    ('Time of Last Message in Group', 'datetime'), ('Time Group Last Updated', 'datetime'))
    return data_headers, data_list, source_path


@artifact_processor
def get_groupMe_chat(files_found, report_folder, seeker, wrap_text):
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT
        messages.created_at,
        groups.name,
        messages.name,
        messages.sender_type,
        CASE WHEN messages.is_system=0 THEN "No" WHEN messages.is_system=1 THEN "Yes" END,
        CASE WHEN messages.hidden=0 THEN "No" WHEN messages.hidden=1 THEN "Yes" END,
        CASE WHEN messages.read=0 THEN "No" WHEN messages.read=1 THEN "Yes" END,
        messages.message_text,
        messages.photo_url,
        messages.photo_uri,
        messages.photo_width,
        messages.photo_height,
        CASE WHEN messages.photo_is_gif=0 THEN "No" WHEN messages.photo_is_gif=1 THEN "Yes" END,
        messages.video_url,
        messages.location_lat,
        messages.location_lng,
        messages.location_name
        FROM messages
        LEFT JOIN groups ON groups.group_id=messages.conversation_id
        ORDER BY messages.created_at ASC
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((_sec_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                          row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16]))

    data_headers = (('Message Time', 'datetime'), 'Group Name', 'Message Sender', 'Message Sender Type',
                    'Is System Message', 'Message Is Hidden', 'Message Is Read', 'Message', 'Picture URL',
                    'Picture Local Storage Location', 'Picture Width', 'Picture Height', 'Picture Is GIF',
                    'Video URL', 'Message Latitude', 'Message Longitude', 'Location Name')
    return data_headers, data_list, source_path
