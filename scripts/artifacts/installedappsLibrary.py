import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc 

def get_installedappsLibrary(files_found, report_folder):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        account,
        doc_id,
        case
        when purchase_time = 0 THEN ''
        when purchase_time > 0 THEN datetime(purchase_time / 1000, "unixepoch")
        END as pt
    FROM
    ownership  
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Installed Apps (Library)')
        report.start_artifact_report(report_folder, 'Installed Apps (Library)')
        report.add_script()
        data_headers = ('Account', 'Doc ID', 'Purchase Time')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Installed Apps (Library) data available')
    
    db.close()
    return