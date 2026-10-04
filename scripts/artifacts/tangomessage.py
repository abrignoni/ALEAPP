# pylint: disable=W0631,W0702,W0718
__artifacts_v2__ = {
    "get_tangomessage": {
        "name": "tangomessage",
        "description": "Parses Tango messages (create time, direction and message) from the Tango tc.db.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Tango",
        "notes": ("Direction is decoded from the messages table 'direction' column. Message is "
                  "derived, not stored: the payload column is base64-decoded, bytes outside ASCII "
                  "are dropped, and the text after the conversation id is shown, so a message with "
                  "non-ASCII characters is not shown in full. Message is blank when the decoded "
                  "payload does not hold the conversation id. Create Time reads create_time as "
                  "Unix milliseconds in UTC. Direction values 1 and 2 are labelled Incoming and "
                  "Outgoing; that mapping is not vendor-documented and no source or measurement "
                  "for it is given here, so the labels are unverified. Unrecognized values are "
                  "reported as stored."),
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
def get_tangomessage(context):
    files_found = context.get_files_found()

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
               case direction when 1 then "Incoming" when 2 then "Outgoing" else direction end direction
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
