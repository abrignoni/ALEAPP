import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_protonmail(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_name = str(file_found)
        
        if file_name.lower().endswith(('-shm','-wal','-journal')):
            continue
            
        if file_name.endswith('-MessagesDatabase.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(messagev3.Time,'unixepoch') AS 'Message Timestamp',
            messagev3.Subject AS 'Subject',
            messagev3.Sender_SenderSerialized AS 'Sender',
            CASE messagev3.Type
                WHEN 0 THEN 'Incoming'
                WHEN 1 THEN 'Draft'
                WHEN 2 THEN 'Outgoing'
            END AS 'Message Direction',
            CASE messagev3.Unread
                WHEN 0 THEN 'Read'
                WHEN 1 THEN 'Unread'
            END AS 'Status',
            messagev3.Size AS 'Message Size',
            CASE messagev3.AccessTime
                WHEN 0 THEN ''
                ELSE datetime(messagev3.AccessTime/1000,'unixepoch')
            END AS 'Accessed Timestamp',
            CASE messagev3.Location
                WHEN 0 THEN 'Inbox'
                WHEN 1 THEN 'Drafts'
                WHEN 2 THEN 'Sent'
                WHEN 3 THEN 'Trash'
                WHEN 6 THEN 'Archive'
                WHEN 7 THEN '7 (TBD)'
            END AS 'Folder',
            CASE messagev3.Starred
                WHEN 0 THEN ''
                WHEN 1 THEN 'Yes'
            END AS 'Starred',
            messagev3.NumAttachments,
            attachmentv3.file_name AS 'Attachment Name',
            attachmentv3.file_size AS 'Attachment Size',
            messagev3.ToList AS 'To List',
            messagev3.ReplyTos AS 'Reply To',
            messagev3.CCList AS 'CC List',
            messagev3.BCCList AS 'BCC List',
            messagev3.Header AS 'Message Header'
            FROM messagev3
            LEFT JOIN attachmentv3 ON attachmentv3.message_id = messagev3.ID
            ORDER BY messagev3.Time ASC
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('ProtonMail - Messages')
                report.start_artifact_report(report_folder, 'ProtonMail - Messages')
                report.add_script()
                data_headers = ('Message Timestamp','Subject','Sender','Message Direction','Status','Message Size','Accessed Timestamp','Folder','Starred','Number of Attachments','Attachment Name','Attachment Size','To List','Reply To','CC List','BCC List','Message Header') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'ProtonMail - Messages'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'ProtonMail - Messages'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No ProtonMail - Messages data available')
            
            db.close()
            
        if file_name.endswith('-ContactsDatabase.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(fullContactsDetails.CreateTime,'unixepoch') AS 'Creation Timestamp',
            datetime(fullContactsDetails.ModifyTIme,'unixepoch') AS 'Modified Timestamp',
            fullContactsDetails.Name AS 'Name',
            contact_emailsv3.Email AS 'Email'
            FROM fullContactsDetails
            LEFT JOIN contact_emailsv3 ON fullContactsDetails.ID = contact_emailsv3.ContactID
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('ProtonMail - Contacts')
                report.start_artifact_report(report_folder, 'ProtonMail - Contacts')
                report.add_script()
                data_headers = ('Creation Timestamp','Modified Timestamp','Name','Email') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'ProtonMail - Contacts'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'ProtonMail - Contacts'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No ProtonMail - Contacts data available')
            
            db.close()
            
        else:
            continue
        
__artifacts__ = {
        "protonmail": (
                "ProtonMail",
                ('*/ch.protonmail.android/databases/*-MessagesDatabase.db*','*/ch.protonmail.android/databases/*-ContactsDatabase.db*'),
                get_protonmail)
}