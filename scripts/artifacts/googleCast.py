__artifacts_v2__ = {
    "googleCast": {
        "name": "Google Cast",
        "description": "Parses Google Cast device information",
        "author": "@deagler4n6 & @stark4n6",
        "creation_date": "2021-01-11",
        "last_update_date": "2025-08-09",
        "requirements": "none",
        "category": "Cast",
        "notes": "",
        "paths": ('*/com.google.android.gms/databases/cast.db*'),
        "output_types": "standard",
        "artifact_icon": "cast",
    }
}

from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

@artifact_processor
def googleCast(files_found, report_folder, seeker, wrap_text):
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
                        last_published = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_published),'UTC')
                    
                    last_discovered = row[14]
                    if last_discovered is None:
                        pass
                    else:
                        last_discovered = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_discovered),'UTC')
                    
                    last_discovered_ble = row[15]
                    if last_discovered_ble is None:
                        pass
                    else:
                        last_discovered_ble = convert_utc_human_to_timezone(convert_ts_human_to_utc(last_discovered_ble),'UTC')
                
                    data_list.append((last_published,row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],last_discovered,last_discovered_ble,file_found))
            db.close()
        else:
            continue # Skip all other files
    
    data_headers = (('Last Published Timestamp','datetime'),'Device ID (SSDP UDN)','Capabilities','Device Version','Device Friendly Name','Device Model Name','Receiver Metrics ID','Service Instance Name','Device IP Address','Device Port','Supported Criteria','RCN Enabled Status','Hotspot BSSID','Cloud Device ID',('Last Discovered Timestamp','datetime'),('Last Discovered By BLE Timestamp','datetime'),'Source File') 
    return data_headers, data_list, 'See source file(s) below:'