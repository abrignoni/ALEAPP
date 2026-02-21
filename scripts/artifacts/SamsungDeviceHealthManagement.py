# Android Samsung Device Health Management Service SDHMS (com.sec.android.sdhms)
# Author:  Marco Neumann (kalinko@be-binary.de)
#
# Requirements:

__artifacts_v2__ = {
  
    "sdhms_config_reloads": {
        "name": "SDHMS Config Reload History",
        "description": "SDHMS Config Reload History - Shows e.g. Reboot of Device. More info: https://bebinary4n6.blogspot.com/2026/01/inside-android-samsung-dhms-extracting.html",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2026-01-10",
        "last_update_date": "2026-01-10",
        "requirements": "",
        "category": "Samsung Device Health Management Service",
        "notes": "",
        "paths": ('*/com.sec.android.sdhms/databases/anomaly.db*'),
        "artifact_icon": "settings"
    },
    "sdhms_netstat": {
        "name": "SDHMS Netstat",
        "description": "SDHMS Network Usage per App. More info: https://bebinary4n6.blogspot.com/2026/01/inside-android-samsung-dhms-extracting.html",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2026-01-10",
        "last_update_date": "2026-01-10",
        "requirements": "",
        "category": "Samsung Device Health Management Service",
        "notes": "",
        "paths": ('*/com.sec.android.sdhms/databases/thermal_log*'),
        "artifact_icon": "bar-chart"
    },
    "sdhms_temperature": {
        "name": "SDHMS Temperature Logs",
        "description": "SDHMS Temperature Logs per Sensor in degree Celsius. More info: https://bebinary4n6.blogspot.com/2026/01/inside-android-samsung-dhms-extracting.html",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2026-01-10",
        "last_update_date": "2026-01-10",
        "requirements": "",
        "category": "Samsung Device Health Management Service",
        "notes": "",
        "paths": ('*/com.sec.android.sdhms/databases/thermal_log*'),
        "artifact_icon": "thermometer"
    },
    "sdhms_cpustats": {
        "name": "SDHMS CPU Stats",
        "description": "SDHMS CPU Usage per Process. More info: https://bebinary4n6.blogspot.com/2026/01/inside-android-samsung-dhms-extracting.html",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2026-01-10",
        "last_update_date": "2026-01-10",
        "requirements": "",
        "category": "Samsung Device Health Management Service",
        "notes": "",
        "paths": ('*/com.sec.android.sdhms/databases/thermal_log*'),
        "artifact_icon": "cpu"
    }

}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records

@artifact_processor
def sdhms_config_reloads(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    query = ('''
        SELECT
        time,
        reason,
        config_key,
        config_version
        FROM config_history
    ''')

    data_list = []

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    for row in db_records:
        config_reload_time = convert_unix_ts_to_utc(int(row[0])/1000)
        reason = row[1]
        config_key = row[2]
        config_version = row[3]

        data_list.append(( config_reload_time, reason, config_key, config_version))

    data_headers = ('Config Reload Time' , 'Config Reload Reason', 'Config Key', 'Config Version')

    return data_headers, data_list, files_found[0]

@artifact_processor
def sdhms_netstat(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    query = ('''
        SELECT
        start_time,
        end_time,
        id,        
        package_name,
        uid,
        net_usage
        FROM NETSTAT
    ''')

    data_list = []

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    for row in db_records:
        start_time = convert_unix_ts_to_utc(int(row[0])/1000)
        end_time = convert_unix_ts_to_utc(int(row[1])/1000)
        entry_id = row[2]
        package_name = row[3]
        package_uid = row[4]
        net_usage = row[5]

        data_list.append(( start_time, end_time, entry_id, package_name, package_uid, net_usage))

    data_headers = ('Start Time', 'End Time', 'Entry ID', 'Package Name', 'Package UID', 'Network Usage')

    return data_headers, data_list, files_found[0]

@artifact_processor
def sdhms_temperature(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    query = ('''
        SELECT
        timestamp,
        skin_temp/10.0 [Chassis Temperature],
        ap_temp/10.0 [Processor Temperature],
        bat_temp/10.0 [Battery Temperature],
        usb_temp/10.0 [USB Temperature],
        chg_temp/10.0 [Charging IC Temperature],
        pa_temp/10.0 [Cellular Radio Temperature],
        wifi_temp/10.0 [WiFi Temperature]
        FROM TEMPERATURE
    ''')

    data_list = []

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    for row in db_records:
        timestamp = convert_unix_ts_to_utc(int(row[0])/1000)
        skin_temp = row[1]
        ap_temp = row[2]
        bat_temp = row[3]
        usb_temp = row[4]
        chg_temp = row[5]
        pa_temp = row[6]
        wifi_temp = row[7]

        data_list.append(( timestamp, skin_temp, ap_temp, bat_temp, usb_temp, chg_temp, pa_temp, wifi_temp))

    data_headers = ('Timestamp', 'Chassis Temperature', 'Processor Temperatur', 'Battery Temperature', 'USB Temperature', 'Charging IC Temperature', 'Cellular Radio Temperature', 'WiFi Temperature')

    return data_headers, data_list, files_found[0]

@artifact_processor
def sdhms_cpustats(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    query = ('''
        SELECT
        start_time,
        end_time,
        uptime [Uptime],
        process_name [Process Name],
        uid [Package ID],
        pid [Process ID],
        process_usage [Process Usage]
        FROM CPUSTAT
    ''')

    data_list = []

    db_records = get_sqlite_db_records(str(files_found[0]), query)

    for row in db_records:
        start_time = convert_unix_ts_to_utc(int(row[0])/1000)
        end_time = convert_unix_ts_to_utc(int(row[1])/1000)
        uptime = row[2]
        process_name = row[3]
        package_id = row[4]
        process_id = row[5]
        process_cpu_usage = row[6]

        data_list.append(( start_time, end_time, uptime, process_name, package_id, process_id, process_cpu_usage))

    data_headers = ('Start Time', 'End Time', 'Uptime', 'Process Name', 'Package ID', 'PRocess ID', 'Process CPU Usage')

    return data_headers, data_list, files_found[0]