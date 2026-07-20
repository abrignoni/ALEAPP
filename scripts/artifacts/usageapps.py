__artifacts_v2__ = {
    "get_usageapps": {
        "name": "usageapps",
        "description": "App usage events from the Device Personalization Services "
                       "reflection_gel_events database (includes deleted apps)",
        "author": "",
        "creation_date": "2020-04-11",
        "last_update_date": "2020-04-11",
        "requirements": "none",
        "category": "App Interaction",
        "notes": "",
        "paths": ('*/com.google.android.as/databases/reflection_gel_events.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "galaxys10_a10": "Android 10 | com.google.android.as vc 1353029 | 1063 rows",
        },
    }
}

import datetime

import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

PROTO_TYPES = {
    '1': {'type': 'bytes', 'name': ''},
    '2': {'type': 'int', 'name': ''},
    '5': {'type': 'message', 'message_typedef': {
        '1': {'type': 'int', 'name': ''},
        '6': {'type': 'fixed32', 'name': ''}}, 'name': ''},
    '8': {'type': 'bytes', 'name': ''},
}


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _to_str(obj):
    '''Recursively decode bytes to str within decoded protobuf structures.'''
    if isinstance(obj, dict):
        return {k: _to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_str(v) for v in obj]
    if isinstance(obj, bytes):
        return obj.decode('utf8', 'backslashreplace')
    return obj


def _scalar(obj):
    '''Keep scalar values; drop nested dict/list structures.'''
    return '' if isinstance(obj, (dict, list)) else obj


@artifact_processor
def get_usageapps(context):
    files_found = context.get_files_found()
    source_path = ''
    data_list = []
    for file_found in files_found:
        file_found = str(file_found).replace('\\', '/')
        if '/mirror/' in file_found:
            continue  # skip magisk mirror duplicates
        if not file_found.endswith('reflection_gel_events.db'):
            continue  # skip -wal/-journal
        source_path = file_found

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('SELECT timestamp, id, proto, generated_from FROM reflection_event')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            deleted = row[1] if row[1] and 'deleted_app' in row[1] else ''
            bundleid, usage = '', ''
            values, _ = blackboxprotobuf.decode_message(row[2], PROTO_TYPES)
            values = _to_str(values)
            for key, val in values.items():
                if key == '1':
                    bundleid = val
                elif key == '5' and isinstance(val, dict):
                    usage = _scalar(val.get('6', ''))
            data_list.append((_ms_to_utc(row[0]), deleted, bundleid, row[3], usage, str(values)))

    data_headers = (
        ('Timestamp', 'datetime'), 'Deleted?', 'BundleID', 'Generated From', 'From in Proto', 'Proto Full')
    return data_headers, data_list, source_path
