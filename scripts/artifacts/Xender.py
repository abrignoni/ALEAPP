import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Xender(files_found, report_folder, seeker, wrap_text):

    source_file = ''

    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('-db'):
            source_file = file_found.replace(seeker.data_folder, '')
            break
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT device_id, nick_name FROM profile WHERE connect_times = 0
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Xender file transfer - contacts')
        report.start_artifact_report(report_folder, 'Xender file transfer - contacts')
        report.add_script()
        data_headers = ('device_id','nick_name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Xender file transfer - contacts'
        tsv(report_folder, data_headers, data_list, tsvname, source_file)
        
    else:
        logfunc('No Xender Contacts found')
        
    try:        
        cursor.execute('''
        SELECT f_path, f_display_name, f_size_str, c_start_time/1000, c_direction, c_session_id, s_name, 
               s_device_id, r_name, r_device_id
          FROM new_history
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Xender file transfer - Messages')
        report.start_artifact_report(report_folder, 'Xender file transfer - Messages')
        report.add_script()
        data_headers = ('file_path','file_display_name','file_size','timestamp','direction', 'to_id', 'from_id','session_id', 'sender_name', 'sender_device_id', 'recipient_name', 'recipient_device_id') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            from_id = ''
            to_id = ''
            if (row[4] == 1):
                direction = 'Outgoing'
                to_id = row[6]
            else:
                direction = 'Incoming'
                from_id = row[6]
                
            createtime = datetime.datetime.utcfromtimestamp(int(row[3])).strftime('%Y-%m-%d %H:%M:%S') 
                        
            data_list.append((row[0], row[1], row[2], createtime, direction, to_id, from_id, row[5], row[6], row[7], row[8], row[9]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Xender file transfer - Messages'
        tsv(report_folder, data_headers, data_list, tsvname, source_file)
        
        tlactivity = f'Xender file transfer - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Xender file transfer messages data available')

    db.close()

__artifacts__ = {
        "Xender": (
                "File Transfer",
                ('*/cn.xender/databases/trans-history-db*'),
                get_Xender)
}