# FairCode FairEmail App (eu.faircode.email)
# Author:  Marco Neumann (kalinko@be-binary.de)
# 
# Tested with the following versions:
# 2024-04-20: Android 14, App: 1.2178

# Requirements: os




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
        "html_columns": ["Signature"],
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
        "requirements": "os",
        "category": "FairCode FairEmail App",
        "notes": "",
        "paths": ('*/eu.faircode.email/databases/fairemail*', '*/eu.faircode.email/files/attachments/*', '*/eu.faircode.email/files/messages/*'),
        "output_types": ["standard"],
        "html_columns": ["Content", "Attachments"],
        "artifact_icon": "mail"
    }
}

import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, media_to_html


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

        data_list.append(( creationdate, lastconnecteddate, account_id, name, email, display_name, signature, server, port, username, password, account_name))

    data_headers = ( 'Creation Date', 'Last Connected Date', 'Account ID', 'Name', 'E-Mail Address', 'Display Name', 'Signature', 'IMAP Server', 'IMAP Port', 'Username', 'Password', 'Account Name')

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

        data_list.append((firstcontacteddate, lastcontacteddate, contact_id, name, email, times_contacted, account_name, username))
     
    data_headers = ('First Contacted', 'Last Contacted', 'Contact ID', 'Contact Display Name', 'E-Mail Address', 'Times Contacted', 'Used Account Name', 'Used Account Username')

    return data_headers, data_list, files_found[0]

@artifact_processor
def get_fair_mail_messages(files_found, report_folder, _seeker, _wrap_text):
    
    # Get the different files found and store their pathes in corresponding lists to work with them
    main_db = ''
    attachments = []
    messages = []

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('fairemail'):
            main_db = file_found

        if 'attachments' in os.path.dirname(file_found):
            attachments.append(file_found)
        
        if 'messages' in os.path.dirname(file_found):
            messages.append(file_found)

        

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
        infrastructure [Backend Infrastructure],
		GROUP_CONCAT(attachment.id, ',') [Attachmernt IDs],
		m.preview
        FROM message m
        LEFT JOIN json_each("from") jefrom
        LEFT JOIN json_each("to") jeto
        LEFT JOIN json_each("cc") jecc
        LEFT JOIN json_each("bcc") jebcc
        INNER JOIN account
        ON account.id = m.account
		INNER JOIN folder
		ON folder.id = m.folder
		LEFT JOIN attachment
		ON attachment.message = m.id
		GROUP BY m.id
    ''')

    db_records = get_sqlite_db_records(main_db, query)




    data_list = []


    for row in db_records:
        content = ''
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
        preview = row[20]
        sent = convert_unix_ts_to_utc(row[13]/1000) if row[13] is not None else None
        received = convert_unix_ts_to_utc(row[14]/1000)
        stored = convert_unix_ts_to_utc(row[15]/1000)
        seen = row[16]
        # check if the mail has attachments, if yes - add them
        # Also inline Attachemts are linked
        if row[19] is None:
            attachment = 0
        else:
            attachment = []
            for att_path in attachments:
                for att_id in row[19].split(','):
                    if str(att_id) in os.path.basename(att_path):
                        attachment.append(media_to_html(os.path.basename(att_path), attachments, report_folder))
        infrastructure = row[18]
        for path in messages:
            try:
                if int(os.path.basename(path)) == message_id:
                    content = media_to_html(str(message_id), messages, report_folder)
                    
            except ValueError:
                continue

        data_list.append((received, sent, stored, account, folder, address_from, name_from, address_to, name_to, address_cc, name_cc, address_bcc, name_bcc, return_path, subject, preview, content, seen, attachment, infrastructure))

    data_headers = ('Date Received', 'Date Sent', 'Date Stored', 'Mail Account', 'Folder', 'Sender Address', 'Sender Name', 'Recipient Address', 'Recipient Name', 'CC Address', 'CC Name', 'BCC Address', 'BCC Name', 'Return Path', 'Subject', 'Preview', 'Content', 'Seen', 'Attachments', 'Infrastructure')

    return data_headers, data_list, main_db
