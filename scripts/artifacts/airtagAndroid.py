# pylint: disable=W0613
__artifacts_v2__ = {
    "airtagAlerts": {
        "name": "Android Airtag Alerts",
        "description": "Parses unknown-tracker (AirTag) alerts (creation and update timestamps, MAC address, device type and alert status) from the Google Play services personalsafety database.",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-08-18",
        "last_update_date": "2025-03-16",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "",
        "paths": '*/com.google.android.gms/databases/personalsafety_db*',
        "output_types": "standard",
        "artifact_icon": "alert-circle",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 4 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 2 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        }
    },
    "airtagScans": {
        "name": "Android Airtag Scans",
        "description": "Parses unknown-tracker (AirTag) scan records (timestamps, MAC address, state, RSSI and location) from the Google Play services personalsafety database.",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-08-18",
        "last_update_date": "2025-03-16",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "",
        "paths": '*/com.google.android.gms/databases/personalsafety_db*',
        "output_types": "all",
        "artifact_icon": "alert-circle",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 43 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 39 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 4 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        }
    },
    "airtagLastScan": {
        "name": "Android Airtag Last Scan",
        "description": "Parses the last unknown-tracker (AirTag) scan time from the personalsafety_info protobuf file.",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-08-18",
        "last_update_date": "2025-03-16",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "",
        "paths": '*/files/personalsafety/shared/personalsafety_info.pb',
        "output_types": "standard",
        "artifact_icon": "alert-circle",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 1 row",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 1 row",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 1 row",
            "userb2_a13": "Android 13 | com.google.android.gms | 1 row",
        }
    },
    "airtagPassiveScan": {
        "name": "Android Airtag Passive Scan",
        "description": "Parses the unknown-tracker (AirTag) passive-scan opt-in setting from the personalsafety_optin protobuf file.",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-08-18",
        "last_update_date": "2025-03-16",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "",
        "paths": '*/files/personalsafety/shared/personalsafety_optin.pb',
        "output_types": "standard",
        "artifact_icon": "alert-circle"
    }
}


import blackboxprotobuf
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, get_binary_file_content, \
    convert_unix_ts_to_utc


@artifact_processor
def airtagAlerts(files_found, report_folder, seeker, wrap_text):
    source_path = get_file_path(files_found, "personalsafety_db")
    data_list = []
    
    query = '''
    SELECT 
        creationTimestampMillis,
        lastUpdatedTimestampMillis,
        macAddress,
        deviceType,
        optionalDeviceData,
        alertLifecycleId,
        alertStatus 
    FROM DeviceData
    '''

    data_headers = (
        ('Creation Timestamp', 'datetime'), 
        ('Last Updated Timestamp', 'datetime'), 
        'MAC Address', 
        'Device Type', 
        'Optional Device Data', 
        'Alert Life Cycle ID', 
        'Alert Status')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        creation_timestamp = convert_unix_ts_to_utc(record[0])
        last_updated_timestamp = convert_unix_ts_to_utc(record[1])
        data_list.append((
            creation_timestamp, 
            last_updated_timestamp, 
            record[2], record[3], record[4], record[5], record[6]
        ))
    
    return data_headers, data_list, source_path

        
@artifact_processor
def airtagScans(files_found, report_folder, seeker, wrap_text):
    source_path = get_file_path(files_found, "personalsafety_db")
    data_list = []
    
    query = '''
    SELECT 
        creationTimestampMillis,
        lastUpdatedTimestampMillis,
        macAddress,
        state,
        blescan,
        locationScan 
    FROM Scan
    '''

    data_headers = (
        ('Creation Timestamp', 'datetime'), 
        ('Last Updated Timestamp', 'datetime'), 
        'MAC Address', 
        'State', 
        'Possible RSSI', 
        'Latitude', 
        'Longitude')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        creation_timestamp, last_updated_timestamp, mac_address, \
            state, blescan, location_scan = record
        creation_timestamp = convert_unix_ts_to_utc(record[0])
        last_updated_timestamp = convert_unix_ts_to_utc(record[1])

        blescan_proto, _ = blackboxprotobuf.decode_message(blescan)
        posrssi = (blescan_proto['2'])
        
        location_scan_proto, _ = blackboxprotobuf.decode_message(location_scan)
        latitude = (location_scan_proto['4']/1e7)
        longitude = (location_scan_proto['5']/1e7)
        
        data_list.append((
            creation_timestamp, last_updated_timestamp, mac_address, 
            state, posrssi, latitude, longitude))

    return data_headers, data_list, source_path

        
@artifact_processor
def airtagLastScan(files_found, report_folder, seeker, wrap_text):
    source_path = get_file_path(files_found, "personalsafety_info.pb")
    data_list = []
    
    proto_data = get_binary_file_content(source_path)

    lastscan, _ = blackboxprotobuf.decode_message(proto_data)
    lastscan = (lastscan['1'])
    lastscan = convert_unix_ts_to_utc(lastscan)
    data_list.append((lastscan, ))

    data_headers = (('Timestamp', 'datetime'),)

    return data_headers, data_list, source_path


@artifact_processor
def airtagPassiveScan(files_found, report_folder, seeker, wrap_text):
    source_path = get_file_path(files_found, "personalsafety_optin.pb")
    data_list = []
    
    proto_data = get_binary_file_content(source_path)

    pass_scan, _ = blackboxprotobuf.decode_message(proto_data)
    pass_scan = (pass_scan['1'])
    
    if pass_scan == 1:
        pass_scan = 'On'
    elif pass_scan == 2:
        pass_scan = 'Off'

    data_list.append((pass_scan, ))

    data_headers = ('Passive Scan', )

    return data_headers, data_list, source_path
