__artifacts_v2__ = {
    "get_adidas_user": {
        "name": "AdidasUser",
        "description": "Get Information related to users from the Adidas Running app stored in user.db",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-03-24",
        "last_update_date": "2023-03-24",
        "requirements": "Python 3.7 or higher",
        "category": "Adidas-Running",
        "notes": "",
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
            my_fitness_pal = 'Connected' if val == 'true' else 'Not Connected'
        elif key == 'isGarminConnected':
            garmin_connect = 'Connected' if val == 'true' else 'Not Connected'
        elif key == 'isPolarConnected':
            polar = 'Connected' if val == 'true' else 'Not Connected'
        elif key == 'lastV3SessionSyncAtLocalTime':
            last_sync = _ms_to_utc(val)

    image_html = f'<img src="{esc(image)}" alt="{esc(image)}" width="50" height="50">' if image else ''
    data_list = [(user_id, name, height, weight, country, gender, email, created_at, image_html, my_fitness_pal, garmin_connect, polar, last_sync)]

    data_headers = ('ID', 'Name', 'Height', 'Weight', 'Country', 'Gender', 'Email', ('Created At', 'datetime'), 'Image', 'My Fitness Pal', 'Garmin Connect', 'Polar', ('LastSync', 'datetime'))
    return data_headers, data_list, source_path
