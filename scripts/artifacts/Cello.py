import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Cello(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
		title,
		case created_date
			when 0 then ''
			else datetime(created_date/1000, 'unixepoch')
		end	as C_D,
		case modified_date
			when 0 then ''
			else datetime(modified_date/1000, 'unixepoch')
		end as M_D,
		case shared_with_me_date
			when 0 then ''
			else datetime(shared_with_me_date/1000, 'unixepoch')
		end	as Shared_D,
		case modified_by_me_date
			when 0 then ''
			else datetime(modified_by_me_date/1000, 'unixepoch')
		end as M_M_D,
		case viewed_by_me_date
			when 0 then ''
			else datetime(viewed_by_me_date/1000, 'unixepoch')
		end	as V_D,
		mime_type,
        Quota_bytes,
		case is_folder
			when 0 then ''
			when 1 then 'Yes'
		end as FOLDER_ITEM,
		case is_owner
			when 0 then ''
			when 1 then 'Yes'
		end as OWNER_ITEM,
		case trashed
			when 0 then ''
			when 1 then 'Yes'
		end as DELETED_ITEM
	FROM items
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Cello')
        report.start_artifact_report(report_folder, 'Cello')
        report.add_script()
        data_headers = ('File Name','Created Date','Modified Date','Shared with User Date','Modified by User Date','Viewed by User Date','Mime Type','Quota Size','Folder','User is Owner','Deleted') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Google Docs - Cello'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Docs - Cello'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Docs - Cello data available')
    
    db.close()
    return
