import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_protonmailContacts(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('ContactsDatabase.db'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(fullContactsDetails.CreateTime,'unixepoch') AS 'Creation Timestamp',
        datetime(fullContactsDetails.ModifyTIme,'unixepoch') AS 'Modified Timestamp',
        fullContactsDetails.Name AS 'Name',
        contact_emailsv3.Email AS 'Email'
        FROM fullContactsDetails
        LEFT JOIN contact_emailsv3 ON fullContactsDetails.ID = contact_emailsv3.ContactID
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('ProtonMail - Contacts')
            report.start_artifact_report(report_folder, 'ProtonMail - Contacts')
            report.add_script()
            data_headers = ('Creation Timestamp','Modified Timestamp','Name','Email') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'ProtonMail - Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'ProtonMail - Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No ProtonMail - Contacts data available')
        
        db.close()