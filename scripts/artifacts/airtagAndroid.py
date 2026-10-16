__artifacts_v2__ = {
    "airtagAlerts": {
        "name": "Android Airtag Alerts",
        "description": "Parses unknown-tracker (AirTag) alerts (creation and update timestamps, MAC address, device type and alert status) from the Google Play services personalsafety database.",
        "author": "@AlexisBrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-08-18",
        "last_update_date": "2025-03-16",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "",
        "paths": '*/com.google.android.gms/databases/personalsafety_db*',
        "output_types": "standard",
        "artifact_icon": "bell-ringing",
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
        "description": "Parses unknown-tracker (AirTag) scan records (timestamps, MAC address, state, and three values decoded without a schema from the bleScan and locationScan blobs) from the Google Play services personalsafety database.",
        "author": "@AlexisBrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-08-18",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "Possible RSSI is field 2 of the bleScan blob. Possible Latitude and Possible "
                 "Longitude are fields 4 and 5 of the locationScan blob divided by 10,000,000. "
                 "Both blobs are decoded without a schema, and the meaning of those fields and "
                 "the scale are not established by a published schema. On the 86 rows of "
                 "kevin_pocox7_a15, pixel7a_a14 and sharon_a14, field 2 was a whole number from "
                 "-98 to -27, and fields 4 and 5 divided by 10,000,000 fell within -90 to 90 and "
                 "-180 to 180 on every row. The values were not compared with another location "
                 "record of those devices, so no map output is produced from them.",
        "paths": '*/com.google.android.gms/databases/personalsafety_db*',
        "output_types": "standard",
        "artifact_icon": "radar",
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
        "description": "Reports field 1 of the personalsafety_info protobuf file, read as Unix milliseconds.",
        "author": "@AlexisBrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-08-18",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "The file is decoded without a schema. That field 1 is the time of the last scan "
                 "is not established by a published schema. On kevin_pocox7_a15, pixel7a_a14 and "
                 "sharon_a14, field 1 read as Unix milliseconds was 200 seconds after, 23 seconds "
                 "before and 72 seconds before the newest creationTimestampMillis in the Scan "
                 "table of personalsafety_db, so it did not equal the time of the newest stored "
                 "scan record on any of the three.",
        "paths": '*/files/personalsafety/shared/personalsafety_info.pb',
        "output_types": "standard",
        "artifact_icon": "clock-search",
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
        "description": "Reports field 1 of the personalsafety_optin protobuf file as stored.",
        "author": "@AlexisBrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-08-18",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Airtag Detection",
        "notes": "The file is decoded without a schema, and what each value of field 1 means is not "
                 "established by a published schema, so the number is reported as stored with no "
                 "label. The file was present on one of the 20 registered Android zip extractions "
                 "(russell_a14), where it held field 1 only; the state of the unknown tracker "
                 "alerts setting on that device is not recorded with the image.",
        "paths": '*/files/personalsafety/shared/personalsafety_optin.pb',
        "output_types": "standard",
        "artifact_icon": "radar-2",
        "sample_data": {
            "russell_a14": "Android 14 | com.google.android.gms | 1 row",
        }
    }
}


from scripts.ilapfuncs import decode_protobuf
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, get_binary_file_content, \
    convert_unix_ts_to_utc, does_column_exist_in_db


@artifact_processor
def airtagAlerts(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "personalsafety_db")
    data_list = []

    # older GmsCore personalsafety_db schemas do not carry these two columns
    device_type_col = 'deviceType' if does_column_exist_in_db(
        source_path, 'DeviceData', 'deviceType') else "NULL AS deviceType"
    optional_data_col = 'optionalDeviceData' if does_column_exist_in_db(
        source_path, 'DeviceData', 'optionalDeviceData') else "NULL AS optionalDeviceData"

    query = f'''
    SELECT
        creationTimestampMillis,
        lastUpdatedTimestampMillis,
        macAddress,
        {device_type_col},
        {optional_data_col},
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
def airtagScans(context):
    files_found = context.get_files_found()
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
        'Possible Latitude', 
        'Possible Longitude')

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        creation_timestamp, last_updated_timestamp, mac_address, \
            state, blescan, location_scan = record
        creation_timestamp = convert_unix_ts_to_utc(record[0])
        last_updated_timestamp = convert_unix_ts_to_utc(record[1])

        blescan_proto = {}
        if blescan:
            blescan_proto, _ = decode_protobuf(blescan)
            blescan_proto = blescan_proto or {}
        posrssi = blescan_proto.get('2', '')

        # a scan row without a location fix carries no lat/long fields
        location_scan_proto = {}
        if location_scan:
            location_scan_proto, _ = decode_protobuf(location_scan)
            location_scan_proto = location_scan_proto or {}
        lat_raw = location_scan_proto.get('4')
        lon_raw = location_scan_proto.get('5')
        latitude = lat_raw / 1e7 if isinstance(lat_raw, (int, float)) else ''
        longitude = lon_raw / 1e7 if isinstance(lon_raw, (int, float)) else ''

        data_list.append((
            creation_timestamp, last_updated_timestamp, mac_address,
            state, posrssi, latitude, longitude))

    return data_headers, data_list, source_path

        
@artifact_processor
def airtagLastScan(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "personalsafety_info.pb")
    data_list = []
    
    proto_data = get_binary_file_content(source_path)

    lastscan, _ = decode_protobuf(proto_data)
    lastscan = (lastscan['1'])
    lastscan = convert_unix_ts_to_utc(lastscan)
    data_list.append((lastscan, ))

    data_headers = (('Field 1 Timestamp', 'datetime'),)

    return data_headers, data_list, source_path


@artifact_processor
def airtagPassiveScan(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "personalsafety_optin.pb")
    data_list = []
    
    proto_data = get_binary_file_content(source_path)

    pass_scan, _ = decode_protobuf(proto_data)
    pass_scan = (pass_scan['1'])

    data_list.append((pass_scan, ))

    data_headers = ('Field 1 (as stored)', )

    return data_headers, data_list, source_path
