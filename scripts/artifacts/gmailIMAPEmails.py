__artifacts_v2__ = {
    "gmailIMAPEmails": {
        "name": "Gmail - IMAP Mailbox Emails",
        "description": "Parses emails from IMAP mailboxes in the Gmail App",
        "author": "ogmini",
        "version": "0.1",
        "creation_date": "2025-08-20",
        "last_update_date": "2025-08-20",
        "requirements": "none",
        "category": "Email",
        "notes": "",
        "paths": ('*/data/com.google.android.gm/databases/EmailProvider.*','*/data/com.google.android.gm/files/body/0/*/*.*'), # TODO: Is hardcoding 0 OK? Possibility of more mailboxes maybe?
        "output_types": "standard",
        "html_columns": ["Body(HTML)"],
        "artifact_icon": "inbox",
    },
}

import os
from datetime import datetime

from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor, convert_unix_ts_to_utc, logfunc

@artifact_processor
def gmailIMAPEmails(files_found, report_folder, seeker, wrap_text):
    emailProviderDB = ''
    source_emailProvider = ''
    
    emailProviderDB_found = []
    source_emailProvider_found = []
    data_list = []

    bodyTxt_list = []
    bodyHtml_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith(('-wal','-shm')):
            continue
        elif os.path.basename(file_found).startswith('.'):
            continue
        if os.path.basename(file_found).startswith('EmailProvider'):
            emailProviderDB = str(file_found)
            source_emailProvider = file_found.replace(seeker.data_folder, '')
            emailProviderDB_found.append(emailProviderDB)
            source_emailProvider_found.append(source_emailProvider)
        if file_found.endswith(('.txt')):
            bodyTxt_list.append(file_found)
        if file_found.endswith(('.html')):
            bodyHtml_list.append(file_found)
        
    for i in range(len(emailProviderDB_found)):
        emailProviderDB = emailProviderDB_found[i]
        source_emailProvider = source_emailProvider_found[i]
        db = open_sqlite_db_readonly(emailProviderDB)
        cursor = db.cursor()
        cursor.execute('''
        select timeStamp, _id, snippet, toList, replyToList, subject, fromList, displayName  
        from Message
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            row = list(row)
            try:
                row[0] = convert_unix_ts_to_utc(row[0])
            except Exception as ex:
                logfunc('Error Timestamp conversion: ', ex)

            # Full message is found elsewhere */data/com.google.android.gm/files/body/[ParentFolder]/[_idFolder]
            # TXT Body
            tBody = ''
            for txtBody in bodyTxt_list:
                if ((os.path.basename(txtBody)) == (str(row[1]) + '.txt')):
                    with open(txtBody, "r", encoding="utf-8") as f:
                        tBody = f.read()

            # HTML Body
            # TODO: Can this be rendered as HTML?
            hBody = ''
            for htmlBody in bodyHtml_list:
                if ((os.path.basename(htmlBody)) == (str(row[1]) + '.html')):
                    with open(htmlBody, "r", encoding="utf-8") as f:
                        hBody = f.read()

            data_list.append((row[0], row[1], row[2], tBody, hBody, row[3], row[4], row[5], row[6], row[7], emailProviderDB))

    data_headers = (('Timestamp','datetime'),'_id','Snippet', 'Body(TXT)', 'Body(HTML)', 'Recipient','Reply To','Subject Line','Mailed By','Signed by', 'Source File')
    return data_headers, data_list, 'See source file(s) below:'