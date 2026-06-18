# pylint: disable=W0611,W0613,W0631
__artifacts_v2__ = {
    "get_meetmechats": {
        "name": "MeetMe Chats",
        "description": "Parses MeetMe Chat database",
        "author": "Matt Beers",
        "creation_date": "2024-12-27",
        "last_update_date": "2024-12-27",
        "requirements": "none",
        "category": "Chats",
        "notes": "",
        "paths": ('*/data/com.myyearbook.m/databases/chats.db*'),
        "output_types": None,
        "artifact_icon": "users",
        "function": "get_meetmechats",
    }
}

#Update line 3-13
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_meetmechats(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('chats.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT 
            messages.sent_at,
            messages.thread_id,
            members.first_name,
            members.last_name,
            messages.sent_by,
            messages.body,
            messages.type,
            messages.local_path
            FROM 
            messages
            LEFT JOIN 
            members
            ON 
            members.member_id = messages.sent_by
            ORDER BY 
            messages.thread_id, 
            messages.sent_at;
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
                
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
            db.close()
                    
        else:
            continue
        
    if data_list:
        description = 'MeetMe Chats' 
        report = ArtifactHtmlReport('MeetMe Chats')
        report.start_artifact_report(report_folder, 'MeetMe Chats', description)
        report.add_script()
        data_headers = ('Timestamp','Thread ID','First Name','Last Name','Sent By','Message Text','Type','Attachment Path') 
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'MeetMe Chats'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'MeetMe Chats'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No MeetMe data available')
