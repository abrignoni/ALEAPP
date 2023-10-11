# Google Fit (GMS)
# Author:  Josh Hickman (josh@thebinaryhick.blog)
# Date 2021-02-05
# Version: 0.1
# Note:  This module only parses the Google Fit database found in com.google.android.gms/databases

import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_googleFitGMS(files_found, report_folder, seeker, wrap_text, time_offset):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('fitness.db'):
            break # Skip all other files
        
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(Sessions.start_time/1000,'unixepoch') AS "Activity Start Time",
    datetime(Sessions.end_time/1000,'unixepoch') AS "Activity End Time",
    Sessions.app_package AS "Contributing App",
    CASE
    WHEN Sessions.activity=7 THEN "Walking"
    WHEN Sessions.activity=8 THEN "Running"
    WHEN Sessions.activity=72 THEN "Sleeping"
    ELSE Sessions.activity
    END AS "Activity Type",
    Sessions.name AS "Activity Name",
    Sessions.description AS "Activity Description"
    FROM
    Sessions
    ORDER BY "Activity Start Time" ASC
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Google Fit (GMS)')
        report.start_artifact_report(report_folder, 'Activity Sessions')
        report.add_script()
        data_headers = ('Activity Start Time','Activity End Time','Contributing App','Activity Type','Activity Name','Activity Description') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Google Fit (GMS) - Activity Sessions'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Fit (GMS) - Activity Sessions'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Fit (GMS) - Activity Sessions data available')
                
__artifacts__ = {
        "GoogleFitGMS": (
                "Google Fit (GMS)",
                ('*/com.google.android.gms/databases/fitness.db.*'),
                get_googleFitGMS)
}