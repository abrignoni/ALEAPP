__artifacts_v2__ = {
    "get_firefoxFormHistory": {
        "name": "Firefox - Form History",
        "description": "Parses Firefox saved form entries (field name, value, times used, first and last used timestamps) from formhistory.sqlite.",
        "author": "",
        "creation_date": "2022-01-12",
        "last_update_date": "2022-01-12",
        "requirements": "none",
        "category": "Firefox",
        "notes": "",
        "paths": ('*/org.mozilla.firefox/files/mozilla/*.default/formhistory.sqlite*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "pixel7a_a14": "Android 14 | org.mozilla.firefox vc 2016030615 | 0 rows",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_firefoxFormHistory(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'formhistory.sqlite':  # skip -journal and other files
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(firstUsed/1000000, 'unixepoch') AS FirstUsed,
        datetime(lastUsed/1000000, 'unixepoch') AS LastUsed,
        fieldname AS FieldName,
        value AS Value,
        timesUsed AS TimesUsed,
        id AS ID
        FROM moz_formhistory
        ORDER BY id ASC
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]),convert_human_ts_to_utc(row[1]),row[2],row[3],row[4],row[5]))

        db.close()

    data_headers = (
        ('First Used Timestamp', 'datetime'),
        ('Last Used Timestamp', 'datetime'),
        'Field Name',
        'Value',
        'Times Used',
        'ID',
    )
    return data_headers, data_list, source_path
