# pylint: disable=W0613
__artifacts_v2__ = {
    "get_userDict": {
        "name": "userDict",
        "description": "",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "User Dictionary",
        "notes": "",
        "paths": ('*/com.android.providers.userdictionary/databases/user_dict.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_userDict(files_found, report_folder, seeker, wrap_text):

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        select word, frequency, locale, appid, shortcut
        from words
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3], row[4]))

    data_headers = ('Word', 'Frequency', 'Locale', 'AppID', 'Shortcut')
    return data_headers, data_list, source_path
