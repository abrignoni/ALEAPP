# pylint: disable=W0613
__artifacts_v2__ = {
    "get_battery_usage_v4": {
        "name": "battery_usage_v4",
        "description": "Parses per-app battery usage (timestamp, application, power consumed, foreground and background usage, battery level and status) from the settings intelligence battery-usage-db-v4 database.",
        "author": "",
        "creation_date": "2021-12-21",
        "last_update_date": "2021-12-21",
        "requirements": "none",
        "category": "Settings Services",
        "notes": "",
        "paths": ('*/com.google.android.settings.intelligence/databases/battery-usage-db-v4*',),
        "output_types": "standard",
        "artifact_icon": "battery",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


@artifact_processor
def get_battery_usage_v4(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_name = str(file_found)
        if not file_name.endswith('battery-usage-db-v4'):
            continue  # Skip -shm, -wal, etc.

        source_path = file_name
        db = open_sqlite_db_readonly(file_name)
        cursor = db.cursor()
        cursor.execute('''
            select
            timestamp,
            appLabel,
            packageName,
            case isHidden when 0 then '' when 1 then 'Yes' end,
            (timestamp-bootTimestamp),
            zoneId,
            totalPower,
            consumePower,
            percentOfTotal,
            foregroundUsageTimeInMs*.001 as 'Foreground Usage (Seconds)',
            backgroundUsageTimeInMs*.001 as 'Background Usage (Seconds)',
            batteryLevel,
            case BatteryStatus when 2 then 'Charging' when 3 then 'Not Charging' when 5 then 'Fully Charged' end
            from BatteryState
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((_ms_to_utc(row[0]), row[1], row[2], row[3], _ms_to_utc(row[4]), row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12]))

    data_headers = (('Timestamp', 'datetime'), 'Application', 'Package Name', 'Hidden', ('Boot Timestamp', 'datetime'), 'Timezone', 'Total Power', 'Consumed Power', '% Of Consumed', 'Foreground Usage (Seconds)', 'Background Usage (Seconds)', 'Battery Level (%)', 'Battery Status')
    return data_headers, data_list, source_path
