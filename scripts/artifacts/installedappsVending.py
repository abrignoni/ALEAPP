import sqlite3
from pathlib import Path

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_column_exist_in_db

def get_installedappsVending(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_name = str(file_found)
        fullpath = Path(file_found)
        user = fullpath.parts[-4]
        if user == 'data':
            user = '0'
        if file_found.endswith('localappstate.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            if does_column_exist_in_db(file_found, 'appstate','install_reason') == True:
                install_reason_query = '''install_reason'''
            else:
                install_reason_query = "'' as install_reason"
        
            cursor.execute(f'''
            SELECT
            CASE first_download_ms
                WHEN '0' THEN '' 
                ELSE
                    datetime(first_download_ms / 1000, "unixepoch")
            END AS 'First_Download_DT',
            package_name,
            title,
            {install_reason_query},
            CASE last_update_timestamp_ms
                WHEN '0' THEN '' 
                ELSE
                    datetime(last_update_timestamp_ms / 1000, "unixepoch")
            END AS 'Last_Updated_DT',
            CASE auto_update
                WHEN '0' THEN ''
                WHEN '1' THEN 'Yes'
            END AS 'Auto_Updated',
            account
            FROM appstate  
            ''')
        
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport(f'Installed Apps (Vending) {user}')
                report.start_artifact_report(report_folder, f'Installed Apps (Vending) for user {user}')
                report.add_script()
                data_headers = ('First Download','Package Name', 'Title', 'Install Reason', 'Last Updated', 'Auto Update?', 'Account')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Installed Apps Vending {user}'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Installed Apps Vending {user}'
                timeline(report_folder, tlactivity, data_list, data_headers)        
            else:
                    logfunc(f'No Installed Apps data available for user {user}')
    
    db.close()

__artifacts__ = {
        "InstalledappsVending": (
                "Installed Apps",
                ('*/com.android.vending/databases/localappstate.db*'),
                get_installedappsVending)
}