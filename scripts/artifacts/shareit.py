import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_shareit(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('history.db'):
            break

    source_file = file_found.replace(seeker.data_folder, '')

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT case history_type when 1 then "Incoming" else "Outgoing" end direction,
               case history_type when 1 then device_id else null end from_id,
               case history_type when 1 then null else device_id end to_id,
               device_name, description, timestamp/1000 as timestamp, file_path
                                FROM history
                                JOIN item where history.content_id = item.item_id
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Shareit file transfer')
        report.start_artifact_report(report_folder, 'shareit file transfer')
        report.add_script()
        data_headers = ('direction','from_id', 'to_id', 'device_name', 'description', 'timestamp', 'file_path') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            timestamp = datetime.datetime.utcfromtimestamp(int(row[5])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((row[0], row[1], row[2], row[3], row[4], timestamp, row[6]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Shareit file transfer'
        tsv(report_folder, data_headers, data_list, tsvname, source_file)
                
        tlactivity = f'Shareit file transfer'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Shareit file transfer data available')

    db.close()

__artifacts__ = {
        "shareit": (
                "File Transfer",
                ('*/com.lenovo.anyshare.gps/databases/history.db*'),
                get_shareit)
}
