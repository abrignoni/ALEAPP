import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_smembersEvents(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select 
    datetime(created_at /1000, "unixepoch"), 
    type, 
    value,
    in_snapshot
    FROM device_events
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung Members - Events')
        report.start_artifact_report(report_folder, 'Samsung Members - Events')
        report.add_script()
        data_headers = ('Created At','Type','Value','Snapshot?' )
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'samsung members - events'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Samsung Members - Events'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Samsung Members - Events data available')
    
    db.close()

__artifacts__ = {
        "smembersEvents": (
                "App Interaction",
                ('*/com.samsung.oh/databases/com_pocketgeek_sdk.db'),
                get_smembersEvents)
}