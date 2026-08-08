# pylint: disable=W0718
__artifacts_v2__ = {
    "get_calllogs": {
        "name": "Call Logs",
        "description": "Parses call logs (number, start and end time, call type, direction and name) from the contacts and logs provider databases.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-17",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Call Logs",
        "notes": "The same 'type' column is read from two different schemas, the AOSP 'calls' table in the contacts provider and the Samsung LogsProvider 'logs' table, and the AOSP CallLog.Calls code set is applied to both. Call type decodes 1 Incoming, 2 Outgoing, 3 Missed, 4 Voicemail, 5 Rejected, 6 Blocked and 7 Answered Externally; any other code is reported as its raw value. Direction is only filled in for the incoming (1) and outgoing (2) codes and is left blank for the rest, so the from_id and to_id columns stay empty for those rows and the number column carries the other party. Reference: AOSP, 'CallLog.Calls constants', https://developer.android.com/reference/android/provider/CallLog.Calls",
        "paths": ('*/com.android.providers.contacts/databases/contact*', '*/com.sec.android.provider.logsprovider/databases/logs.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.contacts | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.contacts | 0 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.contacts | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.contacts | 0 rows",
            "userb2_a13": "Android 13 | com.android.providers.contacts | 0 rows",
        },
    }
}

import datetime
import os

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, does_table_exist_in_db

# AOSP CallLog.Calls type codes, applied to both the AOSP calls table and the
# Samsung LogsProvider logs table, which reuses the same column name
CALL_TYPES = {
    1: 'Incoming',
    2: 'Outgoing',
    3: 'Missed',
    4: 'Voicemail',
    5: 'Rejected',
    6: 'Blocked',
    7: 'Answered Externally',
}
# Only these two codes state who called whom; the others say what happened to
# an entry without the record itself naming a direction
CALL_DIRECTIONS = {1: 'Incoming', 2: 'Outgoing'}


@artifact_processor
def get_calllogs(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_name = str(file_found)
        if os.path.basename(file_name) not in ('contacts2.db', 'contacts.db', 'logs.db'):
            continue  # skip -journal and other files

        source_path = file_name
        db = open_sqlite_db_readonly(file_name)
        calls_table_exists = does_table_exist_in_db(file_name, 'calls')
        cursor = db.cursor()
        table = 'calls' if calls_table_exists else 'logs'
        try:
            cursor.execute(f'''
                SELECT number, date/1000, (date/1000 + duration) as end_date,
                       type, name FROM {table} ORDER BY date DESC;''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            type_code = row[3]
            call_type = CALL_TYPES.get(type_code, type_code)  # unknown codes stay raw
            direction = CALL_DIRECTIONS.get(type_code, '')
            callerId = row[0] if direction == 'Incoming' else None
            calleeId = row[0] if direction == 'Outgoing' else None
            starttime = datetime.datetime.fromtimestamp(int(row[1]), datetime.timezone.utc)
            endtime = datetime.datetime.fromtimestamp(int(row[2]), datetime.timezone.utc)
            data_list.append((callerId, calleeId, starttime, endtime, direction, call_type, row[0], row[4]))

    data_headers = ('from_id', 'to_id', ('start_date', 'datetime'), ('end_date', 'datetime'), 'direction', 'call_type', ('number', 'phonenumber'), 'name')
    return data_headers, data_list, source_path
