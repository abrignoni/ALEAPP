# GroupMe
# Author:  Josh Hickman (josh@thebinaryhick.blog)
# Date 2021-02-XX
# Version: 0.1
# Requirements:  None

import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_groupMe(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        #if not file_found.endswith('burners.db'):
            #continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(groups.created_at,'unixepoch') AS "Group Creation Time",
        groups.name AS "Group Name",
        groups.group_type AS "Group Type",
        members.user_real_name AS "Group Creator",
        members.role as "Creator Role",
        groups.message_count AS "Total Message Count in Group",
        groups.attachment_count AS "Total Attachment Count in Group",
        datetime(groups.last_message_created_at,'unixepoch') AS "Time of Last Message in Group",
        datetime(groups.updated_at,'unixepoch') AS "Time Group Last Updated"
        FROM
        groups
        JOIN members ON members.user_id=groups.creator_user_id
        ORDER BY "Group Creation Time" ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Group Information')
            report.start_artifact_report(report_folder, 'Group Information')
            report.add_script()
            data_headers = ('Group Creation Time','Group Name','Group Type','Group Creator','Creator Role','Total Message Count in Group','Total Attachment Count in Group','Time of Last Message in Group','Time Group Last Updated') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Group Information'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Group Information'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No GroupMe Group Information data available')

        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(messages.created_at,'unixepoch') AS "Message Time",
        groups.name as "Group Name",
        messages.name AS "Message Sender",
        messages.sender_type AS "Message Sender Type",
        CASE
        WHEN messages.is_system=0 THEN "No"
        WHEN messages.is_system=1 THEN "Yes"
        END AS "Is System Message",
        CASE
        WHEN messages.hidden=0 THEN "No"
        WHEN messages.hidden=1 THEN "Yes"
        END AS "Message Is Hidden",
        CASE
        WHEN messages.read=0 THEN "No"
        WHEN messages.read=1 THEN "Yes"
        END AS "Message Read",
        messages.message_text AS "Message",
        messages.photo_url AS "Picture URL",
        messages.photo_uri AS "Picture Local Storage Location",
        messages.photo_width as "Picture Width",
        messages.photo_height AS "Picture Height",
        CASE
        WHEN messages.photo_is_gif=0 THEN "No"
        WHEN messages.photo_is_gif=1 THEN "Yes"
        END AS "Picture is GIF",
        messages.video_url AS "Video URL",
        messages.location_lat AS "Message Latitude",
        messages.location_lng AS "Message Longitude",
        messages.location_name AS "Location Name"
        FROM
        messages
        JOIN groups ON groups.group_id=messages.conversation_id
        ORDER BY "Message Time" ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Chat Information')
            report.start_artifact_report(report_folder, 'Chat Information')
            report.add_script()
            data_headers = ('Message Time','Group Name','Message Sender','Message Sender Type','Is System Message','Message Is Hidden','Message Is Read','Message','Picture URL','Picture Local Storage Location','Picture Width','Picture Heigh','Picture Is GIF','Video URL','Message Latitude','Message Longitude','Location Name') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Chat Information'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Chat Information'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No GroupMe Chat Information data available')
                
        db.close()

__artifacts__ = {
        "GroupMe": (
                "GroupMe",
                ('*/com.groupme.android/databases/groupme.db'),
                get_groupMe)
}