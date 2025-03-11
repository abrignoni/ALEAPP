import sqlite3
from hashlib import sha256

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Viber(files_found, report_folder, seeker, wrap_text):

    source_file_messages = ''
    source_file_data = ''
    viber_data_db = ''
    viber_messages_db = ''
    
    for file_found in files_found:
        
        if file_found.endswith('_messages'):
           viber_messages_db = str(file_found)
           source_file_messages = file_found.replace(seeker.data_folder, '')

        if file_found.endswith('_data'):
           viber_data_db = str(file_found)
           source_file_data = file_found.replace(seeker.data_folder, '')

        if file_found.endswith('viber_prefs'):
            viber_prefs_db = str(file_found)
            viber_prefs_data = file_found.replace(seeker.data_folder, '') 

    db = open_sqlite_db_readonly(viber_data_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT
        datetime(date/1000, 'unixepoch') AS start_time,
        canonized_number,
        case type
            when 2 then "Outgoing"
            else "Incoming"
        end AS direction,
        datetime((date + (duration * 1000))/1000, 'unixepoch') as end_time,
        case viber_call_type
            when 1 then "Audio Call"
            when 4 then "Video Call"
            else "Unknown"
        end AS viber_call_type
        FROM calls
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Viber - Call Logs')
        report.start_artifact_report(report_folder, 'Viber - Call Logs')
        report.add_script()
        data_headers = ('Call Start Time', 'Phone Number','Call Direction', 'Call End Time', 'Call Type') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4]))

        report.write_artifact_data_table(data_headers, data_list, viber_data_db)
        report.end_artifact_report()
        
        tsvname = f'Viber - Call Logs'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_data)

        tlactivity = f'Viber - Call Logs'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Viber Call Logs found')
        
    try:        
        cursor.execute('''
        SELECT
        C.display_name,
        coalesce(D.data2, D.data1, D.data3) as phone_number
        FROM phonebookcontact AS C
        JOIN phonebookdata AS D ON C._id = D.contact_id
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Viber - Contacts')
        report.start_artifact_report(report_folder, 'Viber - Contacts')
        report.add_script()
        data_headers = ('Display Name','Phone Number') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1]))
            
        report.write_artifact_data_table(data_headers, data_list, viber_data_db)
        report.end_artifact_report()
        
        tsvname = f'Viber - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_messages)
        
    else:
        logfunc('No Viber Contacts data available')

    db.close()

    db = open_sqlite_db_readonly(viber_messages_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT 
        datetime(M.msg_date/1000, 'unixepoch') AS msg_date,
        convo_participants.from_number AS from_number, 
        convo_participants.recipients AS recipients, 
        M.conversation_id AS thread_id, 
        M.body AS msg_content, 
        case M.send_type
            when 1 then "Outgoing" 
            else "Incoming"
        end AS direction, 
        M.unread read_status,
        M.extra_uri AS file_attachment                            
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
        data_headers = ('Message Date', 'From Phone Number','Recipients', 'Thread ID', 'Message', 'Direction', 'Read Status', 'File Attachment') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

        report.write_artifact_data_table(data_headers, data_list, viber_messages_db)
        report.end_artifact_report()
        
        tsvname = f'Viber - Messages'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_messages)

        tlactivity = f'Viber - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Viber Messages found')

    db.close
    
    db = open_sqlite_db_readonly(viber_prefs_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT key, value from kvdata WHERE key='key_hidden_chats_pin'
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    if usageentries > 0:
        userPINHash = all_rows[0][1]
        for i in range(0,10000):
            currentPIN = ('{0:04}'.format(i)).encode('utf-8')
            ## Section of code to try the hash process and print passcode if correct
            ## Compare the current PIN SHA256 and the provided PIN hash
            if sha256(currentPIN+"Shawl9_Valid_Yeastv".encode("utf-8")).hexdigest() == userPINHash:
                currentPIN = currentPIN.decode("utf-8")
                break
        report = ArtifactHtmlReport('Viber - Additional')
        report.start_artifact_report(report_folder, 'Viber - Additional')
        report.add_script()
        data_headers = ('User PIN Hash', 'User PIN',) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = [((userPINHash,currentPIN))]

        report.write_artifact_data_table(data_headers, data_list, viber_prefs_db)
        report.end_artifact_report()
        
        tsvname = f'Viber - Additional'
        tsv(report_folder, data_headers, data_list, tsvname, viber_prefs_data)

        tlactivity = f'Viber - Additional'
        timeline(report_folder, tlactivity, data_list, data_headers)     
    else:
        logfunc('No Viber Hidden Chat PIN found')        

    db.close()

__artifacts__ = {
  "Viber": (
    "Viber",
    ('*/com.viber.voip/databases/*'),
    get_Viber)
}