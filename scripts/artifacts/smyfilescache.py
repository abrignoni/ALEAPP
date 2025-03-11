import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, media_to_html

def get_smyfilescache(files_found, report_folder, seeker, text_wrap):
    
    is_windows = is_platform_windows()
    splitter = '\\' if is_windows else '/'
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.db'):
            break
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT
        datetime(date_modified /1000, 'unixepoch'),
        _index,
        _data,
        size,
        datetime(latest /1000, 'unixepoch')
        from FileCache
        ''')
    
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        
        data_list = []
        for row in all_rows:
            thumb = media_to_html(splitter + str(row[1]) + '.jpg', files_found, report_folder)
            
            data_list.append((row[0], thumb, row[1], row[2], row[3], row[4]))
            
        report = ArtifactHtmlReport('My Files DB - Cache Media')
        report.start_artifact_report(report_folder, 'My Files DB - Cache Media')
        report.add_script()
        data_headers = ('Timestamp Modified','Media','Media Cache ID','Path','Size','Latest' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'My Files DB - Cache Media'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'My Files DB - Cache Media'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No My Files DB Stored data available')
    
    try:
        cursor.execute('''
        SELECT
        datetime(date /1000, 'unixepoch'),
        _index,
        path,
        size,
        datetime(latest /1000, 'unixepoch')
        from FileCache
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        
        data_list = []
        for row in all_rows:
            thumb = media_to_html(splitter + str(row[1]) + '.jpg', files_found, report_folder)
            
            data_list.append((row[0], thumb, row[1], row[2], row[3], row[4]))
            
        report = ArtifactHtmlReport('My Files DB - Cache Media')
        report.start_artifact_report(report_folder, 'My Files DB - Cache Media')
        report.add_script()
        data_headers = ('Timestamp Modified','Media','Media Cache ID','Path','Size','Latest' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'My Files DB - Cache Media'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'My Files DB - Cache Media'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No My Files DB Stored data available')
        
    
    db.close()

__artifacts__ = {
        "smyfilescache": (
                "My Files",
                ('*/com.sec.android.app.myfiles/databases/FileCache.db*','*/com.sec.android.app.myfiles/cache/*.*'),
                get_smyfilescache)
}