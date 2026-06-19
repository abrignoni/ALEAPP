# pylint: disable=W0613,W0702
__artifacts_v2__ = {
    "get_imo_account": {
        "name": "IMO - Account ID",
        "description": "",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "IMO",
        "notes": "",
        "paths": ('*/com.imo.android.imous/databases/accountdb.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    },
    "get_imo_messages": {
        "name": "IMO - Messages",
        "description": "",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "IMO",
        "notes": "",
        "paths": ('*/com.imo.android.imous/databases/imofriends.db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    }
}

import datetime
import json

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_imo_account(files_found, report_folder, seeker, wrap_text):
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
def get_imo_messages(files_found, report_folder, seeker, wrap_text):
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
                                    case message_type when 1 then "Incoming" else "Outgoing" end message_type, message_read
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
                else:
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
                data_list.append((timestamp, from_id, to_id, row[2],  row[4], row[5], attachmentPath))
            db.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        'From ID',
        'To ID',
        'Last Message',
        'Direction',
        'Message Read',
        'Attachment',
    )
    return data_headers, data_list, source_path
