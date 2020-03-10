import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc

def get_installedappsVending(files_found, report_folder, seeker):

    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        package_name,
        title,
        datetime(first_download_ms / 1000, "unixepoch") as fdl,
        install_reason,
        auto_update
    FROM appstate  
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Installed Apps (Vending)')
        report.start_artifact_report(report_folder, 'Installed Apps (Vending)')
        report.add_script()
        data_headers = ('Package Name', 'Title', 'First Download', 'Install Reason', 'Auto Update?')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()        
    else:
            logfunc('No Installed Apps data available')
    
    db.close()
    return