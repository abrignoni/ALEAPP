# pylint: disable=E0606,W0612
__artifacts_v2__ = {
    "get_googleNowPlaying": {
        "name": "GoogleNowPlaying",
        "description": "Now Playing history (songs recognised near the device)",
        "author": "",
        "creation_date": "2020-03-22",
        "last_update_date": "2020-03-22",
        "requirements": "none",
        "category": "Now Playing",
        "notes": "",
        "paths": ('*/com.google.intelligence.sense/db/history_db*', '*/com.google.android.as/databases/history_db*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "music",
        "sample_data": {
            "userb2_a13": "Android 13 | com.google.android.as vc 8997612 | 470 rows",
        },
        "html_columns": ['Timestamp'],
    }
}

import time
from scripts.ilapfuncs import decode_protobuf

from html import escape
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, is_platform_windows
from scripts.html_safe import esc

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/'


def recursive_convert_bytes_to_str(obj):
    '''Recursively convert bytes to strings if possible'''
    ret = obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = recursive_convert_bytes_to_str(v)
    elif isinstance(obj, list):
        for index, v in enumerate(obj):
            obj[index] = recursive_convert_bytes_to_str(v)
    elif isinstance(obj, bytes):
        # test for string
        try:
            ret = obj.decode('utf8', 'backslashreplace')
        except UnicodeDecodeError:
            ret = str(obj)
    return ret


def FilterInvalidValue(obj):
    '''Return obj if it is valid, else empty string'''
    # Remove any dictionary or list types
    if isinstance(obj, dict) or isinstance(obj, list):
        return ''
    return obj


def AreContentsSame(last_data_set, timezones, songtitle, artist, duration, album, year):
    return last_data_set[1] == timezones and last_data_set[2] == songtitle and last_data_set[3] == artist and last_data_set[4] == duration and last_data_set[5] == album and last_data_set[6] == year


@artifact_processor
def get_googleNowPlaying(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue
        elif not file_found.endswith('history_db'):
            continue  # Skip all other files (-wal)

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        Select
        CASE
            timestamp
            WHEN
                "0"
            THEN
                ""
            ELSE
                datetime(timestamp / 1000, "unixepoch")
        END AS "timestamp",
        history_entry
        FROM
        recognition_history
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            pb_types = {'9': {'type': 'message', 'message_typedef':
                        {
                        '6': {'type': 'double', 'name': ''}  # This definition converts field to a double from generic fixed64
                        }}
                        }
            last_data_set = []  # Since there are a lot of similar entries differing only in timestamp, we can combine them.

            for row in all_rows:
                timestamp = row[0]
                pb = row[1]

                data, actual_types = decode_protobuf(pb, pb_types)
                data = recursive_convert_bytes_to_str(data)

                try:             timezones = FilterInvalidValue(data["7"])
                except KeyError: timezones = ''

                try:             songtitle = FilterInvalidValue(data["9"]["3"])
                except KeyError: songtitle = ''

                try:             artist = FilterInvalidValue(data["9"]["4"])
                except KeyError: artist = ''

                try:             durationinsecs = data["9"]["6"]
                except KeyError: durationinsecs = ''

                try:             album = FilterInvalidValue(data["9"]["13"])
                except KeyError: album = ''

                try:             year = FilterInvalidValue(data["9"]["14"])
                except KeyError: year = ''

                if durationinsecs:
                    duration = time.strftime('%H:%M:%S', time.gmtime(durationinsecs))
                if not last_data_set:
                    last_data_set = [timestamp, escape(timezones), escape(songtitle), escape(artist), duration, escape(album), year]
                elif AreContentsSame(last_data_set, timezones, songtitle, artist, duration, album, year):
                    if last_data_set[0] == timestamp:  # exact duplicate, do not add
                        pass
                    else:
                        last_data_set[0] += ',<br />' + esc(timestamp)
                else:
                    data_list.append(last_data_set)
                    last_data_set = []
            if last_data_set:
                data_list.append(last_data_set)
            logfunc("{} entries grouped into {}".format(usageentries, len(data_list)))

        db.close()

    data_headers = ('Timestamp', 'Timezone', 'Song Title', 'Artist', 'Duration', 'Album', 'Album Year')
    return data_headers, data_list, source_path
