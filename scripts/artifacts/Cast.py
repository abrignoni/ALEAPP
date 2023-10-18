__artifacts_v2__ = {
    "Cast": {
        "name": "Cast",
        "description": "Parses Cast device information",
        "author": "@deagler4n6",
        "version": "0.0.2",
        "date": "2021-01-11",
        "requirements": "none",
        "category": "Cast",
        "notes": "2023-10-12 - Updated by @KevinPagano3",
        "paths": ('*/com.google.android.gms/databases/cast.db*'),
        "function": "get_Cast"
    }
}

import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_Cast(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('cast.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            case last_published_timestamp_millis
                when 0 then ''
                else datetime(last_published_timestamp_millis/1000, 'unixepoch')
            end as "Last Published Timestamp",
            device_id,
            capabilities,
            device_version,
            friendly_name,
            model_name,
            receiver_metrics_id,
            service_instance_name,
            service_address,
            service_port,
            supported_criteria,
            rcn_enabled_status,
            hotspot_bssid,
            cloud_devcie_id,
            case last_discovered_timestamp_millis
                when 0 then ''
                else datetime(last_discovered_timestamp_millis/1000, 'unixepoch')
            end as "Last Discovered Timestamp",
            case last_discovered_by_ble_timestamp_millis
                when 0 then ''
                else datetime(last_discovered_by_ble_timestamp_millis/1000, 'unixepoch')
            end as "Last Discovered By BLE Timestamp"
            from DeviceInfo
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    last_published = row[0]
                    if last_published is None:
                        pass
                    else:
                        last_published = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_published),time_offset)
                    
                    last_discovered = row[14]
                    if last_discovered is None:
                        pass
                    else:
                        last_discovered = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_discovered),time_offset)
                    
                    last_discovered_ble = row[15]
                    if last_discovered_ble is None:
                        pass
                    else:
                        last_discovered_ble = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_discovered_ble),time_offset)
                
                    data_list.append((last_published,row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],last_discovered,last_discovered_ble,file_found))
            db.close()
        else:
            continue # Skip all other files
    
    if data_list:
        report = ArtifactHtmlReport('Cast')
        report.start_artifact_report(report_folder, 'Cast')
        report.add_script()
        data_headers = ('Last Published Timestamp','Device ID (SSDP UDN)','Capabilities','Device Version','Device Friendly Name','Device Model Name','Receiver Metrics ID','Service Instance Name','Device IP Address','Device Port','Supported Criteria','RCN Enabled Status','Hotspot BSSID','Cloud Device ID','Last Discovered Timestamp','Last Discovered By BLE Timestamp','Source') 
        
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Cast'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Cast'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Cast data available')