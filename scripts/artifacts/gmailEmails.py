__artifacts_v2__ = {
    "gmailEmails": {
        "name": "Gmail - App Emails",
        "description": "Parses emails from Gmail",
        "author": "Alexis Brignoni, Patrick Dalla, @stark4n6",
        "creation_date": "2023-01-04",
        "last_update_date": "2025-07-30",
        "requirements": "none",
        "category": "Email",
        "notes": "",
        "paths": ('*/data/com.google.android.gm/databases/bigTopDataDB.*','*/data/com.google.android.gm/files/downloads/*/attachments/*/*.*'),
        "output_types": "standard",
        "html_columns": ["Message"],
        "artifact_icon": "inbox",
    },
    "gmailLabels": {
        "name": "Gmail - Label Details",
        "description": "Parses email label metadata from Gmail",
        "author": "@stark4n6",
        "creation_date": "2023-01-04",
        "last_update_date": "2025-07-31",
        "requirements": "none",
        "category": "Email",
        "notes": "",
        "paths": ('*/data/com.google.android.gm/databases/bigTopDataDB.*','*/data/com.google.android.gm/files/downloads/*/attachments/*/*.*'),
        "output_types": ["html","tsv","lava"],
        "artifact_icon": "mail",
    },
    "gmailDownloadRequests": {
        "name": "Gmail - Download Requests",
        "description": "Parses download requests from Gmail",
        "author": "@stark4n6",
        "creation_date": "2023-01-04",
        "last_update_date": "2025-07-30",
        "requirements": "none",
        "category": "Email",
        "notes": "",
        "paths": ('*/data/com.google.android.gm/databases/downloader.db*'),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import zlib
import blackboxprotobuf
import os
from datetime import datetime

from scripts.ilapfuncs import open_sqlite_db_readonly, media_to_html, get_sqlite_db_records, artifact_processor

@artifact_processor
def gmailEmails(files_found, report_folder, seeker, wrap_text):
    bigTopDataDB = ''
    source_bigTop = ''
    
    bigTopDataDB_found = []
    source_bigTop_found = []
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith(('-wal','-shm')):
            continue
        elif os.path.basename(file_found).startswith('.'):
            continue
        if os.path.basename(file_found).startswith('bigTopDataDB'):
            bigTopDataDB = str(file_found)
            source_bigTop = file_found.replace(seeker.data_folder, '')
            bigTopDataDB_found.append(bigTopDataDB)
            source_bigTop_found.append(source_bigTop)
        
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
        proto_col = ''
        
        cursor.execute('''PRAGMA table_info(item_messages);''')
        columns_info = cursor.fetchall()
        for col_info in columns_info:
            if col_info[1] == "zipped_message_proto":
                proto_col = col_info[0]
        
        if usageentries > 0:
            for row in all_rows:
                id = row[proto_col]
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
                    
                data_list.append((timestamp,serverid,messagehtml,attachment,attachname,to,toname,replyto,replytoname,subjectline,mailedby,signedby,bigTopDataDB))

    data_headers = (('Timestamp','datetime'),'Email ID','Message','Attachment','Attachment Name','Recipient','Recipient Name','Reply To','Reply To Name','Subject Line','Mailed By','Signed by','Source File')
    return data_headers, data_list, 'See source file(s) below:'

@artifact_processor      
def gmailLabels(files_found, report_folder, seeker, wrap_text):
    bigTopDataDB = ''
    source_bigTop = ''
    
    bigTopDataDB_found = []
    source_bigTop_found = []
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith(('-wal','-shm')):
            continue
        elif os.path.basename(file_found).startswith('.'):
            continue
        if os.path.basename(file_found).startswith('bigTopDataDB'):
            bigTopDataDB = str(file_found)
            source_bigTop = file_found.replace(seeker.data_folder, '')
            bigTopDataDB_found.append(bigTopDataDB)
            source_bigTop_found.append(source_bigTop)
        
    for i in range(len(bigTopDataDB_found)):
        bigTopDataDB = bigTopDataDB_found[i]
        source_bigTop = source_bigTop_found[i]
        
        query = '''
        select
        label_server_perm_id,
        unread_count,
        total_count,
        unseen_count
        from label_counts
        order by label_server_perm_id
        '''
        
        db_records = get_sqlite_db_records(bigTopDataDB, query)
        
        for record in db_records:
            data_list.append((record[0],record[1],record[2],record[3],bigTopDataDB))
    
    data_headers = ('Label','Unread Count','Total Count','Unseen Count','Source File')
    return data_headers, data_list, 'See source file(s) below:'
      
@artifact_processor        
def gmailDownloadRequests(files_found, report_folder, seeker, wrap_text):
    downloaderDB = ''
    source_downloader = ''
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith(('-wal','-shm')):
            continue
        elif os.path.basename(file_found).startswith('.'):
            continue
        if os.path.basename(file_found).startswith('downloader.db'):
            downloaderDB = str(file_found)
            source_downloader = file_found.replace(seeker.data_folder, '')
    
    if downloaderDB != '':
        #Get Gmail download requests
        query = '''
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
        '''
        
        db_records = get_sqlite_db_records(downloaderDB, query)
        
        for record in db_records:
            data_list.append((record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7]))
    
    data_headers = (('Timestamp Requested','datetime'),'Account Name','Download Type','Message ID','URL','Target File Path','Target File Size','Priority')
    return data_headers, data_list, downloaderDB