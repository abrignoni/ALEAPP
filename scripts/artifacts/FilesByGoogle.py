__artifacts_v2__ = {
    "FilesByGoogle": {
        "name": "Files By Google",
        "description": "Parses the Files by Google application",
        "author": "@KevinPagano3",
        "version": "0.0.3",
        "date": "2021-01-18",
        "requirements": "none",
        "category": "Files By Google",
        "notes": "",
        "paths": ('*/com.google.android.apps.nbu.files/databases/files_master_database*','*/com.google.android.apps.nbu.files/databases/search_history_database*'),
        "function": "get_FilesByGoogle"
    }
}

import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_FilesByGoogle(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list_master = []
    data_list_search = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        # Master list
        if file_found.endswith('files_master_database'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
                case file_date_modified_ms
                    when 0 then ''
                    else datetime(file_date_modified_ms/1000,'unixepoch')
                end as file_date_modified_ms,
                root_path,
                root_relative_file_path,
                file_name,
                size,
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
                for row in all_rows:
                    data_list_master.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],file_found))
            db.close()
            
        # Search History
        if file_found.endswith('search_history_database'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
                searched_term,
                case timestamp
                    when 0 then ''
                    else datetime(timestamp/1000,'unixepoch')
                end as timestamp
            from search_history_content
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    data_list_search.append((row[0],row[1],file_found))
            db.close()
            
        else:
            continue # Skip all other files
            
    # Master report
    if data_list_master:    
        report = ArtifactHtmlReport('Files by Google - Files Master')
        report.start_artifact_report(report_folder, 'Files by Google - Files Master')
        report.add_script()
        data_headers = ('Date Modified','Root Path','Root Relative Path','File Name','Size','Mime Type','Media Type','URI','Hidden','Title','Parent Folder','Source') # Don't remove the comma, that is required to make this a tuple as there is only 1 element

        report.write_artifact_data_table(data_headers, data_list_master, file_found)
        report.end_artifact_report()
        
        tsvname = f'Files By Google - Files Master'
        tsv(report_folder, data_headers, data_list_master, tsvname)
        
        tlactivity = f'Files By Google - Files Master'
        timeline(report_folder, tlactivity, data_list_master, data_headers)

    else:
        logfunc('No Files By Google - Files Master data available')
        
    # Search History report
    if data_list_search:
        report = ArtifactHtmlReport('File by Google - Search History')
        report.start_artifact_report(report_folder, 'Files By Google - Search History')
        report.add_script()
        data_headers = ('Search Term','Timestamp') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        
        report.write_artifact_data_table(data_headers, data_list_search, file_found)
        report.end_artifact_report()
        
        tsvname = f'Files By Google - Search History'
        tsv(report_folder, data_headers, data_list_search, tsvname)
        
        tlactivity = f'Files By Google - Search History'
        timeline(report_folder, tlactivity, data_list_search, data_headers)