__artifacts_v2__ = {
    "get_scontextLog": {
        "name": "scontextLog",
        "description": "Parses rows of the use_app table (starttime, stoptime, time_zone, app_id, app_sub_id and duration) from the Samsung ContextLog.db. Each matched ContextLog.db is read.",
        "author": "@abrignoni",
        "creation_date": "2020-04-18",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "App Interaction",
        "notes": "Each file named ContextLog.db among the matches is read once; write-ahead log and journal files are not opened on their own, and the duplicate storage paths of one file are read once. A file that cannot be queried is logged and gives no rows. A Source File column is added only when more than one file gives rows. Start Time and Stop Time are starttime and stoptime read as Unix milliseconds and shown in UTC; Timezone, App ID, APP Sub ID and Duration are as stored, and Duration in Secs is Duration divided by 1000 with the remainder dropped.",
        "paths": ('*/com.samsung.android.providers.context/databases/ContextLog.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}

import datetime
import os
import sqlite3

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_scontextLog(context):
    data_list = []
    row_sources = []
    queried = []
    contributors = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or os.path.basename(file_found) != 'ContextLog.db':
            continue
        db = None
        try:
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
                SELECT starttime, stoptime, time_zone, app_id, app_sub_id, duration, duration/1000
                FROM use_app
            ''')
            all_rows = cursor.fetchall()
        except (sqlite3.Error, OSError, AttributeError) as error:
            logfunc(f'scontextLog: could not read {context.get_relative_path(file_found)}: {error}')
            continue
        finally:
            if db is not None:
                db.close()
        queried.append(file_found)
        if all_rows:
            contributors.append(file_found)
        for row in all_rows:
            start = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] and int(row[0]) > 0 else ''
            stop = datetime.datetime.fromtimestamp(int(row[1]) / 1000, datetime.timezone.utc) if row[1] and int(row[1]) > 0 else ''
            data_list.append((start, stop, row[2], row[3], row[4], row[5], row[6]))
            row_sources.append(file_found)

    data_headers = (('Start Time', 'datetime'), ('Stop Time', 'datetime'), 'Timezone', 'App ID', 'APP Sub ID', 'Duration', 'Duration in Secs')
    if len(contributors) > 1:
        data_headers += ('Source File',)
        data_list = [row + (context.get_relative_path(path),) for row, path in zip(data_list, row_sources)]
    return data_headers, data_list, '\n'.join(contributors or queried)
