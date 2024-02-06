__artifacts_v2__ = {
    "Fitbit": {
        "name": "Fitbit",
        "description": "Parses Fitbit activities",
        "author": "@AlexisBrignoni",
        "version": "0.0.4",
        "date": "2021-04-23",
        "requirements": "none",
        "category": "Fitbit",
        "notes": "Updated 2023-12-12 by @segumarc, wrong file_found was wrote in the 'located at' field in the html report",
        "paths": ('*/com.fitbit.FitbitMobile/databases/activity_db*','*/com.fitbit.FitbitMobile/databases/device_database*','*/com.fitbit.FitbitMobile/databases/exercise_db*','*/com.fitbit.FitbitMobile/databases/heart_rate_db*','*/com.fitbit.FitbitMobile/databases/sleep*','*/com.fitbit.FitbitMobile/databases/social_db*','*/com.fitbit.FitbitMobile/databases/mobile_track_db*'),
        "function": "get_fitbit"
    }
}

import os
import sqlite3
import textwrap

from datetime import datetime, timezone
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_fitbit(files_found, report_folder, seeker, wrap_text, time_offset):
    
    data_list_activity = []
    data_list_devices = []
    data_list_exercises = []
    data_list_heart = []
    data_list_sleep_detail = []
    data_list_sleep_summary = []
    data_list_friends = []
    data_list_user = []
    data_list_steps = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('activity_db'):
            file_found_activity = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime("LOG_DATE"/1000, 'unixepoch'),
            datetime("TIME_CREATED"/1000, 'unixepoch'),
            NAME,
            LOG_TYPE,
            ACTIVE_DURATION,
            SPEED,
            PACE,
            ELEVATION_GAIN,
            AVERAGE_HEART_RATE,
            DISTANCE,
            DISTANCE_UNIT,
            DURATION,
            DURATION/60,
            STEPS,
            DETAILS_TYPE,
            CALORIES,
            MANUAL_CALORIES_POPULATED,
            SOURCE_NAME,
            SOURCE_TYPE,
            HAS_GPS,
            SWIM_LENGTHS,
            POOL_LENGTH,
            POOL_LENGTH_UNIT,
            VERY_ACTIVE_MINUTES,
            MODERATELY_ACTIVE_MINUTES,
            FAT_BURN_HEART_RATE_ZONE,
            CARDIO_HEART_RATE_ZONE,
            PEAK_HEART_RATE_ZONE
            FROM ACTIVITY_LOG_ENTRY
            ''')
    
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    log_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),time_offset)
                    time_create = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),time_offset)
                    data_list_activity.append((log_date,time_create,row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24],row[25],row[26],row[27],file_found))
            db.close() 

        if file_found.endswith('device_database'):
            file_found_device = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime(core_device.lastsynctime/1000, 'unixepoch') AS "Device Last Sync (UTC)",
            core_device.deviceName AS "Device Name",
            core_device.bleMacAddress AS "Bluetooth MAC Address",
            core_device.batteryPercent AS "Battery Percent",
            core_device.deviceType AS "Device Type"
            FROM core_device
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    last_sync = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),time_offset)
                    data_list_devices.append((last_sync,row[1],row[2],row[3],row[4],file_found))
            db.close()
            
        if file_found.endswith('exercise_db'):
            file_found_exercise = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            Select DISTINCT(SESSION_ID)
            from EXERCISE_EVENT
            ''')
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    sessionID = row[0]
                    cursor.execute(f'''
                    Select
                    datetime(TIME/1000,'unixepoch'),
                    LABEL,
                    LATITUDE,
                    LONGITUDE,
                    ACCURACY,
                    ALTITUDE,
                    SPEED,
                    PACE,
                    SESSION_ID
                    from EXERCISE_EVENT
                    where SESSION_ID = "{sessionID}" 
                    ''')
                    all_rows_exercise = cursor.fetchall()
                    usageentries_all = len(all_rows_exercise)
                    if usageentries_all > 0:
                        data_list_current = []
                        data_headers = ('Timestamp','Label','Latitude','Longitude','Accuracy','Altitude','Speed','Pace','Session_ID','Source')
                        for row_exercise in all_rows_exercise:
                            timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(row_exercise[0]),time_offset)
                            data_list_exercises.append((timestamp,row_exercise[1],row_exercise[2],row_exercise[3],row_exercise[4],row_exercise[5],row_exercise[6],row_exercise[7],row_exercise[8],file_found))
                            data_list_current.append((timestamp,row_exercise[1],row_exercise[2],row_exercise[3],row_exercise[4],row_exercise[5],row_exercise[6],row_exercise[7],row_exercise[8],file_found))
                        
                        kmlactivity = f'Fitbit Map - Session ID {sessionID}'
                        kmlgen(report_folder, kmlactivity, data_list_current, data_headers)
                        
                        data_list_current = []
            db.close()
            
        if file_found.endswith('heart_rate_db'):
            file_found_heart = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime("DATE_TIME"/1000, 'unixepoch'),
            AVERAGE_HEART_RATE,
            RESTING_HEART_RATE
            FROM HEART_RATE_DAILY_SUMMARY
            ''')
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    date_time = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),time_offset)
                    data_list_heart.append((date_time,row[1],row[2],file_found))
            db.close()
            
        if file_found.endswith('sleep'):
            file_found_sleep = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime("DATE_TIME"/1000, 'unixepoch'),
            SECONDS,
            LEVEL_STRING,
            LOG_ID
            FROM SLEEP_LEVEL_DATA
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    date_time = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),time_offset)
                    data_list_sleep_detail.append((date_time,row[1],row[2],row[3],file_found))
            
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime("DATE_OF_SLEEP"/1000, 'unixepoch'),
            datetime("START_TIME"/1000, 'unixepoch'),
            SYNC_STATUS_STRING,
            DURATION,
            DURATION/60000,
            MINUTES_AFTER_WAKEUP,
            MINUTES_ASLEEP,
            MINUTES_AWAKE,
            MINUTES_TO_FALL_ASLEEP,
            LOG_ID
            FROM
            SLEEP_LOG
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    date_of_sleep = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),time_offset)
                    start_time = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),time_offset)
                    data_list_sleep_summary.append((date_of_sleep,start_time,row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],file_found))
            db.close()
               
        if file_found.endswith('social_db'):
            file_found_social = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            OWNING_USER_ID,
            ENCODED_ID,
            DISPLAY_NAME,
            AVATAR_URL,
            FRIEND,
            CHILD
            FROM FRIEND
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    data_list_friends.append((row[0],row[1],row[2],row[3],row[4],row[5],file_found))

            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime("LAST_UPDATED"/1000, 'unixepoch'),
            DISPLAY_NAME,
            FULL_NAME,
            ABOUT_ME,
            AVATAR_URL,
            COVER_PHOTO_URL,
            CITY,
            STATE,
            COUNTRY,
            datetime("JOINED_DATE"/1000, 'unixepoch'),
            datetime("DATE_OF_BIRTH"/1000, 'unixepoch'),
            HEIGHT,
            WEIGHT,
            GENDER,
            COACH
            FROM USER_PROFILE
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    last_updated = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),time_offset)
                    joined_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[9]),time_offset)
                    dob_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[10]),time_offset)
                    data_list_user.append((last_updated,row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],joined_date,dob_date,row[11],row[12],row[13],row[14],file_found))
            db.close()
    
        if file_found.endswith('mobile_track_db'):
            file_found_mobile = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            datetime("TIMESTAMP"/1000, 'unixepoch'),
            STEPS_COUNT,
            METS_COUNT,
            datetime("TIME_CREATED"/1000, 'unixepoch'),
            datetime("TIME_UPDATED"/1000, 'unixepoch')
            FROM PEDOMETER_MINUTE_DATA
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),time_offset)
                    time_created = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[3]),time_offset)
                    time_updated = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[4]),time_offset)
                    data_list_steps.append((timestamp,row[1],row[2],time_created,time_updated,file_found))
            db.close()
    
        else:
            continue
 
    if data_list_activity:
        report = ArtifactHtmlReport('Fitbit Activity')
        report.start_artifact_report(report_folder, 'Fitbit Activity')
        report.add_script()
        data_headers = ('Timestamp','Time Created','Name','Log Type','Active Duration','SPEED','Pace','Elevation Gain','Avg Heart Rate','Distance','Distance Unit','Duration', 'Duration in Minutes','Steps','Details Type','Calories','Manual Calories Populated','Source Name','Source Type','Has GPS','Swim Lengths','Pool Length','Pool Length Unit','Very Active Minutes','Moderately Active Minutes','Fat Burn Heart Rate Zone','Cardio Heart Rate Zone','Peak Heart Rate Zone','Source File') 
        report.write_artifact_data_table(data_headers, data_list_activity, file_found_activity)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Activity'
        tsv(report_folder, data_headers, data_list_activity, tsvname)
        
        tlactivity = f'Fitbit Activity'
        timeline(report_folder, tlactivity, data_list_activity, data_headers)
    else:
        logfunc('No Fitbit Activity data available')
        
    if data_list_devices:
        report = ArtifactHtmlReport('Fitbit Device Info')
        report.start_artifact_report(report_folder, 'Fitbit Device Info')
        report.add_script()
        data_headers = ('Last Synced Timestamp','Device Name','Bluetooth MAC Address','Battery Percentage','Device Type','Source File') 
        
        report.write_artifact_data_table(data_headers, data_list_devices, file_found_device)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Device Info'
        tsv(report_folder, data_headers, data_list_devices, tsvname)
        
        tlactivity = f'Fitbit Device Info'
        timeline(report_folder, tlactivity, data_list_devices, data_headers)
    else:
        logfunc('No Fitbit Device Info data available')
    
    if data_list_exercises:
        report = ArtifactHtmlReport('Fitbit Exercise')
        report.start_artifact_report(report_folder, 'Fitbit Exercise')
        report.add_script()
        data_headers = ('Timestamp','Label','Latitude','Longitude','Accuracy','Altitude','Speed','Pace','Session_ID','Source File')
        
        report.write_artifact_data_table(data_headers, data_list_exercises, file_found_exercise)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Exercise'
        tsv(report_folder, data_headers, data_list_exercises, tsvname)
        
        tlactivity = f'Fitbit Exercise'
        timeline(report_folder, tlactivity, data_list_exercises, data_headers)
    else:
        logfunc(f'No Fitbit - Exercise data available')
        
    if data_list_heart:
        report = ArtifactHtmlReport('Fitbit Heart Rate Summary')
        report.start_artifact_report(report_folder, 'Fitbit Heart Rate Summary')
        report.add_script()
        data_headers = ('Timestamp','Avg. Heart Rate','Resting Heart Rate','Source File')
        
        report.write_artifact_data_table(data_headers, data_list_heart, file_found_heart)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Heart Rate Summary'
        tsv(report_folder, data_headers, data_list_heart, tsvname)
        
        tlactivity = f'Fitbit Heart Rate Summary'
        timeline(report_folder, tlactivity, data_list_heart, data_headers)
    else:
        logfunc('No Fitbit Heart Rate Summary data available')
                
    if data_list_sleep_detail:
        report = ArtifactHtmlReport('Fitbit Sleep Detail')
        report.start_artifact_report(report_folder, 'Fitbit Sleep Detail')
        report.add_script()
        data_headers = ('Timestamp','Seconds','Level','Log ID','Source File') 

        report.write_artifact_data_table(data_headers, data_list_sleep_detail, file_found_sleep)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Sleep Detail'
        tsv(report_folder, data_headers, data_list_sleep_detail, tsvname)
        
        tlactivity = f'Fitbit Sleep Detail'
        timeline(report_folder, tlactivity, data_list_sleep_detail, data_headers)
    else:
        logfunc('No Fitbit Sleep Detail data available')
        
    if data_list_sleep_summary:
        report = ArtifactHtmlReport('Fitbit Sleep Summary')
        report.start_artifact_report(report_folder, 'Fitbit Sleep Summary')
        report.add_script()
        data_headers = ('Timestamp','Start Time','Sync Status','Duration in Milliseconds','Duration in Minutes', 'Minutes After Wakeup', 'Minutes Asleep', 'Minutes Awake', 'Minutes to Fall Asleep', 'Log ID', 'Source File') 
        
        report.write_artifact_data_table(data_headers, data_list_sleep_summary, file_found_sleep)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Sleep Summary'
        tsv(report_folder, data_headers, data_list_sleep_summary, tsvname)
    else:
        logfunc('No Fitbit Sleep Summary data available')
    
    if data_list_friends:
        report = ArtifactHtmlReport('Fitbit Friends')
        report.start_artifact_report(report_folder, 'Fitbit Friends')
        report.add_script()
        data_headers = ('Owning UserID','Encoded ID','Display Name','Avatar URL','Friend','Child','Source File') 

        report.write_artifact_data_table(data_headers, data_list_friends, file_found_social)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Friends'
        tsv(report_folder, data_headers, data_list_friends, tsvname)
        
    else:
        logfunc('No Fitbit Friend data available')
      
    if data_list_user:
        report = ArtifactHtmlReport('Fitbit User Profile')
        report.start_artifact_report(report_folder, 'Fitbit User Profile')
        report.add_script()
        data_headers = ('Last Updated','Display Name','Full Name','About Me','Avatar URL', 'Cover Photo URL', 'City', 'State', 'Country', 'Joined Date','Date of Birth','Height','Weight','Gender','Coach','Source File') 
        
        report.write_artifact_data_table(data_headers, data_list_user, file_found_social)
        report.end_artifact_report()
        
        tsvname = f'Fitbit User Profile'
        tsv(report_folder, data_headers, data_list_user, tsvname)
        
        tlactivity = f'Fitbit User Profile'
        timeline(report_folder, tlactivity, data_list_user, data_headers)
        
    else:
        logfunc('No Fitbit User Profile data available')
        
    if data_list_steps:
        report = ArtifactHtmlReport('Fitbit Steps')
        report.start_artifact_report(report_folder, 'Fitbit Steps')
        report.add_script()
        data_headers = ('Timestamp','Steps Count','Mets Count','Time Created','Time Updated','Source File') 
        
        report.write_artifact_data_table(data_headers, data_list_steps, file_found_mobile)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Steps'
        tsv(report_folder, data_headers, data_list_steps, tsvname)
        
        tlactivity = f'Fitbit Steps'
        timeline(report_folder, tlactivity, data_list_steps, data_headers)
        
    else:
        logfunc('No Fitbit Steps data available')
        