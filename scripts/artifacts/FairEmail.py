# FairCode FairEmail App (eu.faircode.email)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2024-04-20: Android 14, App: 1.2178

# Requirements:  




__artifacts_v2__ = {

    
    "get_fair_mail_accounts": {
        "name": "FairEmail - Accounts",
        "description": "FairEmail Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.2",
        "creation_date": "2025-03-08",
        "last_update_date": "2025-11-15",
        "requirements": "none",
        "category": "FairCode FairEmail App",
        "notes": "",
        "paths": ('*/eu.faircode.email/databases/fairemail*'),
        "output_types": ["standard"],
        "artifact_icon": "inbox"
    },
    "get_fair_mail_contacts": {
        "name": "FairEmail - Contacts",
        "description": "FairEmail Contacts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.2",
        "creation_date": "2025-03-08",
        "last_update_date": "2025-11-15",
        "requirements": "none",
        "category": "FairCode FairEmail App",
        "notes": "",
        "paths": ('*/eu.faircode.email/databases/fairemail*'),
        "output_types": ["standard"],
        "artifact_icon": "users"
    }
    ,
    "get_fair_mail_messages": {
        "name": "FairEmail - Messages",
        "description": "FairEmail Messages",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2025-11-16",
        "last_update_date": "2025-11-16",
        "requirements": "none",
        "category": "FairCode FairEmail App",
        "notes": "",
        "paths": ('*/eu.faircode.email/databases/fairemail*', '*/eu.faircode.email/files/attachments/*', '*/eu.faircode.email/files/messages/*'),
        "output_types": ["standard"],
        "artifact_icon": "mail"
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records


@artifact_processor
def get_fair_mail_accounts(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
        
    query = ('''
        SELECT
        identity.account, identity.name, identity.email, identity.display, identity.signature, account.host, account.port, account.user, account.password, account.name, account.created, account.last_connected 
        FROM account
        INNER JOIN identity
        ON account.id = identity.account
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []

    for row in db_records:
        account_id = row[0]
        name = row[1]
        email = row[2]
        display_name = row[3]
        signature = row[4]
        server = row[5]
        port = row[6]
        username = row[7]
        password = row[8]
        account_name = row[9]
        creationdate = convert_unix_ts_to_utc(row[10]/1000)
        lastconnecteddate = convert_unix_ts_to_utc(row[11]/1000)

        data_list.append((account_id, name, email, display_name, signature, server, port, username, password, account_name, creationdate, lastconnecteddate))

    data_headers = ('Account ID', 'Name', 'E-Mail Address', 'Display Name', 'Signature', 'IMAP Server', 'IMAP Port', 'Username', 'Password', 'Account Name', 'Created Date', 'Last Connected Date')

    return data_headers, data_list, files_found[0]

@artifact_processor
def get_fair_mail_contacts(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    query = ('''
        SELECT
        contact.id, contact.name, contact.email, contact.times_contacted, contact.first_contacted, contact.last_contacted, account.name, account.user
        FROM account
        INNER JOIN contact
        ON account.id = contact.account
    ''')

    db_records = get_sqlite_db_records(str(files_found[0]), query)
    

    data_list = []
    for row in db_records:
        contact_id = row[0]
        name = row[1]
        email = row[2]
        times_contacted = row[3]
        firstcontacteddate = convert_unix_ts_to_utc(row[4]/1000)
        lastcontacteddate = convert_unix_ts_to_utc(row[5]/1000)
        account_name = row[6]
        username = row[7]

        data_list.append((contact_id, name, email, times_contacted, firstcontacteddate, lastcontacteddate, account_name, username))
        
    data_headers = ('Contact ID', 'Contact Display Name', 'E-Mail Address', 'Times Contacted', 'First Contacted', 'Last Contacted', 'Used Account Name', 'Used Account Username')

    return data_headers, data_list, files_found[0]

@artifact_processor
def get_fair_mail_messages(files_found, _report_folder, _seeker, _wrap_text):
    
    # Get the different files found and store them in corressponindg lists to work with them
    main_db = ''

    for file_found in files_found:
        file_found = str(file_found)
    
        if file_found.endswith('fairemail'):
            main_db = file_found


    query = ('''
        SELECT m.id [Message ID],
        account.user [Account],
        folder.name [Folder], 
        json_extract(jefrom.value, '$.address') [From Address],
        json_extract(jefrom.value, '$.personal') [From Name],
        json_extract(jeto.value, '$.address') [To Address],
        json_extract(jeto.value, '$.personal') [To Name],
        json_extract(jecc.value, '$.address') [CC Address],
        json_extract(jecc.value, '$.personal') [CC Name],
        json_extract(jebcc.value, '$.address') [BCC Address],
        json_extract(jebcc.value, '$.personal') [BCC Name],
        json_extract(return_path, '$[0].address') [Return Path],
        subject [Subject],
        sent [Timestamp Sent],
        received [Timestamp Received],
        stored [Timestamp Stored], 
        seen [Read?],
        attachments [# of Attachements], 
        infrastructure [Backend Infrastructure]
        FROM message m
        LEFT JOIN json_each("from") jefrom
        LEFT JOIN json_each("to") jeto
        LEFT JOIN json_each("cc") jecc
        LEFT JOIN json_each("bcc") jebcc
        INNER JOIN account
        ON account.id = m.account
		INNER JOIN folder
		ON folder.id = m.folder
    ''')

    db_records = get_sqlite_db_records(main_db, query)


    data_list = []


    for row in db_records:
        message_id = row[0]
        account = row[1]
        folder = row[2]
        address_from = row[3]
        name_from = row[4]
        address_to = row[5]
        name_to = row[6]
        address_cc = row[7]
        name_cc = row[8]
        address_bcc = row[9]
        name_bcc = row[10]
        return_path = row[11]
        subject = row[12]
        sent = convert_unix_ts_to_utc(row[13]/1000) if row[13] is not None else None
        received = convert_unix_ts_to_utc(row[14]/1000)
        stored = convert_unix_ts_to_utc(row[15]/1000)
        seen = row[16]
        attachments = row[17]
        infrastructure = row[18]

        data_list.append((message_id, account, folder, address_from, name_from, address_to, name_to, address_cc, name_cc, address_bcc, name_bcc, return_path, subject, sent, received, stored, seen, attachments, infrastructure))

    data_headers = ('Message ID', 'Mail Account User', 'Mail Folder Name', 'Sender Address', 'Sender Name', 'Receiver Address', 'Receiver Name', 'CC Address', 'CC Name', 'BCC Address', 'BCC Name', 'Return Path', 'Subject', 'Sent', 'Received', 'Stored', 'Seen', 'Attachments', 'Infrastructure')

    return data_headers, data_list, main_db
