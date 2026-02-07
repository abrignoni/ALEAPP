# Module Description: Parses Fitbit data from Android (Phone) and Wear OS (Watch)

import json
import folium 
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

__artifacts_v2__ = {
    "Fitbit": {
        "name": "Fitbit Smartphone Data",
        "description": "Parses Fitbit activities from Android Smartphone app",
        "author": "@AlexisBrignoni",
        "version": "0.0.4",
        "date": "2021-04-23",
        "requirements": "none",
        "category": "Fitbit",
        "notes": "Updated 2023-12-12 by @segumarc",
        "paths": ('*/com.fitbit.FitbitMobile/databases/activity_db*','*/com.fitbit.FitbitMobile/databases/device_database*','*/com.fitbit.FitbitMobile/databases/exercise_db*','*/com.fitbit.FitbitMobile/databases/heart_rate_db*','*/com.fitbit.FitbitMobile/databases/sleep*','*/com.fitbit.FitbitMobile/databases/social_db*','*/com.fitbit.FitbitMobile/databases/mobile_track_db*'),
        "function": "get_fitbit"
    },
    "FitbitWearOS": {
        "name": "Fitbit Wear OS Data",
        "description": "Parses User DB and Passive Stats DB from Pixel Watch/Wear OS",
        "author": "Ganeshbs17",
        "version": "0.0.1",
        "date": "2026-01-12",
        "requirements": "none",
        "category": "Fitbit",
        "notes": "Specific to Pixel Watch/Wear OS",
        "paths": ('*/com.fitbit.FitbitMobile/databases/user.db*', '*/com.fitbit.FitbitMobile/databases/passive_stats.db*'),
        "function": "get_fitbit_wearos"
    }
}

def get_fitbit(files_found, report_folder, _seeker, _wrap_text):
    
    file_found_activity = ''
    file_found_device = ''
    file_found_exercise = ''
    file_found_heart = ''
    file_found_sleep = ''
    file_found_social = ''
    file_found_mobile = ''

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
                    log_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),'UTC')
                    time_create = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),'UTC')
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
                    last_sync = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),'UTC')
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
                            timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(row_exercise[0]),'UTC')
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
                    date_time = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),'UTC')
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
                    date_time = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),'UTC')
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
                    date_of_sleep = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),'UTC')
                    start_time = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[1]),'UTC')
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
                    last_updated = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),'UTC')
                    joined_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[9]),'UTC')
                    dob_date = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[10]),'UTC')
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
                    timestamp = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),'UTC')
                    time_created = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[3]),'UTC')
                    time_updated = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[4]),'UTC')
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
        
        tsvname = 'Fitbit Activity'
        tsv(report_folder, data_headers, data_list_activity, tsvname)
        
        tlactivity = 'Fitbit Activity'
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
        
        tsvname = 'Fitbit Device Info'
        tsv(report_folder, data_headers, data_list_devices, tsvname)
        
        tlactivity = 'Fitbit Device Info'
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
        
        tsvname = 'Fitbit Exercise'
        tsv(report_folder, data_headers, data_list_exercises, tsvname)
        
        tlactivity = 'Fitbit Exercise'
        timeline(report_folder, tlactivity, data_list_exercises, data_headers)
    else:
        logfunc('No Fitbit - Exercise data available')
        
    if data_list_heart:
        report = ArtifactHtmlReport('Fitbit Heart Rate Summary')
        report.start_artifact_report(report_folder, 'Fitbit Heart Rate Summary')
        report.add_script()
        data_headers = ('Timestamp','Avg. Heart Rate','Resting Heart Rate','Source File')
        
        report.write_artifact_data_table(data_headers, data_list_heart, file_found_heart)
        report.end_artifact_report()
        
        tsvname = 'Fitbit Heart Rate Summary'
        tsv(report_folder, data_headers, data_list_heart, tsvname)
        
        tlactivity = 'Fitbit Heart Rate Summary'
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
        
        tsvname = 'Fitbit Sleep Detail'
        tsv(report_folder, data_headers, data_list_sleep_detail, tsvname)
        
        tlactivity = 'Fitbit Sleep Detail'
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
        
        tsvname = 'Fitbit Sleep Summary'
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
        
        tsvname = 'Fitbit Friends'
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
        
        tsvname = 'Fitbit User Profile'
        tsv(report_folder, data_headers, data_list_user, tsvname)
        
        tlactivity = 'Fitbit User Profile'
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
        
        tsvname = 'Fitbit Steps'
        tsv(report_folder, data_headers, data_list_steps, tsvname)
        
        tlactivity = 'Fitbit Steps'
        timeline(report_folder, tlactivity, data_list_steps, data_headers)
        
    else:
        logfunc('No Fitbit Steps data available')

