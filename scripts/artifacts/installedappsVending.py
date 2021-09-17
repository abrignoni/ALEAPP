import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_column_exist_in_db

def get_installedappsVending(files_found, report_folder, seeker, wrap_text):

    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    
    if does_column_exist_in_db(db, 'appstate','install_reason') == True:
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
        report = ArtifactHtmlReport('Installed Apps (Vending)')
        report.start_artifact_report(report_folder, 'Installed Apps (Vending)')
        report.add_script()
        data_headers = ('First Download','Package Name', 'Title', 'Install Reason', 'Last Updated', 'Auto Update?', 'Account')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'installed apps vending'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Installed Apps Vending'
        timeline(report_folder, tlactivity, data_list, data_headers)        
    else:
            logfunc('No Installed Apps data available')
    
    db.close()
    return