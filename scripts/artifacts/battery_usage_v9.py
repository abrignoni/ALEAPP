# Android Settings Services -  Battery Usages v9 (com.android.settings)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions/devices:
# 2024-05-19: Android 14 - Fairphone3 and Fairphone 4

# Requirements: -

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

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_battery_usage_v9(files_found, report_folder, seeker, wrap_text, time_offset):
    
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
                    batteryInformationDebug
                    
                FROM BatteryState
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                
                for row in all_rows:
                    # we need to parse the column batteryInformationDebug - a lot of data is in here
                    battery_debug = {}
                    if row[5]:
                        lines = re.split('\\n', row[5])

                        for line in lines:
                            try:
                                key, value =re.split(':', line)
                                battery_debug[str(key.strip())] =  value.strip().replace('"','')
                            except:
                                continue
                    try:
                        app_label = battery_debug['app_label']
                    except:
                        app_label = 'None'
                    try:
                        is_hidden = battery_debug['is_hidden']
                    except:
                        is_hidden = 'False'
                    try:
                        boot_timestamp = int(battery_debug['boot_timestamp']) / 1000
                    except:
                        boot_timestamp = 'None'
                    try:
                        timezone = battery_debug['zone_id']
                    except:
                        timezone = 'None'
                    try:
                        total_power = battery_debug['total_power']
                    except:
                        total_power = 'None'
                    try:
                        consume_power = battery_debug['consume_power']
                    except:
                        consume_power = 'None'
                    try:
                        foreground = int(battery_debug['foreground_usage_time_in_ms']) / 1000
                    except:
                        foreground = 'None'
                    try:
                        foreground_service = int(battery_debug['foreground_service_usage_time_in_ms']) / 1000
                    except:
                        foreground_service = 'None'
                    try:
                        background = int(battery_debug['background_usage_time_in_ms']) / 1000
                    except:
                        background = 'None'
                    try:
                        battery_level = battery_debug['battery_level']
                    except:
                        battery_level = 'None'
                    try:
                        battery_status = battery_debug['battery_status']
                        match int(battery_status):
                            case 2:
                                battery_status= 'Charging'
                            case 3:
                                battery_status = 'Discharging'
                            case 5:
                                battery_status = 'Fully charged'
                            case _:
                                battery_status = 'Unknown'
                    except:
                        battery_status = 'None'
                    try:
                        battery_health = battery_debug['battery_health']
                        match int(battery_health):
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
                    except:
                        battery_health = 'None'
                    try:
                        drain_type = battery_debug['drain_type']
                    except:
                        drain_type = 'None'


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


def get_app_usage_events(files_found, report_folder, seeker, wrap_text, time_offset):
    
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