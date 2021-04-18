import sqlite3
import io
import json
import os
import shutil

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly

def get_googlePhotosCache(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('disk_cache'):
            break
    
    #file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    
    cursor.execute('''
    select
    datetime(last_modified_time/1000, 'unixepoch'),
    key,
    size,
    case pending_delete
        when 0 then ''
        when 1 then 'Yes'
    end
    from journal
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    
    if usageentries > 0:
        for row in all_rows:
        
            fileNameKey = row[1]
            thumb = ''
            
            for match in files_found:
                if fileNameKey in match:
                    shutil.copy2(match, report_folder)
                    data_file_name = os.path.basename(match)
                    thumb = f'<img src="{report_folder}/{data_file_name}" width="300"></img>'
                
            data_list.append((row[0],row[1],thumb,row[2],row[3]))
    
        report = ArtifactHtmlReport('Google Photos - Cache')
        report.start_artifact_report(report_folder, 'Google Photos - Cache')
        report.add_script()
        data_headers = ('Timestamp','Key','Image','Size','Pending Deletion')
        
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Image'])
        report.end_artifact_report()
        
        tsvname = f'Google Photos - Cache'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Photos - Cache'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Photos - Cache data available')
    
    db.close()
    return