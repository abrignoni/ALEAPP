# pylint: disable=W0613
__artifacts_v2__ = {
    "get_pSettings": {
        "name": "pSettings",
        "description": "",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "Device Info",
        "notes": "",
        "paths": ('*/com.google.android.gsf/databases/googlesettings.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_pSettings(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('googlesettings.db'):
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            select name, value
            from partner
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((row[0], row[1]))

    data_headers = ('Name', 'Value')
    return data_headers, data_list, source_path
