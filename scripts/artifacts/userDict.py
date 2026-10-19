__artifacts_v2__ = {
    "get_userDict": {
        "name": "userDict",
        "description": "Parses the personal user dictionary (word, frequency, locale, app ID and shortcut) from the user dictionary database.",
        "author": "@abrignoni",
        "creation_date": "2020-03-21",
        "last_update_date": "2026-10-19",
        "requirements": "none",
        "category": "User Dictionary",
        "notes": "Every user_dict.db found is read once per storage location: the views of one "
                 "app directory (data/data, data/user/0, data_mirror) are read once, each other "
                 "Android user's copy is read as well, and Source File names the database each row "
                 "came from. The -journal, -wal and -shm files are never opened as the database. 19 "
                 "registered images (17 snapshots of one emulator and 2 phones) hold a copy under "
                 "data/user/10 as well as user 0's; on all of them every copy has an empty words "
                 "table.",
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

from pathlib import Path

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


def _store_paths(context):
    """Every user_dict.db found, one per storage location.

    The paths glob also matches the -journal, -wal and -shm files, and the provider keeps
    one dictionary per Android user, so taking the first match could open a sidecar or
    leave out every user but one. unique_files collapses the views of one app directory
    and keeps each user's copy.
    """
    return [path for path in unique_files(context) if Path(path).name == 'user_dict.db']


@artifact_processor
def get_userDict(context):
    store_paths = _store_paths(context)
    query = '''
        select word, frequency, locale, appid, shortcut
        from words
    '''

    data_list = []
    for source_path in store_paths:
        source_file = context.get_relative_path(source_path)
        for row in get_sqlite_db_records(source_path, query):
            data_list.append((row[0], row[1], row[2], row[3], row[4], source_file))

    data_headers = ('Word', 'Frequency', 'Locale', 'AppID', 'Shortcut', 'Source File')
    return data_headers, data_list, '\n'.join(store_paths)
