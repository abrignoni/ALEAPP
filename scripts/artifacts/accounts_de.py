import glob
import json
import os
import shutil
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_accounts_de(files_found, report_folder, seeker):

    slash = '\\' if is_platform_windows() else '/' 

    # Filter for path xxx/yyy/system_ce/0
    for file_found in files_found:
        file_found = str(file_found)
        parts = file_found.split(slash)
        uid = parts[-2]
        try:
            uid_int = int(uid)
            # Skip sbin/.magisk/mirror/data/system_de/0 , it should be duplicate data??
            if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
                continue
            process_accounts_de(file_found, uid, report_folder)
        except ValueError:
                pass # uid was not a number

def process_accounts_de(folder, uid, report_folder):
    
    #Query to create report
    db = open_sqlite_db_readonly(folder)
    cursor = db.cursor()

    #Query to create report
    cursor.execute('''
    SELECT
        datetime(last_password_entry_time_millis_epoch / 1000, 'unixepoch') as 'last pass entry',
        name,
        type
        FROM
    accounts
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Accounts_de')
        report.start_artifact_report(report_folder, f'accounts_de_{uid}')
        report.add_script()
        data_headers = ('Last password entry','Name','Type')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2]))
        report.write_artifact_data_table(data_headers, data_list, folder)
        report.end_artifact_report()
        
        tsvname = f'accounts de {uid}'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Accounts DE {uid}'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc(f'No accounts_de_{uid} data available')    
    db.close()