import sqlite3
import os
import textwrap
import blackboxprotobuf

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen

def get_airtagAndroid(files_found, report_folder, seeker, wrap_text):
    
    
    for file_found in files_found:
        file_name = str(file_found)
        if not file_found.endswith('personalsafety_db'):
            continue # Skip all other files
            
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        Select 
        macAddress,
        deviceType,
        optionalDeviceData,
        datetime(creationTimestampMillis/1000, 'unixepoch'),
        datetime(lastUpdatedTimestampMillis/1000, 'unixepoch'),
        alertLifecycleId,
        alertStatus from DeviceData
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Android Airtag Alerts')
            report.start_artifact_report(report_folder, 'Android Airtag Alerts')
            report.add_script()
            data_headers = ('Timestamp','Last Updated Timestamp','MAC Address','Device Type','Optional Device Data','Alert Life Cycle ID','Alert Status')
            data_list = []
            for row in all_rows:
                data_list.append((row[3],row[4],row[0],row[1],row[2],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Android Airtag Alerts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Android Airtag Alerts'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Android Airtag Alerts data available')
        
        cursor.execute('''
        Select 
        macAddress,
        datetime(creationTimestampMillis/1000, 'unixepoch'),
        datetime(lastUpdatedTimestampMillis/1000, 'unixepoch'),
        state,
        blescan,
        locationScan from Scan
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Android Airtag Scans')
            report.start_artifact_report(report_folder, 'Android Airtag Scans')
            report.add_script()
            data_headers = ('Timestamp','Last Updated Timestamp','MAC Address','State','Possible RSSI','Latitude','Longitude')
            data_list = []
            for row in all_rows:
                blescanproto, types = blackboxprotobuf.decode_message(row[4])
                posrssi = (blescanproto['2'])
                
                locationscanproto, types = blackboxprotobuf.decode_message(row[5])
                latitude = (locationscanproto['4']/1e7)
                longitude = (locationscanproto['5']/1e7)
                
                data_list.append((row[1],row[2],row[0],row[3],posrssi,latitude,longitude))
                
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Android Airtag Scans'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            kmlactivity = 'Android Airtag Scans'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)
            
            tlactivity = f'Android Airtag Scans'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Android Scans data available')
        
        
        db.close()

__artifacts__ = {
        "airtag alerts": (
                "Airtag Detection",
                ('*/com.google.android.gms/databases/personalsafety_db*'),
                get_airtagAndroid)
}