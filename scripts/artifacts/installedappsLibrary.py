import sqlite3
from pathlib import Path

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

def get_installedappsLibrary(files_found, report_folder, seeker, wrap_text):
    
    
    for file_found in files_found:
        file_name = str(file_found)
        fullpath = Path(file_found)
        user = fullpath.parts[-4]
        if user == 'data':
            user = '0'
        if file_found.endswith('library.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
                case
                when purchase_time = 0 THEN ''
                when purchase_time > 0 THEN datetime(purchase_time / 1000, "unixepoch")
                END as pt,
                account,
                doc_id
            FROM
            ownership  
            ''')
        
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport(f'Installed Apps (Library) for user {user}')
                report.start_artifact_report(report_folder, f'Installed Apps (Library) for user {user}')
                report.add_script()
                data_headers = ('Purchase Time', 'Account', 'Doc ID')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2]))
        
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'installed apps library for user {user}'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Installed Apps Library for user {user}'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc(f'No Installed Apps (Library) data available for user {user}')
            
    db.close()

__artifacts__ = {
        "InstalledappsLibrary": (
                "Installed Apps",
                ('*/com.android.vending/databases/library.db*'),
                get_installedappsLibrary)
}