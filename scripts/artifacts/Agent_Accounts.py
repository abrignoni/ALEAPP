import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_Agent_Accounts(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        data._id,
        data.account_name,
        data.account_type
    FROM data
    ORDER BY 
        data._id ASC
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Agent_Accounts')
        report.start_artifact_report(report_folder, 'Agent_Accounts')
        report.add_script()
        data_headers = ('ID', 'Account', 'Type' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Agent_Accounts'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Agent_Accounts data available')
    
    db.close()
    return

