import os
import shutil
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_table_exist_in_db

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/' 

def get_rcs_db_path(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'mmssms.db': # skip -journal and other files
            continue
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??
        return file_found
    return ''

def get_offline_path(files_found, blob_name):
    #offline_path_relative = "/files/shiny_blobs/blobs"
    for file_found in files_found:
        if file_found.endswith(blob_name):
            file_found = str(file_found)
            return file_found
    return ''

def get_lgRCS(files_found, report_folder, seeker, wrap_text):
    file_found = get_rcs_db_path(files_found)
    if not file_found:
        logfunc('Error: Could not get RCS chat database path for LG phones')
        return

    if report_folder[-1] == slash: 
        folder_name = os.path.basename(report_folder[:-1])
    else:
        folder_name = os.path.basename(report_folder)

    db = open_sqlite_db_readonly(file_found)
    if not does_table_exist_in_db(file_found, 'message'):
        logfunc('No RCS data in this db, \'message\' table is absent!')
        return
    cursor = db.cursor()
    cursor.execute('''
    SELECT 
        CASE WHEN date>0 THEN datetime(date/1000, 'UNIXEPOCH')
            ELSE ""
        END as date,
        address, 
        body,
        read,
        message.thread_id, 
        is_file,
        file_name,
        file_path,
        file_size,
        thumb_file_path,
        thumb_file_size,
        file_xml_path
    FROM message
    left join file_info on  message.message_id = file_info.message_id
    ORDER BY date
        ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('RCS Chats')
        report.start_artifact_report(report_folder, 'RCS')
        report.add_script()
        data_headers = ('Date','Address','Body','Read?','Thread ID','Is File?','Filename','File Path','File Size','Thumb File Path','Thumb File Size','File XML Path')
        data_list = []
        tsv_list = []
        
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],))
        

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'RCS Chats - LG'
        tsv(report_folder, data_headers, tsv_list, tsvname)
        
        tlactivity = f'RCS Chats - LG'
        timeline(report_folder, tlactivity, tsv_list, data_headers)
    else:
        logfunc('No RCS Chats - LG data available')
    
    db.close()

__artifacts__ = {
        "lgRCS": (
                "RCS Chats",
                ('*/mmssms.db*'),
                get_lgRCS)
}
