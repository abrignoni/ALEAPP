__artifacts_v2__ = {

    
    "thunderbird_accounts": {
        "name": "Thunderbird - Accounts",
        "description": "Account settings from the preferences_storage table of the first matched Thunderbird database, one row per account UUID. Username and Password are those of the incoming server settings.",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2025-11-18",
        "last_update_date": "2026-10-04",
        "requirements": "re, json",
        "category": "Thunderbird App",
        "notes": "Only the first matched file is read. An account is a UUID that has an email.0 "
                 "key. Last Sync Time is the stored lastSyncTime value read as Unix milliseconds. "
                 "Username, Password and Incoming Server come from incomingServerSettings, and "
                 "Outgoing Server from outgoingServerSettings. A column is blank for an account "
                 "that lacks the key it is read from. No registered corpus holds this app (20 zip "
                 "listings and 24 tar indexes checked on 2026-10-04); the blank for a missing key "
                 "was checked on a constructed database.",
        "paths": ('*/data/net.thunderbird.android/databases/preferences_storage'),
        "output_types": ["standard"],
        "html_columns": ["Signature"],
        "artifact_icon": "inbox"
    },
     "thunderbird_messages": {
        "name": "Thunderbird - Messages",
        "description": "Messages from each Thunderbird account database: the date and internal_date columns read as Unix milliseconds and shown in UTC, addresses, subject, preview, full text and flags as stored. Rows flagged empty are not included.",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2025-11-20",
        "last_update_date": "2026-10-04",
        "requirements": "re, json",
        "category": "Thunderbird App",
        "notes": "Date is the messages table's date column and Internal Date is its "
                 "internal_date column, both read as Unix milliseconds and shown in UTC. In the "
                 "app's source at commit 9aee4a9, date is the time parsed from the message's Date "
                 "header, or the device time when the message was saved if there is none, and "
                 "internal_date is the message's internal date, which the IMAP code fills from the "
                 "server's INTERNALDATE, or the device time when the message was saved if there is "
                 "none "
                 "(https://github.com/thunderbird/thunderbird-android/blob/"
                 "9aee4a9adcb44ca084ca4e13ee3da564286b0af1/legacy/core/src/main/java/com/fsck/k9/"
                 "mailstore/SaveMessageDataCreator.kt#L22-L24, "
                 "https://github.com/thunderbird/thunderbird-android/blob/"
                 "9aee4a9adcb44ca084ca4e13ee3da564286b0af1/mail/common/src/main/java/com/fsck/k9/"
                 "mail/internet/MimeMessage.java#L144-L158, "
                 "https://github.com/thunderbird/thunderbird-android/blob/"
                 "9aee4a9adcb44ca084ca4e13ee3da564286b0af1/mail/protocols/imap/src/main/java/com/"
                 "fsck/k9/mail/store/imap/RealImapFolder.kt#L797-L799). "
                 "So neither column can be read as the time of sending without the message's own "
                 "headers: a Date header is set by the sender, and a row cannot show whether a "
                 "value is the save time. Which app version wrote a tested database is not "
                 "recorded here. Rows whose empty column is 1 are left out. A database is matched "
                 "to its account by the 36-character UUID in its file name. A file ending in db "
                 "whose name holds no such UUID, or whose UUID is not an account UUID in "
                 "preferences_storage, is skipped and named in the run log. No registered corpus "
                 "holds this app (20 zip listings and 24 tar indexes checked on 2026-10-04); the "
                 "skips were checked on constructed databases. In the Sender, Receiver, CC and BCC columns each "
                 "comma of the stored list is replaced with a line break. The read, flagged, "
                 "answered and forwarded columns are reported as stored.",
        "paths": ('*data/net.thunderbird.android/databases/*',),
        "output_types": ["standard"],
        "html_columns": ["Content"],
        "artifact_icon": "mail"
    }

}

# Android Thunderbird App (net.thunderbird.android)
# Author:  Marco Neumann (kalinko@be-binary.de)
#
# Tested with the following versions:
# 2025-10-27: Android 16, App: 13.0

# Requirements: re, json
import os
import re
import json

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, logfunc
from scripts.context import Context
from scripts.html_safe import safe_source

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
def thunderbird_accounts(context):
    files_found = context.get_files_found()
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')
                   and not x.endswith('journal')]
     
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

    for uuid in uuids:

        last_sync_time = ''
        account_name = ''
        address = ''
        name = ''
        username = ''
        password = ''
        incoming_server = ''
        outgoing_server = ''

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
def thunderbird_messages(context):
    files_found = context.get_files_found()

    preferences_file = [x for x in files_found if "preferences_storage" in x and not x.endswith('journal')]
    uuid_mapping = _map_uuid_to_account(str(preferences_file[0]))
    files_found = [x for x in files_found if x.endswith('db')]
    uuid_regex = re.compile(r'[0-9a-fA-F-]{36}')

    query = ('''
        SELECT
        me.date [Date],
        me.internal_date [Internal Date],
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
    source_paths = set()

    for file in files_found:
        uuid_match = re.search(uuid_regex, os.path.basename(str(file)))
        if uuid_match is None:
            logfunc(f'Thunderbird - Messages: skipped {Context.get_relative_path(str(file))}, '
                    'no account UUID in the file name')
            continue
        if uuid_match.group(0) not in uuid_mapping:
            logfunc(f'Thunderbird - Messages: skipped {Context.get_relative_path(str(file))}, '
                    'its UUID is not an account in preferences_storage')
            continue
        account = uuid_mapping[uuid_match.group(0)]
        db_records = get_sqlite_db_records(str(file), query)

        source_paths.add(str(file))

        for row in db_records:
            date = convert_unix_ts_to_utc(row[0]/1000) if row[0] is not None else None
            internal_date = convert_unix_ts_to_utc(row[1]/1000) if row[1] is not None else None
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


            data_list.append((date, internal_date, account, sender, receiver, cc, bcc, subject, preview, safe_source(content), attachments, read, flagged, answered, forwarded, folder, Context.get_relative_path(str(file))))

    data_headers = ( 'Date', 'Internal Date', 'Account', 'Sender', 'Receiver', 'CC', 'BCC', 'Subject', 'Preview', 'Content', 'Attachments', 'Read?', 'Flagged?', 'Answered?', 'Forwarded?', 'Folder Name', 'Source File')

    return data_headers, data_list, '\n'.join(sorted(source_paths))
