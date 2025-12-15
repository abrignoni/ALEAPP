# Samsung SmartThings
# Author: Kevin Pagano (@KevinPagno3)
# Date: 2022-06-13
# Artifact version: 0.0.1
# Requirements: none

import sqlite3
import textwrap
import scripts.artifacts.artGlobals

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_samsungSmartThings(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('QcDb.db'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(timeStamp/1000,'unixepoch'),
        deviceName,
        deviceType,
        netType,
        wifiP2pMac,
        btMac,
        bleMac
        from devices
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Samsung SmartThings - Quick Connect')
            report.start_artifact_report(report_folder, 'Samsung SmartThings - Quick Connect')
            report.add_script()
            data_headers = ('Connection Timestamp','Device Name','Device Type','Net Type','Wifi P2P MAC','Bluetooth MAC','Bluetooth (LE) MAC') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Samsung SmartThings - Quick Connect'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Samsung SmartThings - Quick Connect'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Samsung SmartThings - Quick Connect data available')
        
        db.close()
        
__artifacts__ = {
        "samsungSmartThings": (
                "Samsung SmartThings",
                ('*/com.samsung.android.oneconnect/databases/QcDB.db*'),
                get_samsungSmartThings)
}
