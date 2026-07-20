__artifacts_v2__ = {
    "get_userDict": {
        "name": "userDict",
        "description": "Parses the personal user dictionary (word, frequency, locale, app ID and shortcut) from the user dictionary database.",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "User Dictionary",
        "notes": "",
        "paths": ('*/com.android.providers.userdictionary/databases/user_dict.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.providers.userdictionary | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.userdictionary | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.userdictionary | 0 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.userdictionary | 0 rows",
            "samsunga53_a14": "Android 14 | com.android.providers.userdictionary | 0 rows",
            "samsungs20_a13": "Android 13 | com.android.providers.userdictionary | 0 rows",
            "sharon_a14": "Android 14 | com.android.providers.userdictionary | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.userdictionary | 0 rows",
            "userb2_a13": "Android 13 | com.android.providers.userdictionary | 0 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_userDict(context):
    files_found = context.get_files_found()

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
