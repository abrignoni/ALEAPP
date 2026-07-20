__artifacts_v2__ = {
    'Life360_User': {
        'name': 'Life360 User',
        'description': 'Parses Life360 User Info',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-11',
        'last_update_date': '2026-06-12',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/com.amplitude.api*',),
        'output_types': 'standard',
        'artifact_icon': 'user',
        'sample_data': {
            'hc_pixel8pro_a16': 'Android 16 | com.life360.android.safetymapd vc 2897710 | 2 rows',
            'pixel7a_a14': 'Android 14 | com.life360.android.safetymapd vc 294540 | 2 rows',
            'sharon_a14': 'Android 14 | com.life360.android.safetymapd vc 296030 | 1 row',
        }
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    logfunc
)

@artifact_processor
def Life360_User(context):

    data_list = []

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'com.amplitude.api')

    query = '''
    SELECT 
        key AS "Key",
        value AS "Value"
    FROM store
    '''

    try:
        db_records = get_sqlite_db_records(source_path, query)

        logfunc(f'Life360_User: Records found = {len(db_records)}')

        for record in db_records:

            data_list.append((record[0], record[1]))

    except Exception as e:  # pylint: disable=broad-exception-caught
        logfunc(f'Error processing Life360 User: {e}')

    data_headers = ('Key', 'Value')

    return data_headers, data_list, source_path