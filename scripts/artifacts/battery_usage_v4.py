import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_battery_usage_v4(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_name = str(file_found)
    
        if file_name.endswith('battery-usage-db-v4'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(timestamp/1000,'unixepoch'),
            appLabel,
            packageName,
            case isHidden
                when 0 then ''
                when 1 then 'Yes'
            end,
            datetime((timestamp-bootTimestamp)/1000,'unixepoch'),
            zoneId,
            totalPower,
            consumePower,
            percentOfTotal,
            foregroundUsageTimeInMs*.001 as 'Foreground Usage (Seconds)',
            backgroundUsageTimeInMs*.001 as 'Background Usage (Seconds)',
            batteryLevel,
            case BatteryStatus
                when 2 then 'Charging'
                when 3 then 'Not Charging'
                when 5 then 'Fully Charged'
            end,
            batteryHealth
            from BatteryState
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],file_found))
            
            db.close()
        else:
            continue # Skip all other files (-shm, -wal, etc.)
    
    if data_list:
        description = 'This is battery usage details pulled from Settings Services'
        report = ArtifactHtmlReport('Settings Services - Battery Usage')
        report.start_artifact_report(report_folder, 'Settings Services - Battery Usage', description)
        report.add_script()
        data_headers = ('Timestamp','Application','Package Name','Hidden','Boot Timestamp','Timezone','Total Power','Consumed Power','% Of Consumed','Foreground Usage (Seconds)','Background Usage (Seconds)','Battery Level (%)','Battery Status','Source File') 

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Settings Services - Battery Usage'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Settings Services - Battery Usage'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Settings Services - Battery Usage data available')

__artifacts__ = {
        "battery_usage_v4": (
                "Settings Services",
                ('*/com.google.android.settings.intelligence/databases/battery-usage-db-v4*'),
                get_battery_usage_v4)
}