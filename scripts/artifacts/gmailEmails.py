import zlib
import sqlite3
import blackboxprotobuf
import os
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, media_to_html

def get_gmailEmails(files_found, report_folder, seeker, wrap_text):
    
    bigTopDataDB = ''
    source_bigTop = ''
    downloaderDB = ''
    source_downloader = ''
    
    bigTopDataDB_found = []
    source_bigTop_found = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('-wal'):
            continue
        elif file_found.endswith('-shm'):
            continue
        elif os.path.basename(file_found).startswith('.'):
            continue
        if os.path.basename(file_found).startswith('bigTopDataDB'):
            bigTopDataDB = str(file_found)
            source_bigTop = file_found.replace(seeker.data_folder, '')
            bigTopDataDB_found.append(bigTopDataDB)
            source_bigTop_found.append(source_bigTop)
        if os.path.basename(file_found).startswith('downloader.db'):
            downloaderDB = str(file_found)
            source_downloader = file_found.replace(seeker.data_folder, '')
        
    for i in range(len(bigTopDataDB_found)):
        bigTopDataDB = bigTopDataDB_found[i]
        source_bigTop = source_bigTop_found[i]
        db = open_sqlite_db_readonly(bigTopDataDB)
        cursor = db.cursor()
        cursor.execute('''
        select *
        from item_messages
        left join item_message_attachments on item_messages.row_id = item_message_attachments.item_messages_row_id
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        filename = file_found
        data_list = []
        
        if usageentries > 0:
            for row in all_rows:
                id = row[7]
                if id is not None:
                    data = id
                    arreglo = bytearray(data)
                    arreglo = arreglo[1:]
                    decompressed_data = zlib.decompress(arreglo)
                    message, typedef = blackboxprotobuf.decode_message(decompressed_data)
                   
                    timestamp = (datetime.utcfromtimestamp(message['17'] / 1000))              
                else:
                    continue

                serverid = row[1]
                attachname = row[15]
                attachhash = row[16]
                attachment = ''
                
                data = id
                arreglo = bytearray(data)
                arreglo = arreglo[1:]
                decompressed_data = zlib.decompress(arreglo)
                message,typedef = blackboxprotobuf.decode_message(decompressed_data)
                
                timestamp = (datetime.utcfromtimestamp(message['17']/1000))
                
                to = (message.get('1', '')).get('2', '') if '1' in message and '2' in message['1'] else '' #receiver
                if isinstance(to, bytes):
                    to = to.decode()

                toname = (message.get('1', '')).get('3', '') if '1' in message and '3' in message['1'] else '' #receiver name
                if isinstance(toname, bytes):
                    toname = toname.decode()
                        
                replyto = (message['11'].get('17', '')) if '11' in message and '17' in message['11'] else '' #reply email
                if isinstance(replyto, bytes):
                    replyto = replyto.decode()
                    
                replytoname = (message['11'].get('15', b'')) #reply name
                if '11' in message and '15' in message['11'] and isinstance(message['11'].get('15', b''), bytes): 
                    replytoname = replytoname.decode() 
                else: 
                    replytoname = (message['11'].get('15', ''))

                subjectline = (message.get('5', '')) #Subject line
                if subjectline != '':
                    if isinstance(subjectline, bytes):
                        subjectline = subjectline.decode()
                    else:
                        subjectline = ''
                
                messagetest = (message.get('6', '')) #HTML message
                if messagetest != '':
                    messagetest = message['6'].get('2','')
                    if messagetest != '':
                        if isinstance(message['6']['2'], list):
                            for x in message['6']['2']:
                                messagehtml = messagehtml + (x['3']['2'].decode())
                        else:
                            messagehtml = (message['6']['2']['3']['2'].decode()) 
               
                mailedby = (message.get('11', {}).get('8', b'')) #mailed by
                if isinstance(message.get('11', {}).get('8', ''), bytes): 
                    mailedby = mailedby.decode() 
                else: 
                    mailedby = ''

                signedby = (message.get('11', {}).get('9', b'')) #signed by
                if isinstance(message.get('11', {}).get('9', ''), bytes): 
                    signedby = signedby.decode() 
                else: 
                    signedby = ''

                if attachname == 'noname':
                    attachname = ''
                elif attachname is None:
                    attachname = ''
                elif attachhash is None:
                    attachhash = ''
                else:
                    for attachpath in files_found:
                        if attachhash in attachpath:
                            if attachpath.endswith(attachname):
                                attachment = media_to_html(attachpath, files_found, report_folder)
                    
                data_list.append((timestamp,serverid,messagehtml,attachment,attachname,to,toname,replyto,replytoname,subjectline,mailedby,signedby))

            description = 'Gmail - App Emails'
            report = ArtifactHtmlReport('Gmail - App Emails')
            report.start_artifact_report(report_folder, 'Gmail - App Emails', description)
            report.add_script()
            data_headers = ('Timestamp','Email ID','Message','Attachment','Attachment Name','To','To Name','Reply To','Reply To Name','Subject Line','Mailed By','Signed by')
            report.write_artifact_data_table(data_headers, data_list, source_bigTop,html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Gmail - App Emails'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = 'Gmail - App Emails'
            timeline(report_folder, tlactivity, data_list, data_headers)
        
        else:
            logfunc('No Gmail - App Emails data available')
            
        cursor = db.cursor()

        #Get Gmail label details
        cursor.execute('''
        select
        label_server_perm_id,
        unread_count,
        total_count,
        unseen_count
        from label_counts
        order by label_server_perm_id
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            description = 'Gmail mail labels'
            report = ArtifactHtmlReport('Gmail - Label Details')
            report.start_artifact_report(report_folder, 'Gmail - Label Details')
            report.add_script()
            data_headers = ('Label','Unread Count','Total Count','Unseen Count')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3]))

            report.write_artifact_data_table(data_headers, data_list, source_bigTop)
            report.end_artifact_report()
            
            tsvname = f'Gmail - Label Details'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('No Gmail - Label Details data available' )

        db.close()
        
    if downloaderDB != '':
        db = open_sqlite_db_readonly(downloaderDB)
        cursor = db.cursor()

        #Get Gmail download requests
        cursor.execute('''
        select 
        datetime(request_time_ms/1000,'unixepoch'),
        account_name,
        type,
        caller_id,
        url,
        target_file_path,
        target_file_size,
        priority
        from download_requests
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            description = 'Gmail download requests'
            report = ArtifactHtmlReport('Gmail - Download Requests')
            report.start_artifact_report(report_folder, 'Gmail - Download Requests')
            report.add_script()
            data_headers = ('Timestamp Requested','Account Name','Download Type','Message ID','URL','Target File Path','Target File Size','Priority')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

            report.write_artifact_data_table(data_headers, data_list, source_downloader)
            report.end_artifact_report()
            
            tsvname = f'Gmail - Download Requests'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Gmail - Download Requests'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Gmail - Download Requests data available')
            
        db.close()
    else:
        logfunc('No Gmail - Download Requests data available')
    
__artifacts__ = {
        "Gmail": (
                "Gmail",
                ('*/data/com.google.android.gm/databases/bigTopDataDB.*','*/data/com.google.android.gm/files/downloads/*/attachments/*/*.*','*/data/com.google.android.gm/databases/downloader.db*'),
                get_gmailEmails)
}