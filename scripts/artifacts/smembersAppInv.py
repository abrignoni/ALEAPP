import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_smembersAppInv(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(last_used / 1000, "unixepoch"),  
    display_name, 
    package_name, 
    system_app, 
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
        data_headers = ('Timestamp','Display Name','Package Name','System App?','Confidence Hash','SHA1','Classification' ) 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'samsung members - apps'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Samsung Members - Apps'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Samsung Members - Apps data available')
    
    db.close()

__artifacts__ = {
        "smembersAppInv": (
                "App Interaction",
                ('*/com.samsung.oh/databases/com_pocketgeek_sdk_app_inventory.db'),
                get_smembersAppInv)
}