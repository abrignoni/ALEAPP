__artifacts_v2__ = {
    "get_blocked_numbers": {
        "name": "Blocked Numbers",
        "description": "Rows of the blocked table in the Android BlockedNumberProvider database blockednumbers.db: the number as stored and its E.164 form",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Phone",
        "notes": "One row per row of the blocked table in each blockednumbers.db found, one database per Android "
                 "user and storage view collapsed to one copy (Source File names the database). The table has three "
                 "columns, all reported as stored: _id, original_number and e164_number. The table holds no "
                 "timestamp, so the artifact has no time column and cannot say when a number was blocked. "
                 "Absence of a row is not evidence that a number was never blocked: whether a number that was "
                 "unblocked leaves a row has not been established, and a dialer may keep a block list in its own "
                 "store, which this artifact does not read. "
                 "In one real Android 16 database with 126 rows, _id ran 1 to 126 with no gap, original_number held "
                 "both national-format and +-prefixed numbers, and e164_number was an empty string, not NULL, on the "
                 "6 rows whose original_number is a 5- or 6-digit number and a +-prefixed number on the other 120; "
                 "those counts are an observation on that database, not a rule for the column. "
                 "On two further databases (561 and 958 rows) _id ran to 612 and 960, so ids are missing from the sequence; "
                 "the table keeps no record of what a missing id held. "
                 "Validation boundary: the schema (blocked with _id, original_number and e164_number, database "
                 "user_version 2) was read from four real Android 16 databases found under data/user_de/0, with "
                 "126, 0, 561 and 958 rows. Other Android versions, a second Android user and the Samsung "
                 "dialer's own list were not examined, and the second-user and storage-view handling was exercised "
                 "on constructed databases only. A database without an e164_number column is read with that column "
                 "blank.",
        "paths": ('*/com.android.providers.blockednumber/databases/blockednumbers.db*',),
        "output_types": "standard",
        "artifact_icon": "phone-off",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | com.android.providers.blockednumber | 126 rows",
            "samsung_ffs_a16_set2": "Android 16 | com.android.providers.blockednumber | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | com.android.providers.blockednumber | 561 rows",
            "samsung_ffs_a16_set4": "Android 16 | com.android.providers.blockednumber | 958 rows",
        },
    }
}

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, null_absent_columns


@artifact_processor
def get_blocked_numbers(context):
    data_headers = ('ID', 'Original Number', 'E.164 Number', 'Source File')
    data_list = []
    sources = []
    query = '''
    SELECT
    _id,
    original_number,
    e164_number
    FROM blocked
    ORDER BY _id;
    '''
    for file_found in unique_files(context):
        if os.path.basename(file_found) != 'blockednumbers.db':
            continue
        sources.append(file_found)
        relative = context.get_relative_path(file_found)
        for record in get_sqlite_db_records(file_found, null_absent_columns(file_found, query)):
            data_list.append((record[0], record[1], record[2], relative))

    return data_headers, data_list, '\n'.join(sources)
