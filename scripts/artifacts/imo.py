import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_imo(files_found, report_folder, seeker, wrap_text):

    source_file_account = ''
    source_file_friends = ''
    for file_found in files_found:
        
        file_name = str(file_found)
        if file_name.endswith('accountdb.db'):
           imo_account_db = str(file_found)
           source_file_account = file_found.replace(seeker.directory, '')

        if file_name.endswith('imofriends.db'):
           imo_friends_db = str(file_found)
           source_file_friends = file_found.replace(seeker.directory, '')

    db = open_sqlite_db_readonly(imo_account_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
             SELECT uid, name FROM account
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('IMO - AccountId')
        report.start_artifact_report(report_folder, 'IMO - AccountId')
        report.add_script()
        data_headers = ('account_id','name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1]))

        report.write_artifact_data_table(data_headers, data_list, imo_account_db)
        report.end_artifact_report()
        
        tsvname = f'IMO - AccountId'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_account)

        tlactivity = f'IMO - AccountId'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No IMO AccountId found')
        
    db.close()

    db = open_sqlite_db_readonly(imo_friends_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
                     SELECT messages.buid AS buid, imdata, last_message, timestamp/1000000000, 
                            case message_type when 1 then "Incoming" else "Outgoing" end message_type, message_read, name
                       FROM messages
                      INNER JOIN friends ON friends.buid = messages.buid
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('IMO - Messages')
        report.start_artifact_report(report_folder, 'IMO - Messages')
        report.add_script()
        data_headers = ('build','imdata', 'last_message', 'timestamp', 'message_type', 'message_read', 'name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[3])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((row[0], row[1], row[2], timestamp, row[4], row[5], row[6]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'IMO - Messages'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_friends)

    else:
        logfunc('No IMO Messages found')

    db.close
    
    return