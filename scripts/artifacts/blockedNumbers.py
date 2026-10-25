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
                 "Absence of a row is not evidence that a number was never blocked. In the AOSP BlockedNumberProvider "
                 "source, unblocking a number deletes its row from the blocked table, and _id is declared INTEGER "
                 "PRIMARY KEY AUTOINCREMENT, so an id is not reused after its row is deleted. Reference: "
                 "https://android.googlesource.com/platform/packages/providers/BlockedNumberProvider/+/"
                 "c8c73fda6b1f3a14baa910e14e8e83246f6e22b1/src/com/android/providers/blockednumber/ "
                 "(BlockedNumberProvider.java, unblock and deleteBlockedNumber; BlockedNumberDatabaseHelper.java, "
                 "createTables). Whether a device maker's build changes this was not examined. A dialer may also keep "
                 "a block list in its own store, which this artifact does not read. "
                 "In one Android 16 database with 126 rows, _id ran 1 to 126 with no gap, original_number held "
                 "both national-format and +-prefixed numbers, and e164_number was an empty string, not NULL, on the "
                 "6 rows whose original_number is a 5- or 6-digit number and a +-prefixed number on the other 120; "
                 "those counts are an observation on that database, not a rule for the column. "
                 "On two further databases (561 and 958 rows) _id ran to 612 and 960, so ids are missing from the sequence; "
                 "the table keeps no record of what a missing id held. "
                 "Validation boundary: the schema (blocked with _id, original_number and e164_number, database "
                 "user_version 2) was read from four Android 16 databases found under data/user_de/0, with "
                 "126, 0, 561 and 958 rows, and was the same on all 50 copies of the database in 34 corpus images, "
                 "two of which hold rows (1 and 6, see sample_data). None of the 34 corpus images held a second Android user's "
                 "database, and the Samsung dialer's own list was not examined; the second-user handling was "
                 "exercised on constructed databases only. A database without an e164_number column is read with "
                 "that column blank.",
        "paths": ('*/com.android.providers.blockednumber/databases/blockednumbers.db*',),
        "output_types": "standard",
        "artifact_icon": "phone-off",
        "sample_data": {
            "cookbook_a11": "Android 11 | com.android.providers.blockednumber | 1 row",
            "hickman_a13": "Android 13 | com.android.providers.blockednumber | 6 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.blockednumber | 0 rows",
            "anne_a15": "Android 15 | com.android.providers.blockednumber | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.blockednumber | 0 rows",
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
