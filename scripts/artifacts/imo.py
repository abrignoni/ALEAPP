# pylint: disable=W0702
__artifacts_v2__ = {
    "get_imo_account": {
        "name": "IMO - Account ID",
        "description": "Parses the local IMO account (account ID and name) from the IMO accountdb.db.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "IMO",
        "notes": "",
        "paths": ('*/com.imo.android.imous/databases/accountdb.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.imo.android.imous vc 2043 | 1 row",
        },
    },
    "get_imo_messages": {
        "name": "IMO - Messages",
        "description": "Parses IMO messages (timestamp, sender and recipient IDs, message, direction, read status and attachments) from the IMO imofriends.db.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "IMO",
        "notes": ("Direction is decoded from the messages table 'message_type' column. "
                  "Direction/status value mappings were established through testing; unrecognized "
                  "values are reported as stored, so rows the mapping does not cover are not "
                  "labelled as sent or received.\n"
                  "In the conversation view only rows labelled Outgoing are attributed to the "
                  "device owner; a row whose direction value is blank or unrecognized is not "
                  "attributed to the owner.\n"
                  "From ID and To ID are filled only when the direction is recognized; the other "
                  "party is reported in Chat Partner regardless."),
        "paths": ('*/com.imo.android.imous/databases/imofriends.db*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.imo.android.imous vc 2043 | 22 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat Partner",
                "textColumn": "Last Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Chat Partner",
                "sentMessageStaticLabel": "Local User"
            }
        },
    }
}

import datetime
import json

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import unique_files


@artifact_processor
def get_imo_account(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('accountdb.db'):
            source_path = file_name
            db = open_sqlite_db_readonly(file_name)
            cursor = db.cursor()
            try:
                cursor.execute('''
                     SELECT uid, name FROM account
                ''')
                all_rows = cursor.fetchall()
            except:
                all_rows = []

            for row in all_rows:
                data_list.append((row[0], row[1]))
            db.close()

    data_headers = ('Account ID', 'Name')
    return data_headers, data_list, source_path


@artifact_processor
def get_imo_messages(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_name = str(file_found)
        if file_name.endswith('imofriends.db'):
            source_path = file_name
            db = open_sqlite_db_readonly(file_name)
            cursor = db.cursor()
            try:
                cursor.execute('''
                             SELECT messages.buid AS buid, imdata, last_message, timestamp/1000000000,
                                    case message_type when 1 then "Incoming" when 2 then "Outgoing" else message_type end message_type, message_read
                               FROM messages
                              INNER JOIN friends ON friends.buid = messages.buid
                ''')
                all_rows = cursor.fetchall()
            except:
                all_rows = []

            for row in all_rows:
                from_id = ''
                to_id = ''
                attachmentPath = ''
                if row[4] == "Incoming":
                    from_id = row[0]
                elif row[4] == "Outgoing":
                    to_id = row[0]
                if row[1] is not None:
                    imdata_dict = json.loads(row[1])

                    # set to none if the key doesn't exist in the dict
                    attachmentOriginalPath = imdata_dict.get('original_path', None)
                    attachmentLocalPath = imdata_dict.get('local_path', None)
                    if attachmentOriginalPath:
                        attachmentPath = attachmentOriginalPath
                    else:
                        attachmentPath = attachmentLocalPath

                timestamp = datetime.datetime.fromtimestamp(int(row[3]), datetime.timezone.utc)
                data_list.append((timestamp, row[4], row[0], row[2], from_id, to_id, row[5], attachmentPath))
            db.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        'Direction',
        'Chat Partner',
        'Last Message',
        'From ID',
        'To ID',
        'Message Read',
        'Attachment',
    )
    return data_headers, data_list, source_path
