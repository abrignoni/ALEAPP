import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly

def get_FacebookMessenger(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('threads_db2'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        case messages.timestamp_ms
            when 0 then ''
            else datetime(messages.timestamp_ms/1000,'unixepoch')
        End	as Datestamp,
        (select json_extract (messages.sender, '$.name')) as "Sender",
        substr((select json_extract (messages.sender, '$.user_key')),10) as "Sender ID",
        messages.thread_key,
        messages.text,
        messages.snippet,
        (select json_extract (messages.attachments, '$[0].filename')) as AttachmentName,
        --messages.attachments,
        --messages.shares,
        (select json_extract (messages.shares, '$[0].name')) as ShareName,
        (select json_extract (messages.shares, '$[0].description')) as ShareDesc,
        (select json_extract (messages.shares, '$[0].href')) as ShareLink
        from messages, threads
        where messages.thread_key=threads.thread_key and generic_admin_message_extensible_data IS NULL and msg_type != -1
        order by messages.thread_key, datestamp;
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Facebook Messenger - Chats')
            report.start_artifact_report(report_folder, 'Facebook Messenger - Chats')
            report.add_script()
            data_headers = ('Timestamp','Sender Name','Sender ID','Thread Key','Message','Snippet','Attachment Name','Share Name','Share Description','Share Link') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Facebook Messenger - Chats'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Facebook Messenger - Chats'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Facebook Messenger - Chats data available')
        
        cursor.execute('''
        select
        datetime((messages.timestamp_ms/1000)-(select json_extract (messages.generic_admin_message_extensible_data, '$.call_duration')),'unixepoch') as "Timestamp",
        (select json_extract (messages.generic_admin_message_extensible_data, '$.caller_id')) as "Caller ID",
        (select json_extract (messages.sender, '$.name')) as "Receiver",
        substr((select json_extract (messages.sender, '$.user_key')),10) as "Receiver ID",
        --messages.generic_admin_message_extensible_data,
        strftime('%H:%M:%S',(select json_extract (messages.generic_admin_message_extensible_data, '$.call_duration')), 'unixepoch')as "Call Duration",
        case (select json_extract (messages.generic_admin_message_extensible_data, '$.video'))
            when false then ''
            else 'Yes'
        End as "Video Call"
        from messages, threads
        where messages.thread_key=threads.thread_key and generic_admin_message_extensible_data NOT NULL
        order by messages.thread_key, "Date/Time End";
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Facebook Messenger - Calls')
            report.start_artifact_report(report_folder, 'Facebook Messenger - Calls')
            report.add_script()
            data_headers = ('Timestamp','Caller ID','Receiver Name','Receiver ID','Call Duration','Video Call') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Facebook Messenger - Calls'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Facebook Messenger - Calls'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Facebook Messenger - Calls data available')
        
        cursor.execute('''
        select
        substr(user_key,10),
        first_name,
        last_name,
        username,
        (select json_extract (profile_pic_square, '$[0].url')) as profile_pic_square,
        case is_messenger_user
            when 0 then ''
            else 'Yes'
        end is_messenger_user,
        case is_friend
            when 0 then 'No'
            else 'Yes'
        end is_friend
        from thread_users
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Facebook Messenger - Contacts')
            report.start_artifact_report(report_folder, 'Facebook Messenger - Contacts')
            report.add_script()
            data_headers = ('User ID','First Name','Last Name','Username','Profile Pic URL','Is App User','Is Friend') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Facebook Messenger - Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Facebook Messenger - Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Facebook Messenger - Contacts data available')
        
        db.close()
        return
