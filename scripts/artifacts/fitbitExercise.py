import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, kmlgen, timeline, is_platform_windows, open_sqlite_db_readonly

def get_fitbitExercise(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if not file_found.endswith('exercise_db'):
            continue # Skip all other files
        
        data_list =[]
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
                    data_list_current =[]
                    data_headers = ('Timestamp','Label','Latitude','Longitude','Accuracy','Altitude','Speed','Pace','Session_ID')
                    for row_exercise in all_rows_exercise:
                        data_list.append((row_exercise[0],row_exercise[1],row_exercise[2],row_exercise[3],row_exercise[4],row_exercise[5],row_exercise[6],row_exercise[7],row_exercise[8]))
                        data_list_current.append((row_exercise[0],row_exercise[1],row_exercise[2],row_exercise[3],row_exercise[4],row_exercise[5],row_exercise[6],row_exercise[7],row_exercise[8]))
                    
                    kmlactivity = f'Fitbit Map - Session ID {sessionID}'
                    kmlgen(report_folder, kmlactivity, data_list_current, data_headers)
                    
                    data_list_current =[]
                
            report = ArtifactHtmlReport('Fitbit Exercise')
            report.start_artifact_report(report_folder, 'Fitbit Exercise')
            report.add_script()
            
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Fitbit Exercise'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Fitbit Exercise'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No Fitbit - Exercise data available')
            
__artifacts__ = {
        "FitbitExercise": (
                "Fitbit",
                ('*/com.fitbit.FitbitMobile/databases/exercise_db*'),
                get_fitbitExercise)
}