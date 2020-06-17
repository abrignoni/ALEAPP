import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_acquiring_contacts3(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
          ContactId,
	  DisplayName,
	  PhoneNumbers,
	  Emails,
	  Notes

    FROM acquired_contacts

    ORDER BY 
	  ContactId ASC
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Contacts')
        report.start_artifact_report(report_folder, 'Contacts')
        report.add_script()
        data_headers = ('Contact ID','Contact Name','Phone Number(s)','Email Address','Notes' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Contacts'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Contacts data available')
    
    db.close()
    return
