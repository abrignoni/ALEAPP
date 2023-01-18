import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_fitbitDevices(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if not file_found.endswith('device_database'):
            continue # Skip all other files
        
        data_list =[]
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(core_device.lastsynctime/1000, 'unixepoch') AS "Device Last Sync (UTC)",
        core_device.deviceName AS "Device Name",
        core_device.bleMacAddress AS "Bluetooth MAC Address",
        core_device.batteryPercent AS "Battery Percent",
        core_device.deviceType AS "Device Type"
        FROM core_device
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Fitbit Device Info')
            report.start_artifact_report(report_folder, 'Fitbit Device Info')
            report.add_script()
            data_headers = ('Last Synced Timestamp','Device Name','Bluetooth MAC Address','Battery Percentage','Device Type') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4]))
                
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Fitbit Device Info'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Fitbit Device Info'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Fitbit Device Info data available')
            
__artifacts__ = {
        "FitbitDevices": (
                "Fitbit",
                ('*/com.fitbit.FitbitMobile/databases/device_database*'),
                get_fitbitDevices)
}