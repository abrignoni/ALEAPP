# pylint: disable=W0613
__artifacts_v2__ = {
    "get_mms_from_backup": {
        "name": "SMS and MMS Backup - MMS",
        "description": "MMS messages recovered from backup.ab telephony backup files",
        "author": "",
        "creation_date": "2024-08-15",
        "last_update_date": "2024-08-15",
        "requirements": "none",
        "category": "SMS & MMS from backup.ab",
        "notes": "",
        "paths": ('*/com.android.providers.telephony/d_f/*_backup',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "get_sms_from_backup": {
        "name": "SMS and MMS Backup - SMS",
        "description": "SMS messages recovered from backup.ab telephony backup files",
        "author": "",
        "creation_date": "2024-08-15",
        "last_update_date": "2024-08-15",
        "requirements": "none",
        "category": "SMS & MMS from backup.ab",
        "notes": "",
        "paths": ('*/com.android.providers.telephony/d_f/*_backup',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    }
}

import datetime
import json
import zlib

from scripts.ilapfuncs import artifact_processor, logfunc, is_platform_windows

# Backup agent code defined here:
# https://cs.android.com/android/platform/superproject/main/+/main:packages/providers/TelephonyProvider/src/com/android/providers/telephony/TelephonyBackupAgent.java

slash = '\\' if is_platform_windows() else '/'

EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

MMS_BOX = {'0': 'All messages', '1': 'Inbox', '2': 'Sent', '3': 'Drafts', '4': 'Outbox', '5': 'Failed'}


def ReadUnixTimeMs(unix_time):
    '''Returns tz-aware UTC datetime from epoch milliseconds, or '' on error.'''
    if unix_time not in ('0', 0, None, ''):
        try:
            return EPOCH + datetime.timedelta(seconds=float(unix_time) / 1000)
        except (ValueError, OverflowError, TypeError) as ex:
            logfunc("ReadUnixTimeMs() Failed to convert " + str(unix_time) + " Error: " + str(ex))
    return ''


def ReadUnixTime(unix_time):
    '''Returns tz-aware UTC datetime from epoch seconds, or '' on error.'''
    if unix_time not in ('0', 0, None, ''):
        try:
            return EPOCH + datetime.timedelta(seconds=float(unix_time))
        except (ValueError, OverflowError, TypeError) as ex:
            logfunc("ReadUnixTime() Failed to convert " + str(unix_time) + " Error: " + str(ex))
    return ''


def read_messages_from_backup(file_found):
    logfunc(f'Processing file {file_found}')
    with open(file_found, 'rb') as f:
        file_content = f.read()
    if file_content[0:1] != b'\x78':  # not zlib compressed
        logfunc('Not the right format!')
        return []
    try:
        data = zlib.decompress(file_content)
    except zlib.error as ex:
        logfunc(str(ex))
        return []
    try:
        return json.loads(data.decode('utf8', 'ignore'))
    except json.JSONDecodeError as ex:
        logfunc(str(ex))
        return []


def _backup_files(files_found, suffix):
    out = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            continue  # Skip mirror, it should be duplicate data
        if file_found.endswith(suffix):
            out.append(file_found)
    return out


@artifact_processor
def get_mms_from_backup(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in _backup_files(files_found, 'mms_backup'):
        source_path = file_found
        for mms in read_messages_from_backup(file_found):
            body = mms.get('mms_body', '')
            if wrap_text:
                body = body.replace("\n", "")
            data_list.append((
                ReadUnixTime(mms.get('date', 0)), ReadUnixTime(mms.get('date_sent', 0)),
                mms.get('ct_l', ''), ', '.join(mms.get('recipients', [])), mms.get('sub', ''),
                mms.get('read', ''), str(mms.get('mms_addresses', [])), mms.get('tr_id', ''),
                mms.get('v', ''), body, mms.get('m_type', ''), MMS_BOX.get(mms.get('msg_box', ''), mms.get('msg_box', ''))))

    data_headers = (('Date', 'datetime'), ('Date sent', 'datetime'), 'Content Location', 'Recipients', 'Subject',
                    'Read', 'MMS Addresses', 'Transaction ID', 'MMS Version', 'Body', 'Message Type', 'Message Box')
    return data_headers, data_list, source_path


@artifact_processor
def get_sms_from_backup(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in _backup_files(files_found, 'sms_backup'):
        source_path = file_found
        for sms in read_messages_from_backup(file_found):
            body = sms.get('body', '')
            if wrap_text:
                body = body.replace("\n", "")
            data_list.append((
                ReadUnixTimeMs(sms.get('date', 0)), ReadUnixTimeMs(sms.get('date_sent', 0)),
                sms.get('read', ''), sms.get('type', ''), body,
                ', '.join(sms.get('recipients', [])), sms.get('address', ''), sms.get('status', '')))

    data_headers = (('Date', 'datetime'), ('Date sent', 'datetime'), 'Read', 'Type', 'Body', 'recipients', ('Address', 'phonenumber'), 'Status')
    return data_headers, data_list, source_path
