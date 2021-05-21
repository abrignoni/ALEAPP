import sqlite3
import datetime
import xmltodict

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Whatsapp(files_found, report_folder, seeker, wrap_text):

    source_file_msg = ''
    source_file_wa = ''
    whatsapp_msgstore_db = ''
    whatsapp_wa_db = ''
    
    for file_found in files_found:
        
        file_name = str(file_found)
        if file_name.endswith('msgstore.db'):
           whatsapp_msgstore_db = str(file_found)
           source_file_msg = file_found.replace(seeker.directory, '')

        if file_name.endswith('wa.db'):
           whatsapp_wa_db = str(file_found)
           source_file_wa = file_found.replace(seeker.directory, '')

    db = open_sqlite_db_readonly(whatsapp_msgstore_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT case CL.video_call when 1 then "Video Call" else "Audio Call" end as call_type, 
               CL.timestamp/1000 as start_time, 
               ((cl.timestamp/1000) + CL.duration) as end_time, 
               case CL.from_me when 0 then "Incoming" else "Outgoing" end as call_direction,
		       J1.raw_string AS from_id,
                            group_concat(J.raw_string) AS group_members
                     FROM   call_log_participant_v2 AS CLP
                            JOIN call_log AS CL
                              ON CL._id = CLP.call_log_row_id
                            JOIN jid AS J
                              ON J._id = CLP.jid_row_id
                            JOIN jid as J1
                              ON J1._id = CL.jid_row_id
                            GROUP  BY CL._id
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Whatsapp - Group Call Logs')
        report.start_artifact_report(report_folder, 'Whatsapp - Group Call Logs')
        report.add_script()
        data_headers = ('Start Time', 'End Time','Call Type', 'Call Direction', 'From ID', 'Group Members') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            starttime = datetime.datetime.fromtimestamp(int(row[1])).strftime('%Y-%m-%d %H:%M:%S')
            endtime = datetime.datetime.fromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append(( starttime, endtime, row[0], row[3], row[4], row[5]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Whatsapp - Group Call Logs'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)

        tlactivity = f'Whatsapp - Group Call Logs'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Whatsapp Group Call Logs found')
        
    try:        
        cursor.execute('''
                     SELECT CL.timestamp/1000 as start_time, 
                            case CL.video_call when 1 then "Video Call" else "Audio Call" end as call_type, 
                            ((CL.timestamp/1000) + CL.duration) as end_time, 
                            J.raw_string AS num, 
                            case CL.from_me when 0 then "Incoming" else "Outgoing" end as call_direction
                     FROM   call_log AS CL 
                            JOIN jid AS J 
                              ON J._id = CL.jid_row_id 
                     WHERE  CL._id NOT IN (SELECT DISTINCT call_log_row_id 
                                           FROM   call_log_participant_v2) 
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Whatsapp - Single Call Logs')
        report.start_artifact_report(report_folder, 'Whatsapp - Single Call Logs')
        report.add_script()
        data_headers = ('Start Time','Call Type','End Time','Number','Call Direction') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            starttime = datetime.datetime.fromtimestamp(int(row[0])).strftime('%Y-%m-%d %H:%M:%S')
            endtime = datetime.datetime.fromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((starttime, row[1], endtime, row[3], row[4]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Whatsapp - Single Call Logs'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)
        
        tlactivity = f'Whatsapp - Single Call Logs'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Whatsapp Single Call Log available')
            
    cursor.execute('''attach database "''' + whatsapp_wa_db + '''" as wadb ''')
    
    try:
        cursor.execute('''
                    SELECT messages.key_remote_jid  AS id, 
                           case 
                              when contact_book_w_groups.recipients is null then messages.key_remote_jid
                              else contact_book_w_groups.recipients
                           end as recipients, 
                           key_from_me              AS direction, 
                           messages.data            AS content, 
                           messages.timestamp/1000       AS send_timestamp, 
                           messages.received_timestamp/1000, 
                           case 
                              when messages.remote_resource is null then messages.key_remote_jid 
                              else messages.remote_resource
                           end AS group_sender,
                           messages.media_url       AS attachment
                    FROM   (SELECT jid, 
                                   recipients 
                            FROM   wadb.wa_contacts AS contacts 
                                   left join (SELECT gjid, 
                                                     Group_concat(CASE 
                                                                    WHEN jid == "" THEN NULL 
                                                                    ELSE jid 
                                                                  END) AS recipients 
                                              FROM   group_participants 
                                              GROUP  BY gjid) AS groups 
                                          ON contacts.jid = groups.gjid 
                            GROUP  BY jid) AS contact_book_w_groups 
                           join messages 
                             ON messages.key_remote_jid = contact_book_w_groups.jid
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Whatsapp - Messages')
        report.start_artifact_report(report_folder, 'Whatsapp - Messages')
        report.add_script()
        data_headers = ('Send Timestamp', 'Received Timestamp','Message ID','Recipients', 'Direction', 'Content', 'Group Sender', 'Attachment') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            sendtime = datetime.datetime.fromtimestamp(int(row[4])).strftime('%Y-%m-%d %H:%M:%S')
            receivetime = datetime.datetime.fromtimestamp(int(row[5])).strftime('%Y-%m-%d %H:%M:%S')

            data_list.append((sendtime, receivetime, row[0], row[1], row[2], row[3],row[6], row[7]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Whatsapp - Messages'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)
        
        tlactivity = f'Whatsapp - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Whatsapp messages data available')
        
    

    db.close()

    db = open_sqlite_db_readonly(whatsapp_wa_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
                     SELECT jid, 
                            CASE 
                              WHEN WC.number IS NULL THEN WC.jid 
                              WHEN WC.number == "" THEN WC.jid 
                              ELSE WC.number 
                            END number, 
                            CASE 
                              WHEN WC.given_name IS NULL 
                                   AND WC.family_name IS NULL 
                                   AND WC.display_name IS NULL THEN WC.jid 
                              WHEN WC.given_name IS NULL 
                                   AND WC.family_name IS NULL THEN WC.display_name 
                              WHEN WC.given_name IS NULL THEN WC.family_name 
                              WHEN WC.family_name IS NULL THEN WC.given_name 
                              ELSE WC.given_name 
                                   || " " 
                                   || WC.family_name 
                            END name 
                     FROM   wa_contacts AS WC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Whatsapp - Contacts')
        report.start_artifact_report(report_folder, 'Whatsapp - Contacts')
        report.add_script()
        data_headers = ('Number','Name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Whatsapp - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_wa)

    else:
        logfunc('No Whatsapp Contacts found')

    db.close

    for file_found in files_found:
        if('com.whatsapp_preferences_light.xml' in file_found):
            with open(file_found, encoding='utf-8') as fd:
                xml_dict = xmltodict.parse(fd.read())
                string_dict = xml_dict.get('map','').get('string','')
                data = []
                for i in range(len(string_dict)):
                    if(string_dict[i]['@name'] == 'push_name'):                 # User Profile Name
                        data.append(string_dict[i]['#text'])
                    if(string_dict[i]['@name'] == 'my_current_status'):         # User Current Status
                        data.append(string_dict[i]['#text'])
                    if(string_dict[i]['@name'] == 'version'):                   # User current whatsapp version
                        data.append(string_dict[i]['#text'])
                    if(string_dict[i]['@name'] == 'ph'):                        # User Mobile Number
                        data.append(string_dict[i]['#text'])
                    if(string_dict[i]['@name'] == 'cc'):                        # User country code
                        data.append(string_dict[i]['#text'])

                if(len(data)>0):
                    report = ArtifactHtmlReport('Whatsapp - User Profile')
                    report.start_artifact_report(report_folder,'Whatapp - User Profile')
                    report.add_script()
                    data_headers = ('Version', 'Name', 'User Status', 'Country Code', 'Mobile Number')
                    data_list = []
                    data_list.append((data[0], data[3], data[2], data[1], data[4]))
                    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                    report.end_artifact_report()

                    tsvname = "Whatsapp - User Profile"
                    tsv(report_folder, data_headers, data_list,tsvname)

                    tlactivity = "Whatsapp - User Profile"
                    timeline(report_folder, tlactivity, data_list, data_headers)
                else:
                    logfunc("No Whatsapp - Profile data found")
    return