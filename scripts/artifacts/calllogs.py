# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_calllogs": {
        "name": "Call Logs",
        "description": "Parses call logs (number, start and end time, direction and name) from the contacts and logs provider databases.",
        "author": "",
        "creation_date": "2021-03-17",
        "last_update_date": "2021-03-17",
        "requirements": "none",
        "category": "Call Logs",
        "notes": "",
        "paths": ('*/com.android.providers.contacts/databases/contact*', '*/com.sec.android.provider.logsprovider/databases/logs.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.contacts | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.contacts | 0 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.contacts | 0 rows",
        },
    }
}

import datetime
import os

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, does_table_exist_in_db


@artifact_processor
def get_calllogs(files_found, report_folder, seeker, wrap_text):

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
                       case type when 1 then "Incoming"
                                 when 3 then "Incoming"
                                 when 2 then "Outgoing"
                                 when 5 then "Outgoing"
                                 else "Unknown" end as direction,
                        name FROM {table} ORDER BY date DESC;''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            callerId = None
            calleeId = None
            if row[3] == "Incoming":
                callerId = row[0]
            else:
                calleeId = row[0]
            starttime = datetime.datetime.fromtimestamp(int(row[1]), datetime.timezone.utc)
            endtime = datetime.datetime.fromtimestamp(int(row[2]), datetime.timezone.utc)
            data_list.append((callerId, calleeId, starttime, endtime, row[3], row[4]))

    data_headers = ('from_id', 'to_id', ('start_date', 'datetime'), ('end_date', 'datetime'), 'direction', 'name')
    return data_headers, data_list, source_path
