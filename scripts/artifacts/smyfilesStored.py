import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_smyfilesStored(files_found, report_folder, seeker, text_wrap):
    
    file_found = str(files_found[0])
    try:
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(date / 1000, "unixepoch"),
        storage,
        path,
        size,
        datetime(latest /1000, "unixepoch")
        from FileCache
        where path is not NULL 
        ''')
    
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
    
    try:
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
            datetime(date_modified / 1000, "unixepoch"),
            storage,
            _data,
            size,
            datetime(latest /1000, "unixepoch")
            from FileCache
            where _data is not NULL 
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    if usageentries > 0:
        report = ArtifactHtmlReport('My Files DB - Stored Files')
        report.start_artifact_report(report_folder, 'My Files DB - Stored Files')
        report.add_script()
        data_headers = ('Timestamp','Storage','Path','Size','Latest' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'my files db - stored files'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'My Files DB - Stored Files'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No My Files DB Stored data available')
    
    db.close()

__artifacts__ = {
        "smyfilesStored": (
                "My Files",
                ('*/com.sec.android.app.myfiles/databases/FileCache.db*'),
                get_smyfilesStored)
}