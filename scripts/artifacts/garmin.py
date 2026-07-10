# pylint: disable=W0613
__artifacts_v2__ = {
    "get_garmin_gcm_cache_activities": {
        "name": "Garmin - GCM Cache Activities",
        "description": "Parses parsed activity details from the Garmin Connect Mobile gcm_cache.db",
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2023-01-18",
        "last_update_date": "2023-01-18",
        "requirements": "none",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/data/com.garmin.android.apps.connectmobile/databases/gcm_cache.db*',),
        "output_types": "all",
        "artifact_icon": "activity",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 0 rows",
        },
    },
    "get_garmin_devices": {
        "name": "Garmin - Devices",
        "description": "Parses paired devices from the Garmin Connect Mobile gcm_cache.db",
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2023-01-18",
        "last_update_date": "2023-01-18",
        "requirements": "none",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/data/com.garmin.android.apps.connectmobile/databases/gcm_cache.db*',),
        "output_types": "standard",
        "artifact_icon": "device-watch",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 1 row",
        },
    },
    "get_garmin_weather": {
        "name": "Garmin - Weather",
        "description": "Parses cached weather records from the Garmin Connect Mobile gcm_cache.db",
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2023-01-18",
        "last_update_date": "2023-01-18",
        "requirements": "none",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/data/com.garmin.android.apps.connectmobile/databases/gcm_cache.db*',),
        "output_types": "all",
        "artifact_icon": "cloud",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 0 rows",
        },
    },
    "get_garmin_notification_details": {
        "name": "Garmin - Notification Details",
        "description": "Parses the full notification_info records (incl. phone number and actions) "
                       "from the Garmin Connect Mobile notification-database",
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2023-01-18",
        "last_update_date": "2023-01-18",
        "requirements": "none",
        "category": "Garmin",
        "notes": "Detailed companion to 'Garmin - Notifications'; keeps the extra columns "
                 "(subtitle, positive/negative action, phone number, post/when timestamps).",
        "paths": ('*/data/com.garmin.android.apps.connectmobile/databases/notification-database*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 45 rows",
        },
    },
    "get_garmin_cache_db_activities": {
        "name": "Garmin - Cache DB Activities",
        "description": "Parses activity_summaries from the Garmin Connect Mobile cache-database",
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2023-01-18",
        "last_update_date": "2023-01-18",
        "requirements": "none",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/data/com.garmin.android.apps.connectmobile/databases/cache-database*',),
        "output_types": "all",
        "artifact_icon": "activity",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 0 rows",
        },
    },
    "get_garmin_sleep_activities": {
        "name": "Garmin - Sleep Activities",
        "description": "Parses sleep_detail (incl. auto-sleep and respiration) from the Garmin "
                       "Connect Mobile cache-database",
        "author": "@KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)",
        "creation_date": "2023-01-18",
        "last_update_date": "2023-01-18",
        "requirements": "none",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/data/com.garmin.android.apps.connectmobile/databases/cache-database*',),
        "output_types": "standard",
        "artifact_icon": "moon",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 0 rows",
        },
    }
}

import calendar
import datetime
import sqlite3
import time

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _str_to_utc(value):
    """Parse a 'YYYY-MM-DD HH:MM:SS' UTC string (from SQL datetime()) into an aware datetime."""
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S').replace(
            tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _hms(seconds):
    """Format a number of seconds as HH:MM:SS (UTC clock), or '' if not numeric."""
    try:
        return time.strftime('%H:%M:%S', time.gmtime(int(seconds)))
    except (ValueError, TypeError, OSError):
        return ''


def _add_seconds_str(ts_str, seconds):
    """Add seconds to a 'YYYY-MM-DD HH:MM:SS' string and return the same string format."""
    try:
        base = calendar.timegm(time.strptime(str(ts_str), '%Y-%m-%d %H:%M:%S'))
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(base + int(seconds)))
    except (ValueError, TypeError, OSError):
        return ''


def _find(files_found, suffix):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if file_found.endswith(suffix):
            return file_found
    return ''


def _q(cursor, sql):
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error:
        return []


