import sqlite3
import datetime
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_imo(files_found, report_folder, seeker, wrap_text):

    source_file_account = ''
    source_file_friends = ''
    for file_found in files_found:
        
        file_name = str(file_found)
        if file_name.endswith('accountdb.db'):
           imo_account_db = str(file_found)
           source_file_account = file_found.replace(seeker.data_folder, '')

        if file_name.endswith('imofriends.db'):
           imo_friends_db = str(file_found)
           source_file_friends = file_found.replace(seeker.data_folder, '')

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
        report = ArtifactHtmlReport('IMO - Account ID')
        report.start_artifact_report(report_folder, 'IMO - Account ID')
        report.add_script()
        data_headers = ('Account ID','Name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1]))

        report.write_artifact_data_table(data_headers, data_list, imo_account_db)
        report.end_artifact_report()
        
        tsvname = f'IMO - Account ID'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_account)
        
    else:
        logfunc('No IMO Account ID found')
        
    db.close()

    db = open_sqlite_db_readonly(imo_friends_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
                     SELECT messages.buid AS buid, imdata, last_message, timestamp/1000000000, 
                            case message_type when 1 then "Incoming" else "Outgoing" end message_type, message_read
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
        data_headers = ('Timestamp','From ID', 'To ID', 'Last Message',  'Direction', 'Message Read', 'Attachment') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            from_id = ''
            to_id = ''
            attachmentPath = ''
            if row[4] == "Incoming":
                from_id = row[0]
            else:
                to_id = row[0]
            if row[1] is not None:
                imdata_dict = json.loads(row[1])
                            
                # set to none if the key doesn't exist in the dict
                attachmentOriginalPath = imdata_dict.get('original_path', None)
                attachmentLocalPath = imdata_dict.get('local_path', None)
                if attachmentOriginalPath:
                    attachmentPath = attachmentOriginalPath
                else:
                    attachmentPath = attachmentLocalPath
                                
            timestamp = datetime.datetime.utcfromtimestamp(int(row[3])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((timestamp, from_id, to_id, row[2],  row[4], row[5], attachmentPath))

        report.write_artifact_data_table(data_headers, data_list, imo_friends_db)
        report.end_artifact_report()
        
        tsvname = f'IMO - Messages'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_friends)
        
        tlactivity = f'IMO - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No IMO Messages found')

    db.close
    
__artifacts__ = {
        "Imo": (
                "IMO",
                ('*/com.imo.android.imous/databases/*.db*'),
                get_imo)
}
    