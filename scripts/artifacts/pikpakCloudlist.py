# pylint: disable=W0613
__artifacts_v2__ = {
    "get_pikpakCloudlist": {
        "name": "PikPak Cloud List",
        "description": "Parses PikPak cloud-stored files (create, modify, delete and update times, user, name, kind, URL and thumbnail) from the PikPak files database.",
        "author": "",
        "creation_date": "2023-03-24",
        "last_update_date": "2023-03-24",
        "requirements": "none",
        "category": "PikPak",
        "notes": "",
        "paths": ('*/com.pikcloud.pikpak/databases/pikpak_files_*.db*',),
        "output_types": "standard",
        "artifact_icon": "file",
        "html_columns": ['Thumbnail Link'],
    }
}

import datetime

from scripts.html_safe import safe_url
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_pikpakCloudlist(files_found, report_folder, seeker, wrap_text):

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.db'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
            SELECT create_time, modify_time, delete_time, local_update_time,
                   user_id, name, kind, url, thumbnail_link
            FROM xpan_files
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            local_update = datetime.datetime.fromtimestamp(int(row[3]) / 1000, datetime.timezone.utc) if row[3] else ''
            link = safe_url(row[8])
            data_list.append((row[0], row[1], row[2], local_update, row[4], row[5], row[6], row[7], link))

    data_headers = ('Create Time', 'Modify Time', 'Delete Time', ('Local Update Time', 'datetime'), 'User ID', 'Name', 'Kind', 'URL', 'Thumbnail Link')
    return data_headers, data_list, source_path