@artifact_processor
def get_garmin_gcm_cache_activities(files_found, report_folder, seeker, wrap_text):
    source = _find(files_found, 'gcm_cache.db')
    data_list = []
    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT
            replace(trim(json_extract(cached_val, '$.summaryDTO.startTimeGMT'),'.0'),'T',' '),
            replace(trim(json_extract(cached_val, '$.summaryDTO.startTimeLocal'),'.0'),'T',' '),
            json_extract(cached_val, '$.summaryDTO.duration'),
            json_extract(cached_val, '$.activityTypeDTO.typeKey'),
            json_extract(cached_val, '$.metadataDTO.userInfoDto.fullname'),
            json_extract(cached_val, '$.metadataDTO.userInfoDto.displayname'),
            round(json_extract(cached_val, '$.summaryDTO.distance')/1609,3),
            round(json_extract(cached_val, '$.summaryDTO.distance')/1000,3),
            json_extract(cached_val, '$.summaryDTO.startLatitude'),
            json_extract(cached_val, '$.summaryDTO.startLongitude'),
            json_extract(cached_val, '$.summaryDTO.endLatitude'),
            json_extract(cached_val, '$.summaryDTO.endLongitude'),
            json_extract(cached_val, '$.summaryDTO.averageHR'),
            json_extract(cached_val, '$.summaryDTO.calories'),
            json_extract(cached_val, '$.activityName'),
            json_extract(cached_val, '$.activityId'),
            json_extract(cached_val, '$.locationName')
        FROM json_activities
        WHERE data_type = 'ACTIVITY_DETAILS'
        ''')
        for row in rows:
            start_dt = _str_to_utc(row[0])
            end_dt = ''
            if start_dt and isinstance(row[2], (int, float)):
                end_dt = start_dt + datetime.timedelta(seconds=row[2])
            data_list.append((start_dt, row[1], end_dt, _hms(row[2]), row[3], row[4], row[5], row[6],
                              row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14],
                              row[15], row[16]))
        db.close()

    data_headers = (('Start Timestamp (UTC)', 'datetime'), 'Start Timestamp (Local)',
                    ('End Timestamp (UTC)', 'datetime'), 'Duration', 'Activity Type',
                    'User Full Name', 'User ID', 'Distance (Miles)', 'Distance (KM)', 'Latitude',
                    'Longitude', 'End Latitude', 'End Longitude', 'Average Heart Rate',
                    'Calories Burned', 'Activity Name', 'Activity ID', 'Location Name')
    return data_headers, data_list, source


@artifact_processor
def get_garmin_devices(files_found, report_folder, seeker, wrap_text):
    source = _find(files_found, 'gcm_cache.db')
    data_list = []
    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT datetime(last_connected_timestamp/1000,'unixepoch'), product_display_name,
        bt_friendly_name, mac_address, connection_type, software_version, unit_id, image_url
        FROM devices
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                              row[7]))
        db.close()

    data_headers = (('Last Connection Timestamp', 'datetime'), 'Product Display Name',
                    'Bluetooth Friendly Name', 'Mac Address', 'Connection Type', 'Software Version',
                    'Unit ID', 'Product Image URL')
    return data_headers, data_list, source


@artifact_processor
def get_garmin_weather(files_found, report_folder, seeker, wrap_text):
    source = _find(files_found, 'gcm_cache.db')
    data_list = []
    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT
            datetime(saved_timestamp/1000,'unixepoch'),
            replace(json_extract(cached_val, '$.issueDate'),'T',' '),
            json_extract(cached_val, '$.latitude'),
            json_extract(cached_val, '$.longitude'),
            json_extract(cached_val, '$.weatherStationDTO.id'),
            json_extract(cached_val, '$.weatherStationDTO.name'),
            json_extract(cached_val, '$.temp'),
            json_extract(cached_val, '$.apparentTemp'),
            json_extract(cached_val, '$.dewPoint'),
            json_extract(cached_val, '$.relativeHumidity'),
            json_extract(cached_val, '$.weatherTypeDTO.desc'),
            json_extract(cached_val, '$.windDirection'),
            json_extract(cached_val, '$.windDirectionCompassPoint'),
            json_extract(cached_val, '$.windSpeed'),
            concept_id
        FROM json_activities
        WHERE data_type = 'ACTIVITY_WEATHER'
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                              row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]))
        db.close()

    data_headers = (('Saved Timestamp', 'datetime'), 'Issue Date', 'Latitude', 'Longitude',
                    'Weather Station ID', 'Weather Station Name', 'Temperature',
                    'Apparent Temperature', 'Dew Point', 'Relative Humidity', 'Weather Type',
                    'Wind Direction (Degrees)', 'Wind Direction (Compass Point)', 'Wind Speed',
                    'Concept ID')
    return data_headers, data_list, source


@artifact_processor
def get_garmin_notification_details(files_found, report_folder, seeker, wrap_text):
    source = _find(files_found, 'notification-database')
    data_list = []
    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT
            CASE WHEN statusTimestamp = 0 THEN '' ELSE datetime(statusTimestamp/1000,'unixepoch') END,
            status, title, subTitle, message, packageName, positiveAction, negativeAction,
            phoneNumber, type,
            datetime(postTime/1000,'unixepoch'),
            datetime("when"/1000,'unixepoch')
        FROM notification_info
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6],
                              row[7], row[8], row[9], _str_to_utc(row[10]), _str_to_utc(row[11])))
        db.close()

    data_headers = (('Status Timestamp', 'datetime'), 'Notification Status', 'Title', 'Subtitle',
                    'Message', 'Package Name', 'Positive Action', 'Negative Action', 'Phone Number',
                    'Type', ('Post Timestamp', 'datetime'), ('When Timestamp', 'datetime'))
    return data_headers, data_list, source


@artifact_processor
def get_garmin_cache_db_activities(files_found, report_folder, seeker, wrap_text):
    source = _find(files_found, 'cache-database')
    data_list = []
    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT
            datetime(json_extract(json, '$.beginTimestamp')/1000,'unixepoch'),
            datetime((json_extract(json, '$.beginTimestamp')/1000)+json_extract(json, '$.duration'),'unixepoch'),
            json_extract(json, '$.startTimeLocal'),
            json_extract(json, '$.duration'),
            json_extract(json, '$.activityType.typeKey'),
            json_extract(json, '$.ownerFullName'),
            displayName,
            round(json_extract(json, '$.distance')/1609,3),
            round(json_extract(json, '$.distance')/1000,3),
            json_extract(json, '$.startLatitude'),
            json_extract(json, '$.startLongitude'),
            json_extract(json, '$.endLatitude'),
            json_extract(json, '$.endLongitude'),
            json_extract(json, '$.averageHR'),
            json_extract(json, '$.calories'),
            json_extract(json, '$.steps'),
            json_extract(json, '$.manufacturer'),
            json_extract(json, '$.deviceId'),
            json_extract(json, '$.locationName'),
            json_extract(json, '$.activityName'),
            activityId,
            datetime(lastUpdate/1000,'unixepoch')
        FROM activity_summaries
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2],
                              _add_seconds_str(row[2], row[3]), _hms(row[3]), row[4], row[5], row[6],
                              row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14],
                              row[15], row[16], row[17], row[18], row[19], row[20],
                              _str_to_utc(row[21])))
        db.close()

    data_headers = (('Start Timestamp (UTC)', 'datetime'), ('End Timestamp (UTC)', 'datetime'),
                    'Start Timestamp (Local)', 'End Timestamp (Local)', 'Duration', 'Activity Type',
                    'Owner Full Name', 'Owner ID', 'Distance (Miles)', 'Distance (KM)', 'Latitude',
                    'Longitude', 'End Latitude', 'End Longitude', 'Average Heart Rate',
                    'Calories Burned', 'Steps', 'Device Manufacturer', 'Device ID', 'Location Name',
                    'Activity Name', 'Activity ID', ('Last Update Timestamp', 'datetime'))
    return data_headers, data_list, source


@artifact_processor
def get_garmin_sleep_activities(files_found, report_folder, seeker, wrap_text):
    source = _find(files_found, 'cache-database')
    data_list = []
    if source:
        db = open_sqlite_db_readonly(source)
        cursor = db.cursor()
        rows = _q(cursor, '''
        SELECT
            datetime(sleepStartTimeGMT/1000,'unixepoch'),
            datetime(sleepEndTimeGMT/1000,'unixepoch'),
            datetime(autoSleepStartTimeGMT/1000,'unixepoch'),
            datetime(autoSleepEndTimeGMT/1000,'unixepoch'),
            sleepTimeInSeconds, deepSleepSeconds, lightSleepSeconds, remSleepSeconds,
            awakeSleepSeconds, averageSpO2Value, lowestSpO2Value, averageRespirationValue,
            lowestRespirationValue, highestRespirationValue,
            datetime(lastUpdated/1000,'unixepoch')
        FROM sleep_detail
        ''')
        for row in rows:
            data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), _str_to_utc(row[2]),
                              _str_to_utc(row[3]), _hms(row[4]), _hms(row[5]), _hms(row[6]),
                              _hms(row[7]), _hms(row[8]), row[9], row[10], row[11], row[12], row[13],
                              _str_to_utc(row[14])))
        db.close()

    data_headers = (('Sleep Start Timestamp (UTC)', 'datetime'),
                    ('Sleep End Timestamp (UTC)', 'datetime'),
                    ('Auto Sleep Start Timestamp (UTC)', 'datetime'),
                    ('Auto Sleep End Timestamp (UTC)', 'datetime'), 'Total Sleep Time', 'Deep Sleep',
                    'Light Sleep', 'REM Sleep', 'Awake Sleep', 'Average Sp02', 'Lowest Sp02',
                    'Average Breaths/min', 'Lowest Breaths/min', 'Highest Breaths/min',
                    ('Last Updated Timestamp', 'datetime'))
    return data_headers, data_list, source
