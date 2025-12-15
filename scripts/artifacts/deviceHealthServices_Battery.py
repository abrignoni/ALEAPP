__artifacts_v2__ = {
    "Turbo_Battery": {
        "name": "Turbo - Phone Battery",
        "description": "Parses battery percentage for devices from Device Health Services",
        "author": "@stark4n6",
        "version": "0.0.1",
        "creation_date": "2021-06-29",
        "last_update_date": "2025-03-08",
        "requirements": "none",
        "category": "Device Health Services",
        "notes": "",
        "paths": ('*/com.google.android.apps.turbo/databases/turbo.db*'),
        "output_types": "all",
        "artifact_icon": "battery-charging"
    },
    "Turbo_Bluetooth": {
        "name": "Turbo - Bluetooth Device Info",
        "description": "Parses bluetooth connected devices from Device Health Services",
        "author": "@stark4n6",
        "version": "0.0.1",
        "creation_date": "2021-06-29",
        "last_update_date": "2025-03-08",
        "requirements": "none",
        "category": "Device Health Services",
        "notes": "",
        "paths": ('*/com.google.android.apps.turbo/databases/bluetooth.db*'),
        "output_types": "all",
        "artifact_icon": "bluetooth"
    }
}

import sqlite3
import textwrap
import os

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

@artifact_processor
def Turbo_Battery(files_found, report_folder, seeker, wrap_text):
    source_file_turbo = ''
    turbo_db = ''
    data_list = []
        
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.lower().endswith('turbo.db'):
            turbo_db = str(file_found)
            source_file_turbo = os.path.basename(file_found)
        
            db = open_sqlite_db_readonly(turbo_db)
            cursor = db.cursor()
            cursor.execute('''
            select
            case timestamp_millis
                when 0 then ''
                else datetime(timestamp_millis/1000,'unixepoch')
            End as D_T,
            battery_level,
            case charge_type
                when 0 then ''
                when 1 then 'Charging Rapidly'
                when 2 then 'Charging Slowly'
                when 3 then 'Charging Wirelessly'
            End as C_Type,
            case battery_saver
                when 2 then ''
                when 1 then 'Enabled'
            End as B_Saver,
            timezone
            from battery_event
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    timestamp = row[0]
                    if timestamp is None:
                        pass
                    else:
                        timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(timestamp),time_offset)
                    data_list.append((timestamp,row[1],row[2],row[3],row[4],file_found))
            
            db.close()
            
    data_headers = (('Timestamp', 'datetime'),'Battery Level','Charge Type','Battery Saver','Timezone','Source')
        
    return data_headers, data_list, source_file_turbo
            
@artifact_processor
def Turbo_Bluetooth(files_found, report_folder, seeker, wrap_text):     
    source_file_bluetooth = ''
    turbo_db = ''
    data_list = []

    if file_found.lower().endswith('bluetooth.db'):
        bluetooth_db = str(file_found)
        source_file_bluetooth = file_found.replace(seeker.directory, '')
    
        db = open_sqlite_db_readonly(bluetooth_db)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(timestamp_millis/1000,'unixepoch'),
        bd_addr,
        device_identifier,
        battery_level,
        volume_level,
        time_zone
        from battery_event
        join device_address on battery_event.device_idx = device_address.device_idx
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            for row in all_rows:
                timestamp = row[0]
                if timestamp is None:
                    pass
                else:
                    timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(timestamp),time_offset)
                data_list.append((timestamp,row[1],row[2],row[3],row[4],row[5],file_found))
        db.close()
        
    data_headers = (('Timestamp','datetime'),'BT Device MAC Address','BT Device ID','Battery Level','Volume Level','Timezone','Source')

    return data_headers, data_list, source_file_bluetooth