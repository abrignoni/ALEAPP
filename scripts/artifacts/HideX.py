import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

def get_HideX(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('hidex.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
                id,
                packageName,
                case isActive
                    WHEN 0 then ''
                    WHEN 1 then 'Yes'
                end
            FROM p_lock_app
            ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('HideX - Locked Apps')
        report.start_artifact_report(report_folder, 'HideX - Locked Apps')
        report.add_script()
        data_headers = ('ID','Package Name','Is Active') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'HideX'
        tsv(report_folder, data_headers, data_list, tsvname)

    else:
        logfunc('No HideX data available')
    
    db.close()

__artifacts__ = {
        "HideX": (
                "GroupMe",
                ('*/com.flatfish.cal.privacy/databases/hidex.db*'),
                get_HideX)
}
