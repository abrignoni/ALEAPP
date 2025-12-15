import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Zapya(files_found, report_folder, seeker, wrap_text):
    file_found = str(files_found[0])
    source_file = file_found.replace(seeker.data_folder, '')
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT device, name, direction, createtime/1000, path, title FROM transfer
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Zapya')
        report.start_artifact_report(report_folder, 'Zapya')
        report.add_script()
        data_headers = ('Device','Name','direction', 'fromid', 'toid', 'createtime','path', 'title') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
                        
        for row in all_rows:
            from_id = ''
            to_id = ''
            if (row[2] == 1):
                direction = 'Outgoing'
                to_id = row[0]
            else:
                direction = 'Incoming'
                from_id = row[0]
            
            createtime = datetime.datetime.utcfromtimestamp(int(row[3])).strftime('%Y-%m-%d %H:%M:%S')            
            data_list.append((row[0], row[1], direction, from_id, to_id, createtime, row[4], row[5]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Zapya'
        tsv(report_folder, data_headers, data_list, tsvname, source_file)
        
        tlactivity = f'Zapya'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Zapya data available')
    
    db.close()

__artifacts__ = {
        "Zapya": (
                "File Transfer",
                ('*/com.dewmobile.kuaiya.play/databases/transfer20.db*'),
                get_Zapya)
}