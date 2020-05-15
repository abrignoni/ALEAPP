import glob
import json
import os
import shutil
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_accounts_ce_authtokens(files_found, report_folder, seeker):

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
            process_accounts_ce_authtokens(file_found, uid, report_folder)
        except ValueError:
                pass # uid was not a number

def process_accounts_ce_authtokens(folder, uid, report_folder):
    
    #Query to create report
    db = sqlite3.connect(folder)
    cursor = db.cursor()

    #Query to create report
    cursor.execute('''
    SELECT
        accounts._id,
        accounts.name,
        accounts.type,
        authtokens.type,
        authtokens.authtoken
    FROM accounts, authtokens
    WHERE
        accounts._id = authtokens.accounts_id
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Authokens')
        report.start_artifact_report(report_folder, f'Authtokens_{uid}')
        report.add_script()
        data_headers = ('ID', 'Name', 'Account Type','Authtoken Type', 'Authtoken')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4]))
        report.write_artifact_data_table(data_headers, data_list, folder)
        report.end_artifact_report()
        
        tsvname = f'authtokens {uid}'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc(f'No Authtokens_{uid} data available')    
    db.close()