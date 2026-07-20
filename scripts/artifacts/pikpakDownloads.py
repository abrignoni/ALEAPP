__artifacts_v2__ = {
    "get_pikpakDownloads": {
        "name": "PikPak Downloads",
        "description": "Parses PikPak downloads (create and modify times, title, local storage path and URL) from the PikPak downloads database.",
        "author": "",
        "creation_date": "2023-03-24",
        "last_update_date": "2023-03-24",
        "requirements": "none",
        "category": "PikPak",
        "notes": "",
        "paths": ('*/com.pikcloud.pikpak/databases/pikpak_downloads.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


@artifact_processor
def get_pikpakDownloads(context):
    files_found = context.get_files_found()

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
            SELECT create_time, lastmod, title, _data, uri
            from xl_downloads
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((_ms_to_utc(row[0]), _ms_to_utc(row[1]), row[2], row[3], row[4]))

    data_headers = (('Create Time', 'datetime'), ('Modify Time', 'datetime'), 'Title', 'Local Storage', 'URL')
    return data_headers, data_list, source_path
