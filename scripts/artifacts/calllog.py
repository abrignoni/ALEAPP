# pylint: disable=W0613
__artifacts_v2__ = {
    "get_calllog": {
        "name": "Call logs ",
        "description": "Parses the call log (date, number, type, duration, location and transcription) from the contacts provider calllog.db.",
        "author": "",
        "creation_date": "2020-03-02",
        "last_update_date": "2020-03-02",
        "requirements": "none",
        "category": "Call Logs",
        "notes": "",
        "paths": ('*/com.android.providers.contacts/databases/calllog.db*', '*/com.samsung.android.providers.contacts/databases/calllog.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "html_columns": ['Type'],
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

CALL_TYPE_ICONS = {
    'Incoming': ' <i data-feather="phone-incoming" stroke="green"></i>',
    'Outgoing': ' <i data-feather="phone-outgoing" stroke="green"></i>',
    'Missed': ' <i data-feather="phone-missed" stroke="red"></i>',
    'Voicemail': ' <i data-feather="voicemail" stroke="brown"></i>',
    'Rejected': ' <i data-feather="x" stroke="red"></i>',
    'Blocked': ' <i data-feather="phone-off" stroke="red"></i>',
    'Answered Externally': ' <i data-feather="phone-forwarded"></i>',
}


@artifact_processor
def get_calllog(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('calllog.db'):
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT
            date,
            CASE WHEN phone_account_address is NULL THEN ' ' ELSE phone_account_address END as phone_account_address,
            number,
            CASE
                WHEN type = 1 THEN  'Incoming'
                WHEN type = 2 THEN  'Outgoing'
                WHEN type = 3 THEN  'Missed'
                WHEN type = 4 THEN  'Voicemail'
                WHEN type = 5 THEN  'Rejected'
                WHEN type = 6 THEN  'Blocked'
                WHEN type = 7 THEN  'Answered Externally'
                ELSE 'Unknown'
            END as types,
            duration,
            CASE WHEN geocoded_location is NULL THEN ' ' ELSE geocoded_location END as geocoded_location,
            countryiso,
            CASE WHEN _data is NULL THEN ' ' ELSE _data END as _data,
            CASE WHEN mime_type is NULL THEN ' ' ELSE mime_type END as mime_type,
            CASE WHEN transcription is NULL THEN ' ' ELSE transcription END as transcription,
            deleted
            FROM calls
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            call_date = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            call_type = row[3]
            call_type_html = call_type + CALL_TYPE_ICONS.get(call_type, '')
            data_list.append((call_date, row[1], row[2], call_type_html, str(row[4]), row[5], row[6], row[7], row[8], row[9], str(row[10])))

    data_headers = (('Call Date', 'datetime'), 'Phone Account Address', ('Partner', 'phonenumber'), 'Type', 'Duration in Secs', 'Partner Location', 'Country ISO', 'Data', 'Mime Type', 'Transcription', 'Deleted')
    return data_headers, data_list, source_path
