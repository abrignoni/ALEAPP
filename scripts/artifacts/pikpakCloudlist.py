__artifacts_v2__ = {
    "get_pikpakCloudlist": {
        "name": "PikPak Cloud List",
        "description": "Parses PikPak cloud-stored files (create, modify, delete and update times, "
                       "user, name, kind, URL and thumbnail) from each PikPak files database "
                       "found (pikpak_files_*.db).",
        "author": "@abrignoni",
        "creation_date": "2023-03-24",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "PikPak",
        "notes": "Each matched pikpak_files_*.db is read once per storage view. A Source "
                 "File column is added when rows come from more than one database. A "
                 "database that cannot be queried is named in the run log and skipped. "
                 "Create Time, Modify Time and Delete Time are reported as stored.",
        "paths": ('*/com.pikcloud.pikpak/databases/pikpak_files_*.db*',),
        "output_types": "standard",
        "artifact_icon": "file",
        "html_columns": ['Thumbnail Link'],
    }
}

import datetime
import sqlite3

from scripts.artifacts.storagePathViews import unique_files
from scripts.html_safe import safe_url
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_pikpakCloudlist(context):
    data_list = []
    origins = []
    sources = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue
        relative = context.get_relative_path(file_found)
        try:
            db = open_sqlite_db_readonly(file_found)
            try:
                all_rows = db.cursor().execute('''
                    SELECT create_time, modify_time, delete_time, local_update_time,
                           user_id, name, kind, url, thumbnail_link
                    FROM xpan_files
                ''').fetchall()
            finally:
                db.close()
        except sqlite3.Error as error:
            logfunc(f'PikPak Cloud List: could not query {relative}: {error}')
            continue

        for row in all_rows:
            try:
                local_update = (datetime.datetime.fromtimestamp(int(row[3]) / 1000, datetime.timezone.utc)
                                if row[3] else '')
            except (ValueError, TypeError, OverflowError, OSError):
                local_update = ''
            link = safe_url(row[8])
            data_list.append((row[0], row[1], row[2], local_update, row[4], row[5], row[6], row[7], link))
            origins.append(relative)
        sources.append(file_found)

    data_headers = ('Create Time', 'Modify Time', 'Delete Time', ('Local Update Time', 'datetime'), 'User ID', 'Name', 'Kind', 'URL', 'Thumbnail Link')
    if len(sources) > 1:
        data_headers += ('Source File',)
        data_list = [row + (origin,) for row, origin in zip(data_list, origins)]
    return data_headers, data_list, '\n'.join(sources)
