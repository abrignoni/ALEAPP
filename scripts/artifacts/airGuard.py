__artifacts_v2__ = {
    "AirGuard": {
        "name": "AirGuard",
        "description": "Parses the AirGuard AirTag app",
        "author": "@AlexisBrignoni",
        "version": "0.0.2",
        "date": "2022-01-08",
        "requirements": "none",
        "category": "AirTags",
        "notes": "",
        "paths": ('*/de.seemoo.at_tracking_detection.release/databases/attd_db*'),
        "function": "get_airGuard"
    }
}

import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen, does_table_exist_in_db, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_airGuard(files_found, report_folder, seeker, wrap_text):
    
    data_list_scans = []
    data_list_tracker = []
    
    for file_found in files_found:
        file_name = str(file_found)
        
        if file_found.endswith('attd_db'):
            db = open_sqlite_db_readonly(file_found)
            location_table_exists = does_table_exist_in_db(file_found, 'location')
            cursor = db.cursor()
            if location_table_exists:
                cursor.execute('''
                SELECT
                device.lastSeen AS "Last Time Device Seen",
                beacon.receivedAt AS "Time (Local)",
                beacon.deviceAddress AS "Device MAC Address",
                location.latitude AS "Latitude",
                location.longitude as "Longitude",
                beacon.rssi AS "Signal Strength (RSSI)",
                device.deviceType AS "Device Type",
                device.firstDiscovery AS "First Time Device Seen",
                device.lastNotificationSent as "Last Time User Notified"
                FROM
                beacon
                LEFT JOIN device on device.address = beacon.deviceAddress
                LEFT JOIN location on location.locationId = beacon.locationId
                ''')
            else:    
                cursor.execute('''
                SELECT
                device.lastSeen AS "Last Time Device Seen",
                beacon.receivedAt AS "Time (Local)",
                beacon.deviceAddress AS "Device MAC Address",
                beacon.latitude AS "Latitude",
                beacon.longitude as "Longitude",
                beacon.rssi AS "Signal Strength (RSSI)",
                device.deviceType AS "Device Type",
                device.firstDiscovery AS "First Time Device Seen",
                device.lastNotificationSent as "Last Time User Notified"
                FROM
                beacon
                LEFT JOIN device on device.address=beacon.deviceAddress
                ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    last_time_dev_seen = str(row[0]).replace("T", " ")
                    if last_time_dev_seen is None or last_time_dev_seen == 'None':
                        pass
                    else:
                        last_time_dev_seen = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_time_dev_seen),'UTC')
                    
                    time_local = str(row[1]).replace("T", " ")
                    if time_local is None or time_local == 'None':
                        pass
                    else:
                        time_local = convert_utc_human_to_timezone(convert_ts_human_to_utc(time_local),'UTC')
                    
                    first_time_dev_seen = str(row[7]).replace("T", " ")
                    if first_time_dev_seen is None or first_time_dev_seen == 'None':
                        pass
                    else:
                        first_time_dev_seen = convert_utc_human_to_timezone(convert_ts_human_to_utc(first_time_dev_seen),'UTC')
                        
                    last_time_user_notified = str(row[8]).replace("T", " ")
                    if last_time_user_notified is None or last_time_user_notified == 'None':
                        pass
                    else:
                        last_time_user_notified = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_time_user_notified),'UTC')

                    data_list_tracker.append((last_time_dev_seen,time_local,row[2],row[3],row[4],row[5],row[6],first_time_dev_seen,last_time_user_notified,file_found))
            
            cursor = db.cursor()
            cursor.execute('''   
            SELECT
            startDate,
            endDate,
            duration AS "Duration (Seconds)",
            noDevicesFound,
            CASE isManual
                WHEN 0 THEN 'No'
                WHEN 1 THEN 'Yes'
            END,
            scanMode
            FROM scan
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    start_scan_ts = str(row[0]).replace("T", " ")
                    if start_scan_ts is None or start_scan_ts == 'None':
                        pass
                    else:
                        start_scan_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(start_scan_ts),'UTC')
                    
                    end_scan_ts = str(row[1]).replace("T", " ")
                    if end_scan_ts is None or end_scan_ts == 'None':
                        pass
                    else:
                        end_scan_ts = convert_utc_human_to_timezone(convert_ts_human_to_utc(end_scan_ts),'UTC')
                    
                    data_list_scans.append((start_scan_ts,end_scan_ts,row[2],row[3],row[4],row[5],file_found))
            db.close()
  
        else:
            continue # Skip all other files
        
    if data_list_tracker:        
        report = ArtifactHtmlReport('AirGuard AirTag Tracker')
        report.start_artifact_report(report_folder, 'AirGuard AirTag Tracker')
        report.add_script()
        data_headers = ('Last Time Device Seen','Time (Local)','Device MAC Address','Latitude','Longitude','Signal Strength (RSSI)','Device Type','First Time Device Seen','Last Time User Notified','Source File')
        data_headers_kml = ('Timestamp','Time (Local)','Device MAC Address','Latitude','Longitude','Signal Strength (RSSI)','Device Type','First Time Device Seen','Last Time User Notified','Source File')
        
        report.write_artifact_data_table(data_headers, data_list_tracker, file_found)
        report.end_artifact_report()
        
        tsvname = f'AirGuard AirTag Tracker'
        tsv(report_folder, data_headers, data_list_tracker, tsvname)
        
        tlactivity = f'AirGuard AirTag Tracker'
        timeline(report_folder, tlactivity, data_list_tracker, data_headers)
        
        kmlactivity = 'AirGuard AirTag Tracker'
        kmlgen(report_folder, kmlactivity, data_list_tracker, data_headers_kml)
        
    else:
        logfunc('No AirGuard AirTag Tracker data available')
        
    if data_list_scans:
        report = ArtifactHtmlReport('AirGuard AirTag Scans')
        report.start_artifact_report(report_folder, 'AirGuard AirTag Scans')
        report.add_script()
        data_headers = ('Start Scan Timestamp','End Scan Timestamp','Duration (Seconds)','Devices Found','Manual Scan?','Scan Mode','Source File') 
        data_headers_kml = ('Timestamp','End Scan Timestamp','Duration (Seconds)','Devices Found','Manual Scan?','Scan Mode','Source File') 

        report.write_artifact_data_table(data_headers, data_list_scans, file_found)
        report.end_artifact_report()
        
        tsvname = f'AirGuard AirTag Scans'
        tsv(report_folder, data_headers, data_list_scans, tsvname)
        
        tlactivity = f'AirGuard AirTag Scans'
        timeline(report_folder, tlactivity, data_list_scans, data_headers)
        
    else:
        logfunc('No AirGuard AirTag Scans data available')