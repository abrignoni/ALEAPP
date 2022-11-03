import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly

def get_FacebookMessenger(files_found, report_folder, seeker, wrap_text):
    
    #logfunc(str(files_found))
    for file_found in files_found:
        file_found = str(file_found)
        
        if 'mirror' in file_found: #remove to process mirror data. Should be a copy of actual data.
            continue 
        
        if '/user/0/' in file_found: #remove to process user 0. Should be a copy data in /data/data/com.facebook.orca
            continue
            
                
        if 'user' in file_found:
            usernum = file_found.split("/")
            usernum = '_'+str(usernum[-4])
        else:
            usernum = ''
            
        if 'katana' in file_found:
            typeof = ' App '
        elif 'orca' in file_found:
            typeof = ' Messenger '
        else:
            typeof =''
        
        if file_found.endswith('threads_db2-uid') or (file_found.startswith('ssus.') and file_found.endswith('threads_db2')):
            source_file = file_found.replace(seeker.directory, '')
            userid = ''
            data_list = []
            with open(file_found, 'r') as dat:
                for line in dat:
                    userid = line
                    if userid != '':
                        data_list.append((userid,))
            logfunc(f'Userid: {str(userid)}')            
            if len(userid) > 0:
                report = ArtifactHtmlReport('Facebook - User ID')
                report.start_artifact_report(report_folder, f'Facebook{typeof}- User ID{usernum}')
                report.add_script()
                data_headers = ('User ID',) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Facebook{typeof}- User ID{usernum}'
                tsv(report_folder, data_headers, data_list, tsvname, source_file)
            
        if not file_found.endswith('threads_db2'):
            continue # Skip all other files
    
        source_file = file_found.replace(seeker.directory, '')
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
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
            (select json_extract (messages.shares, '$[0].name')) as ShareName,
            (select json_extract (messages.shares, '$[0].description')) as ShareDesc,
            (select json_extract (messages.shares, '$[0].href')) as ShareLink
            from messages, threads
            where messages.thread_key=threads.thread_key and generic_admin_message_extensible_data IS NULL and msg_type != -1
            order by messages.thread_key, datestamp;
            ''')
            snippet = 1
        except:
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
            (select json_extract (messages.attachments, '$[0].filename')) as AttachmentName,
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
            report = ArtifactHtmlReport('Facebook - Chats')
            report.start_artifact_report(report_folder, f'Facebook{typeof}- Chats{usernum}')
            report.add_script()
            data_list = []
            
            if snippet == 1:
                data_headers = ('Timestamp','Sender Name','Sender ID','Thread Key','Message','Snippet','Attachment Name','Share Name','Share Description','Share Link')
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))
            else:
                data_headers = ('Timestamp','Sender Name','Sender ID','Thread Key','Message','Attachment Name','Share Name','Share Description','Share Link')
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
                    
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Facebook Messenger{typeof}-- Chats{usernum}'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)
            
            tlactivity = f'Facebook Messenger{typeof}-- Chats{usernum}'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No Facebook{typeof} - Chats data available{usernum}')
        
        cursor.execute('''
        select
        datetime((messages.timestamp_ms/1000)-(select json_extract (messages.generic_admin_message_extensible_data, '$.call_duration')),'unixepoch') as "Timestamp",
        (select json_extract (messages.generic_admin_message_extensible_data, '$.caller_id')) as "Caller ID",
        (select json_extract (messages.sender, '$.name')) as "Receiver",
        substr((select json_extract (messages.sender, '$.user_key')),10) as "Receiver ID",
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
            report = ArtifactHtmlReport('Facebook - Calls')
            report.start_artifact_report(report_folder, f'Facebook{typeof}- Calls{usernum}')
            report.add_script()
            data_headers = ('Timestamp','Caller ID','Receiver Name','Receiver ID','Call Duration','Video Call') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Facebook{typeof}- Calls{usernum}'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)
            
            tlactivity = f'Facebook{typeof}- Calls{usernum}'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No Facebook{typeof}- Calls data available{usernum}')
        
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
            report = ArtifactHtmlReport('Facebook - Contacts')
            report.start_artifact_report(report_folder, f'Facebook{typeof}- Contacts{usernum}')
            report.add_script()
            data_headers = ('User ID','First Name','Last Name','Username','Profile Pic URL','Is App User','Is Friend') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Facebook{typeof}- Contacts{usernum}'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)
            
            tlactivity = f'Facebook{typeof}- Contacts{usernum}'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No Facebook{typeof}- Contacts data available{usernum}')
        
        db.close()
        
__artifacts__ = {
        "FacebookMessenger": (
                "Facebook Messenger",
                ('*/*threads_db2*'),
                get_FacebookMessenger)
}
