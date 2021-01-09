import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Zapya(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT device, name, direction, createtime, path, title FROM transfer
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Zapya')
        report.start_artifact_report(report_folder, 'Zapya')
        report.add_script()
        data_headers = ('Device','Name','direction','createtime','path', 'title') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Zapya'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Zapya'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Zapya data available')
    
    db.close()
    return