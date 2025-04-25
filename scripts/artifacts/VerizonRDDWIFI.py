# Module Description: Parses Verizon RDD Wifi Data
# Author: John Hyla
# Date: 2023-07-07
# Artifact version: 0.0.1
# Requirements: none

import os
import sqlite3
import datetime
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_rdd_wifi(files_found, report_folder, seeker, wrap_text):

    source_file = ''
    for file_found in files_found:
        file_name = str(file_found)

        db = open_sqlite_db_readonly(file_name)
        cursor = db.cursor()
        try:

            cursor.execute('''
                SELECT datetime(timestamp/1000, "UNIXEPOCH") as timestamp, 
                eventid,
                event, 
                data
                  FROM TABLERDDWIFIDATA
                  ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except Exception as e:
            print (e)
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('Verizon RDD - WIFI Data')
            report.start_artifact_report(report_folder, 'Verizon RDD - WIFI Data')
            report.add_script()
            data_headers = ('Timestamp', 'Event ID', 'Event', 'BSSID', 'SSID', 'IP', 'SessionTime', 'DataTx', 'DataRx', 'Cell ID') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []

            for row in all_rows:
                json_data = json.loads(row[3])
                data_list.append((row[0], row[1], row[2], json_data.get('wifiinfo').get('bssid'), json_data.get('wifiinfo').get('ssid'), json_data.get('returnedIP'), json_data.get('totalSessionTime'), json_data.get('sessionWifiTx'), json_data.get('sessionWifiRx'), json_data.get('cellId')))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Verizon RDD - WIFI Data'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)
            
        else:
            logfunc('No WIFI Data found')
            

        db.close()
    
    return


__artifacts__ = {
    "VerizonRDD-WIFI": (
        "Verizon RDD Analytics",
        ('*/com.verizon.mips.services/databases/RDD_WIFI_DATA_DATABASE'),
        get_rdd_wifi)
}