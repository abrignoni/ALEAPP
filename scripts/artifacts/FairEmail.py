__artifacts_v2__ = {

    
    "get_fair_mail_accounts": {
        "name": "FairEmail - Accounts",
        "description": "FairEmail Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2025-03-08",
        "last_update_date": "2026-10-05",
        "requirements": "none",
        "category": "FairCode FairEmail App",
        "notes": "Server Host (as stored) and Server Port (as stored) hold account.host and account.port. The stored fields do not establish a protocol or successful connection. The query does not limit rows to IMAP accounts. No sample_data is recorded for this artifact.",
        "paths": ('*/eu.faircode.email/databases/fairemail*'),
        "output_types": ["standard"],
        "html_columns": ["Signature"],
        "artifact_icon": "inbox"
    },
    "get_fair_mail_contacts": {
        "name": "FairEmail - Contacts",
        "description": "FairEmail Contacts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
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
        "creation_date": "2025-11-16",
        "last_update_date": "2026-10-04",
        "requirements": "os",
        "category": "FairCode FairEmail App",
        "notes": ("The Sender, Recipient, CC and BCC columns list every entry of the message's from, to, cc and bcc "
                  "fields in stored order, separated by '; '. A name column keeps an empty place for an entry "
                  "that stores no name, so the nth name belongs to the nth address. Return Path shows the first "
                  "entry of the return_path field only. An attachment file is linked when the part of its name "
                  "before the first dot equals an attachment id stored for the message; the app names these "
                  "files '<id>' or '<id>.<name>' (Reference: M66B, FairEmail, "
                  "https://github.com/M66B/FairEmail/blob/e54d23edf04068814c387b93e1d4dab8f6f6d2cc/app/src/main/java/eu/faircode/email/EntityAttachment.java#L206-L213). "
                  "No registered corpus holds this app's data, so the address listing and the attachment "
                  "matching were exercised on a constructed database built from the app's published schema "
                  "version 301, not on a device image. No sample_data is recorded for this artifact."),
        "paths": ('*/eu.faircode.email/databases/fairemail*', '*/eu.faircode.email/files/attachments/*', '*/eu.faircode.email/files/messages/*'),
        "output_types": ["standard"],
        "html_columns": ["Content", "Attachments"],
        "artifact_icon": "mail"
    }
}

# FairCode FairEmail App (eu.faircode.email)
# Author:  Marco Neumann (kalinko@be-binary.de)
# 
# Tested with the following versions:
# 2024-04-20: Android 14, App: 1.2178

# Requirements: os
import json
import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, check_in_media
from scripts.html_safe import safe_source


def _address_parts(stored):
    # message.from, to, cc and bcc each hold a JSON array of objects with an
    # "address" key and an optional "personal" key. Every entry is returned, in
    # stored order, joined with '; '. An entry without a personal name keeps an
    # empty place so the two lists stay in step.
    if stored is None:
        return None, None
    try:
        entries = json.loads(stored)
    except (TypeError, ValueError):
        return stored, None
    if not isinstance(entries, list):
        return stored, None
    addresses = []
    names = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        addresses.append(str(entry.get('address') or ''))
        names.append(str(entry.get('personal') or ''))
    if not addresses:
        return None, None
    return ('; '.join(addresses) if any(addresses) else None,
            '; '.join(names) if any(names) else None)


@artifact_processor
def get_fair_mail_accounts(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
        
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

        data_list.append(( creationdate, lastconnecteddate, account_id, name, email, display_name, safe_source(signature), server, port, username, password, account_name))

    data_headers = ( 'Creation Date', 'Last Connected Date', 'Account ID', 'Name', 'E-Mail Address', 'Display Name', 'Signature', 'Server Host (as stored)', 'Server Port (as stored)', 'Username', 'Password', 'Account Name')

    return data_headers, data_list, files_found[0]

@artifact_processor
def get_fair_mail_contacts(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
    
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
def get_fair_mail_messages(context):
    files_found = context.get_files_found()
    
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
        m."from" [From],
        m."to" [To],
        m."cc" [CC],
        m."bcc" [BCC],
        json_extract(return_path, '$[0].address') [Return Path],
        subject [Subject],
        sent [Timestamp Sent],
        received [Timestamp Received],
        stored [Timestamp Stored], 
        seen [Read?],
        attachments [# of Attachements], 
        infrastructure [Backend Infrastructure],
        (SELECT GROUP_CONCAT(attachment.id, ',') FROM attachment
         WHERE attachment.message = m.id) [Attachment IDs],
        m.preview
        FROM message m
        INNER JOIN account
        ON account.id = m.account
        INNER JOIN folder
        ON folder.id = m.folder
    ''')

    db_records = get_sqlite_db_records(main_db, query)




    data_list = []


    for row in db_records:
        content = ''
        message_id = row[0]
        account = row[1]
        folder = row[2]
        address_from, name_from = _address_parts(row[3])
        address_to, name_to = _address_parts(row[4])
        address_cc, name_cc = _address_parts(row[5])
        address_bcc, name_bcc = _address_parts(row[6])
        return_path = row[7]
        subject = row[8]
        preview = row[16]
        sent = convert_unix_ts_to_utc(row[9]/1000) if row[9] is not None else None
        received = convert_unix_ts_to_utc(row[10]/1000)
        stored = convert_unix_ts_to_utc(row[11]/1000)
        seen = row[12]
        # check if the mail has attachments, if yes - add them
        # Also inline Attachemts are linked
        attachment = ''
        if row[15] is not None:
            # Require an actual file so a matched directory is never passed to
            # check_in_media (which returns None for a directory), and only append a
            # truthy ref so no None lands in the media list -- a None serialized to
            # null in the json.dumps'd media cell crashes the LAVA viewer on hover.
            # FairEmail names an attachment file "<id>" or "<id>.<name>", so the
            # file is matched on the whole id before the first dot.
            attachment_refs = []
            for att_path in attachments:
                if not os.path.isfile(att_path):
                    continue
                att_file_id = os.path.basename(att_path).split('.', 1)[0]
                for att_id in row[15].split(','):
                    if str(att_id) == att_file_id:
                        ref = check_in_media(att_path, os.path.basename(att_path))
                        if ref:
                            attachment_refs.append(ref)
            if len(attachment_refs) == 1:
                attachment = attachment_refs[0]
            elif attachment_refs:
                attachment = attachment_refs
        infrastructure = row[14]
        for path in messages:
            if not os.path.isfile(path):
                continue
            try:
                if int(os.path.basename(path)) == message_id:
                    ref = check_in_media(path, os.path.basename(path))
                    if ref:
                        content = ref
                    
            except ValueError:
                continue

        data_list.append((received, sent, stored, account, folder, address_from, name_from, address_to, name_to, address_cc, name_cc, address_bcc, name_bcc, return_path, subject, preview, content, seen, attachment, infrastructure))

    data_headers = ('Date Received', 'Date Sent', 'Date Stored', 'Mail Account', 'Folder', 'Sender Address', 'Sender Name', 'Recipient Address', 'Recipient Name', 'CC Address', 'CC Name', 'BCC Address', 'BCC Name', 'Return Path', 'Subject', 'Preview', ('Content', 'media'), 'Seen', ('Attachments', 'media'), 'Infrastructure')

    return data_headers, data_list, main_db
