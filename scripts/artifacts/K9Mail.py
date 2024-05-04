# K-9 Mail App (com.fsck.k9)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2024-05-04: Android 13, App: 6.802

# Requirements:  datetime, json




__artifacts_v2__ = {

    
    "K9MailAccounts": {
        "name": "K-9 Mail - Accounts",
        "description": "K-9 Mail - Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-05-04",
        "requirements": "none",
        "category": "K-9 Mail",
        "notes": "",
        "paths": ('*/com.fsck.k9/databases/preferences_storage'),
        "function": "get_k9mail_accounts"
    }
}



import datetime
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_k9mail_accounts(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for K-9 Mail - Accounts")
    files_found = [x for x in files_found if not x.endswith('journal')]
    file_found = str(files_found[0])
    
    # First get the UUID of the existing Accounts
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
        SELECT value 
        FROM preferences_storage
        WHERE primkey = 'accountUuids'
    ''')
    data_rows = cursor.fetchall()
    accountUUIDS = []
    for row in data_rows:
        accountUUIDS = row[0].split(',')
    
    if len(accountUUIDS):
        logfunc(f"Found {len(accountUUIDS)}  K-9 Mail- Accounts")

        description = f"Existing accounts in the K-9 Mail App."
        report = ArtifactHtmlReport('K-9 Mail - Accounts')
        report.start_artifact_report(report_folder, 'K-9 Mail - Accounts', description)
        report.add_script()
        data_headers = ('Internal Account UUID', 'Mail-Address', 'Name', 'Username', 'Password', 'Last Sync Time', 'Incoming Server', 'Outgoing Server', 'Incoming Server Settings', 'Outgoing Server Settings')
        data_list = []
        # Now get the entries per UUID from the same table
        for UUID in accountUUIDS:

            cursor.execute('''
                SELECT * 
                FROM preferences_storage
                WHERE primkey LIKE ?
            ''', (UUID + '%',))

            all_rows = cursor.fetchall()
            account_entries = len(all_rows)
            if account_entries > 0:
                logfunc(f"Found {account_entries}  K-9 Mail- Accounts")
                
                mail_address = ''
                username = ''
                name = ''
                password = ''
                last_sync = ''
                server_in = ''
                server_out = ''
                server_in_settings = ''
                server_out_settings = ''


                for row in all_rows:
                    if 'email.0' in row[0]:
                        mail_address = row[1]
                    if 'name.0' in row[0]:
                        name = row[1]
                    if 'lastSyncTime' in row[0]:
                        last_sync = datetime.datetime.fromtimestamp(int(row[1])/1000).strftime('%Y-%m-%d %H:%M:%S')
                    if 'incomingServerSettings' in row[0]:
                        server_in_settings = row[1]
                        json_data = json.loads(server_in_settings)
                        username = json_data["username"]
                        password = json_data["password"]
                        server_in = str(json_data["host"]) + ":" + str(json_data["port"])
                    if 'outgoingServerSettings' in row[0]:
                        server_out_settings = row[1]
                        json_data = json.loads(server_out_settings)
                        server_out = str(json_data["host"]) + ":" + str(json_data["port"])


                data_list.append((UUID, mail_address, name, username, password, last_sync, server_in, server_out, server_in_settings, server_out_settings))

            else:
                logfunc(f"Warning! No entries found for K-9 Mail Account UUID {UUID}. This should not happen.")
        
        tableID = 'k9mail_accounts'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'K-9 Mail - Accounts'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'K-9 Mail - Accounts'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No K-9 Mail Account data found!')

    db.close()