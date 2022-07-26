import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_smanagerLow(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT 
    datetime(start_time /1000, "unixepoch"),
    datetime(end_time /1000, "unixepoch"),
    id,
    package_name,
    uploaded,
    datetime(created_at /1000, "unixepoch"),
    datetime(modified_at /1000, "unixepoch")
    from usage_log
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung Smart Manager - Usage')
        report.start_artifact_report(report_folder, 'Samsung Smart Manager - Usage')
        report.add_script()
        data_headers = ('Start Time','End Time','ID','Package Name', 'Uploaded?', 'Created', 'Modified' )
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'samsung smart manager - usage'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Samsung Smart Manager - Usage'
        timeline(report_folder, tlactivity, data_list, data_headers) 
    else:
        logfunc('No Samsung Smart Manager - Usage data available')
    
    db.close()

__artifacts__ = {
        "smanagerLow": (
                "App Interaction",
                ('*/com.samsung.android.sm/databases/lowpowercontext-system-db'),
                get_smanagerLow)
}