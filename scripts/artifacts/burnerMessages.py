__artifacts_v2__ = {
    "burnerMessages": {
        "name": "Burner: Second Phone Number",
        "description": "Parses Burner Messages",
        "author": "Heather Charpentier (With Tons of Help from Alexis Brignoni!)",
        "version": "0.0.1",
        "date": "2024-02-15",
        "requirements": "none",
        "category": "Burner",
        "notes": "",
        "paths": ('*/data/data/com.adhoclabs.burner/databases/burnerDatabase.db*'),
        "function": "get_burnerMessages"
    }
}

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_burnerMessages(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('burnerDatabase.db'):
            db = open_sqlite_db_readonly(file_found)
            #SQL QUERY TIME!
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(json_extract(MessageEntity.value, '$.dateCreated')/1000, 'unixepoch') as Date_Created,
            json_extract(MessageEntity.value, '$.contactPhoneNumber') as Contact,
            json_extract(MessageEntity.value, '$.message') as Message,
            CASE json_extract(MessageEntity.value, '$.direction') 
                WHEN 1 THEN 'Incoming'
                WHEN 2 THEN 'Outgoing'
                ELSE 'Unknown'
            END as Direction,
            CASE json_extract(MessageEntity.value, '$.read')
                WHEN 1 THEN 'True'
                WHEN 0 THEN 'False'
                ELSE 'Unknown'
            END as Read
            FROM MessageEntity
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
               
                    data_list.append((row[0],row[1],row[2],row[3],row[4]))
            db.close()
                    
        else:
            continue
        
    if data_list:
        description = 'Burner: Second Phone Number'
        report = ArtifactHtmlReport('Burner Messages')
        report.start_artifact_report(report_folder, 'Burner Messages', description)
        report.add_script()
        data_headers = ('Timestamp','Contact','Message Text','Direction','Read Status')
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Burner Messages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Burner Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No Burner data available')
