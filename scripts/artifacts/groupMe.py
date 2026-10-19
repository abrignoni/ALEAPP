__artifacts_v2__ = {
    "get_groupMe": {
        "name": "GroupMe - Group Information",
        "description": "GroupMe group information",
        "author": "Josh Hickman (josh@thebinaryhick.blog)",
        "creation_date": "2021-02-01",
        "last_update_date": "2026-10-19",
        "requirements": "None",
        "category": "GroupMe",
        "notes": "Message Count (stored) and Attachment Count (stored) are the counter values held in "
                 "the groups table; they are not counts of the messages and attachments recovered by "
                 "this artifact. Group Creator and Creator Role are read from the creator's own "
                 "membership row for that group (the members row matching both the group's "
                 "creator_user_id and its group_id; the members table has a unique index on user_id "
                 "and group_id, so a group is reported once). A group whose creator has no row in "
                 "the members table is reported with both cells empty; no tested image held such a "
                 "group, and this was exercised on a constructed copy of the pixel7a_a14 database "
                 "with the creator's members row removed. " "Every groupme.db found is read once per storage location: the views of one app "
                 "directory (data/data, data/user/0, data_mirror) are read once, a second Android "
                 "user's copy is read as well, and Source File names the database each row came "
                 "from. The -journal, -wal and -shm files are never opened as the database. On "
                 "pixel3_a12 the database sits under three views and is read once; no tested image "
                 "holds a second user's copy.",
        "paths": ('*/com.groupme.android/databases/groupme.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.groupme.android vc 240460204 | 1 row",
            "pixel3_a12": "Android 12 | com.groupme.android vc 213010104 | 2 rows",
            "russell_pixel6a_a13": "Android 13 | com.groupme.android vc 231500204 | 1 row",
            "russell_a14": "Android 14 | com.groupme.android vc 242190204 | 0 rows",
            "hickman_a13": "Android 13 | 2 rows",
        },
    },
    "get_groupMe_chat": {
        "name": "GroupMe - Chat Information",
        "description": "GroupMe chat information",
        "author": "Josh Hickman (josh@thebinaryhick.blog), @AlexisBrignoni, Codex",
        "creation_date": "2021-02-01",
        "last_update_date": "2026-10-19",
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
                 "com.groupme.android vc 240460204). On the two deleted rows in the tested images (one "
                 "on pixel7a_a14, one on hickman_a13) the stored message_text reads the literal 'This "
                 "message was deleted'. read (as stored) "
                 "is the messages.read value returned by SQLite without a value mapping; what sets it "
                 "and the meanings of its values are not established. Message Hidden "
                 "(as stored) is the stored integer rather than Yes/No, because the column takes values "
                 "beyond 0 and 1: the only non-zero value seen is 2, on a system row reading 'A message "
                 "was deleted.' A store whose messages table lacks deleted_at and deletion_actor "
                 "has them "
                 "read as NULL, which was exercised on a constructed copy with the two columns dropped "
                 "and not on any tested image. " "Every groupme.db found is read once per storage location: the views of one app "
                 "directory (data/data, data/user/0, data_mirror) are read once, a second Android "
                 "user's copy is read as well, and Source File names the database each row came "
                 "from. The -journal, -wal and -shm files are never opened as the database. On "
                 "pixel3_a12 the database sits under three views and is read once; no tested image "
                 "holds a second user's copy.",
        "paths": ('*/com.groupme.android/databases/groupme.db*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.groupme.android vc 240460204 | 86 rows",
            "pixel3_a12": "Android 12 | com.groupme.android vc 213010104 | 26 rows",
            "russell_pixel6a_a13": "Android 13 | com.groupme.android vc 231500204 | 1 row",
            "russell_a14": "Android 14 | com.groupme.android vc 242190204 | 0 rows",
            "hickman_a13": "Android 13 | 59 rows",
        },
    }
}

import datetime
from pathlib import Path

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, null_absent_columns


def _store_paths(context):
    """Every groupme.db the seeker found, one per storage location.

    The paths glob also matches groupme.db-journal, -wal and -shm, so taking the first
    match could open a sidecar as the database. unique_files collapses the views of one
    app directory (data/data, data/user/0, data_mirror) and keeps a second Android
    user's copy, which is read too.
    """
    return [path for path in unique_files(context) if Path(path).name == 'groupme.db']


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


@artifact_processor
def get_groupMe(context):
    store_paths = _store_paths(context)
    query = '''
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
        LEFT JOIN members ON members.user_id=groups.creator_user_id
        AND members.group_id=groups.group_id
        ORDER BY groups.created_at ASC
    '''

    data_list = []
    for source_path in store_paths:
        source_file = context.get_relative_path(source_path)
        for row in get_sqlite_db_records(source_path, query):
            data_list.append((_sec_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                              _sec_to_utc(row[7]), _sec_to_utc(row[8]), source_file))

    data_headers = (('Group Creation Time', 'datetime'), 'Group Name', 'Group Type', 'Group Creator', 'Creator Role',
                    'Message Count (stored)', 'Attachment Count (stored)',
                    ('Time of Last Message in Group', 'datetime'), ('Time Group Last Updated', 'datetime'),
                    'Source File')
    return data_headers, data_list, '\n'.join(store_paths)


@artifact_processor
def get_groupMe_chat(context):
    store_paths = _store_paths(context)
    query = '''
        SELECT
        messages.created_at,
        messages.deleted_at,
        groups.name,
        messages.name,
        messages.sender_type,
        CASE WHEN messages.is_system=0 THEN "No" WHEN messages.is_system=1 THEN "Yes" END,
        messages.hidden,
        messages.read,
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
    '''

    data_list = []
    for source_path in store_paths:
        source_file = context.get_relative_path(source_path)
        for row in get_sqlite_db_records(source_path, null_absent_columns(source_path, query)):
            data_list.append((_sec_to_utc(row[0]), _sec_to_utc(row[1]), row[2], row[3], row[4], row[5],
                              row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14],
                              row[15], row[16], row[17], row[18], source_file))

    data_headers = (('Message Time', 'datetime'), ('Message Deletion Time', 'datetime'),
                    'Group Name', 'Message Sender', 'Message Sender Type',
                    'Is System Message', 'Message Hidden (as stored)', 'read (as stored)',
                    'Message Deletion Actor (as stored)', 'Message', 'Picture URL',
                    'Picture URI', 'Picture Width', 'Picture Height', 'Picture Is GIF',
                    'Video URL', 'Message Latitude', 'Message Longitude', 'Location Name', 'Source File')
    return data_headers, data_list, '\n'.join(store_paths)
