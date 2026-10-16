__artifacts_v2__ = {
    "get_adidas_user": {
        "name": "AdidasUser",
        "description": "Parses the userProperty key and value rows of the Adidas Running app's user.db into one row.",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}, @AlexisBrignoni, Codex",
        "creation_date": "2023-03-24",
        "last_update_date": "2026-10-04",
        "requirements": "Python 3.7 or higher",
        "category": "Adidas-Running",
        "notes": "The lastV3SessionSyncAtLocalTime column holds that key's value as stored, as text. "
                 "The key name says local time; the unit and the zone of the value are not "
                 "established, so it is not converted. The My Fitness Pal, Garmin Connect and Polar "
                 "columns hold the stored values of the MY_FITNESS_PAL_CONNECTED, isGarminConnected "
                 "and isPolarConnected keys, as stored; they are blank when the key is absent. "
                 "Created At is the createdAt value read as Unix milliseconds; that unit comes from "
                 "the module's original code and no source for it was found. One row is emitted "
                 "even when no key is present. No registered corpus holds this app's user.db "
                 "(44 Android corpora checked on 2026-10-04), so none of this was measured on data.",
        "paths": ('*com.runtastic.android/databases/user.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "html_columns": ['Image'],
    }
}

import datetime

from scripts.html_safe import esc
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


@artifact_processor
def get_adidas_user(context):
    files_found = context.get_files_found()
    logfunc("Processing data for Adidas User")
    files_found = [x for x in files_found if not str(x).endswith('-journal')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        Select *
        from userProperty
    ''')
    all_rows = cursor.fetchall()
    db.close()

    user_id = name = height = weight = country = gender = email = ''
    created_at = image = my_fitness_pal = garmin_connect = polar = last_sync = ''
    for row in all_rows:
        key = row[2]
        val = row[1]
        if key == 'userId':
            user_id = val
        elif key == 'FirstName':
            name = val
        elif key == 'LastName':
            name = (name + ' ' + val).strip()
        elif key == 'Height':
            height = val
        elif key == 'Weight':
            weight = val
        elif key == 'CountryCode':
            country = val
        elif key == 'Gender':
            gender = val
        elif key == 'EMail':
            email = val
        elif key == 'createdAt':
            created_at = _ms_to_utc(val)
        elif key == 'AvatarUrl':
            image = val
        elif key == 'MY_FITNESS_PAL_CONNECTED':
            my_fitness_pal = val
        elif key == 'isGarminConnected':
            garmin_connect = val
        elif key == 'isPolarConnected':
            polar = val
        elif key == 'lastV3SessionSyncAtLocalTime':
            last_sync = '' if val is None else str(val)

    # The avatar URL is remote, so an <img> here would make opening the report
    # fetch it and disclose the examination to the service. Report the URL as
    # escaped text instead; the evidence is preserved, nothing is fetched.
    image_html = esc(image) if image else ''
    data_list = [(user_id, name, height, weight, country, gender, email, created_at, image_html, my_fitness_pal, garmin_connect, polar, last_sync)]

    data_headers = ('ID', 'Name', 'Height', 'Weight', 'Country', 'Gender', 'Email', ('Created At', 'datetime'), 'Image', 'My Fitness Pal', 'Garmin Connect', 'Polar', 'lastV3SessionSyncAtLocalTime')
    return data_headers, data_list, source_path
