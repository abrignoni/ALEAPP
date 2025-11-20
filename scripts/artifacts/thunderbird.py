# Android Thunderbird App (net.thunderbird.android)
# Author:  Marco Neumann (kalinko@be-binary.de)
# 
# Tested with the following versions:
# 2025-10-27: Android 16, App: 13.0 

# Requirements: re, json




__artifacts_v2__ = {

    
    "get_thunderbird_accounts": {
        "name": "Thunderbird - Accounts",
        "description": "FairEmail Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2025-11-18",
        "last_update_date": "2025-11-18",
        "requirements": "re, json",
        "category": "Thunderbird App",
        "notes": "",
        "paths": ('*/net.thunderbird.android/databases/preferences_storage'),
        "output_types": ["standard"],
        "html_columns": ["Signature"],
        "artifact_icon": "inbox"
    }

}

import re
import json

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records


@artifact_processor
def get_thunderbird_accounts(files_found, _report_folder, _seeker, _wrap_text):
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

    # Get the UUIDs of the existing accounts,
    uuid_regex = re.compile(r'^[0-9a-fA-F-]{36}')
    uuids = {uuid_regex.match(s[0]).group() for s in db_records if uuid_regex.match(s[0])}
    
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

