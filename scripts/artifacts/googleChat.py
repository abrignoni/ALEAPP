# Google Chat Messages & Group Information
# Author:  Josh Hickman (josh@thebinaryhick.blog) & Alexis Brignoni (https://linqapp.com/abrignoni)
# Date 2021-02-05
# Version: 0.1
# Requirements:  blackboxprotobuf

import os
import sqlite3
import textwrap
import blackboxprotobuf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_googleChat(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)  
        if file_found.endswith('dynamite.db'):
            break
        else:
            continue # Skip all other files
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(topic_messages.create_time/1000000,'unixepoch') AS "Message Time (UTC)",
    Groups.name AS "Group Name",
    users.name AS "Sender",
    topic_messages.text_body AS "Message",
    topic_messages.annotation AS "Message Attachment"
    FROM
    topic_messages
    JOIN Groups on Groups.group_id=topic_messages.group_id
    JOIN users ON users.user_id=topic_messages.creator_id
    ORDER BY "Timestamp (UTC)" ASC
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    if usageentries > 0:
        for x in all_rows:
            values = blackboxprotobuf.decode_message(x[4])
            if x[4] == b'':
                data_list.append((x[0], x[1], x[2], x[3], '', '', '', '','','','',''))
            else:
                #images section
                try:
                    item11 = (values[0]['1']['10'].get('3').decode('utf-8'))
                    item12 = (values[0]['1']['10'].get('4').decode('utf-8'))
                    item13 = (values[0]['1']['10']['5']['1'])
                    item14 = (values[0]['1']['10']['5']['2'])
                    data_list.append((x[0], x[1], x[2], x[3], '', '', '', '', item11, item12, item13, item14))
                    continue
                except:
                    pass
                #meeting plain section
                try:
                    item8 = (values[0]['1']['12']['1']['1'].decode('utf-8'))
                    item9 = (values[0]['1']['12']['1']['3'].decode('utf-8'))
                    item10 = (values[0]['1']['12']['1']['2'].decode('utf-8'))
                    data_list.append((x[0], x[1], x[2], x[3], item9, item10, '', '','','','',''))
                    continue
                except:
                    pass
                    
                #meeting with sender name
                try:
                    item4 = (values[0]['1'][0]['12']['1']['1'].decode('utf-8'))
                    item5 = (values[0]['1'][0]['12']['1']['3'].decode('utf-8'))
                    item6 = (values[0]['1'][0]['12']['1']['6']['16']['1'].decode('utf-8'))
                    item7 = (values[0]['1'][0]['12']['1']['6']['16']['2'].decode('utf-8'))
                    data_list.append((x[0], x[1], x[2], x[3], item5, item6, item7, '','','','',''))
                    continue
                except:
                    pass
                    
                try:
                    item1 = (values[0]['1'][0]['12']['1']['1'].decode('utf-8'))
                    item2 = (values[0]['1'][0]['12']['1']['3'].decode('utf-8'))
                    item3 = (values[0]['1'][0]['12']['1']['2'].decode('utf-8'))
                    data_list.append((x[0], x[1], x[2], x[3], item2, item3, '','','','','',''))
                except:
                    pass
                
    if usageentries > 0:
        report = ArtifactHtmlReport('Google Chat Messages')
        report.start_artifact_report(report_folder, 'Chat Messages')
        report.add_script()
        data_headers = ('Message Timestamp (UTC)','Group Name','Sender','Message','Meeting Code', 'Meeting URL','Meeting Sender','Meeting Sender Profile Pic URL','Filename','File Type','Width','Height')

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Google Chat Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Chat Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Chat Messages data available')

    cursor.execute('''
    SELECT
    datetime(Groups.create_time/1000000,'unixepoch') AS "Group Created Time (UTC)",
    Groups.name AS "Group Name",
    users.name AS "Group Creator",
    datetime(Groups.last_view_time/1000000,'unixepoch') AS "Time Group Last Viewed (UTC)"
    FROM
    Groups
    JOIN users ON users.user_id=Groups.creator_id
    ORDER BY "Group Created Time (UTC)" ASC
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Google Chat Group Information')
        report.start_artifact_report(report_folder, 'Group Information')
        report.add_script()
        data_headers = ('Group Created Time (UTC)','Group Name','Group Creator','Time Group Last Viewed (UTC)') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Google Chat Group Information'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Chat Group Information'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Chat Group Information data available')
            
    db.close()

__artifacts__ = {
        "GoogleChat": (
                "Google Chat",
                ('*/com.google.android.gm/databases/user_accounts/*/dynamite.db*','*/com.google.android.apps.dynamite/databases/dynamite.db*'),
                get_googleChat)
}