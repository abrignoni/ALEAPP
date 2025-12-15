import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_firefoxFormHistory(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'formhistory.sqlite': # skip -journal and other files
            continue
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(firstUsed/1000000, 'unixepoch') AS FirstUsed,
        datetime(lastUsed/1000000, 'unixepoch') AS LastUsed,
        fieldname AS FieldName,
        value AS Value,
        timesUsed AS TimesUsed,
        id AS ID
        FROM moz_formhistory
        ORDER BY id ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox - Form History')
            report.start_artifact_report(report_folder, 'Firefox - Form History')
            report.add_script()
            data_headers = ('First Used Timestamp','Last Used Timestamp','Field Name','Value','Times Used','ID')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox - Form History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Firefox - Form History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox - Form History data available')
        
        db.close()
    
__artifacts__ = {
        "FirefoxFormHistory": (
                "Firefox",
                ('*/org.mozilla.firefox/files/mozilla/*.default/formhistory.sqlite*'),
                get_firefoxFormHistory)
}