__artifacts_v2__ = {
    "get_pSettings": {
        "name": "pSettings",
        "description": "Parses Google partner settings (name and value) from the Google services framework googlesettings.db.",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": ('*/com.google.android.gsf/databases/googlesettings.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
        "sample_data": {
            "galaxys10_a10": "Android 10 | com.google.android.gsf | 13 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gsf | 18 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gsf | 57 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gsf | 33 rows",
            "sharon_a14": "Android 14 | com.google.android.gsf | 18 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gsf | 30 rows",
            "userb2_a13": "Android 13 | com.google.android.gsf | 36 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_pSettings(context):
    files_found = context.get_files_found()

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
