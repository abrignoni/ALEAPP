__artifacts_v2__ = {
    "GooglePlaySearches": {
        "name": "Google Play Searches",
        "description": "Rows of the suggestions table in the Google Play Store suggestions.db: the date (read as Unix milliseconds, UTC), display1 and query columns",
        "author": "Alexis Brignoni, @AlexisBrignoni, Codex",
        "creation_date": "2020-04-02",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Google Play Store",
        "notes": "Every suggestions.db the paths match is read, once per Android user: where an "
                 "extraction holds the same user's file under more than one storage path "
                 "(data/data, data/user/N, data_mirror/data_ce) one copy is read. Source File "
                 "names the database each row came from. On russell_pixel6a_a13 the file exists "
                 "for Android users 0 and 10 with 12 and 10 rows; samsungs20_a13 holds a second "
                 "copy under user/150 with 1 row beside the 21 of the main copy. Timestamp is the "
                 "date column read as Unix milliseconds and shown in UTC to the whole second; the "
                 "column is declared LONG and held a 13 digit integer on every row of the 20 "
                 "databases read from 17 registered zip extractions. A blank or non-numeric date "
                 "is left blank. The table's CREATE statement declares display1 UNIQUE ON CONFLICT "
                 "REPLACE, so one display1 text has at most one row in a database. What causes the "
                 "app to write a row is not established.",
        "paths": ('*/com.android.vending/databases/suggestions.db*'),
        "output_types": "standard",
        'artifact_icon': 'search',
        "sample_data": {
            "anne_a15": "Android 15 | com.android.vending vc 84801930 | 4 rows",
            "galaxys10_a10": "Android 10 | com.android.vending vc 82481710 | 5 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.vending vc 85180930 | 34 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.vending vc 84812830 | 23 rows",
            "pixel7a_a14": "Android 14 | com.android.vending vc 84191730 | 48 rows",
            "samsunga53_a14": "Android 14 | com.android.vending vc 84913330 | 26 rows",
            "samsungs20_a13": "Android 13 | com.android.vending vc 84962330 | 22 rows",
            "sharon_a14": "Android 14 | com.android.vending vc 84222730 | 25 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.vending vc 83631220 | 22 rows",
            "userb2_a13": "Android 13 | com.android.vending vc 84371930 | 9 rows",
        }
    }
}

import os
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _ms_to_utc(value):
    """The date column, Unix milliseconds, as a UTC datetime to the whole second."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return ''
    try:
        return _EPOCH_UTC + timedelta(seconds=int(value) // 1000)
    except (OverflowError, ValueError):
        return ''


@artifact_processor
def GooglePlaySearches(context):
    data_list = []
    sources = []

    query = '''
    SELECT
    date,
    display1,
    query
    from suggestions
    '''

    for file_found in unique_files(context):
        if os.path.basename(file_found) != 'suggestions.db':
            continue
        db_records = get_sqlite_db_records(file_found, query)
        if isinstance(db_records, list):
            # get_sqlite_db_records returns a list only when the open or the query failed
            continue
        sources.append(file_found)
        relative = context.get_relative_path(file_found)
        for record in db_records:
            data_list.append((_ms_to_utc(record[0]), record[1], record[2], relative))

    data_headers = (('Timestamp', 'datetime'), 'Display', 'Query', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
