# pylint: disable=W0613
__artifacts_v2__ = {
    "get_HideX": {
        "name": "HideX",
        "description": "Parses the list of apps hidden or locked by the HideX privacy app (package name and active state) from hidex.db.",
        "author": "",
        "creation_date": "2021-10-12",
        "last_update_date": "2021-10-12",
        "requirements": "none",
        "category": "GroupMe",
        "notes": "",
        "paths": ('*/com.flatfish.cal.privacy/databases/hidex.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "message",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_HideX(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('hidex.db'):
            source_path = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
                id,
                packageName,
                case isActive
                    WHEN 0 then ''
                    WHEN 1 then 'Yes'
                end
            FROM p_lock_app
            ''')

            all_rows = cursor.fetchall()
            for row in all_rows:
                data_list.append((row[0],row[1],row[2]))
            db.close()

    data_headers = ('ID', 'Package Name', 'Is Active')
    return data_headers, data_list, source_path
