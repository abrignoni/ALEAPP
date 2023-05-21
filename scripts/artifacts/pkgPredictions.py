# Package Predictions - Parses Samsung package prediction details
# Author:  Kevin Pagano (https://startme.stark4n6.com)
# Date 2023-05-01
# Version: 0.1
# Requirements:  None

import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen

def get_pkgPredictions(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)  
        if file_found.endswith('PkgPredictions.db'):
            break
        else:
            continue # Skip all other files
            
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(launch_time/1000,'unixepoch') as "Launch Timestamp",
    running_pkg,
    apk_version,
    activity_name,
    previous_one,
    previous_two,
    previous_three,
    case screen_orientation
        when 0 then 'Vertical'
        when 1 then 'Horizontal'
    end as "Screen Orientation",
    wifi_status,
    bt_status,
    hour_of_day,
    case day_of_week
        when 1 then 'Sunday'
        when 2 then 'Monday'
        when 3 then 'Tuesday'
        when 4 then 'Wednesday'
        when 5 then 'Thursday'
        when 6 then 'Friday'
        when 7 then 'Saturday'
    end as "Day of Week",
    prediction,
    predict_time,
    user_id,
    id
    from tbl_Sample
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Package Predictions')
        report.start_artifact_report(report_folder, 'Package Predictions')
        report.add_script()
        data_headers = ('Launch Timestamp','Running Package','APK Version','Activity Name','Previous Launch (1)','Previous Launch (2)','Previous Launch (3)','Screen Orientation','Wifi Status','Bluetooth Status','Hour of Launch (Local)','Day of Launch','Prediction','Predict Time','User ID','ID')
        
        data_list = []
        for row in all_rows:
            predictions = row[12].replace('0_&_','').replace(';','\n')
        
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],predictions,row[13],row[14],row[15]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Package Predictions'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Package Predictions'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Package Predictions data available')
                
    db.close()

__artifacts__ = {
        "pkgPredictions": (
                "Package Predictions",
                ('*/system/PkgPredictions.db*'),
                get_pkgPredictions)
}
    