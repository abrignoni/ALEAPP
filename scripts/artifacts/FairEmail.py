# FairCode FairEmail App (eu.faircode.email)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2024-04-20: Android 14, App: x.x.x

# Requirements:  datetime




__artifacts_v2__ = {

    
    "FairEmailAccounts": {
        "name": "FairEmail - Accounts",
        "description": "FairEmail Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2025-03-08",
        "requirements": "none",
        "category": "FairCode FairEmail App",
        "notes": "",
        "paths": ('*/eu.faircode.email/databases/fairemail'),
        "function": "get_fairemail_accounts"
    },
        "FairEmailContacts": {
        "name": "FairEmail - Contacts",
        "description": "FairEmail Contacts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2025-03-08",
        "requirements": "none",
        "category": "FairCode FairEmail App",
        "notes": "",
        "paths": ('*/eu.faircode.email/databases/fairemail'),
        "function": "get_fairemail_contacts"
    }
}



import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_fairemail_accounts(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for FairEmail App - Accounts")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
        SELECT
        identity.account, identity.name, identity.email, identity.display, identity.signature, account.host, account.port, account.user, account.password, account.name, account.created, account.last_connected 
        FROM account
        INNER JOIN identity
        ON account.id = identity.account
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  FairEmail - Accounts")
        description = f"Existing accounts in FairEmail App."
        report = ArtifactHtmlReport('FairEmail - Accounts')
        report.start_artifact_report(report_folder, 'FairEmail - Accounts', description)
        report.add_script()
        data_headers = ('Account ID', 'Name', 'E-Mail Address', 'Display Name', 'Signature', 'IMAP Server', 'IMAP Port', 'Username', 'Password', 'Account Name', 'Created Date', 'Last Connected Date')
        data_list = []
        for row in all_rows:
            id = row[0]
            name = row[1]
            email = row[2]
            display_name = row[3]
            signature = row[4]
            server = row[5]
            port = row[6]
            username = row[7]
            password = row[8]
            account_name = row[9]
            creationdate = datetime.datetime.fromtimestamp(row[10]/1000).strftime('%Y-%m-%d %H:%M:%S')
            lastconnecteddate = datetime.datetime.fromtimestamp(row[11]/1000).strftime('%Y-%m-%d %H:%M:%S')

            data_list.append((id, name, email, display_name, signature, server, port, username, password, account_name, creationdate, lastconnecteddate))

        tableID = 'FairEmail_accounts'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'FairEmail - Accounts'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'FairEmail - Accounts'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No FairEmail Account data found!')

    db.close()

def get_fairemail_contacts(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for FairEmail App - Contacts")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
        SELECT
        contact.id, contact.name, contact.email, contact.times_contacted, contact.first_contacted, contact.last_contacted, account.name, account.user
        FROM account
        INNER JOIN contact
        ON account.id = contact.account
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  FairEmail - Contacts")
        description = f"Contacted contacts in FairEmail App."
        report = ArtifactHtmlReport('FairEmail - Contacts')
        report.start_artifact_report(report_folder, 'FairEmail - Contacts', description)
        report.add_script()
        data_headers = ('Contact ID', 'Contact Display Name', 'E-Mail Address', 'Times Contacted', 'First Contacted', 'Last Contacted', 'Used Account Name', 'Used Account Username')
        data_list = []
        for row in all_rows:
            id = row[0]
            name = row[1]
            email = row[2]
            times_contacted = row[3]
            firstcontacteddate = datetime.datetime.fromtimestamp(row[4]/1000).strftime('%Y-%m-%d %H:%M:%S')
            lastcontacteddate = datetime.datetime.fromtimestamp(row[5]/1000).strftime('%Y-%m-%d %H:%M:%S')
            account_name = row[6]
            username = row[7]

            data_list.append((id, name, email, times_contacted, firstcontacteddate, lastcontacteddate, account_name, username))

        tableID = 'FairEmail_Contacts'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'FairEmail - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'FairEmail - Contacts'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No FairEmail Contact data found!')

    db.close()
