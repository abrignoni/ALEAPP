__artifacts_v2__ = {
    
    "history_log": {
        "name": "Samsung Knox History Log",
        "description": 'Entries from the Samsung Knox Secure Folder HistoryLog table (history_log_database), with the stored timestamp text, tag and message.',
        "author": "Alexis Brignoni {linqapp.com/abrignoni}, @AlexisBrignoni, Codex",
        "creation_date": "2026-02-27",
        "last_update_date": "2026-11-17",
        "requirements": "sqlite",
        "category": "Samsung History Log",
        "notes": (
            "The timestamp column is text with no zone recorded. Timestamp shows that text as "
            "stored, with no conversion, and it is not typed as a date and time. Known data "
            "(samsung_a166u_a16_known_20261117, phone zone UTC-5 on that date): one file was "
            "moved from Android user 0's Download folder into the Secure Folder with My Files "
            "between 14:59:49 and 15:00:46 UTC, per the session record, and the Secure Folder "
            "was created at about 14:53:57 UTC. The HistoryLog held a request record stored as "
            "10:00:32 and a result record stored as 10:00:36, both naming [0 -> 150]. Read as "
            "phone local time these are 15:00:32 and 15:00:36 UTC, inside the move window; read "
            "as UTC they would fall before the Secure Folder existed. On this known data the "
            "stored text is phone local time. One device and one move: other devices and app "
            "versions are not exercised. Every matched history_log_database is read, with one "
            "copy kept where the extraction holds the same file under more than one storage "
            "path, and Source File names the database each row came from. A database with no "
            "HistoryLog table is skipped and named in the run log. The write-ahead log and "
            "journal beside the database are matched so the database is read with them; on the "
            "known data both records were in the -wal. Of the registered zip images, only "
            "samsung_a166u_a16_known_20261117 holds history_log_database (in Android user 0's "
            "com.samsung.knox.securefolder container); registered tar images were not checked. "
            "The reading of more than one database was exercised on constructed databases only."
        ),
        "paths": ('*/com.samsung.knox.securefolder/databases/history_log_database*',),
        "output_types": ["standard"],
        "artifact_icon": "database",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.knox.securefolder | history_log_database | 2 rows",
        },
    }
}

# Samsung Android History Log
# Author:  Alexis Brignoni (linqapp.com/abrignoni)
from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    does_table_exist_in_db,
    get_sqlite_db_records,
    logfunc,
)

@artifact_processor
def history_log(context):
    files_found = [x for x in unique_files(context)
                   if x.endswith('history_log_database')]

    query = ('''
        SELECT 
        timestamp,
        id,
        tag,
        message
        FROM HistoryLog
    ''')

    data_list = []
    sources = []

    for file_found in files_found:
        if not does_table_exist_in_db(file_found, 'HistoryLog'):
            logfunc(f'Samsung Knox History Log - no HistoryLog table in '
                    f'{context.get_relative_path(file_found)}')
            continue

        source_file = context.get_relative_path(file_found)
        db_records = get_sqlite_db_records(file_found, query)

        for row in db_records:
            # The stored text carries no zone, so it is reported as stored.
            data_list.append((row[0], row[1], row[2], row[3], source_file))

        sources.append(file_found)

    data_headers = ('Timestamp', 'ID', 'Tag', 'Message', 'Source File')

    return data_headers, data_list, '\n'.join(sources)
