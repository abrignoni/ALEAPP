import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_providers_calendar(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
          Calendars.account_name,
	  Events.title,
	  Events.eventLocation,
	  Events.description,
	  datetime(Events.dtstart/1000, 'unixepoch'),
	  datetime(Events.dtend/1000, 'unixepoch'),
	  Events.eventTimezone
    FROM Events
    INNER JOIN Calendars ON Calendars._id = Events.calendar_id
    ORDER BY 
	  Events.dtstart DESC
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Calendars')
        report.start_artifact_report(report_folder, 'Calendars')
        report.add_script()
        data_headers = ('Calendar Account','Event Title','Event Location','Event Description','Event Start Date/Time','Event End Date/Time','Event Timezone' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Calendars'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Calendar data available')
    
    db.close()
    return
