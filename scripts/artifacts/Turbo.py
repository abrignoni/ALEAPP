import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Turbo(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
		case timestamp_millis
			when 0 then ''
			else datetime(timestamp_millis/1000,'unixepoch')
		End as D_T,
		battery_level,
		case charge_type
			when 0 then ''
			when 1 then 'Charging Rapidly'
			when 2 then 'Charging Slowly'
			when 3 then 'Charging Wirelessly'
		End as C_Type,
		case battery_saver
			when 2 then ''
			when 1 then 'Enabled'
		End as B_Saver,
		timezone
	from battery_event
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Turbo')
        report.start_artifact_report(report_folder, 'Turbo')
        report.add_script()
        data_headers = ('Date/Time','Battery %','Charge Type','Battery Saver','Timezone') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Turbo'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Turbo'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Turbo data available')
    
    db.close()
    return
