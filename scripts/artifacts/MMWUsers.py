# pylint: disable=W0613
__artifacts_v2__ = {
    "get_map_users": {
        "name": "MapUsers",
        "description": "Get Information related to the user from the Map My Walk app",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-03-25",
        "last_update_date": "2023-03-25",
        "requirements": "Python 3.7 or higher",
        "category": "Map-My-Walk",
        "notes": "",
        "paths": ('*com.mapmywalk.android2/databases/mmdk_user*',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "html_columns": ['Profile Image URL'],
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
def get_map_users(files_found, report_folder, seeker, wrap_text):

    files_found = [x for x in files_found if not str(x).endswith('-journal')
                   and not str(x).endswith('_gear') and not str(x).endswith('_gear-journal')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        Select id, username, email, display_name, birthdate, gender, height, weight, timezone,
               date_joined, last_login, location_country, profile_image_medium
        from user_entity
    ''')
    all_rows = cursor.fetchall()
    db.close()
    logfunc(f"Found {len(all_rows)} entries in users")

    data_list = []
    for row in all_rows:
        height = round(row[6], 2) if row[6] is not None else row[6]
        weight = round(row[7], 2) if row[7] is not None else row[7]
        if row[12]:
            image = '<img src="' + esc(row[12]) + '" alt="' + esc(str(row[10])) + '" width="50" height="50">'
        else:
            image = 'N/A'
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], height, weight, row[8],
                          _ms_to_utc(row[9]), _ms_to_utc(row[10]), row[11], image))

    data_headers = ('ID', 'Username', 'Email', 'Name', 'Birthdate', 'Gender', 'Height', 'Weight', 'Timezone', ('Date Joined', 'datetime'), ('Last Login', 'datetime'), 'Location Country', 'Profile Image URL')
    return data_headers, data_list, source_path
