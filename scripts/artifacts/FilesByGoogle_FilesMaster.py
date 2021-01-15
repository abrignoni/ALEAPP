import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_FilesByGoogle_FilesMaster(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
        root_path,
        root_relative_file_path,
        file_name,
        size,
        case file_date_modified_ms
            when 0 then ''
            else datetime(file_date_modified_ms/1000,'unixepoch')
        end as file_date_modified_ms,
        mime_type,
        case media_type
            when 0 then 'App/Data'
            when 1 then 'Picture'
            when 2 then 'Audio'
            when 3 then 'Video'
            when 6 then 'Text'
        end as media_type,
        uri,
        case is_hidden
            when 0 then ''
            when 1 then 'Yes'
        end as is_hidden,
        title,
        parent_folder_name
    from files_master_table
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Files by Google - Files Master')
        report.start_artifact_report(report_folder, 'Files by Google - Files Master')
        report.add_script()
        data_headers = ('Root Path','Root Relative Path','File Name','Size','Date Modified','Mime Type','Media Type','URI','Hidden','Title','Parent Folder') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Files By Google - Files Master'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Files By Google - Files Master'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Files By Google - Files Master data available')
    
    db.close()
    return
