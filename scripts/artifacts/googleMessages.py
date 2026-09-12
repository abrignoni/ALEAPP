__artifacts_v2__ = {
    "get_googleMessages": {
        "name": "GoogleMessages",
        "description": "Google Messages",
        "author": "Josh Hickman (josh@thebinaryhick.blog)",
        "creation_date": "2021-01-30",
        "last_update_date": "2026-08-10",
        "requirements": "None",
        "category": "Google Messages",
        "notes": ("Direction comes from the sending participant's sub_id. AOSP treats -2 as the "
                  "marker for a participant other than the device's own, so a sender whose sub_id "
                  "is anything else is the self participant and the message is outgoing. A row "
                  "whose sub_id is NULL is left blank rather than assigned a direction, because a "
                  "NULL comparison is neither true nor false and would otherwise fall through to "
                  "Incoming.\n"
                  "Reference: AOSP Messaging, 'ParticipantData (OTHER_THAN_SELF_SUB_ID = -2, "
                  "isSelf())', https://android.googlesource.com/platform/packages/apps/Messaging/"
                  "+/refs/heads/main/src/com/android/messaging/datamodel/data/ParticipantData.java"),
        "paths": ('*/com.google.android.apps.messaging/databases/bugle_db*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.apps.messaging vc 289151900 | 94 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.messaging vc 311755063 | 81 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.messaging vc 289151063 | 243 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.messaging vc 238308063 | 1123 rows",
            "samsunga53_a14": "Android 14 | com.google.android.apps.messaging vc 292971900 | 45 rows",
            "samsungs20_a13": "Android 13 | com.google.android.apps.messaging vc 293261063 | 40 rows",
            "sharon_a14": "Android 14 | com.google.android.apps.messaging vc 161637900 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.messaging vc 186597063 | 36 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.messaging vc 259818063 | 21 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "conversationLabelColumn": "Other Participant/Conversation Name",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Message Sender"
            }
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, null_absent_columns, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import unique_files


@artifact_processor
def get_googleMessages(context):
    files_found = unique_files(context)

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if not file_found.endswith('bugle_db'):
            continue  # Skip all other files

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        # Older bugle_db generations lack file_size_bytes and local_cache_path
        # on parts (community report, PR #638/#633); absent columns are read
        # as NULL so the query works across generations.
        cursor.execute(null_absent_columns(file_found, '''
        SELECT
        parts.timestamp,
        parts.content_type AS "Message Type",
        conversations.name AS "Other Participant/Conversation Name",
        participants.display_destination AS "Message Sender",
        parts.text AS "Message",
        CASE
        WHEN parts.file_size_bytes=-1 THEN "N/A"
        ELSE parts.file_size_bytes
        END AS "Attachment Byte Size",
        parts.local_cache_path AS "Attachment Location",
        parts.conversation_id AS "Conversation ID",
        CASE
        WHEN participants.sub_id IS NULL THEN ''
        WHEN participants.sub_id != -2 THEN 'Outgoing'
        ELSE 'Incoming'
        END AS "Direction"
        FROM
        parts
        JOIN messages ON messages._id=parts.message_id
        JOIN participants ON participants._id=messages.sender_id
        JOIN conversations ON conversations._id=parts.conversation_id
        ORDER BY parts.timestamp ASC
        '''))
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((timestamp, row[8], row[3], row[2], row[4], row[1], row[5], row[6], row[7]))

    data_headers = (('Message Timestamp', 'datetime'), 'Direction', ('Message Sender', 'phonenumber'), 'Other Participant/Conversation Name', 'Message', 'Message Type', 'Attachment Byte Size', 'Attachment Location', 'Conversation ID')
    return data_headers, data_list, source_path
