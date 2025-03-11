# Burner
# Author:  Josh Hickman (josh@thebinaryhick.blog)
# Date 2021-02-05
# Version: 0.1
# Requirements:  None

import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_burner(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        #if not file_found.endswith('burners.db'):
            #continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(burners.date_created/1000,'unixepoch') AS "Number Creation Time",
        burners.name AS "Phone Number Name",
        burners.phone_number_id AS "Number",
        datetime(burners.last_updated_date/1000,'unixepoch') AS "Number Time Last Updated",
        datetime(burners.expiration_date/1000,'unixepoch') AS "Number Expiration Time",
        burners.total_minutes AS "Phone Minutes Allotment",
        burners.remaining_minutes AS "Phone Minutes Remaining",
        burners.total_texts AS "Text Message Allotment",
        burners.remaining_texts AS "Text Messages Remaining"
        FROM
        burners
        ORDER BY "Number Creation Time" ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            #logfunc(str(all_rows))
            report = ArtifactHtmlReport('Number Information')
            report.start_artifact_report(report_folder, 'Number Information')
            report.add_script()
            data_headers = ('Number Creation Time','Number Name','Number','Number Time Last Updated','Number Expiration Time','Phone Minutes Allotment','Phone Minutes Remaining','Text Messages Allotment','Text Messages Remaining') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Number Information'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Number Information'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Burner Number Information data available')

        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(messages.date_created/1000,'unixepoch') AS "Communication Time",
        messages.contact_phone_number AS "Other Party Number",
        contacts.name AS "Other Party Contact Name",
        CASE
        WHEN messages.direction=1 THEN "Incoming"
        WHEN messages.direction=2 THEN "Outgoing"
        ELSE messages.direction
        END AS "Communication Direction",
        CASE
        WHEN messages.message_type=1 THEN "Call"
        WHEN messages.message_type=2 THEN "Text Message"
        ELSE messages.message_type
        END AS "Communication Type",
        messages.message AS "Message",
        messages.asset_url AS "Message Attachment (URL)",
        messages.duration as "Approximate Call Duration (minutes)"
        FROM
        messages
        JOIN contacts ON contacts.phone_number=messages.contact_phone_number
        ORDER BY "Communication Time" ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Communication Information')
            report.start_artifact_report(report_folder, 'Communication Information')
            report.add_script()
            data_headers = ('Communication Time','Other Party Number','Other Party Contact Name','Communication Direction','Communication Type','Message','Message Attachment (URL)','Approximate Call Duration (minutes)') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Communication Information'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Communication Information'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Burner Communication Information data available')
                
        db.close()
        
__artifacts__ = {
        "Burner": (
                "Burner",
                ('*/com.adhoclabs.burner/databases/burners.db'),
                get_burner)
}