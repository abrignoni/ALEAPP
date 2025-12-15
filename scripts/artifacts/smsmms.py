import os
import shutil
import sqlite3

from html import escape
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_table_exist_in_db, does_column_exist_in_db

# Reference for flag values for mms:
# ---------------------------------- 
# https://developer.android.com/reference/android/provider/Telephony.Mms.Addr#TYPE
# https://android.googlesource.com/platform/frameworks/opt/mms/+/4bfcd8501f09763c10255442c2b48fad0c796baa/src/java/com/google/android/mms/pdu/PduHeaders.java

mms_query = \
'''
    SELECT pdu._id as mms_id, 
        thread_id, 
        CASE WHEN date>0 THEN datetime(pdu.date, 'UNIXEPOCH')
             ELSE ""
        END as date,
        CASE WHEN date_sent>0 THEN datetime(pdu.date_sent, 'UNIXEPOCH')
             ELSE ""
        END as date_sent,
        read,
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x89)as "FROM",
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x97)as "TO",
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x82)as "CC",
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x81)as "BCC",
        CASE WHEN msg_box=1 THEN "Received" 
             WHEN msg_box=2 THEN "Sent" 
             ELSE msg_box 
        END as msg_box,
        part._id as part_id, seq, ct, cl, _data, text 
    FROM pdu LEFT JOIN part ON part.mid=pdu._id
    ORDER BY pdu._id, date, part_id 
'''

sms_query =\
'''
    SELECT _id as msg_id, thread_id, address, person, 
        CASE WHEN date>0 THEN datetime(date/1000, 'UNIXEPOCH')
             ELSE ""
        END as date,
        CASE WHEN date_sent>0 THEN datetime(date_sent/1000, 'UNIXEPOCH')
             ELSE ""
        END as date_sent,
        read,
        CASE WHEN type=1 THEN "Received"
             WHEN type=2 THEN "Sent"
             WHEN type=3 THEN "Draft"
             WHEN type=4 THEN "Outbox"
             WHEN type=5 THEN "Failed"
             WHEN type=6 THEN "Queued"
             {extendedType}
             ELSE type 
        END as type,
        body, service_center, error_code
    FROM {smsTableName}
    ORDER BY date
'''

lgElectronicsExtendedTypes =\
'''
             WHEN type=7 THEN "Blocked Number"
             WHEN type=8 THEN "Scheduled Send"
             WHEN type=19 THEN "Broadcast Alert"
'''

def GetSmsQueryForTable(tableName, extendedTypes = ''):
    return sms_query.format(smsTableName = tableName, extendedType = extendedTypes)

def AppendSmsRowToDataList(data_list, row, wrap_text):
    if wrap_text:
        data_list.append((row['date'],row['msg_id'], row['thread_id'], row['address'],
            row['person'],row['date_sent'], row['read'],
            row['type'], row['body'].replace("\n",""), row['service_center'], row['error_code']))        
    else:
        data_list.append((row['date'],row['msg_id'], row['thread_id'], row['address'],
            row['person'],row['date_sent'], row['read'],
            row['type'], row['body'], row['service_center'], row['error_code']))

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/' 

def get_sms_mms(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue
        #elif file_found.find('{0}user_de{0}'.format(slash)) >= 0:
        #    # Skip data/user_de/0/com.android.providers.telephony/databases/mmssms.db, it is always empty
        #    continue
        elif not file_found.endswith('mmssms.db'):
            continue # Skip all other files
        
        db = open_sqlite_db_readonly(file_found)
        db.row_factory = sqlite3.Row # For fetching columns by name

        got_messages = read_sms_messages(db, report_folder, file_found, seeker, wrap_text)
        read_mms_messages(db, report_folder, file_found, seeker)

        db.close()
        if got_messages:
            return
        
def read_sms_messages(db, report_folder, file_found, seeker, wrap_text):
    samsung_spam_sms_table_exists = does_table_exist_in_db(file_found, 'spam_sms')
    lg_electronics_device_data = does_column_exist_in_db(file_found, 'sms', 'lgeSiid')
    cursor = db.cursor()

    if not lg_electronics_device_data:
        cursor.execute(GetSmsQueryForTable('sms'))
    else:
        cursor.execute(GetSmsQueryForTable('sms', lgElectronicsExtendedTypes))

    all_rows = cursor.fetchall()
    entries = len(all_rows)
    if entries > 0:
        report = ArtifactHtmlReport('SMS messages')
        report.start_artifact_report(report_folder, 'SMS messages')
        report.add_script()
        data_headers = ('Date','MSG ID', 'Thread ID', 'Address', 'Contact ID',  
            'Date sent', 'Read', 'Type', 'Body', 'Service Center', 'Error code')
        data_list = []
        for row in all_rows:
            AppendSmsRowToDataList(data_list, row, wrap_text)
            
        if samsung_spam_sms_table_exists:
            cursor.execute(GetSmsQueryForTable('spam_sms'))
            all_rows = cursor.fetchall()
            entries = len(all_rows)
            if entries > 0:
                for row in all_rows:
                    AppendSmsRowToDataList(data_list, row, wrap_text)

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'sms messages'
        tsv(report_folder, data_headers, data_list, tsvname, file_found.replace(seeker.data_folder, ''))
        
        tlactivity = f'SMS Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No SMS messages found!')
        return False
    return True

