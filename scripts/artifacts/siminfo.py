import glob
import json
import os
import shutil
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, logdevinfo, is_platform_windows, open_sqlite_db_readonly

def get_siminfo(files_found, report_folder, seeker, wrap_text):

    slash = '\\' if is_platform_windows() else '/' 
    # Filter for path xxx/yyy/system_ce/0
    for file_found in files_found:
        file_found = str(file_found)
        parts = file_found.split(slash)
        uid = parts[-4]
        try:
            uid_int = int(uid)
            # Skip sbin/.magisk/mirror/data/system_de/0 , it should be duplicate data??
            if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
                continue
            process_siminfo(file_found, uid, report_folder)
        except ValueError:
                pass # uid was not a number

def process_siminfo(folder, uid, report_folder):
    
    #Query to create report
    db = open_sqlite_db_readonly(folder)
    cursor = db.cursor()

    #Query to create report
    try:
        cursor.execute('''
        SELECT
            number,
            imsi,
            display_name,
            carrier_name,
            iso_country_code,
            carrier_id,
            icc_id
        FROM
            siminfo
        ''')
    except:
        cursor.execute('''
        SELECT
            number,
            card_id,
            display_name,
            carrier_name,
            carrier_name,
            carrier_name,
            icc_id
        FROM
            siminfo
        ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Device Info')
        report.start_artifact_report(report_folder, f'SIM_info_{uid}')
        report.add_script()
        data_headers = ('Number', 'IMSI', 'Display Name','Carrier Name', 'ISO Code', 'Carrier ID', 'ICC ID')
        
        data_list = []
        for row in all_rows:
            if row[3] == row[4]:
                row1 = ''
                row4 = ''
                row5 = ''
            else:
                row1 = row[1]
                row4 = row[4]
                row5 = row[5]
            data_list.append((row[0], row1, row[2], row[3], row4, row5, row[6]))
            logdevinfo(f"<b>SIM Number & IMSI: </b>{row[0]} - {row1}")
            logdevinfo(f"<b>SIM Display Name: </b>{row[2]}")
        report.write_artifact_data_table(data_headers, data_list, folder)
        report.end_artifact_report()
        
        tsvname = f'Sim info {uid}'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc(f'No SIM_Info{uid} data available')    
    db.close()

__artifacts__ = {
        "siminfo": (
                "Device Info",
                ('*/user_de/*/com.android.providers.telephony/databases/telephony.db'),
                get_siminfo)
}