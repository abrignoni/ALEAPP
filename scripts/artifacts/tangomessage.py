# pylint: disable=W0613,W0631,W0702,W0718
__artifacts_v2__ = {
    "get_tangomessage": {
        "name": "tangomessage",
        "description": "",
        "author": "",
        "creation_date": "2021-03-11",
        "last_update_date": "2021-03-11",
        "requirements": "none",
        "category": "Tango",
        "notes": "",
        "paths": ('*/com.sgiggle.production/files/tc.db*',),
        "output_types": "standard",
        "artifact_icon": "message",
    }
}

import base64
import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _decodeMessage(wrapper, message):
    result = ""
    decoded = base64.b64decode(message)
    try:
        Z = decoded.decode("ascii", "ignore")
        result = Z.split(wrapper)[1]
    except Exception as ex:
        print ("Error decoding a Tango message. " + str(ex))
    return result


@artifact_processor
def get_tangomessage(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('tc.db'):
            break

    source_path = file_found

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT conv_id, payload, create_time/1000 as create_time,
               case direction when 1 then "Incoming" else "Outgoing" end direction
          FROM messages ORDER BY create_time DESC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    data_list = []
    if usageentries > 0:
        for row in all_rows:
            message = _decodeMessage(row[0], row[1])
            timestamp = datetime.datetime.fromtimestamp(int(row[2]), datetime.timezone.utc)

            data_list.append((timestamp, row[3], message))

    db.close()

    data_headers = (('Create Time', 'datetime'), 'Direction', 'Message')
    return data_headers, data_list, source_path
