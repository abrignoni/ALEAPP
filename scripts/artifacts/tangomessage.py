# pylint: disable=W0631,W0702,W0718
__artifacts_v2__ = {
    "get_tangomessage": {
        "name": "tangomessage",
        "description": "Parses Tango messages (create time, direction and message) from the Tango tc.db.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-11",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Tango",
        "notes": ("Direction is decoded from the messages table 'direction' column. Message is "
                  "derived, not stored: the payload column is base64-decoded, the bytes are read as "
                  "UTF-8 with any byte sequence that is not valid UTF-8 dropped, and the text "
                  "between the first occurrence of the conversation id and the next one, or the "
                  "end of the payload, is shown. The layout of the payload is not sourced here, "
                  "so the cell can hold bytes that are not message text and can stop short of a "
                  "message that itself holds the conversation id. Message is blank when the "
                  "payload is empty, is not base64, or does not hold the conversation id; the "
                  "run log gives the count of such rows. No registered corpus holds this app, so "
                  "the reading is not exercised on real data. Create Time reads create_time as "
                  "Unix milliseconds in UTC and is blank when the column is empty. Direction values 1 and 2 are labelled Incoming and "
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

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _decodeMessage(wrapper, message):
    """Text between the first and second conversation id, or None when not found."""
    try:
        decoded = base64.b64decode(message)
        text = decoded.decode("utf-8", "ignore")
        return text.split(str(wrapper))[1]
    except Exception:
        return None


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
    except Exception as ex:
        logfunc(f'tangomessage: could not query the messages table: {ex}')
        usageentries = 0

    data_list = []
    undecoded = 0
    if usageentries > 0:
        for row in all_rows:
            message = _decodeMessage(row[0], row[1])
            if message is None:
                undecoded += 1
                message = ''
            timestamp = ''
            if row[2] is not None:
                timestamp = datetime.datetime.fromtimestamp(int(row[2]), datetime.timezone.utc)

            data_list.append((timestamp, row[3], message))

    db.close()
    if undecoded:
        logfunc(f'tangomessage: {undecoded} message payload(s) gave no text '
                '(empty, not base64, or no conversation id in the payload)')

    data_headers = (('Create Time', 'datetime'), 'Direction', 'Message')
    return data_headers, data_list, source_path
