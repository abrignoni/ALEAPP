__artifacts_v2__ = {
    "sdhmsBatteryAppHistory": {
        "name": "SDHMS Battery App History",
        "description": "Per-app usage in time windows from the sec_batterystats_history database of com.sec.android.sdhms (APP_HISTORY table): power "
                       "drain, foreground/background time, CPU, wakelocks, network packets, "
                       "GPS and audio use per uid.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Samsung Device Health Management Service",
        "notes": "Window Start and Window End are start_time and end_time read as Unix "
                 "milliseconds. Foreground Time, Background Time, CPU Time, Wakelock Time, GPS Time and Audio Time are fg_time, bg_time, cpu_time, wakelock_time, gps_time and audio_time as stored. Their unit is not established. Where the database has no bluetooth_scan column the "
                 "Bluetooth Scan column is empty.",
        "paths": ('*/com.sec.android.sdhms/databases/sec_batterystats_history*',),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.sdhms | 1533 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.sdhms | 3341 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.sdhms | 397 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.sdhms | 246 rows",
            "sharon_a14": "Android 14 | com.sec.android.sdhms | 961 rows",
        },
    },
    "sdhmsBatteryDeviceHistory": {
        "name": "SDHMS Battery Device History",
        "description": "Device-wide screen and discharge figures in time windows from the sec_batterystats_history database of com.sec.android.sdhms (DEVICE_HISTORY table).",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Samsung Device Health Management Service",
        "notes": "Window Start and Window End are start_time and end_time read as Unix "
                 "milliseconds. Screen On Time and Screen Off Time are labelled in "
                 "milliseconds; that unit is not sourced here. Where the database has no "
                 "screen_on_count column the Screen On Count, High Brightness Time and High "
                 "Refresh Time columns are empty.",
        "paths": ('*/com.sec.android.sdhms/databases/sec_batterystats_history*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.sdhms | 322 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.sdhms | 567 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.sdhms | 37 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.sdhms | 42 rows",
            "sharon_a14": "Android 14 | com.sec.android.sdhms | 69 rows",
        },
    },
    "sdhmsBatteryEventHistory": {
        "name": "SDHMS Battery Event History",
        "description": "Battery events from the sec_batterystats_history database of com.sec.android.sdhms (BATTERY_EVENT_HISTORY table). Event type "
                       "and value are stored as integers whose meaning is not established, "
                       "so they are reported as stored.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Samsung Device Health Management Service",
        "notes": "Where the table has no id column the ID column is empty.",
        "paths": ('*/com.sec.android.sdhms/databases/sec_batterystats_history*',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.sdhms | 232 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.sdhms | 362 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.sdhms | 23 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.sdhms | 225 rows",
            "sharon_a14": "Android 14 | com.sec.android.sdhms | 67 rows",
        },
    },
    "sdhmsBatterySystemHistory": {
        "name": "SDHMS Battery System History",
        "description": "System power drain in time windows from the sec_batterystats_history database of com.sec.android.sdhms (SYSTEM_HISTORY table). The drain type is stored as a raw integer and is reported "
                       "as-is.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Samsung Device Health Management Service",
        "notes": "Window Start and Window End are start_time and end_time read as Unix "
                 "milliseconds. Used Time is the used_time column as stored. Its unit is not "
                 "established. On samsungs20_a13, the 38 rows of one Drain Type hold values close "
                 "to the window length in seconds, and the 10 rows of the other hold about 158 to "
                 "1,001 times that length. On galaxys10_a10 no Drain Type follows that pattern, "
                 "so do not carry it to another image.",
        "paths": ('*/com.sec.android.sdhms/databases/sec_batterystats_history*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.sdhms | 490 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.sdhms | 577 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.sdhms | 36 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.sdhms | 48 rows",
            "sharon_a14": "Android 14 | com.sec.android.sdhms | 83 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc, does_column_exist_in_db, is_sqlite_sidecar


def _history_db(context):
    '''First sec_batterystats_history database, skipping -wal/-shm sidecars and mirrors.'''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if is_sqlite_sidecar(file_found):
            continue
        if 'data_mirror' in file_found:
            continue
        return file_found
    return None


def _ms_to_utc(value):
    if not value:
        return ''
    return convert_unix_ts_to_utc(int(value) / 1000)


@artifact_processor
def sdhmsBatteryAppHistory(context):
    data_list = []
    source_path = _history_db(context)

    if source_path:
        # older One UI versions do not have the bluetooth_scan column
        has_bt_scan = does_column_exist_in_db(source_path, 'APP_HISTORY', 'bluetooth_scan')
        bt_scan_column = 'bluetooth_scan' if has_bt_scan else "''"
        db_records = get_sqlite_db_records(source_path, f'''
            SELECT start_time, end_time, uid, power, screen_power, fg_time, bg_time,
                   cpu_time, wakelock_time, mobile_packet, wifi_packet, wakeup_alarm,
                   gps_time, audio_time, mobile_active, {bt_scan_column}
            FROM APP_HISTORY
            ORDER BY start_time DESC, APP_HISTORY.rowid
        ''')

        for row in db_records:
            data_list.append((_ms_to_utc(row[0]), _ms_to_utc(row[1])) + tuple(row[2:]))

    data_headers = (
        ('Window Start', 'datetime'),
        ('Window End', 'datetime'),
        'UID',
        'Power',
        'Screen Power',
        'Foreground Time',
        'Background Time',
        'CPU Time',
        'Wakelock Time',
        'Mobile Packets',
        'Wi-Fi Packets',
        'Wakeup Alarms',
        'GPS Time',
        'Audio Time',
        'Mobile Active',
        'Bluetooth Scan',
    )
    return data_headers, data_list, source_path


@artifact_processor
def sdhmsBatteryDeviceHistory(context):
    data_list = []
    source_path = _history_db(context)

    if source_path:
        # older One UI versions lack the screen_on_count/high_brightness_time/
        # high_refresh_time columns
        if does_column_exist_in_db(source_path, 'DEVICE_HISTORY', 'screen_on_count'):
            newer_columns = 'screen_on_count, high_brightness_time, high_refresh_time'
        else:
            newer_columns = "'', '', ''"
        db_records = get_sqlite_db_records(source_path, f'''
            SELECT start_time, end_time, all_power, screen_power, screen_on_time,
                   screen_off_time, screen_on_discharge, screen_off_discharge,
                   {newer_columns}
            FROM DEVICE_HISTORY
            ORDER BY start_time DESC
        ''')

        for row in db_records:
            data_list.append((_ms_to_utc(row[0]), _ms_to_utc(row[1])) + tuple(row[2:]))

    data_headers = (
        ('Window Start', 'datetime'),
        ('Window End', 'datetime'),
        'All Power',
        'Screen Power',
        'Screen On Time (ms)',
        'Screen Off Time (ms)',
        'Screen On Discharge',
        'Screen Off Discharge',
        'Screen On Count',
        'High Brightness Time (ms)',
        'High Refresh Time (ms)',
    )
    return data_headers, data_list, source_path


@artifact_processor
def sdhmsBatteryEventHistory(context):
    data_list = []
    source_path = _history_db(context)

    if source_path:
        # older One UI versions lack the id column
        id_column = 'id' if does_column_exist_in_db(
            source_path, 'BATTERY_EVENT_HISTORY', 'id') else "''"
        db_records = get_sqlite_db_records(source_path, f'''
            SELECT update_time, event_type, event_value, {id_column}
            FROM BATTERY_EVENT_HISTORY
            ORDER BY update_time DESC
        ''')

        for row in db_records:
            data_list.append((_ms_to_utc(row[0]), row[1], row[2], row[3]))

    data_headers = (
        ('Update Time', 'datetime'),
        'Event Type',
        'Event Value',
        'ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def sdhmsBatterySystemHistory(context):
    data_list = []
    source_path = _history_db(context)

    if source_path:
        db_records = get_sqlite_db_records(source_path, '''
            SELECT start_time, end_time, drain_type, power, used_time
            FROM SYSTEM_HISTORY
            ORDER BY start_time DESC
        ''')

        for row in db_records:
            data_list.append((_ms_to_utc(row[0]), _ms_to_utc(row[1]), row[2], row[3], row[4]))

    data_headers = (
        ('Window Start', 'datetime'),
        ('Window End', 'datetime'),
        'Drain Type',
        'Power',
        'Used Time',
    )
    return data_headers, data_list, source_path
