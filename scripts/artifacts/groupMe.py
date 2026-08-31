__artifacts_v2__ = {
    "get_groupMe": {
        "name": "GroupMe - Group Information",
        "description": "GroupMe group information",
        "author": "Josh Hickman (josh@thebinaryhick.blog)",
        "creation_date": "2021-02-01",
        "last_update_date": "2026-08-18",
        "requirements": "None",
        "category": "GroupMe",
        "notes": "Message Count (stored) and Attachment Count (stored) are the counter values held in "
                 "the groups table; they are not counts of the messages and attachments recovered by "
                 "this artifact. Group Creator and Creator Role are read from the creator's own "
                 "membership row for that group; the members table holds one row per group and user.",
        "paths": ('*/com.groupme.android/databases/groupme.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.groupme.android vc 240460204 | 1 row",
            "pixel3_a12": "Android 12 | com.groupme.android vc 213010104 | 2 rows",
            "russell_pixel6a_a13": "Android 13 | com.groupme.android vc 231500204 | 1 row",
            "russell_a14": "Android 14 | com.groupme.android vc 242190204 | 0 rows",
        },
    },
    "get_groupMe_chat": {
        "name": "GroupMe - Chat Information",
        "description": "GroupMe chat information",
        "author": "Josh Hickman (josh@thebinaryhick.blog)",
        "creation_date": "2021-02-01",
        "last_update_date": "2026-08-18",
        "requirements": "None",
        "category": "GroupMe",
        "notes": "Message Deletion Time and Message Deletion Actor (as stored) are the messages table's "
                 "deleted_at and deletion_actor columns. deleted_at is 0 where no deletion timestamp is "
                 "stored, reported here as an empty cell rather than an epoch date. The database's own "
                 "search_messages_view selects only rows where deleted_at = 0. The value domain of "
                 "deletion_actor is not documented, so it is reported as stored; 'sender' is the only "
                 "value seen in the tested images, and the app binary references the literals 'sender' "
                 "and 'admin' in the method that handles these two columns "
                 "(com.groupme.android.message.MessageUtils.getAffectedItems, base.apk of "
                 "com.groupme.android vc 240460204). On the one deleted row in the tested images the "
                 "stored message_text reads the literal 'This message was deleted'. Message Hidden "
                 "(as stored) is the stored integer rather than Yes/No, because the column takes values "
                 "beyond 0 and 1: the only non-zero value seen is 2, on a system row reading 'A message "
                 "was deleted.' The app's own migration adds deleted_at and deletion_actor to an existing "
                 "messages table, so a store written before that release lacks them; absent columns are "
                 "read as NULL, which was exercised on a constructed copy with the two columns dropped "
                 "and not on any tested image.",
        "paths": ('*/com.groupme.android/databases/groupme.db*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.groupme.android vc 240460204 | 86 rows",
            "pixel3_a12": "Android 12 | com.groupme.android vc 213010104 | 26 rows",
            "russell_pixel6a_a13": "Android 13 | com.groupme.android vc 231500204 | 1 row",
            "russell_a14": "Android 14 | com.groupme.android vc 242190204 | 0 rows",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, null_absent_columns, open_sqlite_db_readonly


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


@artifact_processor
def get_groupMe(context):
    files_found = context.get_files_found()
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
        AND members.group_id=groups.group_id
        ORDER BY groups.created_at ASC
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((_sec_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                          _sec_to_utc(row[7]), _sec_to_utc(row[8])))

    data_headers = (('Group Creation Time', 'datetime'), 'Group Name', 'Group Type', 'Group Creator', 'Creator Role',
                    'Message Count (stored)', 'Attachment Count (stored)',
                    ('Time of Last Message in Group', 'datetime'), ('Time Group Last Updated', 'datetime'))
    return data_headers, data_list, source_path


@artifact_processor
def get_groupMe_chat(context):
    files_found = context.get_files_found()
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute(null_absent_columns(source_path, '''
        SELECT
        messages.created_at,
        messages.deleted_at,
        groups.name,
        messages.name,
        messages.sender_type,
        CASE WHEN messages.is_system=0 THEN "No" WHEN messages.is_system=1 THEN "Yes" END,
        messages.hidden,
        CASE WHEN messages.read=0 THEN "No" WHEN messages.read=1 THEN "Yes" END,
        messages.deletion_actor,
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
    '''))
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((_sec_to_utc(row[0]), _sec_to_utc(row[1]), row[2], row[3], row[4], row[5], row[6],
                          row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                          row[16], row[17], row[18]))

    data_headers = (('Message Time', 'datetime'), ('Message Deletion Time', 'datetime'),
                    'Group Name', 'Message Sender', 'Message Sender Type',
                    'Is System Message', 'Message Hidden (as stored)', 'Message Is Read',
                    'Message Deletion Actor (as stored)', 'Message', 'Picture URL',
                    'Picture URI', 'Picture Width', 'Picture Height', 'Picture Is GIF',
                    'Video URL', 'Message Latitude', 'Message Longitude', 'Location Name')
    return data_headers, data_list, source_path
