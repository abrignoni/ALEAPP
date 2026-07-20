# pylint: disable=W0613
__artifacts_v2__ = {
    "get_samsungWeatherClockInfo": {
        "name": "Samsung Weather Clock - Info",
        "description": "Parses current conditions from the Samsung Weather Clock (timestamp, timezone, location, temperature, conditions, sunrise and sunset) from the WeatherClock database.",
        "author": "",
        "creation_date": "2021-10-13",
        "last_update_date": "2021-10-13",
        "requirements": "none",
        "category": "Samsung Weather Clock",
        "notes": "",
        "paths": ('*/com.sec.android.daemonapp/databases/WeatherClock*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.daemonapp | 5 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.daemonapp | 1 row",
            "samsunga53_a14": "Android 14 | com.sec.android.daemonapp | 1 row",
            "samsungs20_a13": "Android 13 | com.sec.android.daemonapp | 1 row",
            "sharon_a14": "Android 14 | com.sec.android.daemonapp | 1 row",
        },
    },
    "get_samsungWeatherClockDaily": {
        "name": "Samsung Weather Clock - Daily",
        "description": "Parses the Samsung Weather Clock daily forecast (timestamp, location, temperature, conditions and daily high and low) from the WeatherClock database.",
        "author": "",
        "creation_date": "2021-10-13",
        "last_update_date": "2021-10-13",
        "requirements": "none",
        "category": "Samsung Weather Clock",
        "notes": "",
        "paths": ('*/com.sec.android.daemonapp/databases/WeatherClock*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.daemonapp | 40 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.daemonapp | 8 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.daemonapp | 8 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.daemonapp | 8 rows",
            "sharon_a14": "Android 14 | com.sec.android.daemonapp | 8 rows",
        },
    },
    "get_samsungWeatherClockHourly": {
        "name": "Samsung Weather Clock - Hourly",
        "description": "Parses the Samsung Weather Clock hourly forecast (timestamp, location, temperature, conditions, rain probability and wind) from the WeatherClock database.",
        "author": "",
        "creation_date": "2021-10-13",
        "last_update_date": "2021-10-13",
        "requirements": "none",
        "category": "Samsung Weather Clock",
        "notes": "",
        "paths": ('*/com.sec.android.daemonapp/databases/WeatherClock*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.daemonapp | 120 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.daemonapp | 24 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.daemonapp | 24 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.daemonapp | 24 rows",
            "sharon_a14": "Android 14 | com.sec.android.daemonapp | 24 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


def _weatherclock_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('WeatherClock'):
            return file_found
    return None


@artifact_processor
def get_samsungWeatherClockInfo(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = _weatherclock_db(files_found) or ''
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(COL_WEATHER_TIME/1000,'unixepoch'),
        COL_WEATHER_TIMEZONE,
        case COL_WEATHER_IS_DAYLIGHT_SAVING
            WHEN 0 THEN 'No'
            WHEN 1 THEN 'Yes'
        end,
        COL_WEATHER_CURRENT_TEMP,
        COL_WEATHER_WEATHER_TEXT,
        COL_WEATHER_NAME,
        COL_WEATHER_STATE,
        COL_WEATHER_COUNTRY,
        datetime(COL_WEATHER_UPDATE_TIME/1000,'unixepoch'),
        datetime(COL_WEATHER_SUNRISE_TIME/1000,'unixepoch'),
        datetime(COL_WEATHER_SUNSET_TIME/1000,'unixepoch'),
        COL_WEATHER_FEELSLIKE_TEMP,
        COL_WEATHER_HIGH_TEMP,
        COL_WEATHER_LOW_TEMP,
        COL_WEATHER_PROVIDER_NAME,
        COL_WEATHER_URL
        from TABLE_WEATHER_INFO
        ''')
        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],row[4],row[5],row[6],row[7],convert_human_ts_to_utc(row[8]),convert_human_ts_to_utc(row[9]),convert_human_ts_to_utc(row[10]),row[11],row[12],row[13],row[14],row[15]))
        db.close()

    data_headers = (
        ('Timestamp', 'datetime'), 'Timezone', 'Is Daylight Savings', 'Current Temp', 'Weather Text',
        'City', 'State', 'Country', ('Update Timestamp', 'datetime'), ('Sunrise Timestamp', 'datetime'),
        ('Sunset Timestamp', 'datetime'), 'Feels Like Temp', 'High Temp', 'Low Temp', 'Weather Provider', 'URL',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_samsungWeatherClockDaily(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = _weatherclock_db(files_found) or ''
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(TABLE_DAILY_INFO.COL_DAILY_TIME/1000,'unixepoch'),
        TABLE_WEATHER_INFO.COL_WEATHER_NAME,
        TABLE_WEATHER_INFO.COL_WEATHER_STATE,
        TABLE_WEATHER_INFO.COL_WEATHER_COUNTRY,
        TABLE_DAILY_INFO.COL_DAILY_CURRENT_TEMP,
        TABLE_DAILY_INFO.COL_DAILY_WEATHER_TEXT,
        TABLE_DAILY_INFO.COL_DAILY_URL,
        TABLE_DAILY_INFO.COL_DAILY_HIGH_TEMP,
        TABLE_DAILY_INFO.COL_DAILY_LOW_TEMP
        from TABLE_DAILY_INFO
        join TABLE_WEATHER_INFO on TABLE_DAILY_INFO.COL_WEATHER_KEY = TABLE_WEATHER_INFO.COL_WEATHER_KEY
        ''')
        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
        db.close()

    data_headers = (
        ('Timestamp', 'datetime'), 'City', 'State', 'Country', 'Current Temp',
        'Weather Text', 'URL', 'Daily High Temp', 'Daily Low Temp',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_samsungWeatherClockHourly(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = _weatherclock_db(files_found) or ''
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(TABLE_HOURLY_INFO.COL_HOURLY_TIME/1000,'unixepoch'),
        TABLE_WEATHER_INFO.COL_WEATHER_NAME,
        TABLE_WEATHER_INFO.COL_WEATHER_STATE,
        TABLE_WEATHER_INFO.COL_WEATHER_COUNTRY,
        TABLE_HOURLY_INFO.COL_HOURLY_CURRENT_TEMP,
        TABLE_HOURLY_INFO.COL_HOURLY_WEATHER_TEXT,
        TABLE_HOURLY_INFO.COL_HOURLY_RAIN_PROBABILITY,
        TABLE_HOURLY_INFO.COL_HOURLY_WIND_DIRECTION,
        TABLE_HOURLY_INFO.COL_HOURLY_WIND_SPEED,
        TABLE_HOURLY_INFO.COL_HOURLY_URL
        from TABLE_HOURLY_INFO
        join TABLE_WEATHER_INFO on TABLE_HOURLY_INFO.COL_WEATHER_KEY = TABLE_WEATHER_INFO.COL_WEATHER_KEY
        ''')
        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))
        db.close()

    data_headers = (
        ('Timestamp', 'datetime'), 'City', 'State', 'Country', 'Current Temp',
        'Weather Text', 'Rain Probability', 'Wind Direction', 'Wind Speed', 'URL',
    )
    return data_headers, data_list, source_path
