# Android Thunderbird App (net.thunderbird.android)
# Author:  Marco Neumann (kalinko@be-binary.de)
#
# Tested with the following versions:
# 2025-10-27: Android 16, App: 13.0

# Requirements: re, json

__artifacts_v2__ = {

    
    "thunderbird_accounts": {
        "name": "Thunderbird - Accounts",
        "description": "Thunderbird Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2025-11-18",
        "last_update_date": "2025-11-18",
        "requirements": "re, json",
        "category": "Thunderbird App",
        "notes": "",
        "paths": ('*/data/net.thunderbird.android/databases/preferences_storage'),
        "output_types": ["standard"],
        "html_columns": ["Signature"],
        "artifact_icon": "inbox"
    },
     "thunderbird_messages": {
        "name": "Thunderbird - Messages",
        "description": "Thunderbird Messages",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2025-11-20",
        "last_update_date": "2025-11-20",
        "requirements": "re, json",
        "category": "Thunderbird App",
        "notes": "",
        "paths": ('*data/net.thunderbird.android/databases/*', '*data/net.thunderbird.android/databases/*_att/*'),
        "output_types": ["standard"],
        "html_columns": ["Content"],
        "artifact_icon": "mail"
    }

}

import re
import json

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records

def _map_uuid_to_account(file):
    # Helper method to get the mapping of the uuid to the set up accounts
    # Because we need this mapping in all artifact processors
    query = ('''
    SELECT *
    FROM preferences_storage
    WHERE primkey LIKE '%email.0%'
    ''')

    db_records = get_sqlite_db_records(str(file), query)

    # Get the UUIDs of the existing accounts
    uuid_regex = re.compile(r'^[0-9a-fA-F-]{36}')
    uuids = {uuid_regex.match(s[0]).group() for s in db_records if uuid_regex.match(s[0])}

    uuid_mapping = {}

    for uuid in uuids:
        for row in db_records:
            if uuid in row[0]:
                uuid_mapping[uuid] = row[1]
       
    return uuid_mapping

@artifact_processor
def thunderbird_accounts(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
     
    query = ('''
        SELECT *
        FROM preferences_storage
        WHERE primkey LIKE '%email.0%'
        OR primkey LIKE '%name.0%'
        OR primkey LIKE '%lastSyncTime%'
        OR primkey LIKE '%description%'
        OR primkey LIKE '%incomingServerSettings%'
        OR primkey LIKE '%outgoingServerSettings%'
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    uuid_mapping = _map_uuid_to_account(str(files_found[0]))
    uuids = list(uuid_mapping.keys())

    data_list = []

    last_sync_time = 0
    account_name = ''
    address = ''
    name = ''
    username = ''
    password = ''
    incoming_server = ''
    outgoing_server = ''

    for uuid in uuids:

        for row in db_records:
            if uuid + '.lastSyncTime' == row[0]:
                last_sync_time = convert_unix_ts_to_utc(int(row[1])/1000)
            if uuid + '.description' == row[0]:
                account_name = row[1]
            if uuid + '.email.0' == row[0]:
                address = row[1]
            if uuid + '.name.0' == row[0]:
                name = row[1]
            if uuid + '.incomingServerSettings' == row[0]:
                username = json.loads(row[1])["username"]
                password = json.loads(row[1])["password"]
                incoming_server = json.loads(row[1])["host"]
            if uuid + '.outgoingServerSettings' == row[0]:
                outgoing_server = json.loads(row[1])["host"]


        data_list.append(( last_sync_time, account_name, address, name, username, password, incoming_server, outgoing_server))

    data_headers = ( 'Last Sync Time', 'Account Name', 'Mail Address', 'Shown Name', 'Username', 'Password', 'Incoming Server', 'Outgoing Server')

    return data_headers, data_list, files_found[0]


@artifact_processor
def thunderbird_messages(files_found, _report_folder, _seeker, _wrap_text):

    preferences_file = [x for x in files_found if "preferences_storage" in x and not x.endswith('journal')]
    uuid_mapping = _map_uuid_to_account(str(preferences_file[0]))
    files_found = [x for x in files_found if x.endswith('db')]
    uuid_regex = re.compile(r'[0-9a-fA-F-]{36}')

    query = ('''
        SELECT
        me.date [Timestamp Sent],
        me.internal_date [Timestamp Stored],
        me.sender_list [Sender],
        me.to_list [Receiver],
        me.cc_list [CC],
        me.bcc_list [BCC],
        me.subject [Subject],
        me.preview [Preview],
        me.attachment_count [# of Attachments],
        me.read [Read?],
        me.flagged [flagged?],
        me.answered [Answered?],
        me.forwarded [Forwarded?],
        fo.name [Folder],
        mfc.c0fulltext [Content]
        FROM messages me
        LEFT JOIN folders fo
        ON fo.id = me.folder_id
        LEFT JOIN messages_fulltext_content mfc
        ON mfc.docid = me.id
		WHERE me.empty is not 1
    ''')
    
    data_list = []

    for file in files_found:
        db_records = get_sqlite_db_records(str(file), query)
        try:
            account = uuid_mapping[re.search(uuid_regex, file).group(0)]
        except KeyError:
            continue
    
        for row in db_records:
            sent = convert_unix_ts_to_utc(row[0]/1000) if row[0] is not None else None
            stored = convert_unix_ts_to_utc(row[1]/1000) if row[1] is not None else None
            sender = str(row[2]).replace(",", "\n")
            receiver = str(row[3]).replace(",", "\n")
            cc = str(row[4]).replace(",", "\n")
            bcc = str(row[5]).replace(",", "\n")
            subject = row[6]
            preview = row[7]
            attachments = row[8]
            read = row[9]
            flagged = row[10]
            answered = row[11]
            forwarded = row[12]
            folder = row[13]
            content = row[14]


            data_list.append((sent, stored, account, sender, receiver, cc, bcc, subject, preview, content, attachments, read, flagged, answered, forwarded, folder, str(file)))

    data_headers = ( 'Timestamp Sent', 'Timestamp Stored', 'Account', 'Sender', 'Receiver', 'CC', 'BCC', 'Subject', 'Preview', 'Content', 'Attachments', 'Read?', 'Flagged?', 'Answered?', 'Forwarded?', 'Folder Name', 'Source File')

    return data_headers, data_list, 'See source file(s) below:'