import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Cast(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
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
        case last_published_timestamp_millis
            when 0 then ''
            else datetime(last_published_timestamp_millis/1000, 'unixepoch')
        end as "Last Published Timestamp",
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
        report = ArtifactHtmlReport('Cast')
        report.start_artifact_report(report_folder, 'Cast')
        report.add_script()
        data_headers = ('Device ID (SSDP UDN)','Capabilities','Device Version','Device Friendly Name','Device Model Name','Receiver Metrics ID','Service Instance Name','Device IP Address','Device Port','Supported Criteria','RCN Enabled Status','Hotspot BSSID','Cloud Device ID','Last Published Timestamp','Last Discovered Timestamp','Last Discovered By BLE Timestamp') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Cast'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Cast'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Cast data available')
    
    db.close()
    return
