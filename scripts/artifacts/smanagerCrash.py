import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_smanagerCrash(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(crash_time / 1000, "unixepoch"),
    package_name
    from crash_info
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung Smart Manager - Crash')
        report.start_artifact_report(report_folder, 'Samsung Smart Manager - Crash')
        report.add_script()
        data_headers = ('Timestamp','Package Name')
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'samsung smart manager - crash'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Samsung Smart Manager - Crash'
        timeline(report_folder, tlactivity, data_list, data_headers) 
    else:
        logfunc('No Samsung Smart Manager - Crash data available')
    
    db.close()

__artifacts__ = {
        "smanagerCrash": (
                "App Interaction",
                ('*/com.samsung.android.sm/databases/sm.db'),
                get_smanagerCrash)
}