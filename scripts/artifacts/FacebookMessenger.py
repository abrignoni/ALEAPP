#2023-02-03: Added support for new msys_database format - Kevin Pagano

import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly

def get_FacebookMessenger(files_found, report_folder, seeker, wrap_text):
    
    slash = '\\' if is_platform_windows() else '/'
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if 'mirror' in file_found: #remove to process mirror data. Should be a copy of actual data.
            continue 
        
        if '/user/0/' in file_found: #remove to process user 0. Should be a copy data in /data/data/com.facebook.orca
            continue
            
                
        if 'user' in file_found:
            usernum = file_found.split(slash)
            usernum = '_'+str(usernum[-4])
        else:
            usernum = ''
            
        if 'katana' in file_found:
            typeof = ' App '
        elif 'orca' in file_found:
            typeof = ' Messenger '
        else:
            typeof =''
        
        if file_found.endswith('threads_db2-uid'):
            source_file = file_found.replace(seeker.data_folder, '')
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
                
            continue
        
        if file_found.endswith(('-shm','-wal')):
            continue
        
        if file_found.find('msys_database_') >= 0:
            source_file = file_found.replace(seeker.data_folder, '')
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(messages.timestamp_ms/1000,'unixepoch') as "Message Time",
            contacts.name as "Sender",
            messages.sender_id as "Sender Account ID",
            messages.thread_key as "Thread Key",
            messages.text as "Message",
            attachments.title_text as "Snippet",
            attachments.subtitle_text as "Call/Location Information",
            attachments.filename as "Attachment File Name",
            attachments.playable_url_mime_type as "Attachment Type",
            attachments.playable_url as "Attachment URL",
            attachment_ctas.native_url as "Location Lat/Long",
            reactions.reaction as "Reaction",
            datetime(reactions.reaction_creation_timestamp_ms/1000,'unixepoch') as "Reaction Time",
            case
            when messages.is_admin_message = 1 then "Yes"
            when messages.is_admin_message = 0 then "No"
            else messages.is_admin_message
            end as "Is Admin Message",
            messages.message_id as "Message ID"
            from messages
            join contacts on contacts.id = messages.sender_id
            left join attachments on attachments.message_id = messages.message_id
            left join attachment_ctas on messages.message_id = attachment_ctas.message_id
            left join reactions on reactions.message_id = messages.message_id
            order by "Message Time" ASC
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Facebook - Chats - msys_database')
                report.start_artifact_report(report_folder, f'Facebook{typeof}- Chats{usernum} - msys_database')
                report.add_script()
                data_headers = ('Message Timestamp','Sender','Sender ID','Thread Key','Message','Snippet','Call/Location Information','Attachment Name','Attachment Type','Attachment URL','Location Lat/Long','Reaction','Reaction Timestamp','Is Admin Message','Message ID') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Facebook{typeof}- Chats{usernum} - msys_database'
                tsv(report_folder, data_headers, data_list, tsvname, source_file)
                
            else:
                logfunc(f'No Facebook{typeof}- Chats{usernum} - msys_database data available')
            
            cursor.execute('''
            select
            datetime(call_log.call_timestamp_ms/1000,'unixepoch') as "Call Timestamp",
            strftime('%H:%M:%S',call_log.call_duration, 'unixepoch')as "Call Duration",
            contacts.name as "Party Name",
            case call_log.call_direction
                when 1 then "Outgoing"
                when 2 then "Incoming"
            end as "Call Direction",
            case call_log.call_media_type
                when 2 then "Yes"
                else ""
            end as "Video Call",
            case has_been_seen
                when 0 then 'No'
                when 1 then 'Yes'
            end as "Call Answered",
            call_log.thread_key
            from call_log
            left join contacts on contacts.id = call_log.thread_key
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Facebook - Calls - msys_database')
                report.start_artifact_report(report_folder, f'Facebook{typeof}- Calls{usernum} - msys_database')
                report.add_script()
                data_headers = ('Call Timestamp','Call Duration','Party Name','Call Direction','Video Call','Call Answered','Thread Key') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Facebook{typeof}- Calls{usernum} - msys_database'
                tsv(report_folder, data_headers, data_list, tsvname, source_file)
                
            else:
                logfunc(f'No Facebook{typeof}- Calls{usernum} - msys_database data available')
                
            cursor.execute('''
            select
            id,
            name,
            normalized_name_for_search,
            username,
            profile_picture_large_url,
            email_address,
            phone_number,
            case is_messenger_user
                when 0 then ""
                when 1 then "Yes"
            end as "Messenger User",
            case friendship_status
                when 0 then "N/A (Self)"
                when 1 then "Friends"
                when 2 then "Friend Request Received"
                when 3 then "Friend Request Sent"
                when 4 then "Not Friends"
            end as "Friendship Status",
            substr(datetime(birthday_timestamp,'unixepoch'),6,5) as "Birthdate (MM-DD)"
            from contacts
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Facebook - Contacts - msys_database')
                report.start_artifact_report(report_folder, f'Facebook{typeof}- Contacts{usernum} - msys_database')
                report.add_script()
                data_headers = ('Facebook ID','Name','Normalized Name','User Name','Profile Pic URL','Email Address','Phone Number','Is Messenger User','Friendship Status','Birthday Timestamp') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Facebook{typeof}- Contacts{usernum} - msys_database'
                tsv(report_folder, data_headers, data_list, tsvname, source_file)
                
            else:
                logfunc(f'No Facebook{typeof}- Contacts{usernum} - msys_database data available')   
            
            db.close()
            
            continue

        if (file_found.startswith('ssus.') and file_found.endswith('threads_db2')) or file_found.endswith('threads_db2'):
            source_file = file_found.replace(seeker.data_folder, '')
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
                (select json_extract (messages.shares, '$[0].href')) as ShareLink,
                message_reactions.reaction as "Message Reaction",
                datetime(message_reactions.reaction_timestamp/1000,'unixepoch') as "Message Reaction Timestamp",
                messages.msg_id
                from messages, threads
                left join message_reactions on message_reactions.msg_id = messages.msg_id
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
                (select json_extract (messages.shares, '$[0].href')) as ShareLink,
                message_reactions.reaction as "Message Reaction",
                datetime(message_reactions.reaction_timestamp/1000,'unixepoch') as "Message Reaction Timestamp",
                messages.msg_id
                from messages, threads
                left join message_reactions on message_reactions.msg_id = messages.msg_id
                where messages.thread_key=threads.thread_key and generic_admin_message_extensible_data IS NULL and msg_type != -1
                order by messages.thread_key, datestamp;
                ''')
                
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Facebook - Chats - threads_db2')
                report.start_artifact_report(report_folder, f'Facebook{typeof}- Chats{usernum} - threads_db2')
                report.add_script()
                data_list = []
                
                if snippet == 1:
                    data_headers = ('Timestamp','Sender Name','Sender ID','Thread Key','Message','Snippet','Attachment Name','Share Name','Share Description','Share Link','Message Reaction','Message Reaction Timestamp','Message ID')
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
                else:
                    data_headers = ('Timestamp','Sender Name','Sender ID','Thread Key','Message','Attachment Name','Share Name','Share Description','Share Link','Message Reaction','Message Reaction Timestamp','Message ID')
                    for row in all_rows:
                        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))
                        
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Facebook Messenger{typeof}- Chats{usernum} - threads_db2'
                tsv(report_folder, data_headers, data_list, tsvname, source_file)
                
                tlactivity = f'Facebook Messenger{typeof}- Chats{usernum} - threads_db2'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc(f'No Facebook{typeof}- Chats{usernum} - threads_db2 data available')
            
            cursor.execute('''
            select
            datetime((messages.timestamp_ms/1000)-(select json_extract (messages.generic_admin_message_extensible_data, '$.call_duration')),'unixepoch') as "Call Timestamp",
            strftime('%H:%M:%S',(select json_extract (messages.generic_admin_message_extensible_data, '$.call_duration')), 'unixepoch')as "Call Duration",
            (select json_extract (messages.generic_admin_message_extensible_data, '$.caller_id')) as "Caller ID",
            (select json_extract (messages.sender, '$.name')) as "Receiver",
            substr((select json_extract (messages.sender, '$.user_key')),10) as "Receiver ID",
            case (select json_extract (messages.generic_admin_message_extensible_data, '$.video'))
                when false then ''
                else 'Yes'
            End as "Video Call",
            messages.thread_key
            from messages, threads
            where messages.thread_key=threads.thread_key and generic_admin_message_extensible_data NOT NULL
            order by messages.thread_key, "Date/Time End";
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Facebook - Calls - threads_db2')
                report.start_artifact_report(report_folder, f'Facebook{typeof}- Calls{usernum} - threads_db2')
                report.add_script()
                data_headers = ('Timestamp','Call Duration','Caller ID','Receiver Name','Receiver ID','Video Call','Thread Key') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Facebook{typeof}- Calls{usernum} - threads_db2'
                tsv(report_folder, data_headers, data_list, tsvname, source_file)
                
                tlactivity = f'Facebook{typeof}- Calls{usernum} - threads_db2'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc(f'No Facebook{typeof}- Calls{usernum} - threads_db2 data available')
            
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
                when 1 then 'Yes'
            end is_friend,
            friendship_status,
            contact_relationship_status
            from thread_users
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Facebook - Contacts - threads_db2')
                report.start_artifact_report(report_folder, f'Facebook{typeof}- Contacts{usernum} - threads_db2')
                report.add_script()
                data_headers = ('User ID','First Name','Last Name','Username','Profile Pic URL','Is Messenger User','Is Friend','Friendship Status','Contact Relationship Status') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Facebook{typeof}- Contacts{usernum} - threads_db2'
                tsv(report_folder, data_headers, data_list, tsvname, source_file)
                
            else:
                logfunc(f'No Facebook{typeof}- Contacts{usernum} - threads_db2 data available')
            
            db.close()
            
            continue

        else:
            continue # Skip all other files
    
__artifacts__ = {
        "FacebookMessenger": (
                "Facebook Messenger",
                ('*/*threads_db2*','*/msys_database*'),
                get_FacebookMessenger)
}
