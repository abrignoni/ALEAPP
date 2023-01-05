import zlib
import sqlite3
import blackboxprotobuf
import os
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly, media_to_html


def get_gmailEmails(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('-wal'):
            continue
        elif file_found.endswith('-shm'):
            continue
        elif os.path.basename(file_found).startswith('.'):
            continue
        elif os.path.basename(file_found).startswith('bigTopDataDB'):
            break
        
    db = open_sqlite_db_readonly(file_found)
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
            to = (message['1']['2'].decode()) #receiver
            toname = (message['1'].get('3','')) #receiver name
            if isinstance(toname, bytes):
                toname = toname.decode()
                
            replyto = (message['11'].get('17', '')) #reply email
            if isinstance(replyto, bytes):
                    replyto = replyto.decode()
            else:
                replyto = ''
                
            replytoname = (message['11'].get('15', '')) #reply name
            if isinstance(replytoname, bytes):
                replytoname = replytoname.decode()
            else:
                replytoname = ''
            
            subjectline = (message['5'].decode()) #Subject line
            
            if isinstance(message['6']['2'], list):
                for x in message['6']['2']:
                    messagehtml = messagehtml + (x['3']['2'].decode())
            else:
                messagehtml = (message['6']['2']['3']['2'].decode()) #HTML message
                        
            mailedby = (message['11']['8'].decode()) #mailed by
            signedby = (message['11'].get('9', '')) #signed by
            if signedby != '':
                signedby = signedby.decode()
            
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
                            #print(attachpath)
                            attachment = media_to_html(attachpath, files_found, report_folder)
                
            
            
            data_list.append((timestamp,serverid,messagehtml,attachment,attachname,to,toname,replyto,replytoname,subjectline,mailedby,signedby))

        description = 'Gmail App Emails'
        report = ArtifactHtmlReport('Gmail App Emails')
        report.start_artifact_report(report_folder, 'Gmail App Emails', description)
        report.add_script()
        data_headers = ('Timestamp','Email ID','Message','Attachment','Attachment Name','To','To Name','Reply To','Reply To Name','Subject Line','Mailed By','Signed by')
        report.write_artifact_data_table(data_headers, data_list, filename,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Gmail App Emails'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Gmail App Emails'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No Gmail App Emails data available')
    
__artifacts__ = {
        "Gmail": (
                "Gmail",
                ('*/data/com.google.android.gm/databases/bigTopDataDB.*','*/data/com.google.android.gm/files/downloads/*/attachments/*/*.*'),
                get_gmailEmails)
}