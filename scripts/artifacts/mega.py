# MEGA
# Author:  Kevin Pagano (@KevinPagano3)
# Website: stark4n6.com
# Date 2021-01-31
# Version: 0.1
# Requirements:  None

import json
import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_mega(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(history.ts,'unixepoch'),
        contacts.email,
        CASE history.type
            WHEN 1 THEN 'Chat Message'
            WHEN 2 THEN 'Joined the group chat'
            WHEN 6 THEN 'Group Call Ended'
            WHEN 7 THEN 'Group Call Started'
            WHEN 101 THEN 'Attachment'
        END AS Type,
        history.data
        FROM history
        LEFT JOIN contacts ON contacts.userid = history.userid
        ORDER BY history.ts ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('MEGA - Chat')
            report.start_artifact_report(report_folder, 'MEGA - Chat')
            report.add_script()
            data_headers = ('Message Timestamp','Sender','Message Type','Chat Message','Attachment Name') 
            data_list = []
            for row in all_rows:
                attachment_name = ''
                chat_message = ''
                if row[2] == 'Chat Message':
                   chat_contents = row[3]
                   chat_message = chat_contents[0:]
                   chat_message = (str(chat_message)[2:-1])
                   
                   data_list.append((row[0],row[1],row[2],chat_message,attachment_name))
                
                elif row[2] == 'Attachment':
                    json_contents = row[3]
                    json_string = json_contents[2:]
                    json_string = (str(json_string)[2:-1])
                    
                    json_export = json.loads(json_string)
                    
                    attachment_name = json_export[0]['name']
                    
                    data_list.append((row[0],row[1],row[2],chat_message,attachment_name))
                else:
                    data_list.append((row[0],row[1],row[2],chat_message,attachment_name))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'MEGA - Chat'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'MEGA - Chat'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No MEGA - Chat data available')
        
        db.close()

__artifacts__ = {
        "mega": (
                "Mega",
                ('*/mega.privacy.android.app/karere-*.db*'),
                get_mega)
}