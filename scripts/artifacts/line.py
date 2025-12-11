import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_line(files_found, report_folder, seeker, wrap_text):

    source_file_msg = ''
    source_file_call = ''
    line_call_db = ''
    line_msg_db = ''
    
    for file_found in files_found:
        
        file_name = str(file_found)
        if file_name.lower().endswith('naver_line'):
           line_msg_db = str(file_found)
           source_file_msg = file_found.replace(seeker.data_folder, '')

        if file_name.lower().endswith('call_history'):
           line_call_db = str(file_found)
           source_file_call = file_found.replace(seeker.data_folder, '')

    db = open_sqlite_db_readonly(line_msg_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
                   SELECT m_id, server_name FROM   contacts
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Line - Contacts')
        report.start_artifact_report(report_folder, 'Line - Contacts')
        report.add_script()
        data_headers = ('user_id','user_name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Line - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)
        
    else:
        logfunc('No Line Contact Logs found')
        
    try:        
        cursor.execute('''
                    SELECT contact_book_w_groups.id, 
                           contact_book_w_groups.members, 
                           messages.from_mid, 
                           messages.content, 
                           messages.created_time/1000, 
                           messages.attachement_type, 
                           messages.attachement_local_uri, 
                           case messages.status when 1 then "Incoming" 
                           else "Outgoing" end status                           
                    FROM   (SELECT id, 
                                   Group_concat(M.m_id) AS members 
                            FROM   membership AS M 
                            GROUP  BY id 
                            UNION 
                            SELECT m_id, 
                                   NULL 
                            FROM   contacts) AS contact_book_w_groups 
                           JOIN chat_history AS messages 
                             ON messages.chat_id = contact_book_w_groups.id 
                    WHERE  attachement_type != 6
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Line - Messages')
        report.start_artifact_report(report_folder, 'Line - Messages')
        report.add_script()
        data_headers = ('Start Time','From ID', 'To ID', 'Direction', 'Thread ID', 'Message', 'Attachments') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            thread_id = None
            if row[1] == None:
                thread_id = row[0]
            to_id = None
            if row[4] == "Outgoing":
                if ',' in row[1]:
                    to_id = row[1]
                else:
                    to_id = row[0]
            attachment = row[6]
            if row[6] is None:
                attachment = None
            elif 'content' in row[6]:
                attachment = None
            created_time = datetime.datetime.utcfromtimestamp(int(row[4])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((created_time, row[2], to_id, row[7], thread_id, row[3], attachment))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Line - Messages'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)
        
        tlactivity = f'Line - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Line Messages available')
            

    db.close()

    db = open_sqlite_db_readonly(line_call_db)
    cursor = db.cursor()
    cursor.execute('''attach database "''' + line_msg_db + '''" as naver_line ''')
    try:
        cursor.execute('''
                    SELECT case Substr(calls.call_type, -1) when "O" then "Outgoing"
                           else "Incoming" end AS direction, 
                           calls.start_time/1000              AS start_time, 
                           calls.end_time/1000                AS end_time, 
                           case when Substr(calls.call_type, -1) = "O" then contact_book_w_groups.members 
                           else null end AS group_members,  
                           calls.caller_mid, 
                           case calls.voip_type when "V" then "Video" 
                              when "A" then "Audio"
                              when "G" then calls.voip_gc_media_type 
                           end   AS call_type
                    FROM   (SELECT id, 
                                   Group_concat(M.m_id) AS members 
                            FROM   membership AS M 
                            GROUP  BY id 
                            UNION 
                            SELECT m_id, 
                                   NULL 
                            FROM   naver_line.contacts) AS contact_book_w_groups 
                           JOIN call_history AS calls 
                             ON calls.caller_mid = contact_book_w_groups.id

        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Line - Call Logs')
        report.start_artifact_report(report_folder, 'Line - Call Logs')
        report.add_script()
        data_headers = ('Start Time', 'End Time', 'To ID', 'From ID', 'Direction', 'Call Type') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            start_time = datetime.datetime.utcfromtimestamp(int(row[1])).strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.datetime.utcfromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((start_time, end_time, row[3], row[4], row[0], row[5]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Line - Call Logs'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_call)
        
        tlactivity = f'Line - Call Logs'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Line Call Logs found')

    db.close
    
__artifacts__ = {
        "line": (
                "Line",
                ('*/jp.naver.line.android/databases/**'),
                get_line)
}