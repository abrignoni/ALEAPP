__artifacts_v2__ = {
    "gmailIMAPEmails": {
        "name": "Gmail - IMAP Mailbox Emails",
        "description": "Parses emails from IMAP mailboxes in the Gmail App",
        "author": "ogmini",
        "version": "0.1",
        "creation_date": "2025-08-20",
        "last_update_date": "2025-10-11", 
        "requirements": "none",
        "category": "Email",
        "notes": "", 
        "paths": ('*/data/com.google.android.gm/databases/EmailProvider.*','*/data/com.google.android.gm/files/body/0/*/*.*','*/data/com.google.android.gm/databases/*.db_att/*','*/data/com.google.android.gm/cache/*.attachment'), 
        "output_types": "standard",
        "html_columns": ["Body(HTML)"],
        "artifact_icon": "inbox",
    },
    "gmailIMAPAccounts": {
        "name": "Gmail - IMAP Accounts",
        "description": "Parses IMAP Accounts in the Gmail App",
        "author": "ogmini",
        "version": "0.1",
        "creation_date": "2025-10-11", 
        "last_update_date": "2025-10-11", 
        "requirements": "none",
        "category": "Email",
        "notes": "", 
        "paths": ('*/data/com.google.android.gm/databases/EmailProvider.*'), 
        "output_types": "standard",
        "artifact_icon": "user", 
    }
}

import os
import urllib.parse

from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor, convert_unix_ts_to_utc, logfunc, media_to_html

@artifact_processor
def gmailIMAPEmails(files_found, report_folder, _seeker, _wrap_text):
    emailProviderDB = ''    
    emailProviderDB_found = []

    data_list = []

    bodyTxt_list = []
    bodyHtml_list = []
    
    attachRecv_list = []
    attachSent_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith(('-wal','-shm','-journal')):
            continue
        elif os.path.basename(file_found).startswith('.'):
            continue
        if os.path.basename(file_found).startswith('EmailProvider'):
            emailProviderDB = str(file_found) 
            emailProviderDB_found.append(emailProviderDB)
        if file_found.endswith(('.txt')):
            bodyTxt_list.append(file_found)
        if file_found.endswith(('.html')):
            bodyHtml_list.append(file_found)
        if os.path.basename(os.path.dirname(file_found)).endswith(('.db_att')):        
            attachRecv_list.append(file_found)
        if file_found.endswith(('.attachment')):
            attachSent_list.append(file_found)
        
    for i in range(len(emailProviderDB_found)):
        emailProviderDB = emailProviderDB_found[i]
        
        db = open_sqlite_db_readonly(emailProviderDB)
        cursor = db.cursor()
        cursor.execute('''
        select M.timeStamp, M._id, M.snippet, M.toList, M.replyToList, M.subject, M.fromList, M.displayName, M.flagRead, M.flagAttachment,
        A._id as AccountID,
        MB.displayName
        from Message as M
        inner join Account as A on A._id = M.AccountKey
		inner join Mailbox as MB on M.mailboxKey = MB._id
        ''')
        
        all_rows = cursor.fetchall()
        for row in all_rows:
            row = list(row)
            try:
                row[0] = convert_unix_ts_to_utc(row[0])
            except (TypeError, ValueError, OverflowError, OSError) as ex:
                logfunc(f'Error Timestamp conversion: {ex}')

            # BODY Files - Full message is found elsewhere */data/com.google.android.gm/files/body/[ParentFolder]/[_idFolder]
            # TXT Body
            tBody = ''
            for txtBody in bodyTxt_list:
                if ((os.path.basename(txtBody)) == (str(row[1]) + '.txt')):
                    with open(txtBody, "r", encoding="utf-8") as f:
                        tBody = f.read()

            # HTML Body
            hBody = ''
            for htmlBody in bodyHtml_list:
                if ((os.path.basename(htmlBody)) == (str(row[1]) + '.html')):
                    with open(htmlBody, "r", encoding="utf-8") as f:
                        hBody = f.read()
            
            # ATTACHMENTS - Files can be stored in two different locations depending if they are sent or received.            
            AttachmentPaths = []
            if (row[9] == 1):
                cursor_attach = db.cursor()
                cursor_attach.execute('''
                select A.accountKey, A._id, A.fileName, A.mimeType, A.cachedFile
                from Attachment as A
                where messageKey = ?
                ''', (row[1],))
                
                attach_rows = cursor_attach.fetchall()
                for row_a in attach_rows:
                    row_a = list(row_a)
                    accountID = row_a[0]
                    attachmentID = row_a[1]
                    
                    if (row_a[4] is None):
                        # Received Attachment */data/com.google.android.gm/databases/*.db_att/*.*
                        for rAttach in attachRecv_list:
                            if (((os.path.basename(rAttach)) == f'{attachmentID}') and ((os.path.basename(os.path.dirname(rAttach))) == f'{accountID}.db_att')):
                                AttachmentPaths.append([row_a[2], media_to_html(rAttach, files_found, report_folder)])
                    else:
                        # Sent Attachment /data/com.google.android.gm/cache/*.attachment
                        uri = row_a[4]
                        fileName = ''
                        parsedUri = urllib.parse.urlparse(uri)
                        
                        queryParams = urllib.parse.parse_qs(parsedUri.query)
                        filePathEncoded = queryParams.get("filePath", [None])[0]

                        if filePathEncoded:
                            filePath = urllib.parse.unquote(filePathEncoded)
                            fileName = os.path.basename(filePath).replace(":", "_")
                            
                            for sAttach in attachSent_list:
                                if ((os.path.basename(sAttach)) == fileName):
                                    AttachmentPaths.append([row_a[2], media_to_html(sAttach, files_found, report_folder)])
                           
            data_list.append((row[0], row[1], row[2], tBody, hBody, row[3], row[4], row[5], row[6], row[7], row[8], row[9], AttachmentPaths, row[11], emailProviderDB))

    data_headers = (('Timestamp','datetime'),'_id','Snippet', 'Body(TXT)', 'Body(HTML)', 'Recipient','Reply To','Subject Line','Mailed By','Signed by', 'Read', 'AttachmentFlag', 'Attachments', 'Mailbox Folder', 'Source File')
    return data_headers, data_list, 'See source file(s) below:'
    
@artifact_processor
def gmailIMAPAccounts(files_found, _report_folder, _seeker, _wrap_text):
    emailProviderDB = '' 
    emailProviderDB_found = []

    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith(('-wal','-shm','-journal')):
            continue
        elif os.path.basename(file_found).startswith('.'):
            continue
        if os.path.basename(file_found).startswith('EmailProvider'):
            emailProviderDB = str(file_found)
            emailProviderDB_found.append(emailProviderDB)
        
    for i in range(len(emailProviderDB_found)):
        emailProviderDB = emailProviderDB_found[i]
        
        db = open_sqlite_db_readonly(emailProviderDB)
        cursor = db.cursor()
        cursor.execute('''
        select A._id, A.displayName, A.emailAddress, A.senderName, H.login, H.password, H.address, H.port
        from Account as A
        inner join HostAuth as H on (A.hostAuthKeyRecv  = H._id) or (A.hostAuthKeySend = H._id)
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            row = list(row)

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], emailProviderDB))

    data_headers = ('_id', 'displayName', 'emailAddress', 'senderName', 'login','password','address','port', 'Source File')
    return data_headers, data_list, 'See source file(s) below:'