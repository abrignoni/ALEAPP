import sqlite3
import datetime
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_skype(files_found, report_folder, seeker, wrap_text):

    user_id = None
    source_file = ''
    for file_found in files_found:
        
        file_name = str(file_found)
        if (('live' in file_name.lower()) and ('db-journal' not in file_name.lower())):
           skype_db = str(file_found)
           # File name has a format of live: which does not write out to a file system correctly
           # so this will fix it to the original name from what is actually written out.
           (head, tail) = os.path.split(file_found.replace(seeker.data_folder, ''))
           source_file = os.path.join(head, "live:" + tail[5:])
        else:
           continue


        db = open_sqlite_db_readonly(skype_db)
        cursor = db.cursor()
            
        try:
            cursor.execute('''
                         SELECT entry_id,
                      CASE
                        WHEN Ifnull(first_name, "") == "" AND Ifnull(last_name, "") == "" THEN entry_id
                        WHEN first_name is NULL THEN replace(last_name, ",", "")
                        WHEN last_name is NULL THEN replace(first_name, ",", "")
                        ELSE replace(first_name, ",", "") || " " || replace(last_name, ",", "")
                      END AS name
               FROM user 
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            user_id = all_rows[0]
           
            
        try:        
            cursor.execute('''
                    SELECT 
                           contact_book_w_groups.conversation_id, 
                           contact_book_w_groups.participant_ids, 
                           messages.time/1000 as start_date, 
                           messages.time/1000 + messages.duration as end_date, 
                           case messages.is_sender_me when 0 then "Incoming" else "Outgoing"
                           end is_sender_me, 
                           messages.person_id AS sender_id 
                    FROM   (SELECT conversation_id, 
                                   Group_concat(person_id) AS participant_ids 
                            FROM   particiapnt 
                            GROUP  BY conversation_id 
                            UNION 
                            SELECT entry_id AS conversation_id, 
                                   NULL 
                            FROM   person) AS contact_book_w_groups 
                           join chatitem AS messages 
                             ON messages.conversation_link = contact_book_w_groups.conversation_id 
                    WHERE  message_type == 3
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('Skype - Call Logs')
            report.start_artifact_report(report_folder, 'Skype - Call Logs')
            report.add_script()
            data_headers = ('Start Time', 'End Time', 'From ID', 'To ID', 'Call Direction') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                to_id = None
                if row[4] == "Outgoing":
                    if ',' in row[1]:
                        to_id = row[1]
                    else:
                        to_id = row[0]
                starttime = datetime.datetime.utcfromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')
                endtime = datetime.datetime.utcfromtimestamp(int(row[3])).strftime('%Y-%m-%d %H:%M:%S')
                data_list.append((starttime, endtime, row[5], to_id, row[4]))
                
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Skype - Call Logs'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)
            
            tlactivity = f'Skype - Call Logs'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Skype Call Log available')
                
        try:        
            cursor.execute('''
		    SELECT contact_book_w_groups.conversation_id,
                           contact_book_w_groups.participant_ids,
                           messages.time/1000,
                           messages.content,
                           messages.device_gallery_path,
                           case messages.is_sender_me when 0 then "Incoming" else "Outgoing"
                           end is_sender_me, 
                           messages.person_id
                           FROM   (SELECT conversation_id,
                                   Group_concat(person_id) AS participant_ids
                            FROM   particiapnt
                            GROUP  BY conversation_id
                            UNION
                            SELECT entry_id as conversation_id,
                                   NULL
                            FROM   person) AS contact_book_w_groups
                           JOIN chatitem AS messages
                             ON messages.conversation_link = contact_book_w_groups.conversation_id
                    WHERE message_type != 3
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('Skype - Messages')
            report.start_artifact_report(report_folder, 'Skype - Messages')
            report.add_script()
            data_headers = ('Send Time','Thread ID', 'Content', 'Direction', 'From ID', 'To ID', 'Attachment') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                thread_id = None
                if row[1] == None:
                    thread_id  = row[0]
                to_id = None
                if row[5] == "Outgoing":
                    if row[1] == None:
                        to_id = None
                    elif ',' in row[1]:
                        to_id = row[1]
                    else:
                        to_id = row[0]
                sendtime = datetime.datetime.utcfromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')

                data_list.append((sendtime, thread_id,  row[3], row[5], row[6], to_id, row[4]))
                
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Skype - Messages'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)
            
            tlactivity = f'Skype - Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Skype messages data available')
            
        
        try:
            cursor.execute('''
                    SELECT entry_id, 
                           CASE
                             WHEN Ifnull(first_name, "") == "" AND Ifnull(last_name, "") == "" THEN entry_id
                             WHEN first_name is NULL THEN replace(last_name, ",", "")
                             WHEN last_name is NULL THEN replace(first_name, ",", "")
                             ELSE replace(first_name, ",", "") || " " || replace(last_name, ",", "")
                           END AS name
                    FROM   person 
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('Skype - Contacts')
            report.start_artifact_report(report_folder, 'Skype - Contacts')
            report.add_script()
            data_headers = ('Entry ID','Name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Skype - Contacts'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)

        else:
            logfunc('No Skype Contacts found')

        db.close
        
__artifacts__ = {
        "skype": (
                "Skype",
                ('*/com.skype.raider/databases/live*'),
                get_skype)
}