import datetime
import json
import zlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

# Backup agent code defined here:
# https://cs.android.com/android/platform/superproject/main/+/main:packages/providers/TelephonyProvider/src/com/android/providers/telephony/TelephonyBackupAgent.java

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/' 

def ReadUnixTimeMs(unix_time): # Unix timestamp is time epoch beginning 1970/1/1
    '''Returns datetime object, or empty string upon error'''
    if unix_time not in ('0', 0, None, ''):
        try:
            if isinstance(unix_time, str):
                unix_time = float(unix_time)
            return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=unix_time/1000)
        except (ValueError, OverflowError, TypeError) as ex:
            logfunc("ReadUnixTimeMs() Failed to convert timestamp from value " + str(unix_time) + " Error was: " + str(ex))
    return ''

def ReadUnixTime(unix_time): # Unix timestamp is time epoch beginning 1970/1/1
    '''Returns datetime object, or empty string upon error'''
    if unix_time not in ('0', 0, None, ''):
        try:
            if isinstance(unix_time, str):
                unix_time = float(unix_time)
            return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=unix_time)
        except (ValueError, OverflowError, TypeError) as ex:
            logfunc("ReadUnixTime() Failed to convert timestamp from value " + str(unix_time) + " Error was: " + str(ex))
    return ''

def read_messages_from_backup(file_found):
    logfunc(f'Processing file {file_found}')
    with open(file_found, 'rb') as f:
        file_content = f.read()
        if file_content[0:1] == b'\x78': # zlib compressed
            try:
                data = zlib.decompress(file_content)  
            except zlib.error as ex:
                logfunc(ex)
                return []
            data_str = data.decode('utf8', 'ignore')
            try:
                msg_data = json.loads(data_str)
                return msg_data
            except json.JSONDecodeError as ex:
                logfunc(str(ex))
        else:
            logfunc('Not the right format!')
    return []

def get_sms_mms_from_backup(files_found, report_folder, seeker, wrap_text):
    sms_messages = []
    mms_messages = []

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue
        
        if file_found.endswith('sms_backup'):
            messages = read_messages_from_backup(file_found)
            sms_messages.extend(messages)
        elif file_found.endswith('mms_backup'):
            messages = read_messages_from_backup(file_found)
            mms_messages.extend(messages)
        else:
            logfunc(f'unknown file found: {file_found}')
            continue

    if mms_messages:
        report = ArtifactHtmlReport('MMS messages')
        report.start_artifact_report(report_folder, 'MMS messages')
        report.add_script()
        data_headers = ('Date', 'Date sent', 'Content Location', 'Recipients', 'Subject',
                        'Read', 'MMS Addresses', 'Transaction ID', 'MMS Version',
                        'Body', 'Message Type', 'Message Box')
        data_list = []
        for mms in mms_messages:
            mbox = mms.get('msg_box', '')
            if mbox == '0':
                mbox = 'All messages'
            elif mbox == '1':
                mbox = 'Inbox'
            elif mbox == '2':
                mbox = 'Sent'
            elif mbox == '3':
                mbox = 'Drafts'
            elif mbox == '4':
                mbox = 'Outbox'
            elif mbox == '5':
                mbox = 'Failed'

            body = mms.get('mms_body', '')
            if wrap_text:
                body = body.replace("\n", "")
                
            data_list.append((ReadUnixTime(mms.get('date', 0)),
                             ReadUnixTime(mms.get('date_sent', 0)),
                             mms.get('ct_l', ''),
                             ', '.join(mms.get('recipients', [])),
                             mms.get('sub', ''),
                             mms.get('read', ''),
                             str(mms.get('mms_addresses', [])),
                             mms.get('tr_id', ''),
                             mms.get('v', ''),
                             body,
                             mms.get('m_type', ''),
                             mbox
                             ),)
            
        logfunc(f'Total mms messages = {len(mms_messages)}')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'mms messages'
        tsv(report_folder, data_headers, data_list, tsvname, file_found.replace(seeker.data_folder, ''))
        
        tlactivity = f'MMS Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)

    if sms_messages:
        report = ArtifactHtmlReport('SMS messages')
        report.start_artifact_report(report_folder, 'SMS messages')
        report.add_script()
        data_headers = ('Date', 'Date sent', 'Read', 'Type', 'Body', 'recipients', 'Address', 'Status')
        data_list = []

        for sms in sms_messages:
            body = sms.get('body', '')
            if wrap_text:
                body = body.replace("\n", "")
            data_list.append((ReadUnixTimeMs(sms.get('date', 0)),
                             ReadUnixTimeMs(sms.get('date_sent', 0)),
                             sms.get('read', ''),
                             sms.get('type', ''),
                             body,
                             ', '.join(sms.get('recipients', [])),
                             sms.get('address', ''),
                             sms.get('status', '')
                            ),)
        logfunc(f'Total sms messages = {len(sms_messages)}')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'sms messages'
        tsv(report_folder, data_headers, data_list, tsvname, file_found.replace(seeker.data_folder, ''))
        
        tlactivity = f'SMS Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No SMS or MMS messages found!')
        return False
    return True

__artifacts__ = {
        "sms_mms_backup": (
                "SMS & MMS from backup.ab",
                ('*/com.android.providers.telephony/d_f/*_backup'),
                get_sms_mms_from_backup
        )
}