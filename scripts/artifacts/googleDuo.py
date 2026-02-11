import os
import shutil
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

def get_googleDuo(files_found, report_folder, _seeker, _wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('tachyon.db'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        # --- Query 1: Activity History ---
        cursor.execute('''
        select
        datetime(timestamp_usec/1000000, 'unixepoch') as 'Timestamp',
        substr(self_id, 0,instr(self_id, '|')) as 'Local User',
        substr(other_id, 0,instr(other_id, '|')) as 'Remote User',
        duo_users.contact_display_name as 'Contact Name',
        case activity_type
            when 1 then 'Call'
            when 2 then 'Note'
            when 4 then 'Reaction'
        end as 'Activity Type',
        case call_state
            when 0 then 'Left Message'
            when 1 then 'Missed Call'
            when 2 then 'Answered'
            when 4 then ''
        end as 'Call Status',
        case outgoing
            when 0 then 'Incoming'
            when 1 then 'Outgoing'
        end as 'Direction'
        from activity_history
        left join duo_users on duo_users.user_id = substr(other_id, 0,instr(other_id, '|'))
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Duo - Call History')
            report.start_artifact_report(report_folder, 'Google Duo - Call History')
            report.add_script()
            data_headers = ('Timestamp','Local User','Remote User','Contact Name','Activity Type','Call Status','Direction') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Google Duo - Call History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Google Duo - Call History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Google Duo - Call History data available')
    
        # --- Query 2: Contacts ---
        cursor.execute('''
        select
        case system_contact_last_update_millis
            when 0 then ''
            else datetime(system_contact_last_update_millis/1000, 'unixepoch')
        end as 'Last Updated Timestamp',
        contact_display_name as 'Contact Name',
        user_id as 'Contact Info',
        contact_phone_type_custom as 'Contact Label',
        contact_id as 'Contact ID'
        from duo_users
        ORDER by contact_id
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Duo - Contacts')
            report.start_artifact_report(report_folder, 'Google Duo - Contacts')
            report.add_script()
            data_headers = ('Last Updated Timestamp','Contact Name','Contact Info','Contact Label','Contact ID')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'Google Duo - Contacts'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Google Duo - Contacts'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Google Duo - Contacts data available')
    
        # --- Query 3: Messages / Notes (FIXED) ---
        
        # Check if 'saved_status' column exists in 'messages' table
        try:
            cursor.execute("PRAGMA table_info(messages)")
            columns = [column[1] for column in cursor.fetchall()]
            has_saved_status = 'saved_status' in columns
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            has_saved_status = False

        # Define the 'File Saved' column selection based on availability
        if has_saved_status:
            saved_status_query = """
            case saved_status
                when 0 then ''
                when 1 then 'Yes'
            end as 'File Saved'
            """
        else:
            saved_status_query = "'' as 'File Saved'"

        query_messages = f'''
        select
        case sent_timestamp_millis
            when 0 then ''
            else datetime(sent_timestamp_millis/1000,'unixepoch')
        end as 'Sent Timestamp',
        case received_timestamp_millis
            when 0 then ''
            else datetime(received_timestamp_millis/1000,'unixepoch')
        end as 'Received Timestamp',
        case seen_timestamp_millis
            when 0 then ''
            else datetime(seen_timestamp_millis/1000,'unixepoch')
        end as 'Viewed Timestamp',
        sender_id,
        recipient_id,
        content_uri,
        replace(content_uri, rtrim(content_uri, replace(content_uri, '/', '')), '') as 'File Name',
        content_size_bytes,
        {saved_status_query}
        from messages
        '''

        cursor.execute(query_messages)

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        
        if usageentries > 0:
            for row in all_rows:
            
                sent_ts = row[0]
                received_ts = row[1]
                viewed_ts = row[2]
                sender_id = row[3]
                recipient_id = row[4]
                # row[5] is content_uri, unused in report logic, removed to fix pylint warning
                content_name = row[6]
                content_size = row[7]
                file_saved = row[8]
                thumb = ''
                
                for match in files_found:
                    if content_name in match:
                        shutil.copy2(match, report_folder)
                        data_file_name = os.path.basename(match)
                        thumb = f'<img src="{report_folder}/{data_file_name}" width="300"></img>'
            
                # FIX: Using the variables defined above instead of row[] indices
                data_list.append((sent_ts, received_ts, viewed_ts, sender_id, recipient_id, thumb, content_size, file_saved))
            
            report = ArtifactHtmlReport('Google Duo - Notes')
            report.start_artifact_report(report_folder, 'Google Duo - Notes')
            report.add_script()
            data_headers = ('Sent Timestamp','Received Timestamp','Viewed Timestamp','Sender','Recipient','Content','Size','File Saved')

            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Content'])
            report.end_artifact_report()
            
            tsvname = 'Google Duo - Notes'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Google Duo - Notes'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Google Duo - Notes data available')
    
    db.close()

__artifacts__ = {
        "googleDuo": (
                "Google Duo",
                ('*/com.google.android.apps.tachyon/databases/tachyon.db*','*/com.google.android.apps.tachyon/files/media/*.*'),
                get_googleDuo)
}