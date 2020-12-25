import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Viber(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        
        if file_found.endswith('_messages'):
           viber_messages_db = str(file_found)
#        file_found = str(file_found)
 
        if file_found.endswith('_data'):
           viber_data_db = str(file_found)        
#        if file_found.endswith('-db'):
#            break
        
    db = open_sqlite_db_readonly(viber_data_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT canonized_number, case type when 2 then "Outgoing" else "Incoming" end AS direction, 
               duration as duration_in_seconds, date AS start_time, 
               case viber_call_type when 1 then "Audio Call" when 4 then "Video Call" else "Unknown" end AS call_type
          FROM calls 
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Viber - call logs')
        report.start_artifact_report(report_folder, 'Viber - call logs')
        report.add_script()
        data_headers = ('canonized_number','call_direction', 'duration_in_seconds', 'start_time', 'call_type') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Viber - call logs'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Viber - call logs'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Viber Call Logs found')
        
    try:        
        cursor.execute('''
        SELECT C.display_name, coalesce(D.data2, D.data1, D.data3) as phone_number 
          FROM phonebookcontact AS C JOIN phonebookdata AS D ON C._id = D.contact_id
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Viber - Contacts')
        report.start_artifact_report(report_folder, 'Viber - Contacts')
        report.add_script()
        data_headers = ('display_name','phone_number') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Viber - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Viber Contacts data available')

    db.close()

    db = open_sqlite_db_readonly(viber_messages_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
                     SELECT convo_participants.from_number AS from_number, 
                            convo_participants.recipients  AS recipients, 
                            M.conversation_id              AS thread_id, 
                            M.body                         AS msg_content, 
                            case M.send_type when 1 then "Outgoing" else "Incoming" end AS direction, 
                            M.msg_date                     AS msg_date, 
                            case M.unread when 0 then "Read" else "Unread" end AS read_status,
                            M.extra_uri                    AS file_attachment                            
                     FROM   (SELECT *, 
                                    group_concat(TO_RESULT.number) AS recipients 
                             FROM   (SELECT P._id     AS FROM_ID, 
                                            P.conversation_id, 
                                            PI.number AS FROM_NUMBER 
                                     FROM   participants AS P 
                                            JOIN participants_info AS PI 
                                              ON P.participant_info_id = PI._id) AS FROM_RESULT 
                                    JOIN (SELECT P._id AS TO_ID, 
                                                 P.conversation_id, 
                                                 PI.number 
                                          FROM   participants AS P 
                                                 JOIN participants_info AS PI 
                                                   ON P.participant_info_id = PI._id) AS TO_RESULT 
                                      ON FROM_RESULT.from_id != TO_RESULT.to_id 
                                         AND FROM_RESULT.conversation_id = TO_RESULT.conversation_id 
                             GROUP  BY FROM_RESULT.from_id) AS convo_participants 
                            JOIN messages AS M 
                              ON M.participant_id = convo_participants.from_id 
                                 AND M.conversation_id = convo_participants.conversation_id
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Viber - Messages')
        report.start_artifact_report(report_folder, 'Viber - Messages')
        report.add_script()
        data_headers = ('from_number','recipients', 'thread_id', 'msg_content', 'direction', 'msg_date', 'read_status', 'file_attachment') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Viber - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Viber - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Viber Messages found')

    db.close
    
    return