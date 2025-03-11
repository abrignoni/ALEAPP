import sqlite3
import os
import textwrap
import blackboxprotobuf
import datetime

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
    
    for file_found in files_found:
        file_name = str(file_found)
        if not file_found.endswith('personalsafety_info.pb'):
            continue # Skip all other files
        
        with open(file_found, 'rb') as f:
            protodata = f.read()
            
        lastscan, types = blackboxprotobuf.decode_message(protodata)
        lastscan = (lastscan['1'])
        lastscan = (datetime.datetime.utcfromtimestamp(int(lastscan)/1000).strftime('%Y-%m-%d %H:%M:%S'))
        
        report = ArtifactHtmlReport('Android Airtag Last Scan')
        report.start_artifact_report(report_folder, 'Android Airtag Last Scan')
        report.add_script()
        data_headers = ('Timestamp',)
        data_list = []
        
        data_list.append((lastscan,))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Android Airtag Last Scan'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Android Airtag Last Scan'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    for file_found in files_found:
        file_name = str(file_found)
        if not file_found.endswith('personalsafety_optin.pb'):
            continue # Skip all other files
        
        with open(file_found, 'rb') as f:
            protodata = f.read()
            
        passscan, types = blackboxprotobuf.decode_message(protodata)
        passscan = (passscan['1'])
        
        if passscan == 1:
            passscan = 'On'
        elif passscan == 2:
            passscan = 'Off'
        
        report = ArtifactHtmlReport('Android Airtag Passive Scan')
        report.start_artifact_report(report_folder, 'Android Airtag Passive Scan')
        report.add_script()
        data_headers = ('Passive Scan',)
        data_list = []
        
        data_list.append((passscan,))
        
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Android Airtag Passive Scan'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Android Airtag Passive Scan'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
            
__artifacts__ = {
        "airtag alerts": (
                "Airtag Detection",
                ('*/com.google.android.gms/databases/personalsafety_db*','*/files/personalsafety/shared/personalsafety_info.pb','*/files/personalsafety/shared/personalsafety_optin.pb'),
                get_airtagAndroid)
}