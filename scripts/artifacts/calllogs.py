# pylint: disable=W0718
__artifacts_v2__ = {
    "get_calllogs": {
        "name": "Call Logs",
        "description": "Parses call log rows (number, start time, stored duration, call type, direction and name) from the contacts provider calls table and the Samsung LogsProvider logs table. For the calls table an end time is computed by this parser as the start plus the stored duration.",
        "author": "@markmckinnon, @AlexisBrignoni, Codex",
        "creation_date": "2021-03-17",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Call Logs",
        "notes": "start_date is the stored 'date' column read as milliseconds since the Unix epoch and shown in UTC, with the milliseconds kept. duration is the stored 'duration' column, as stored. end_date is not stored: for the AOSP calls table this parser computes it as the start plus the duration read as seconds, and it is blank when either value is missing or is not a number. AOSP documents the calls 'date' column as milliseconds since the epoch and 'duration' as seconds (https://github.com/aosp-mirror/platform_frameworks_base/blob/0d3ff311e6e80dee7fe88a2a2cfa272ce231c3c6/core/java/android/provider/CallLog.java#L955-L965). No source was found for the units of the Samsung logs table: its 'date' column is read as milliseconds by this parser, which is not established, and end_date is left blank for its rows. No listed corpus returned a row, so the time handling was exercised only on a database built for the test. The same 'type' column is read from two different schemas, the AOSP 'calls' table in the contacts provider and the Samsung LogsProvider 'logs' table, and the AOSP CallLog.Calls code set is applied to both. Whether the Samsung logs table uses those codes, and whether every row of it is a call, is not established; no listed corpus returned a row. Call type decodes 1 Incoming, 2 Outgoing, 3 Missed, 4 Voicemail, 5 Rejected, 6 Blocked and 7 Answered Externally; any other code is reported as its raw value. Direction is only filled in for the incoming (1) and outgoing (2) codes and is left blank for the rest, so the from_id and to_id columns stay empty for those rows and the number column carries the other party. Reference: Android Developers, 'CallLog.Calls' API reference, https://developer.android.com/reference/android/provider/CallLog.Calls (read 2026-10-03)",
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


def _from_epoch_ms(value):
    """Stored milliseconds since the Unix epoch as a UTC datetime, milliseconds kept."""
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return None


@artifact_processor
def get_calllogs(context):
    files_found = context.get_files_found()

    data_list = []
    source_paths = []
    for file_found in files_found:
        file_name = str(file_found)
        if os.path.basename(file_name) not in ('contacts2.db', 'contacts.db', 'logs.db'):
            continue  # skip -journal and other files

        if does_table_exist_in_db(file_name, 'calls'):
            table = 'calls'
        elif does_table_exist_in_db(file_name, 'logs'):
            table = 'logs'
        else:
            # Current Android keeps the call log in calllog.db rather than the
            # contacts provider, so contacts2.db carries neither table. That file
            # has nothing for this artifact; the calllog module covers the rest.
            continue

        source_paths.append(file_name)
        db = open_sqlite_db_readonly(file_name)
        cursor = db.cursor()
        try:
            cursor.execute(f'''
                SELECT number, date, duration,
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
            duration = row[2]
            starttime = _from_epoch_ms(row[1])
            endtime = None
            # Only the AOSP calls table has a sourced duration unit (seconds)
            if table == 'calls' and starttime is not None and isinstance(duration, (int, float)):
                try:
                    endtime = starttime + datetime.timedelta(seconds=duration)
                except OverflowError:
                    endtime = None
            data_list.append((callerId, calleeId, starttime, endtime, duration, direction, call_type, row[0], row[4]))

    data_headers = ('from_id', 'to_id', ('start_date', 'datetime'), ('end_date', 'datetime'), 'duration', 'direction', 'call_type', ('number', 'phonenumber'), 'name')
    return data_headers, data_list, '\n'.join(source_paths)
