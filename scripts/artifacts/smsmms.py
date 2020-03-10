import os
import sqlite3

from html import escape
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc

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
    ORDER BY pdu._id, date 
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
             ELSE type 
        END as type,
        body, service_center, error_code
    FROM sms
    ORDER BY date
'''

def get_sms_mms(files_found, report_folder, seeker):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('mmssms.db'):
            continue # Skip all other files
        
        db = sqlite3.connect(file_found)
        db.row_factory = sqlite3.Row # For fetching columns by name

        read_sms_messages(db)
        read_mms_messages(db)

        db.close()
        return
        
def read_sms_messages(db):
    cursor = db.cursor()
    cursor.execute(sms_query)
    all_rows = cursor.fetchall()
    entries = len(all_rows)
    if entries > 0:
        report = ArtifactHtmlReport('SMS messages')
        report.start_artifact_report(report_folder, 'SMS & MMS')
        report.add_script()
        data_headers = ('MSG ID', 'Thread ID', 'Address', 'Contact ID', 'Date', 
            'Date sent', 'Read', 'Type', 'Body', 'Service Center', 'Error code')
        data_list = []
        for row in all_rows:
            data_list.append((row['msg_id'], row['thread_id'], row['address'],
                row['person'], row['date'], row['date_sent'], row['read'],
                row['type'], row['service_center'], row['error_code']))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No SMS messages found!')

def read_mms_messages(db):        
    cursor = db.cursor()
    cursor.execute(mms_query)
    all_rows = cursor.fetchall()
    entries = len(all_rows)
    if entries > 0:
        report = ArtifactHtmlReport('MMS messages')
        report.start_artifact_report(report_folder, 'SMS & MMS')
        report.add_script()
        data_headers = ('MSG ID', 'Thread ID', 'Date', 'Date sent', 'Read',
            'From', 'To', 'Cc', 'Bcc', 'Body')
        data_list = []

        #TODO Process the rows to combine ones that are from a single message, 
        #     recraete the HTML and images. copy the images.
        for row in all_rows:
            data_list.append((row['mms_id'], row['thread_id'], row['address'],
                row['person'], row['date'], row['date_sent'], row['read'],
                row['type'], row['service_center'], row['error_code']))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No MMS messages found!')