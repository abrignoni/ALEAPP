import sqlite3
import os
import textwrap

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_frosting(files_found, report_folder, seeker, wrap_text, time_offset):
    
    
    for file_found in files_found:
        file_name = str(file_found)
        if not file_found.endswith('frosting.db'):
            continue # Skip all other files
            
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        case last_updated
            when 0 then ''
            else datetime(last_updated/1000,'unixepoch')
        end	as "Last Updated",
        pk,
        apk_path
        from frosting
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('App Updates (Frosting.db)')
            report.start_artifact_report(report_folder, 'App Updates (Frosting.db)')
            report.add_script()
            data_headers = ('Last Updated Timestamp','App Package Name','APK Path') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'App Updates (Frosting.db)'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'App Updates (Frosting.db)'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No App Updates (Frosting.db) data available')
        
        db.close()

__artifacts__ = {
        "frosting": (
                "Installed Apps",
                ('*/com.android.vending/databases/frosting.db*'),
                get_frosting)
}