import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_acquiring_contacts2(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        datetime(calls.date/1000, 'unixepoch'),
        calls.name,
        calls.number,
	CASE calls.type
            WHEN "1"
			THEN "Incoming Call"
            WHEN "2" 
			THEN "Outgoing Call"
	    WHEN "3" 
			THEN "Missed Call"
            ELSE "type"
            END 'Call Type/Direction'
    FROM calls

    ORDER BY 
	calls.date ASC
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Call Logs')
        report.start_artifact_report(report_folder, 'Call Logs')
        report.add_script()
        data_headers = ('Date/Time','Contact Name','Number','Call Type' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Call Logs'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Calls Logs data available')
    
    db.close()
    return
