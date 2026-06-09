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

#Ok tambahkan UTC utk timezone dan tambahkan battery saver untuk 0 enable, dan 2 disable
@artifact_processor
def Turbo_Battery(files_found, report_folder, seeker, wrap_text):
    source_file_turbo = ''
    data_list = []
    time_offset = 'UTC'  

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.lower().endswith('turbo.db'):
            continue
        
        #BugFix
        source_file_turbo = os.path.basename(file_found)
        
        try:
            db = open_sqlite_db_readonly(file_found)
        except Exception as e:
            # Bisa ganti dengan logfunc jika ada
            print(f"[!] Failed to open database {file_found}: {e}")
            continue
        
        cursor = db.cursor()
        cursor.execute('''
            SELECT
                CASE timestamp_millis
                    WHEN 0 THEN ''
                    ELSE datetime(timestamp_millis/1000, 'unixepoch')
                END AS D_T,
                battery_level,
                CASE charge_type
                    WHEN 0 THEN ''
                    WHEN 1 THEN 'Charging Rapidly'
                    WHEN 2 THEN 'Charging Slowly'
                    WHEN 3 THEN 'Charging Wirelessly'
                END AS C_Type,
                -- CASE battery_saver
                --     WHEN 2 THEN ''
                --     WHEN 1 THEN 'Enabled'
                -- END AS B_Saver,
                CASE battery_saver
                    WHEN 0 THEN 'Enabled'
                    WHEN 2 THEN 'Disabled'  
                    ELSE battery_saver  
                END AS B_Saver,
                timezone
            FROM battery_event
        ''')
        
        all_rows = cursor.fetchall()
        db.close()
        
        if len(all_rows) == 0:
            continue
        
        for row in all_rows:
            timestamp = row[0]
            if timestamp and timestamp != '':
                timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(timestamp), time_offset)
            else:
                timestamp = ''
            
            data_list.append((
                timestamp,
                row[1],  
                row[2],  
                row[3],  
                row[4],  
                source_file_turbo
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Battery Level',
        'Charge Type',
        'Battery Saver',
        'Timezone',
        'Source'
    )

    return data_headers, data_list, source_file_turbo

@artifact_processor
def Turbo_Bluetooth(files_found, report_folder, seeker, wrap_text):     
    source_file_bluetooth = ''
    data_list = []
    time_offset = 'UTC'

    for file_found in files_found:
        file_found = str(file_found)

        # cek file yang benar
        if not file_found.lower().endswith('bluetooth.db'):
            continue

        bluetooth_db = file_found
        source_file_bluetooth = os.path.basename(file_found)
       
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
        join device_address 
            on battery_event.device_idx = device_address.device_idx
        ''')

        all_rows = cursor.fetchall()
        
        for row in all_rows:
            timestamp = row[0]
            if timestamp:
                timestamp = convert_utc_human_to_timezone(
                    convert_ts_human_to_utc(timestamp),
                    time_offset
                )
            
            data_list.append((
                timestamp,
                row[1],  
                row[2],  
                row[3],  
                row[4],  
                row[5],  
                file_found
            ))

        db.close()
        
    data_headers = (
        ('Timestamp','datetime'),
        'BT Device MAC Address',
        'BT Device ID',
        'Battery Level',
        'Volume Level',
        'Timezone',
        'Source'
    )

    return data_headers, data_list, source_file_bluetooth
