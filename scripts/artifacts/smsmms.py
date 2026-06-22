# pylint: disable=W0613
__artifacts_v2__ = {
    "get_sms_mms": {
        "name": "SMS Messages",
        "description": "SMS messages from mmssms.db (incl. LG extended types and Samsung spam_sms)",
        "author": "",
        "creation_date": "2020-03-10",
        "last_update_date": "2020-03-10",
        "requirements": "none",
        "category": "SMS & MMS",
        "notes": "",
        "paths": ('*/com.android.providers.telephony/databases/mmssms*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "get_sms_mms_mms": {
        "name": "MMS Messages",
        "description": "MMS messages and attachments from mmssms.db",
        "author": "",
        "creation_date": "2020-03-10",
        "last_update_date": "2020-03-10",
        "requirements": "none",
        "category": "SMS & MMS",
        "notes": "",
        "paths": ('*/com.android.providers.telephony/databases/mmssms*',
                  '*/com.android.providers.telephony/app_parts/*',
                  '*/com.android.providers.telephony/parts/*'),
        "output_types": "standard",
        "artifact_icon": "image",
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly, does_table_exist_in_db,
                               does_column_exist_in_db, check_in_media)

_SMS_QUERY = '''
    SELECT _id as msg_id, thread_id, address, person, date, date_sent, read,
        CASE WHEN type=1 THEN 'Received' WHEN type=2 THEN 'Sent' WHEN type=3 THEN 'Draft'
             WHEN type=4 THEN 'Outbox' WHEN type=5 THEN 'Failed' WHEN type=6 THEN 'Queued'
             {extendedType} ELSE type END as type,
        body, service_center, error_code
    FROM {smsTableName}
    ORDER BY date
'''

_LG_EXTENDED_TYPES = '''
    WHEN type=7 THEN 'Blocked Number' WHEN type=8 THEN 'Scheduled Send'
    WHEN type=19 THEN 'Broadcast Alert'
'''

_MMS_QUERY = '''
    SELECT pdu._id as mms_id, thread_id, pdu.date as date, pdu.date_sent as date_sent, read,
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x89) as "FROM",
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x97) as "TO",
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x82) as "CC",
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x81) as "BCC",
        part._id as part_id, seq, ct, cl, _data, text
    FROM pdu LEFT JOIN part ON part.mid=pdu._id
    ORDER BY pdu._id, date, part_id
'''


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _rows(source_path, sql):
    db = open_sqlite_db_readonly(source_path)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _mmssms_dbs(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('mmssms.db') and '/mirror/' not in file_found.replace('\\', '/'):
            yield file_found


@artifact_processor
def get_sms_mms(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for source_path in _mmssms_dbs(files_found):
        extended = _LG_EXTENDED_TYPES if does_column_exist_in_db(source_path, 'sms', 'lgeSiid') else ''
        tables = ['sms']
        if does_table_exist_in_db(source_path, 'spam_sms'):
            tables.append('spam_sms')
        for table in tables:
            ext = extended if table == 'sms' else ''
            for r in _rows(source_path, _SMS_QUERY.format(smsTableName=table, extendedType=ext)):
                data_list.append((_ms_to_utc(r['date']), r['msg_id'], r['thread_id'], r['address'],
                                  r['person'], _ms_to_utc(r['date_sent']), r['read'], r['type'],
                                  r['body'], r['service_center'], r['error_code']))

    data_headers = (('Date', 'datetime'), 'MSG ID', 'Thread ID', 'Address', 'Contact ID',
                    ('Date Sent', 'datetime'), 'Read', 'Type', 'Body', 'Service Center', 'Error Code')
    return data_headers, data_list, source_path


@artifact_processor
def get_sms_mms_mms(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for source_path in _mmssms_dbs(files_found):
        for r in _rows(source_path, _MMS_QUERY):
            if r['ct'] == 'application/smil':  # presentation layer, not content
                continue
            data_path = r['_data']
            media_ref = ''
            body = ''
            if data_path:
                name = os.path.basename(str(data_path))
                match = next((str(f) for f in files_found if os.path.basename(str(f)) == name), None)
                if match:
                    media_ref = check_in_media(match, name) or ''
                else:
                    body = str(data_path)
            else:
                body = r['text'] or ''
            data_list.append((_sec_to_utc(r['date']), r['mms_id'], r['thread_id'],
                              _sec_to_utc(r['date_sent']), r['read'], r['FROM'], r['TO'], r['CC'],
                              r['BCC'], body, media_ref))

    data_headers = (('Date', 'datetime'), 'MSG ID', 'Thread ID', ('Date Sent', 'datetime'), 'Read',
                    'From Address', 'To Address', 'Cc', 'Bcc', 'Body', ('Media', 'media'))
    return data_headers, data_list, source_path
