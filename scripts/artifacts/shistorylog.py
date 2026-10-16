__artifacts_v2__ = {
    
    "history_log": {
        "name": "Samsung Knox History Log",
        "description": 'Entries from the Samsung Knox Secure Folder HistoryLog table (history_log_database), with the stored timestamp text, tag and message.',
        "author": "Alexis Brignoni {linqapp.com/abrignoni}, @AlexisBrignoni, Codex",
        "creation_date": "2026-02-27",
        "last_update_date": "2026-10-04",
        "requirements": "sqlite",
        "category": "Samsung History Log",
        "notes": (
            "The timestamp column is text with no zone recorded. Timestamp shows that text as "
            "stored, with no conversion, and it is not typed as a date and time. Which zone the "
            "app writes it in is not established. Every matched history_log_database is read, "
            "with one copy kept where the extraction holds the same file under more than one "
            "storage path, and Source File names the database each row came from. A database "
            "with no HistoryLog table is skipped and named in the run log. The write-ahead log "
            "and journal beside the database are matched so the database is read with them. "
            "No registered image was found to hold a HistoryLog table: the five images listed "
            "in the sample data of the Samsung Secure Folder - History Log artifact "
            "(samsungSecureFolderHistoryLog.py) hold none, and other registered images were "
            "not checked for this artifact. The reading of more than one database and the "
            "stored text output were exercised on constructed databases only."
        ),
        "paths": ('*/com.samsung.knox.securefolder/databases/history_log_database*',),
        "output_types": ["standard"],
        "artifact_icon": "database"
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