# pylint: disable=broad-exception-caught
def get_fitbit_wearos(files_found, report_folder, _seeker, _wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        # --- PROCESS USER.DB ---
        if file_found.endswith('user.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            # 1. User Profile
            try:
                cursor.execute('''
                SELECT
                    fullName,
                    displayName,
                    email,
                    gender,
                    dateOfBirth,
                    height,
                    weight,
                    memberSince,
                    userId
                FROM FitbitProfileEntity
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - User Profile (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - User Profile (Wear OS)','User account details including Display Name, DOB, Gender, and Join Date. Parsed from FitbitProfileEntity table.')
                    report.add_script()
                    data_headers = ('Full Name', 'Display Name', 'Email', 'Gender', 'DOB', 'Height', 'Weight', 'Member Since', 'User ID')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - User Profile (Wear OS)')
            except Exception as e:
                logfunc(f'Error parsing Fitbit Profile: {e}')

            # 2. Activity / Workout History
            try:
                cursor.execute('''
                SELECT
                    datetime(startTime/1000, 'unixepoch') as "Start Time",
                    name as "Activity Name",
                    duration/1000/60 as "Duration (Mins)",
                    distance,
                    distanceUnit,
                    steps,
                    calories,
                    averageHeartRate,
                    elevationGain,
                    activeZoneMinutes,
                    logId
                FROM ActivityExerciseEntity
                ORDER BY startTime DESC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - Activity History (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Activity History (Wear OS)', 'Log of exercises and activities including duration, distance, and calories. Parsed from ActivityExerciseEntity table.')
                    report.add_script()
                    data_headers = ('Start Time', 'Activity Name', 'Duration (Mins)', 'Distance', 'Unit', 'Steps', 'Calories', 'Avg HR', 'Elevation', 'AZM', 'Log ID')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - Activity History (Wear OS)')
                    timeline(report_folder, 'Fitbit - Activity History (Wear OS)', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit Activity History: {e}')

            # 3. DAILY Summaries
            try:
                cursor.execute('''
                SELECT
                    date,
                    totalMinutesMoving,
                    totalMinutesSedentary,
                    longestDuration as "Longest Sedentary Duration",
                    longestStart as "Longest Sedentary Start Time"
                FROM SedentaryDataEntity
                ORDER BY date DESC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - Daily Activity (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Daily Activity (Wear OS)','Daily summary of total minutes moved vs. sedentary minutes. Parsed from SedentaryDataEntity table.')
                    report.add_script()
                    data_headers = ('Date', 'Total Moving Mins', 'Total Sedentary Mins', 'Longest Sedentary Duration (Mins)', 'Longest Sedentary Start Time')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2], row[3], row[4]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - Daily Activity (Wear OS)')
                    timeline(report_folder, 'Fitbit - Daily Activity (Wear OS)', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit Daily Summaries: {e}')

            # 4. HOURLY Steps (Flattened JSON)
            try:
                cursor.execute('''
                SELECT
                    date,
                    hourlyData
                FROM SedentaryDataEntity
                ORDER BY date DESC
                ''')
                all_rows = cursor.fetchall()
                hourly_data_list = []
                for row in all_rows:
                    date_str = row[0]
                    json_data = row[1]
                    if json_data:
                        try:
                            parsed_json = json.loads(json_data)
                            hourly_list = parsed_json.get('hourlyData', [])
                            for hour_entry in hourly_list:
                                time_str = hour_entry.get('dateTime', '')
                                steps_str = hour_entry.get('steps', '0')
                                full_timestamp = f"{date_str} {time_str}"
                                hourly_data_list.append((full_timestamp, date_str, time_str, steps_str))
                        except ValueError:
                            pass
                if len(hourly_data_list) > 0:
                    report = ArtifactHtmlReport('Fitbit - Hourly Steps (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Hourly Steps (Wear OS)','Granular hourly step counts parsed from JSON blobs stored in the SedentaryDataEntity table.')
                    report.add_script()
                    data_headers = ('Full Timestamp', 'Date', 'Time', 'Steps')
                    report.write_artifact_data_table(data_headers, hourly_data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, hourly_data_list, 'Fitbit - Hourly Steps (Wear OS)')
                    timeline(report_folder, 'Fitbit - Hourly Steps (Wear OS)', hourly_data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit Hourly Steps: {e}')

            # 5. Sleep Logs
            try:
                cursor.execute('''
                SELECT
                    datetime(startTime/1000, 'unixepoch') as "Sleep Start",
                    datetime(endTime/1000, 'unixepoch') as "Sleep End",
                    dateOfSleep,
                    minutesAsleep,
                    minutesAwake,
                    minutesToFallAsleep,
                    minutesAfterWakeup,
                    type as "Sleep Type",
                    isMainSleep
                FROM FitbitSleepDateEntity
                ORDER BY startTime DESC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - Sleep Logs (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Sleep Logs (Wear OS)','Main sleep session logs including start/end times and sleep stages. Parsed from FitbitSleepDateEntity table.')
                    report.add_script()
                    data_headers = ('Sleep Start', 'Sleep End', 'Date of Sleep', 'Mins Asleep', 'Mins Awake', 'Time to Fall Asleep', 'Time After Wakeup', 'Type', 'Is Main Sleep')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - Sleep Logs (Wear OS)')
                    timeline(report_folder, 'Fitbit - Sleep Logs (Wear OS)', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit Sleep Logs: {e}')
            
            db.close()

        # --- PROCESS PASSIVE_STATS.DB ---
        elif file_found.endswith('passive_stats.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            # 1. Exercise Summaries
            try:
                cursor.execute('''
                SELECT
                    datetime(time/1000, 'unixepoch') as "Start Time",
                    sessionId,
                    exerciseTypeId as "Activity Type ID",
                    totalDistanceMm / 1000000.0 as "Distance (KM)",
                    steps,
                    caloriesBurned,
                    avgHeartRate,
                    elevationGainFt
                FROM ExerciseSummaryEntity
                ORDER BY time DESC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - Workouts (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Workouts (Wear OS)','Workout summaries including steps, calories etc. Parsed from ExerciseSummaryEntity table.')
                    report.add_script()
                    data_headers = ('Start Time', 'Session ID', 'Activity Type ID', 'Distance (KM)', 'Steps', 'Calories', 'Avg HR', 'Elevation (ft)')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - Workouts (Wear OS)')
                    timeline(report_folder, 'Fitbit - Workouts (Wear OS)', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit Workouts: {e}')

            # 2. Exercise GPS
            try:
                cursor.execute('''
                SELECT
                    datetime(time/1000, 'unixepoch') as "Timestamp",
                    latitude,
                    longitude,
                    altitude,
                    speed,
                    bearing,
                    estimatedPositionError
                FROM ExerciseGpsEntity
                ORDER BY time ASC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    # 1. Generate the standard text report first
                    report = ArtifactHtmlReport('Fitbit - GPS Trackpoints (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - GPS Trackpoints (Wear OS)', 'GPS Coordinates. <b><a href="Fitbit/Fitbit_GPS_Map.html" target="_blank">click here to open in new tab</a></b>')
                    report.add_script()

                    data_headers = ('Timestamp', 'Latitude', 'Longitude', 'Altitude', 'Speed', 'Est. Error')
                    data_list = []
                    points = []

                    for row in all_rows:
                        # Add to text report
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[6]))
                        
                        # Add to Map Points (Filter out valid 0.0 or nulls if needed)
                        if row[1] and row[2]:
                            points.append((row[1], row[2]))

                    # ---------------------------------------------------------
                    # MAP GENERATION (Folium)
                    # ---------------------------------------------------------
                    if len(points) > 0:
                        try:
                            # Center map on the first point
                            m = folium.Map(location=points[0], zoom_start=13, tiles='OpenStreetMap')
                            
                            # Add the route line
                            folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)
                            
                            # Add Start/End markers
                            folium.Marker(points[0], popup='Start', icon=folium.Icon(color='green', icon='play')).add_to(m)
                            folium.Marker(points[-1], popup='End', icon=folium.Icon(color='red', icon='stop')).add_to(m)

                            # Save HTML map to the report folder
                            map_filename = 'Fitbit_GPS_Map.html'
                            map_path = os.path.join(report_folder, map_filename)
                            m.save(map_path)
                            
                            logfunc(f'Map generated: {map_path}')
                        except Exception as e:
                            logfunc(f'Error generating map: {str(e)}')
                    # ---------------------------------------------------------

                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    
                    # --- START: INJECT IFRAME AT BOTTOM ---
                    if len(points) > 0:
                        report.add_section_heading('Interactive Map Preview')
                        report.add_map('<iframe src="Fitbit/Fitbit_GPS_Map.html" width="100%" height="600" class="map"></iframe>')
                    # --- END: INJECT IFRAME AT BOTTOM ---

                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - GPS Trackpoints (Wear OS)')
                    timeline(report_folder, 'Fitbit - GPS Trackpoints (Wear OS)', data_list, data_headers)
                    kmlgen(report_folder, 'Fitbit_GPS_WearOS', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit GPS: {e}')

            # 3. Heart Rate Stats
            try:
                cursor.execute('''
                SELECT
                    datetime(startTime/1000, 'unixepoch') as "Start Time",
                    datetime(endTime/1000, 'unixepoch') as "End Time",
                    value as "BPM",
                    accuracy
                FROM HeartRateStatEntity
                ORDER BY startTime DESC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - Heart Rate Stats (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Heart Rate Stats (Wear OS)','Heart rate statistics (BPM). Parsed from HeartRateStatEntity table.')
                    report.add_script()
                    data_headers = ('Start Time', 'End Time', 'BPM', 'Accuracy')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2], row[3]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - Heart Rate Stats (Wear OS)')
                    timeline(report_folder, 'Fitbit - Heart Rate Stats (Wear OS)', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit HR Stats: {e}')

            # 4. Live Pace
            try:
                cursor.execute('''
                SELECT
                    datetime(timeSeconds/1000, 'unixepoch') as "Timestamp",
                    sessionId,
                    statType,
                    value
                FROM LivePaceEntity
                ORDER BY timeSeconds DESC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - Live Pace (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Live Pace (Wear OS)','Live pace statistics during workouts. Parsed from LivePaceEntity table.')
                    report.add_script()
                    data_headers = ('Timestamp', 'Session ID', 'Stat Type', 'Value')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2], row[3]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - Live Pace (Wear OS)')
                    timeline(report_folder, 'Fitbit - Live Pace (Wear OS)', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit Live Pace: {e}')

            # 5. Sleep Periods
            try:
                cursor.execute('''
                SELECT
                    datetime(sleepStartTime/1000, 'unixepoch') as "Sleep Start",
                    datetime(sleepEndTime/1000, 'unixepoch') as "Sleep End",
                    (sleepEndTime - sleepStartTime)/1000/60 as "Duration (Mins)"
                FROM LocalSleepPeriodsEntity
                ORDER BY sleepStartTime DESC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - Sleep (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Sleep (Wear OS)', 'Raw sleep periods detected by device. Parsed from LocalSleepPeriodsEntity table.')
                    report.add_script()
                    data_headers = ('Sleep Start', 'Sleep End', 'Duration (Mins)')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - Sleep (Wear OS)')
                    timeline(report_folder, 'Fitbit - Sleep (Wear OS)', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit Sleep: {e}')

            # 6. Active Zone Minutes
            try:
                cursor.execute('''
                SELECT
                    datetime(startTime/1000, 'unixepoch') as "Start Time",
                    datetime(endTime/1000, 'unixepoch') as "End Time",
                    activeZone,
                    value as "Points",
                    lastBpm
                FROM PassiveAzmEntity
                ORDER BY startTime DESC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - Active Zones (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Active Zones (Wear OS)','Minutes spent in elevated heart rate zones (Fat Burn = 1x, Cardio/Peak = 2x). Indicates physical exertion intensity. Parsed from PassiveAzmEntity table.')
                    report.add_script()
                    data_headers = ('Start Time', 'End Time', 'Zone ID', 'Points', 'Last BPM')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2], row[3], row[4]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - Active Zones (Wear OS)')
                    timeline(report_folder, 'Fitbit - Active Zones (Wear OS)', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit AZM: {e}')

            # 7. Exercise Splits
            try:
                cursor.execute('''
                SELECT
                    datetime(time/1000, 'unixepoch') as "Split Time",
                    sessionId,
                    avgPaceMilliSecPerKm / 1000 / 60.0 as "Avg Pace (Min/Km)",
                    avgHeartRate,
                    steps,
                    caloriesBurned
                FROM ExerciseSplitAnnotationEntity
                ORDER BY time ASC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - Workout Splits (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Workout Splits (Wear OS)','Performance metrics (Pace, HR, Steps). Parsed from ExerciseSplitAnnotationEntity table.')
                    report.add_script()
                    data_headers = ('Split Time', 'Session ID', 'Avg Pace (Min/Km)', 'Avg HR', 'Steps', 'Calories')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - Workout Splits (Wear OS)')
                    timeline(report_folder, 'Fitbit - Workout Splits (Wear OS)', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit Splits: {e}')

            # 8. Opaque HR
            try:
                cursor.execute('''
                SELECT
                    datetime(timestamp/1000, 'unixepoch') as "Timestamp",
                    baseHeartRate as "Base HR",
                    confidence as "Confidence (0-3)"
                FROM OpaqueHeartRateEntity
                ORDER BY timestamp DESC
                ''')
                all_rows = cursor.fetchall()
                if len(all_rows) > 0:
                    report = ArtifactHtmlReport('Fitbit - Opaque HR (Wear OS)')
                    report.start_artifact_report(report_folder, 'Fitbit - Opaque HR (Wear OS)','Raw heart rate sensor readings. Parsed from OpaqueHeartRateEntity table.')
                    report.add_script()
                    data_headers = ('Timestamp', 'Base HR', 'Confidence')
                    data_list = []
                    for row in all_rows:
                        data_list.append((row[0], row[1], row[2]))
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    tsv(report_folder, data_headers, data_list, 'Fitbit - Opaque HR (Wear OS)')
                    timeline(report_folder, 'Fitbit - Opaque HR (Wear OS)', data_list, data_headers)
            except Exception as e:
                logfunc(f'Error parsing Fitbit Opaque HR: {e}')

            db.close()