__artifacts_v2__ = {
    "airtagAlerts": {
        "name": "Android Airtag Alerts",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-08-18",
        "last_update_date": "2025-03-16",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "",
        "paths": '*/com.google.android.gms/databases/personalsafety_db*',
        "output_types": "standard",
        "artifact_icon": "alert-circle"
    },
    "airtagScans": {
        "name": "Android Airtag Scans",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-08-18",
        "last_update_date": "2025-03-16",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "",
        "paths": '*/com.google.android.gms/databases/personalsafety_db*',
        "output_types": "all",
        "artifact_icon": "alert-circle"
    },
    "airtagLastScan": {
        "name": "Android Airtag Last Scan",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2023-08-18",
        "last_update_date": "2025-03-16",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "",
        "paths": '*/files/personalsafety/shared/personalsafety_info.pb',
        "output_types": "standard",
        "artifact_icon": "alert-circle"
    },
    "airtagPassiveScan": {
        "name": "Android Airtag Passive Scan",
        "description": "",
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

        blescan_proto, types = blackboxprotobuf.decode_message(blescan)
        posrssi = (blescan_proto['2'])
        
        location_scan_proto, types = blackboxprotobuf.decode_message(location_scan)
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
