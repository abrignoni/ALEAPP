# Module Description: Parses Fitbit User DB from Wear OS devices to extract user profile, activity history, daily summaries, hourly steps, and sleep logs.
# Author: ganeshbs17
# Date: 2025-01-09
# Artifact version: 1.0.4
# Requirements: none

import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

def get_fitbit_user_db(files_found, report_folder, seeker, wrap_text):
    
    source_db = ''
    for file_found in files_found:
        if file_found.endswith('user.db'):
            source_db = file_found
            break
            
    if source_db:
        db = open_sqlite_db_readonly(source_db)
        cursor = db.cursor()

        # -----------------------------------------------------------------------
        # 1. User Profile
        # -----------------------------------------------------------------------
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
                report = ArtifactHtmlReport('Fitbit - User Profile')
                report.start_artifact_report(report_folder, 'Fitbit - User Profile')
                report.add_script()
                
                data_headers = ('Full Name', 'Display Name', 'Email', 'Gender', 'DOB', 'Height', 'Weight', 'Member Since', 'User ID')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - User Profile')
            else:
                logfunc('No Fitbit User Profile found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit Profile: {e}')

        # -----------------------------------------------------------------------
        # 2. Activity / Workout History
        # -----------------------------------------------------------------------
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
                report = ArtifactHtmlReport('Fitbit - Activity History')
                report.start_artifact_report(report_folder, 'Fitbit - Activity History')
                report.add_script()
                
                data_headers = ('Start Time', 'Activity Name', 'Duration (Mins)', 'Distance', 'Unit', 'Steps', 'Calories', 'Avg HR', 'Elevation', 'AZM', 'Log ID')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - Activity History')
                timeline(report_folder, 'Fitbit - Activity History', data_list, data_headers)
            else:
                logfunc('No Fitbit Activity History found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit Activity History: {e}')

        # -----------------------------------------------------------------------
        # 3. DAILY Summaries (One row per day)
        # -----------------------------------------------------------------------
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
            
            daily_rows = cursor.fetchall()
            
            if len(daily_rows) > 0:
                report = ArtifactHtmlReport('Fitbit - Daily Activity Summary')
                report.start_artifact_report(report_folder, 'Fitbit - Daily Activity Summary')
                report.add_script()
                
                data_headers = ('Date', 'Total Moving Mins', 'Total Sedentary Mins', 'Longest Sedentary Duration (Mins)', 'Longest Sedentary Start Time')
                data_list = []
                for row in daily_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - Daily Activity Summary')
                # Timeline optional for Daily stats, but good for overview
                timeline(report_folder, 'Fitbit - Daily Activity Summary', data_list, data_headers)
            else:
                logfunc('No Fitbit Daily Summaries found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit Daily Summaries: {e}')

        # -----------------------------------------------------------------------
        # 4. HOURLY Steps (Flattened JSON)
        # -----------------------------------------------------------------------
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
                            
                            # Create a full timestamp for the timeline
                            full_timestamp = f"{date_str} {time_str}"
                            
                            hourly_data_list.append((full_timestamp, date_str, time_str, steps_str))
                            
                    except ValueError:
                        pass

            if len(hourly_data_list) > 0:
                report = ArtifactHtmlReport('Fitbit - Hourly Steps')
                report.start_artifact_report(report_folder, 'Fitbit - Hourly Steps')
                report.add_script()
                
                data_headers = ('Full Timestamp', 'Date', 'Time', 'Steps')

                report.write_artifact_data_table(data_headers, hourly_data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, hourly_data_list, 'Fitbit - Hourly Steps')
                timeline(report_folder, 'Fitbit - Hourly Steps', hourly_data_list, data_headers)
            else:
                logfunc('No Fitbit Hourly Steps found')

        except Exception as e:
            logfunc(f'Error parsing Fitbit Hourly Steps: {e}')

        # -----------------------------------------------------------------------
        # 5. Sleep Logs
        # -----------------------------------------------------------------------
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
                report = ArtifactHtmlReport('Fitbit - Sleep Logs')
                report.start_artifact_report(report_folder, 'Fitbit - Sleep Logs')
                report.add_script()
                
                data_headers = ('Sleep Start', 'Sleep End', 'Date of Sleep', 'Mins Asleep', 'Mins Awake', 'Time to Fall Asleep', 'Time After Wakeup', 'Type', 'Is Main Sleep')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - Sleep Logs')
                timeline(report_folder, 'Fitbit - Sleep Logs', data_list, data_headers)
            else:
                logfunc('No Fitbit Sleep Logs found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit Sleep Logs: {e}')

        db.close()
    else:
        logfunc('Fitbit user.db not found')

__artifacts__ = {
        "FitbitUserDb": (
                "Fitbit",
                ('*/databases/user.db'),
                get_fitbit_user_db)
}