class MmsMessage:
    def __init__(self, mms_id, thread_id, date, date_sent, read, From, to, cc, bcc, type, part_id, seq, ct, cl, data, text):
        self.mms_id = mms_id
        self.thread_id = thread_id
        self.date = date
        self.date_sent = date_sent
        self.read = read
        self.From = From
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.type = type
        self.part_id = part_id
        self.seq = seq
        self.ct = ct
        self.cl = cl
        self.data = data
        self.text = text
        # Added
        self.body = ''
        self.filename = ''

def add_mms_to_data_list(data_list, mms_list, folder_name):
    '''Reads messages from mms_list and adds valid mms messages to data_list'''
    for mms in mms_list:
        if mms.ct == 'application/smil': # content type is smil, skipping this
            continue
        else:
            if mms.filename:
                if mms.ct.find('image') >= 0:
                    body = '<a href="{1}/{0}"><img src="{1}/{0}" class="img-fluid z-depth-2 zoom" style="max-height: 400px" title="{0}"></a>'.format(mms.filename, folder_name)
                elif mms.ct.find('audio') >= 0:
                    body = '<audio controls><source src="{1}/{0}"></audio>'.format(mms.filename, folder_name)
                elif mms.ct.find('video') >= 0:
                    body = '<video controls width="250"><source src="{1}/{0}"></video>'.format(mms.filename, folder_name)
                else:
                    logfunc(f'Unknown body type, content type = {mms.ct}')
                    body = '<a href="{1}/{0}">{0}</a>'.format(mms.filename, folder_name)
            else:
                body = mms.body
            
            mms_data = [mms.mms_id, mms.thread_id, 
                        mms.date, mms.date_sent, mms.read, 
                        mms.From, mms.to, mms.cc, mms.bcc, 
                        body]
            data_list.append(mms_data)

def read_mms_messages(db, report_folder, file_found, seeker):    

    if report_folder[-1] == slash: 
        folder_name = os.path.basename(report_folder[:-1])
    else:
        folder_name = os.path.basename(report_folder)
    
    cursor = db.cursor()
    cursor.execute(mms_query)
    all_rows = cursor.fetchall()
    entries = len(all_rows)
    if entries > 0:
        report = ArtifactHtmlReport('MMS messages')
        report.start_artifact_report(report_folder, 'MMS messages')
        report.add_script()
        data_headers = ('Date', 'MSG ID', 'Thread ID', 'Date sent', 'Read',
            'From', 'To', 'Cc', 'Bcc', 'Body')
        data_list = []

        last_id = 0
        temp_mms_list = []
        for row in all_rows:
            id = row['mms_id']
            if id != last_id: # Start of new message, write out old message in temp buffer
                add_mms_to_data_list(data_list, temp_mms_list, folder_name)
                # finished writing
                last_id = id
                temp_mms_list = []

            msg = MmsMessage(row['date'], row['mms_id'], row['thread_id'], 
                 row['date_sent'], row['read'],
                row['FROM'], row['TO'], row['CC'], row['BCC'], row['msg_box'], 
                row['part_id'], row['seq'], row['ct'], row['cl'], 
                row['_data'], row['text'])
            temp_mms_list.append(msg)

            data_file_path = row['_data']
            if data_file_path == None: # Has text, no file
                msg.body = row['text']
            else:
                # Get file from path
                if data_file_path[0] == '/':
                    temp_path = data_file_path[1:]
                else:
                    temp_path = data_file_path
                
                path_parts = temp_path.split('/')
                # This next routine reduces /data/xx/yy/img.jpg to /xx/yy/img.jpg removing the
                # first folder in the path, so that if our root (starting point) is inside 
                # that folder, it will still find the file
                if len(path_parts) > 2:
                    path_parts.pop(0)
                    temp_path = '/'.join(path_parts)

                if is_windows:
                    temp_path = temp_path.replace('/', '\\')
                data_file_path_regex = f'**{slash}' + temp_path

                files_found = seeker.search(data_file_path_regex)
                if files_found:
                    data_file_real_path = str(files_found[0])
                    shutil.copy2(data_file_real_path, report_folder)
                    data_file_name = os.path.basename(data_file_real_path)
                    msg.filename = data_file_name
                else:
                    logfunc(f'File not found: {data_file_path}')
        # add last msg to list
        add_mms_to_data_list(data_list, temp_mms_list, folder_name)

        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'mms messages'
        tsv(report_folder, data_headers, data_list, tsvname, file_found.replace(seeker.data_folder, ''))
        
        tlactivity = f'MMS Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No MMS messages found!')
        return False
    return True

__artifacts__ = {
        "sms_mms": (
                "SMS & MMS",
                ('*/com.android.providers.telephony/databases/mmssms*'),
                get_sms_mms)
}