import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen

def get_airGuard(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    device.lastSeen AS "Last Time Device Seen",
    beacon.receivedAt AS "Time (Local)",
    beacon.deviceAddress AS "Device MAC Address",
    beacon.longitude AS "Latitude",
    beacon.latitude as "Longitude",
    beacon.rssi AS "Signal Strength (RSSI)",
    device.firstDiscovery AS "First Time Device Seen",
    device.lastNotificationSent as "Last Time User Notified"
    FROM
    beacon
    LEFT JOIN device on device.address=beacon.deviceAddress
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('AirGuard AirTag Tracker')
        report.start_artifact_report(report_folder, 'AirGuard AirTag Tracker')
        report.add_script()
        data_headers = ('Last Time Device Seen','Time (Local)','Device MAC Address','Latitude','Longitude','Signal Strength (RSSI)','First Time Device Seen','Last Time User Notified') 
        data_headers_kml = ('Timestamp','Time (Local)','Device MAC Address','Latitude','Longitude','Signal Strength (RSSI)','First Time Device Seen','Last Time User Notified') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'AirGuard AirTag Tracker'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'AirGuard AirTag Tracker'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        kmlactivity = 'AirGuard AirTag Tracker'
        kmlgen(report_folder, kmlactivity, data_list, data_headers_kml)
        
    else:
        logfunc('No AirGuard AirTag Tracker data available')
        
    db.close()

__artifacts__ = {
        "AirGuard": (
                "AirTags",
                ('*/de.seemoo.at_tracking_detection.release/databases/attd_db'),
                get_airGuard)
}