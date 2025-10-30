import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_samsungWeatherClock(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('WeatherClock'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
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
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Samsung Weather Clock - Info')
            report.start_artifact_report(report_folder, 'Samsung Weather Clock - Info')
            report.add_script()
            data_headers = ('Timestamp','Timezone','Is Daylight Savings','Current Temp','Weather Text','City','State','Country','Update Timestamp','Sunrise Timestamp','Sunset Timestamp','Feels Like Temp','High Temp','Low Temp','Weather Provider','URL') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Samsung Weather Clock - Info'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Samsung Weather Clock - Info'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Samsung Weather Clock - Info data available')
    
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
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Samsung Weather Clock - Daily')
            report.start_artifact_report(report_folder, 'Samsung Weather Clock - Daily')
            report.add_script()
            data_headers = ('Timestamp','City','State','Country','Current Temp','Weather Text','URL','Daily High Temp','Daily Low Temp') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Samsung Weather Clock - Daily'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Samsung Weather Clock - Daily'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Samsung Weather Clock - Daily data available')
    
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
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Samsung Weather Clock - Hourly')
            report.start_artifact_report(report_folder, 'Samsung Weather Clock - Hourly')
            report.add_script()
            data_headers = ('Timestamp','City','State','Country','Current Temp','Weather Text','Rain Probability','Wind Direction','Wind Speed','URL') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Samsung Weather Clock - Hourly'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Samsung Weather Clock - Hourly'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Samsung Weather Clock - Hourly data available')
        
    db.close()

__artifacts__ = {
        "samsungWeatherClock": (
                "Samsung Weather Clock",
                ('*/com.sec.android.daemonapp/databases/WeatherClock*'),
                get_samsungWeatherClock)
}

