__artifacts_v2__ = {
    "sChats": {
        "name": "Sideline Chats and Calls",
        "description": "Parses Sideline's textfree database",
        "author": "Matt Beers",
        "version": "0.0.1",
        "date": "2024-02-08",
        "requirements": "none",
        "category": "Chats",
        "notes": "",
        "paths": ('*/data/com.sideline.phone.number/databases/textfree*'),
        "function": "get_schats"
    }
}

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_schats(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('textfree'):
            db = open_sqlite_db_readonly(file_found)
            #SQL QUERY TIME!
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(conversation_item.timestamp / 1000, 'unixepoch', 'localtime') AS TIMESTAMP,
            contact_address.native_first_name,
            contact_address.native_last_name,
            CASE conversation_item.method
            WHEN '1' THEN 'Text'
            WHEN '3' THEN 'Call'
            WHEN '8' THEN 'Voicemail'
            ELSE 'Unknown'
            END AS method,
            conversation_item.message_text,
            conversation_item.duration,
            conversation_item.address
            FROM
            contact_address
            JOIN
            conversation_item ON contact_address.address_e164 = conversation_item.address
            ORDER BY
            conversation_item.timestamp DESC
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                #    last_mod_date = row[0]
                #   if last_mod_date is None:
                #       pass
                #   else:
                #       last_mod_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_mod_date),time_offset)
                
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
            db.close()
                    
        else:
            continue
        
    if data_list:
        description = 'Sideline Chats and Calls'
        report = ArtifactHtmlReport('Sideline Chats')
        report.start_artifact_report(report_folder, 'Sideline Chats', description)
        report.add_script()
        data_headers = ('Timestamp','First Name','Last Name','Method','Message Text','Duration','Phone Number')
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Sideline Chats'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Sideline Chats'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No Sideline data available')
