import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_textnow(files_found, report_folder, seeker, wrap_text):

    source_file_msg = ''

    for file_found in files_found:
        
        file_name = str(file_found)
        if file_name.endswith('textnow_data.db'):
           textnow_db = str(file_found)
           source_file_msg = file_found.replace(seeker.data_folder, '')

    db = open_sqlite_db_readonly(textnow_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
                    SELECT contact_value     AS num, 
                           case message_direction when 2 then "Outgoing" else "Incoming" end AS direction, 
                            date/1000 + message_text      AS duration, 
                            date/1000              AS datetime 
                      FROM  messages AS M 
                     WHERE  message_type IN ( 100, 102 )
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Text Now - Call Logs')
        report.start_artifact_report(report_folder, 'Text Now - Call Logs')
        report.add_script()
        data_headers = ('Start Time', 'End Time', 'From ID', 'To ID', 'Call Direction') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            phone_number_from = None
            phone_number_to = None
            if row[1] == "Outgoing":
                phone_number_to = row[0]
            else:
                phone_number_from = row[0]
            starttime = datetime.datetime.utcfromtimestamp(int(row[3])).strftime('%Y-%m-%d %H:%M:%S')
            endtime = datetime.datetime.utcfromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((starttime, endtime, phone_number_from, phone_number_to, row[1]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Text Now - Call Logs'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)

        tlactivity = f'Text Now - Call Logs'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Text Now Call Logs found')
        
    
    try:
        cursor.execute('''
                    SELECT CASE 
                             WHEN messages.message_direction == 2 THEN NULL 
                             WHEN contact_book_w_groups.to_addresses IS NULL THEN 
                             messages.contact_value 
                           END from_address, 
                           CASE 
                             WHEN messages.message_direction == 1 THEN NULL 
                             WHEN contact_book_w_groups.to_addresses IS NULL THEN 
                             messages.contact_value 
                             ELSE contact_book_w_groups.to_addresses 
                           END to_address, 
                           CASE messages.message_direction
                             WHEN 1 THEN "Incoming"
                             ELSE "Outgoing" 
                           END message_direction, 
                           messages.message_text, 
                           messages.READ, 
                           messages.DATE/1000, 
                           messages.attach, 
                           thread_id 
                    FROM   (SELECT GM.contact_value, 
                                   Group_concat(GM.member_contact_value) AS to_addresses, 
                                   G.contact_value                       AS thread_id 
                            FROM   group_members AS GM 
                                   join GROUPS AS G 
                                     ON G.contact_value = GM.contact_value 
                            GROUP  BY GM.contact_value 
                            UNION 
                            SELECT contact_value, 
                                   NULL, 
                                   NULL 
                            FROM   contacts) AS contact_book_w_groups 
                           join messages 
                             ON messages.contact_value = contact_book_w_groups.contact_value 
                    WHERE  message_type NOT IN ( 102, 100 ) 
        ''')
        
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Text Now - Messages')
        report.start_artifact_report(report_folder, 'Text Now - Messages')
        report.add_script()
        data_headers = ('Send Timestamp','Message ID','From ID', 'To ID', 'Direction', 'Message', 'Read',  'Attachment') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            sendtime = datetime.datetime.utcfromtimestamp(int(row[5])).strftime('%Y-%m-%d %H:%M:%S')

            data_list.append((sendtime, row[7], row[0], row[1], row[2], row[3], row[4],  row[6]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Text Now - Messages'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)
        
        tlactivity = f'Text Now - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Text Now messages data available')

    cursor = db.cursor()
    try:
        cursor.execute('''
                     SELECT C.contact_value AS number,  
                            CASE 
                              WHEN contact_name IS NULL THEN contact_value 
                              WHEN contact_name == "" THEN contact_value 
                              ELSE contact_name 
                            END             name 
                     FROM   contacts AS C        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Text Now - Contacts')
        report.start_artifact_report(report_folder, 'Text Now - Contacts')
        report.add_script()
        data_headers = ('number','name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Text Now - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_msg    )

    else:
        logfunc('No Text Now Contacts found')

    db.close
    
__artifacts__ = {
    "textnow": (
        "Text Now",
        ('*/com.enflick.android.TextNow/databases/textnow_data.db*'),
        get_textnow)
}