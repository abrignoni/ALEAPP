import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_smyfilesRecents(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.db'):
            break
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    try:
        cursor.execute('''
        select
        datetime(date_modified / 1000, "unixepoch"),
        name,
        size,
        _data,
        ext,
        _source,
        _description,
        datetime(recent_date / 1000, "unixepoch")
        from recent_files 
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0    
        
    if usageentries > 0:
        report = ArtifactHtmlReport('My Files DB - Recent Files')
        report.start_artifact_report(report_folder, 'My Files DB - Recent Files')
        report.add_script()
        data_headers = ('Timestamp','Name','Size','Data','Ext.', 'Source', 'Description', 'Recent Timestamp' ) 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'my files db - recent files'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'My Files DB - Recent Files'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No My Files DB Recents data available')
    
    try:
        cursor.execute('''
        SELECT
        datetime (recent_files.recent_date/1000, "unixepoch") as "Recent Date",
        datetime(recent_files.date_modified/1000, "unixepoch") as "Recent Files",
        recent_files.file_id as "File ID",
        recent_files.package_name as "Package Name",
        recent_files.path as "Path",
        recent_files.size as "Size",
        case recent_files.is_download
            WHEN '1' THEN "True"
            WHEN '0' THEN "False"
        end "Downloaded?",
        case recent_files.is_hidden
            WHEN '1' THEN "True"
            WHEN '0' THEN "False"
        end "Hidden",
        case recent_files.is_trashed
            WHEN '1' then  "True"
            when '0' then "False"
        end "Trashed"
        from recent_files
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0    
        
    if usageentries > 0:
        report = ArtifactHtmlReport('My Files DB - Recent Files')
        report.start_artifact_report(report_folder, 'My Files DB - Recent Files')
        report.add_script()
        data_headers = ('Recent Timestamp','Modified Timestamp','File ID','Package Name','Path', 'Size', 'Is Downloaded?', 'Is Hidden?','Is Trashed?' ) 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'my files db - recent files'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'My Files DB - Recent Files'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No My Files DB Recents data available')
    
    db.close()

__artifacts__ = {
        "smyfilesRecents": (
                "My Files",
                ('*/com.sec.android.app.myfiles/databases/myfiles.db*','*/com.sec.android.app.myfiles/databases/FileInfo.db*'),
                get_smyfilesRecents)
}