# Module Description: Parses Fitbit Passive Stats DB from Wear OS 
# Author: ganeshbs17
# Date: 2025-01-09
# Artifact version: 1.0.2
# Requirements: none

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

def get_fitbit_passive_stats(files_found, report_folder, seeker, wrap_text):
    
    # Locate the specific database file
    source_db = ''
    for file_found in files_found:
        if file_found.endswith('passive_stats.db'):
            source_db = file_found
            break
            
    if source_db:
        db = open_sqlite_db_readonly(source_db)
        cursor = db.cursor()

        # -----------------------------------------------------------------------
        # 1. Exercise Summaries 
        # -----------------------------------------------------------------------
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
                report = ArtifactHtmlReport('Fitbit - Workouts')
                report.start_artifact_report(report_folder, 'Fitbit - Workouts')
                report.add_script()
                
                data_headers = ('Start Time', 'Session ID', 'Activity Type ID', 'Distance (KM)', 'Steps', 'Calories', 'Avg HR', 'Elevation (ft)')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - Workouts')
                timeline(report_folder, 'Fitbit - Workouts', data_list, data_headers)
            else:
                logfunc('No Fitbit Workout Summaries found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit Workouts: {e}')

        # -----------------------------------------------------------------------
        # 2. Exercise GPS Data (Track Points)
        # -----------------------------------------------------------------------
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
                report = ArtifactHtmlReport('Fitbit - GPS Trackpoints')
                report.start_artifact_report(report_folder, 'Fitbit - GPS Trackpoints')
                report.add_script()
                
                data_headers = ('Timestamp', 'Latitude', 'Longitude', 'Altitude', 'Speed', 'Bearing', 'Est. Error')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - GPS Trackpoints')
                timeline(report_folder, 'Fitbit - GPS Trackpoints', data_list, data_headers)
            else:
                logfunc('No Fitbit GPS data found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit GPS: {e}')

        # -----------------------------------------------------------------------
        # 3. Heart Rate Stats 
        # -----------------------------------------------------------------------
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
                report = ArtifactHtmlReport('Fitbit - Heart Rate Stats')
                report.start_artifact_report(report_folder, 'Fitbit - Heart Rate Stats')
                report.add_script()
                
                data_headers = ('Start Time', 'End Time', 'BPM', 'Accuracy')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - Heart Rate Stats')
                timeline(report_folder, 'Fitbit - Heart Rate Stats', data_list, data_headers)
            else:
                logfunc('No Fitbit Heart Rate Stats found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit HR Stats: {e}')

        # -----------------------------------------------------------------------
        # 4. Live Pace
        # -----------------------------------------------------------------------
        try:
            # Note: timeSeconds column contains milliseconds in newer app versions
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
                report = ArtifactHtmlReport('Fitbit - Live Pace')
                report.start_artifact_report(report_folder, 'Fitbit - Live Pace')
                report.add_script()
                
                data_headers = ('Timestamp', 'Session ID', 'Stat Type', 'Value')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - Live Pace')
                timeline(report_folder, 'Fitbit - Live Pace', data_list, data_headers)
            else:
                logfunc('No Fitbit Live Pace data found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit Live Pace: {e}')

        # -----------------------------------------------------------------------
        # 5. Sleep Periods
        # -----------------------------------------------------------------------
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
                report = ArtifactHtmlReport('Fitbit - Sleep')
                report.start_artifact_report(report_folder, 'Fitbit - Sleep')
                report.add_script()
                
                data_headers = ('Sleep Start', 'Sleep End', 'Duration (Mins)')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - Sleep')
                timeline(report_folder, 'Fitbit - Sleep', data_list, data_headers)
            else:
                logfunc('No Fitbit Sleep data found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit Sleep: {e}')

        # -----------------------------------------------------------------------
        # 6. Active Zone Minutes (AZM)
        # -----------------------------------------------------------------------
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
                report = ArtifactHtmlReport('Fitbit - Active Zones')
                report.start_artifact_report(report_folder, 'Fitbit - Active Zones')
                report.add_script()
                
                data_headers = ('Start Time', 'End Time', 'Zone ID', 'Points', 'Last BPM')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - Active Zones')
                timeline(report_folder, 'Fitbit - Active Zones', data_list, data_headers)
            else:
                logfunc('No Fitbit AZM data found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit AZM: {e}')

        # -----------------------------------------------------------------------
        # 7. Exercise Splits (Pace/Km)
        # -----------------------------------------------------------------------
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
                report = ArtifactHtmlReport('Fitbit - Workout Splits')
                report.start_artifact_report(report_folder, 'Fitbit - Workout Splits')
                report.add_script()
                
                data_headers = ('Split Time', 'Session ID', 'Avg Pace (Min/Km)', 'Avg HR', 'Steps', 'Calories')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - Workout Splits')
                timeline(report_folder, 'Fitbit - Workout Splits', data_list, data_headers)
            else:
                logfunc('No Fitbit Splits found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit Splits: {e}')

        # -----------------------------------------------------------------------
        # 8. Opaque Heart Rate (Raw Sensor Data)
        # -----------------------------------------------------------------------
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
                report = ArtifactHtmlReport('Fitbit - Opaque HR')
                report.start_artifact_report(report_folder, 'Fitbit - Opaque HR')
                report.add_script()
                
                data_headers = ('Timestamp', 'Base HR', 'Confidence')
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2]))

                report.write_artifact_data_table(data_headers, data_list, source_db)
                report.end_artifact_report()
                
                tsv(report_folder, data_headers, data_list, 'Fitbit - Opaque HR')
                timeline(report_folder, 'Fitbit - Opaque HR', data_list, data_headers)
            else:
                logfunc('No Fitbit Opaque HR data found')
        except Exception as e:
            logfunc(f'Error parsing Fitbit Opaque HR: {e}')

        db.close()
    else:
        logfunc('Fitbit passive_stats.db not found')

__artifacts__ = {
        "FitbitPassiveStats": (
                "Fitbit",
                ('*/databases/passive_stats.db'),
                get_fitbit_passive_stats)
}
