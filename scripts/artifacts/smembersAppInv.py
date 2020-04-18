import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_smembersAppInv(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select 
    display_name, 
    package_name, 
    system_app, 
    datetime(last_used / 1000, "unixepoch"), 
    confidence_hash,
    sha1,
    classification
    from android_app
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung Members - Apps')
        report.start_artifact_report(report_folder, 'Samsung Members - Apps')
        report.add_script()
        data_headers = ('Display Name','Package Name','System App?','Timestamp','Confidence Hash','SHA1','Classification' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Samsung Members - Apps data available')
    
    db.close()
    return