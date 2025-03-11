import blackboxprotobuf
import json
import sqlite3
import time
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


def get_usageapps(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue
        elif not file_found.endswith('reflection_gel_events.db'):
            continue # Skip all other files (-wal, -journal)

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(timestamp /1000, 'UNIXEPOCH') as timestamp,
        id,
        proto,
        generated_from
        FROM
        reflection_event
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)

        if usageentries > 0:
            description = 'This is data stored by the reflection_gel_events.db, which '\
                        'shows data usage from apps to included deleted apps. '
            report = ArtifactHtmlReport('Device Personalization Services')
            report.start_artifact_report(report_folder, 'Personalization Services', description)
            report.add_script()
            
            data_headers = ('Timestamp', 'Deleted?', 'BundleID', 'From', 'From in Proto', 'Proto Full')
            data_list = []
            types = (
                    {'1': {'type': 'bytes', 'name': ''}, 
                    '2': {'type': 'int', 'name': ''}, 
                    '5': {'type': 'message', 'message_typedef': 
                    {'1': {'type': 'int', 'name': ''}, 
                    '6': {'type': 'fixed32', 'name': ''}}, 'name': ''}, 
                    '8': {'type': 'bytes', 'name': ''}}
                    )
            for row in all_rows:
                timestamp = row[0]
                idb = row[1]
                pb = row[2]
                generated = row[3]
                
                if 'deleted_app' in idb:
                    pass
                else:
                    idb = ''
                
                values, actual_types = blackboxprotobuf.decode_message(pb, types)
                values = recursive_convert_bytes_to_str(values)

                for key, val in values.items():
                    #print(key, val)
                    if key == '1':
                        bundleid = val
                    if key == '5':
                        try:             timestamp = FilterInvalidValue(val['1'])
                        except KeyError: timestamp = ''
                        
                        try:             usage = FilterInvalidValue(val['6'])
                        except KeyError: usage = ''
                    if key == '8':
                        source = val
                    else:
                        source =''
                    
                data_list.append((row[0], idb, bundleid, row[3], usage, values))
                
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'personalization services'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Personalization Services'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Usage Apps data available')
        
        db.close()

__artifacts__ = {
        "usageapps": (
                "App Interaction",
                ('*/com.google.android.as/databases/reflection_gel_events.db*'),
                get_usageapps)
}