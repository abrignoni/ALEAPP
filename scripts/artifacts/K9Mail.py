# K-9 Mail App (com.fsck.k9)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2024-05-04: Android 13, App: 6.802

# Requirements:  datetime, json, base64




__artifacts_v2__ = {

    
    "K9MailData": {
        "name": "K-9 Mail - Data",
        "description": "K-9 Mail - Data",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-05-04",
        "requirements": "datetime, json, base64",
        "category": "K-9 Mail",
        "notes": "Get Account informations and E-Mails feom K-9 Mail App. Based on https://bebinary4n6.blogspot.com/2024/05/app-k-9-mail-for-android.html",
        "paths": ('*/com.fsck.k9/databases/*'),
        "function": "get_k9mail_data"
    }
}

import datetime
import json
import base64
import quopri

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly




def get_k9mail_data(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for K-9 Mail - Accounts")
 
    accountUUIDS = []
    mail_addresses = []
 
    files_found = [x for x in files_found if x.endswith('db') or x.endswith('preferences_storage')]
    
    for file_found in files_found:
        # First get the data of the existing accounts and create this artifact
        if file_found.endswith('preferences_storage'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
                SELECT value 
                FROM preferences_storage
                WHERE primkey = 'accountUuids'
            ''')
            data_rows = cursor.fetchall()
            for row in data_rows:
                accountUUIDS = row[0].split(',')
            
            if len(accountUUIDS):
                logfunc(f"Found {len(accountUUIDS)}  K-9 Mail - Accounts")

                description = f"Existing accounts in the K-9 Mail App. Based on https://bebinary4n6.blogspot.com/2024/05/app-k-9-mail-for-android.html"
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

                    mail_address = ''
                    username = ''
                    name = ''
                    password = ''
                    last_sync = ''
                    server_in = ''
                    server_out = ''
                    server_in_settings = ''
                    server_out_settings = ''
                    all_rows = cursor.fetchall()
                    account_entries = len(all_rows)
                    if account_entries > 0:
                        for row in all_rows:
                            if 'email.0' in row[0]:
                                mail_address = row[1]
                                mail_addresses.append(mail_address)
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
        
        # okay, now lets get the mail/message data for the accounts
        for UUID, account in zip(accountUUIDS, mail_addresses):
            if UUID in file_found:
                db = open_sqlite_db_readonly(file_found)
                cursor = db.cursor()
                cursor.execute('''
                    SELECT deleted, subject, date, sender_list, to_list, cc_list, bcc_list, reply_to_list, attachment_count, internal_date, preview, read, flagged, answered, forwarded,  name, root, header, (SELECT encoding FROM message_parts M_INNER WHERE M_INNER.root = M_OUTER.ROOT AND seq = 1) AS encoding, (SELECT data FROM message_parts M_INNER WHERE M_INNER.root = M_OUTER.ROOT AND seq = 1) AS data, data_location  
                    FROM message_parts M_OUTER  
                    JOIN messages ON messages.message_part_id = M_OUTER.root  
                    JOIN folders ON folders.id =  messages.folder_id  
                    WHERE seq = 0
                ''')
                data_rows = cursor.fetchall()
                
                if len(data_rows):
                    logfunc(f"Found {len(data_rows)}  K-9 Mail - Messages for account {account}")

                    description = f"Existing E-Mails for the Account {account} in the K-9 Mail App. Based on https://bebinary4n6.blogspot.com/2024/05/app-k-9-mail-for-android.html"
                    report = ArtifactHtmlReport(f'K-9 Mail - Mails for Account {account}')
                    report.start_artifact_report(report_folder, f'K-9 Mail - Mails for Account {account}', description)
                    report.add_script()
                    data_headers = ('Date Sent', 'Folder', 'Subject', 'Message Preview', 'From', 'To', 'CC', 'BCC', 'Reply To', '# of Attachments', 'Content', 'Date Received', 'Deleted', 'Read', 'Flagged', 'Answered', 'Forwarded', 'Header')
                    data_list = []
                    for row in data_rows:
                        date_sent = datetime.datetime.fromtimestamp(int(row[2])/1000).strftime('%Y-%m-%d %H:%M:%S')
                        folder = row[15]
                        subject = row[1]
                        sender = row[3]
                        to = row[4]
                        cc = row[5]
                        bcc = row[6]
                        reply_to = row[7]
                        attachment_count = row[8]
                        date_received = datetime.datetime.fromtimestamp(int(row[9])/1000).strftime('%Y-%m-%d %H:%M:%S')
                        message_preview = row[10]
                        read_flag = 'Yes' if row[11] == 1 else 'No'
                        flagged_flag = 'Yes' if row[12] == 1 else 'No'
                        answered_flag = 'Yes' if row[13] == 1 else 'No'
                        forwarded_flag = 'Yes' if row[14] == 1 else 'No'
                        deleted_flag = 'Yes' if row[0] == 1 else 'No'
                        header = row[17].decode('UTF-8')
                        content = ''
                        # Decocding is needed
                        if row[18] == 'base64':
                            content = base64.b64decode(row[19]).decode('UTF-8')
                        elif row[19]:
                            content = row[19]

                        data_list.append((date_sent, folder, subject, message_preview, sender, to, cc, bcc, reply_to, attachment_count, content, date_received, deleted_flag, read_flag, flagged_flag, answered_flag, forwarded_flag, header))

                    tableID = 'k9mail_messages_' + UUID

                    report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
                    report.end_artifact_report()

                    tsvname = f'K-9 Mail - Mails {account}'
                    tsv(report_folder, data_headers, data_list, tsvname)

                    tlactivity = f'K-9 Mail - Mails {account}'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                else:
                    logfunc(f"No messages found for K-9 Mail Account {account}.")

                db.close()
