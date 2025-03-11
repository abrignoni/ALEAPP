import blackboxprotobuf
import json
import sqlite3
import time

from html import escape
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

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
        

def get_googleNowPlaying(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue
        elif not file_found.endswith('history_db'):
            continue # Skip all other files (-wal)

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
            description = 'This is data stored by the Now Playing feature in Pixel phones, which shows song data on the lock screen for any music playing nearby. It\'s part of <a href="https://play.google.com/store/apps/details?id=com.google.intelligence.sense" target="_blank">Pixel Ambient Services</a> or part of <a href="https://play.google.com/store/apps/details?id=com.google.android.as" target="_blank">Pixel Device Personalization Services</a> depending on OS version.'
            report = ArtifactHtmlReport('Now Playing History')
            report.start_artifact_report(report_folder, 'Now Playing', description)
            report.add_script()
            
            data_headers = ('Timestamp', 'Timezone', 'Song Title', 'Artist', 'Duration',
                            'Album', 'Album Year')
            data_list = []

            pb_types = {'9': {'type': 'message', 'message_typedef': 
                        {
                        '6': {'type': 'double', 'name': ''} # This definition converts field to a double from generic fixed64
                        } }
                        }
            last_data_set = [] # Since there are a lot of similar entries differing only in timestamp, we can combine them.
            
            for row in all_rows:
                timestamp = row[0]
                pb = row[1]

                data, actual_types = blackboxprotobuf.decode_message(pb, pb_types)
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
                    if last_data_set[0] == timestamp: # exact duplicate, do not add
                        pass
                    else:
                        last_data_set[0] += ',<br />' + timestamp
                else:
                    data_list.append(last_data_set)
                    last_data_set = []
            if last_data_set:
                data_list.append(last_data_set)
            logfunc("{} entries grouped into {}".format(usageentries, len(data_list)))
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = f'Google Now Playing'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Google Now Playing'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Google Now Playing history')

        db.close()

__artifacts__ = {
        "GoogleNowPlaying": (
                "Now Playing",
                ('*/com.google.intelligence.sense/db/history_db*','*/com.google.android.as/databases/history_db*'),
                get_googleNowPlaying)
}
