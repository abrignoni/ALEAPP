__artifacts_v2__ = {
    "get_rdd_analytics": {
        "name": "VerizonRDD-Battery",
        "description": "Module Description: Parses Verizon RDD Analytics Battery History",
        "author": "John Hyla",
        "creation_date": "2023-07-07",
        "last_update_date": "2023-07-07",
        "requirements": "none",
        "category": "Verizon RDD Analytics",
        "notes": "",
        "paths": ('*/com.verizon.mips.services/databases/RDD_ANALYTICS_DATABASE',),
        "output_types": None,
        "artifact_icon": "battery",
    }
}

import os
import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_rdd_analytics(files_found, report_folder, seeker, wrap_text):

    source_file = ''
    for file_found in files_found:
        file_name = str(file_found)

        db = open_sqlite_db_readonly(file_name)
        cursor = db.cursor()
        try:

            cursor.execute('''
                SELECT datetime(ActualTime/1000, "UNIXEPOCH") as actual_time, 
                FormattedTime,
                BatteryLevel, 
                GPS, 
                Charging, 
                ScreenOn,
                Brightness, 
                BatteryTemp
                  FROM TableBatteryHistory
                  ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except Exception as e:
            print (e)
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('Verizon RDD - Battery History')
            report.start_artifact_report(report_folder, 'Verizon RDD - Battery History')
            report.add_script()
            data_headers = ('ActualTime', 'FormattedTime', 'BatteryLevel', 'GPS', 'Charging', 'ScreenOn', 'Brightness', 'BatteryTemp') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Verizon RDD - Battery History'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)
            
        else:
            logfunc('No Battery History found')
            

        db.close()
    
    return

