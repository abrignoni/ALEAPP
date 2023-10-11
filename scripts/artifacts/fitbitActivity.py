import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_fitbitActivity(files_found, report_folder, seeker, wrap_text, time_offset):
    
    file_found = str(files_found[0])
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
        report = ArtifactHtmlReport('Fitbit Activity')
        report.start_artifact_report(report_folder, 'Fitbit Activity')
        report.add_script()
        data_headers = ('Timestamp','Time Created','Name','Log Type','Active Duration','SPEED','Pace','Elevation Gain','Avg Heart Rate','Distance','Distance Unit','Duration', 'Duration in Minutes','Steps','Details Type','Calories','Manual Calories Populated','Source Name','Source Type','Has GPS','Swim Lengths','Pool Length','Pool Length Unit','Very Active Minutes','Moderately Active Minutes','Fat Burn Heart Rate Zone','Cardio Heart Rate Zone','Peak Heart Rate Zone') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24],row[25],row[26],row[27]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Activity'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Fitbit Activity'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Fitbit Activity data available')
        
    db.close()
    
__artifacts__ = {
        "FitbitActivity": (
                "Fitbit",
                ('*/com.fitbit.FitbitMobile/databases/activity_db*'),
                get_fitbitActivity)
}

    