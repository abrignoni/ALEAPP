import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_smyFiles(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.db'):
            break
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    try:
        cursor.execute('''
        select 
        datetime(mDate / 1000, 'unixepoch'),
        mName,
        mFullPath,
        mIsHidden,
        mTrashed,
        _source,
        _description,
        _from_s_browser
        from download_history
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('My Files DB - Download History')
        report.start_artifact_report(report_folder, 'My Files DB - Download History')
        report.add_script()
        data_headers = ('Timestamp','Name','Full Path','Is Hidden','Trashed?', 'Source', 'Description', 'From S Browser?' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'My Files db - Download History'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'My Files DB - Download History'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No My Files DB Download History data available')
        
    try:
        cursor.execute('''
        select 
        datetime(date / 1000, 'unixepoch'),
        name,
        size,
        _data,
        _source,
        _description,
        _from_s_browser
        from download_history
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('My Files DB - Download History')
        report.start_artifact_report(report_folder, 'My Files DB - Download History')
        report.add_script()
        data_headers = ('Timestamp','Name','Size','Data','Source', 'Description', 'From S Browser?' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'My Files db - Download History'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'My Files DB - Download History'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No My Files DB Download History pre-Android 12 data available')
        
    try:        
        cursor.execute('''
        select 
        datetime(mDate / 1000, 'unixepoch'),
        mName,
        mFullPath,
        mIsHidden,
        mTrashed,
        _source,
        _description,
        _from_s_browser
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
        data_headers = ('Timestamp','Name','Full Path','Is Hidden','Trashed?', 'Source', 'Description', 'From S Browser?' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'My Files db - Recent Files'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'My Files DB - Recent Files'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No My Files DB Recent Files data available')

    db.close()

__artifacts__ = {
        "smyFiles": (
                "My Files",
                ('*/com.sec.android.app.myfiles/databases/MyFiles*.db*','*/com.sec.android.app.myfiles/databases/myfiles.db*'),
                get_smyFiles)
}