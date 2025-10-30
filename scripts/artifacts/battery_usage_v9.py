# Android Settings Services -  Battery Usages v9 (com.android.settings)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.2
# 
# Tested with the following versions/devices:
# 2024-05-19: Android 14 - Fairphone3 and Fairphone 4


# Requirements: re, blackboxprotobuf

__artifacts_v2__ = {

    
    "battery_usage_v9": {
        "name": "Settings Services - Battery Usages v9 - Battery States",
        "description": "Getting Battery Usage data out of the database battery-usage-db-v9. Introduced with Android 14",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-05-12",
        "requirements": "re",
        "category": "Settings Services - Battery Usage v9 - Battery States",
        "notes": "Getting battery usage data from Settings Services - Android 14 - Based on post https://bebinary4n6.blogspot.com/2024/05/android-14-battery-usage-and-app-usage.html",
        "paths": ('*/user_de/*/com.android.settings/databases/battery-usage-db-v9'),
        "function": "get_battery_usage_v9"
    },
    "app_battery_usage_v9": {
        "name": "Settings Services - App Battery Usages v9 - App Battery Usage Events",
        "description": "Getting Battery Usage data out of the database battery-usage-db-v9. Introduced with Android 14",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-05-12",
        "requirements": "re",
        "category": "Settings Services - Battery Usage v9 - App Battery Usage Events",
        "notes": "Getting App Battery Usage Event from Settings Services - Based on https://bebinary4n6.blogspot.com/2024/05/android-14-battery-usage-and-app-usage.html",
        "paths": ('*/user_de/*/com.android.settings/databases/battery-usage-db-v9'),
        "function": "get_app_usage_events"
    }
}

import re
import blackboxprotobuf
import base64

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_battery_usage_v9(files_found, report_folder, seeker, wrap_text):
    
    data_headers = []
    data_list = []
    
    for file_found in files_found:
        file_name = str(file_found)
    
        if file_name.endswith('battery-usage-db-v9'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
                SELECT 
                    uid, 
                    packageName,  
                    DATETIME(timestamp/1000, 'unixepoch') AS timestamp, 
                    consumerType,
                    isFullChargeCycleStart, 
                    batteryInformation,
                    batteryInformationDebug
                    
                FROM BatteryState
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                
                for row in all_rows:
                    # we need to parse the column batteryInformationDebug - a lot of data is in here
                    battery_info_proto, types = blackboxprotobuf.decode_message(base64.b64decode(row[5]))
                    app_label = battery_info_proto['7']
                    is_hidden = battery_info_proto['2']
                    boot_timestamp = battery_info_proto['3'] / 1000
                    timezone = battery_info_proto['4']
                    total_power = 'NOVALUE'
                    consume_power = 'NOVALUE'
                    foreground = battery_info_proto['14'] / 1000
                    foreground_service = battery_info_proto['20'] / 1000
                    background = battery_info_proto['15'] / 1000
                    battery_level = battery_info_proto['1']['1']
                    match int(battery_info_proto['1']['2']):
                             case 2:
                                 battery_status= 'Charging'
                             case 3:
                                 battery_status = 'Discharging'
                             case 5:
                                 battery_status = 'Fully charged'
                             case _:
                                 battery_status = 'Unknown'
                    match int(battery_info_proto['1']['3']):
                        case 1:
                            battery_health= 'Unknown'
                        case 2:
                            battery_health= 'Good'
                        case 3:
                            battery_health = 'Overheat'
                        case 4:
                            battery_health = 'Dead'
                        case 5:
                            battery_health = 'Over Voltage'
                        case 6:
                            battery_health = 'Unspecified Failure'
                        case 7:
                            battery_health = 'Cold'
                        case _:
                            battery_health = 'None'
                    drain_type = battery_info_proto['13']
                    battery_debug = {}
                    if row[6]:
                        lines = re.split('\\n', row[6])

                        for line in lines:
                            try:
                                key, value =re.split(':', line)
                                battery_debug[str(key.strip())] =  value.strip().replace('"','')
                            except:
                                continue
                    try:
                        total_power = battery_debug['total_power']
                    except:
                        pass                    
                    try:
                        consume_power = battery_debug['consume_power']
                    except:
                        pass

                    data_list.append((row[2], app_label, row[1], is_hidden, boot_timestamp, timezone, total_power, consume_power, foreground, foreground_service, background, battery_level, battery_status, battery_health, drain_type, file_found))
                        
            
            db.close()
        else:
            continue # Skip all other files (-shm, -wal, etc.)
    
    if data_list:
        description = 'This is battery usage details pulled from Settings Services - new version introduced with Android 14 - Based on https://bebinary4n6.blogspot.com/2024/05/android-14-battery-usage-and-app-usage.html'
        report = ArtifactHtmlReport('Settings Services - Battery Usage v9 - Battery States')
        report.start_artifact_report(report_folder, 'Settings Services - Battery Usage v9 - Battery States', description)
        report.add_script()
        data_headers = ('Timestamp','Application','Package Name','Hidden','Boot Timestamp','Timezone','Total Power','Consumed Power','Foreground Usage (Seconds)', 'Foreground Service Usage (seconds)', 'Background Usage (Seconds)','Battery Level (%)','Battery Status', 'Battery Health', 'Drain Type', 'Source File') 

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()
        
        tsvname = f'Settings Services - Battery Usage v9 - Battery States'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Settings Services - Battery Usage v9 - Battery States'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Settings Services - Battery Usage v9 - Battery States data available')


def get_app_usage_events(files_found, report_folder, seeker, wrap_text):
    
    data_headers = []
    data_list = []
    
    for file_found in files_found:
        file_name = str(file_found)
    
        if file_name.endswith('battery-usage-db-v9'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
                SELECT 
                    uid,
                    userId,
                    DATETIME(timestamp/1000, 'unixepoch') AS timestamp, 
                    case appUsageEventType
                        when 1 then 'Paused'
                        when 2 then 'Resumed'
                    end,
                    packageName,  
                    taskRootPackageName,
                    instanceId
                    
                FROM AppUsageEventEntity
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], file_name))
                        
            
            db.close()
        else:
            continue # Skip all other files (-shm, -wal, etc.)
    
    if data_list:
        description = 'This is app battery usage events pulled from Settings Services - Based on https://bebinary4n6.blogspot.com/2024/05/android-14-battery-usage-and-app-usage.html'
        report = ArtifactHtmlReport('Settings Services - App Battery Usage Events')
        report.start_artifact_report(report_folder, 'Settings Services - App Battery Usage Events', description)
        report.add_script()
        data_headers = ('uid', 'userId', 'Timestamp', 'App Usage Event Type', 'Package Name', 'Root Package Name', 'Instance Id', 'Source File') 

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()
        
        tsvname = f'Settings Services - App Battery Usage Events'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Settings Services - App Battery Usage Events'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Settings Services - App Battery Usage Events data available')