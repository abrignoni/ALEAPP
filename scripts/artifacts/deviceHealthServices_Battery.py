# pylint: disable=W0718
__artifacts_v2__ = {
    "Turbo_Battery": {
        "name": "Turbo - Phone Battery",
        "description": "Battery level records from the battery_event table of Device Health Services' turbo.db, with the charge type and battery saver values as stored.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2021-06-29",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Device Health Services",
        "notes": "One row per battery_event record. Timestamp is timestamp_millis read as Unix "
                 "milliseconds and reported in UTC, in whole seconds. Timezone is the timezone text "
                 "stored on the row; it is not applied to Timestamp. Charge Type (as stored) and "
                 "Battery Saver (as stored) are the charge_type and battery_saver integers; no "
                 "source for their meaning was found, so they are not labelled. On the copies of "
                 "turbo.db in hc_pixel8pro_a16, pixel7a_a14 and russell_pixel6a_a13 (7,417 records "
                 "in four files) charge_type held 0, 1 or 2 and battery_saver held 2 on every record.",
        "paths": ('*/com.google.android.apps.turbo/databases/turbo.db*',),
        "output_types": "all",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.apps.turbo | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.apps.turbo vc 10235989 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.turbo vc 10272287 | 397 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.turbo vc 10270262 | 1416 rows",
            "samsunga53_a14": "Android 14 | com.google.android.apps.turbo | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.apps.turbo | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.apps.turbo vc 10261629 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.turbo vc 10261629 | 5604 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.turbo vc 10270697 | 572 rows",
        }
    },
    "Turbo_Bluetooth": {
        "name": "Turbo - Bluetooth Device Info",
        "description": "Parses the battery and volume level events recorded for Bluetooth devices in Device Health Services' bluetooth.db",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2021-06-29",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Device Health Services",
        "notes": "Timestamp is timestamp_millis read as Unix milliseconds and reported in UTC, in "
                 "whole seconds. Timezone is the time_zone text stored on the row; it is not applied "
                 "to Timestamp. No registered image listed in sample_data holds a record, so the "
                 "output is unexercised on real data.",
        "paths": ('*/com.google.android.apps.turbo/databases/bluetooth.db*',),
        "output_types": "all",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "galaxys10_a10": "Android 10 | com.google.android.apps.turbo vc 10235989 | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.apps.turbo | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.apps.turbo vc 10261629 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.turbo vc 10261629 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.turbo vc 10270697 | 0 rows",
        }
    }
}

import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_utc
from scripts.artifacts.storagePathViews import unique_files

@artifact_processor
def Turbo_Battery(context):
    files_found = unique_files(context)
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
            charge_type,
            battery_saver,
            timezone
            from battery_event
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    timestamp = row[0]
                    if timestamp:
                        try:
                            timestamp = convert_ts_human_to_utc(timestamp)
                        except Exception:
                            pass
                    data_list.append((timestamp,row[1],row[2],row[3],row[4],context.get_relative_path(file_found)))
            
            db.close()
            
    data_headers = (('Timestamp', 'datetime'),'Battery Level','Charge Type (as stored)','Battery Saver (as stored)','Timezone','Source')
        
    return data_headers, data_list, source_file_turbo
            
@artifact_processor
def Turbo_Bluetooth(context):
    files_found = unique_files(context)
    source_file_bluetooth = ''
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.lower().endswith('bluetooth.db'):
            bluetooth_db = str(file_found)
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
            join device_address on battery_event.device_idx = device_address.device_idx
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    timestamp = row[0]
                    if timestamp:
                        try:
                            timestamp = convert_ts_human_to_utc(timestamp)
                        except Exception:
                            pass
                    data_list.append((timestamp,row[1],row[2],row[3],row[4],row[5],context.get_relative_path(file_found)))
            db.close()

    data_headers = (('Timestamp','datetime'),'BT Device MAC Address','BT Device ID','Battery Level','Volume Level','Timezone','Source')

    return data_headers, data_list, source_file_bluetooth
