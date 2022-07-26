import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_protonmailMessages(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('MessagesDatabase.db'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(messagev3.Time,'unixepoch') AS 'Message Timestamp',
        messagev3.Subject AS 'Subject',
        messagev3.Sender_SenderSerialized AS 'Sender',
        CASE messagev3.Type
            WHEN 0 THEN 'Incoming'
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
            WHEN 7 THEN 'Sent'
        END AS 'Folder',
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
            data_headers = ('Message Timestamp','Subject','Sender','Message Direction','Status','Message Size','Accessed Timestamp','Folder','Attachment Name','Attachment Size','Message Header') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[14]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'ProtonMail - Messages'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'ProtonMail - Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No ProtonMail - Messages data available')
        
        db.close()
        
__artifacts__ = {
        "protonmailMessages": (
                "ProtonMail",
                ('*/data/data/ch.protonmail.android/databases/*-MessagesDatabase.db*'),
                get_protonmailMessages)
}