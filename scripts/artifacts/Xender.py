# pylint: disable=W0718
__artifacts_v2__ = {
    "get_Xender": {
        "name": "Xender - Connected Devices",
        "description": "Devices recorded in the Xender profile table, with how many times each connected and when it last did",
        "author": "@markmckinnon",
        "creation_date": "2020-12-24",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "File Transfer",
        "notes": ("One row per row of the profile table in cn.xender/databases/trans-history-db. "
                  "The table is the app's record of the remote devices it has connected to: "
                  "device_id, the nickname that device advertised, its device type, how many "
                  "times it has connected, and when it last did. "
                  "**This artifact previously filtered on connect_times = 0 and could therefore "
                  "never return a row.** The filter was removed. In the app's own code there is "
                  "exactly one place that builds a profile row, saveRemoteDeviceInfo in "
                  "cn/xender/core/provider/a.java, and it sets connect_times to 1 the first time "
                  "a device is seen and to the previous value plus one afterwards, alongside "
                  "last_connect_date from System.currentTimeMillis(). The column is declared "
                  "INTEGER NOT NULL with no default and the data access object's only insert "
                  "binds that value, so a row written by that path carries at least 1 and "
                  "the old query matched nothing. That mapping was read from a **decompiled "
                  "build** of version 18.8.0.prime, not from published source, and is cited as "
                  "such; 332 of 14,054 classes did not decompile, so it is a thorough reading "
                  "rather than an exhaustive one. "
                  "Last Connected is last_connect_date, Unix milliseconds, reported as UTC. "
                  "Connect Times is the count as stored. Device Type and Deleted are reported as "
                  "stored because no source for their code lists was found. "
                  "What a row supports is bounded: it records that the app holds a profile for "
                  "that device, with the count and time the app itself wrote. It does not say "
                  "what was transferred, which is the separate Messages artifact. "
                  "No registered corpus carries Xender, so this could not be re-derived from "
                  "case data. On an emulator with the app installed and opened, the profile "
                  "table was present and empty, which also shows the device does not write its "
                  "own profile there. A populated table needs a second device to connect to, "
                  "which was not available, so the columns are code-present and unexercised "
                  "against real rows."),
        "paths": ('*/cn.xender/databases/trans-history-db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "users",
    },
    "get_Xender_messages": {
        "name": "Xender - Messages",
        "description": "Parses Xender file transfer history (file path, name, size, timestamp, direction and sender and recipient details) from the Xender trans-history database.",
        "author": "@markmckinnon",
        "creation_date": "2020-12-24",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "File Transfer",
        "notes": ("Direction is decoded from the new_history 'c_direction' column. Direction/status "
                  "value mappings were established through testing; unrecognized values are "
                  "reported as stored.\n"
                  "to_id and from_id carry the recipient and sender device IDs recorded on the same "
                  "row (r_device_id and s_device_id) and are left blank when the database does not "
                  "hold them. The sender and recipient name columns are names, not identifiers."),
        "paths": ('*/cn.xender/databases/trans-history-db*',),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import datetime

from scripts.ilapfuncs import convert_unix_ts_to_utc, artifact_processor, logfunc, open_sqlite_db_readonly


def _xender_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('-db'):
            return file_found
    return ''


def _ms(value):
    """A Unix millisecond stamp as UTC, blank for the app's 0 default."""
    if not value:
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value // 1000)
    except (OverflowError, OSError, ValueError):
        return ''


@artifact_processor
def get_Xender(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = _xender_db(files_found)
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''SELECT last_connect_date, nick_name, device_id, device_type,
                                     connect_times, mac, _u_id, deleted
                              FROM profile
                              ORDER BY last_connect_date DESC''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()
        for row in all_rows:
            data_list.append((_ms(row[0]), row[1] or '', row[2] or '', row[3],
                              row[4], row[5] or '', row[6] or '', row[7]))

    data_headers = (('Last Connected', 'datetime'), 'Nickname', 'Device Id',
                    'Device Type (as stored)', 'Connect Times', 'MAC', 'User Id',
                    'Deleted (as stored)')
    return data_headers, data_list, source_path


@artifact_processor
def get_Xender_messages(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = _xender_db(files_found)
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT f_path, f_display_name, f_size_str, c_start_time, c_direction, c_session_id, s_name,
                       s_device_id, r_name, r_device_id
                FROM new_history
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            # Only c_direction = 1 is identified; any other value is reported as stored.
            direction = {1: 'Outgoing'}.get(row[4], '' if row[4] is None else row[4])
            # The parties come from the row's own device ID columns rather than being
            # inferred from the direction value; s_name/r_name are names, not IDs.
            from_id = row[7] if row[7] else ''
            to_id = row[9] if row[9] else ''
            createtime = datetime.datetime.fromtimestamp(int(row[3]) / 1000, datetime.timezone.utc) if row[3] else ''
            data_list.append((row[0], row[1], row[2], createtime, direction, to_id, from_id, row[5], row[6], row[7], row[8], row[9]))

    data_headers = ('file_path', 'file_display_name', 'file_size', ('timestamp', 'datetime'), 'direction', 'to_id',
                    'from_id', 'session_id', 'sender_name', 'sender_device_id', 'recipient_name', 'recipient_device_id')
    return data_headers, data_list, source_path
