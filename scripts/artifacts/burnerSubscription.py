__artifacts_v2__ = {
    "get_burnerSubscription": {
        "name": "Burner - Subscription",
        "description": "Parses the SubscriptionEntity rows of burnerDatabase.db (burner IDs, creation and renewal dates, SKU, store, trial value and state). Trial Extracted Value and Trial JSON Type retain SQLite json_extract/json_type results without assigning trial-state meanings.",
        "author": "Heather Charpentier (With Tons of Help from Alexis Brignoni!), @AlexisBrignoni, Codex",
        "version": "0.0.1",
        "creation_date": "2024-02-15",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Burner",
        "notes": "Trial Extracted Value is SQLite json_extract(value, '$.trial'); Trial JSON Type "
                 "is json_type for the same path. Boolean true/false extract as 1/0 but their "
                 "types distinguish them from numbers. JSON null has type null and a SQL NULL "
                 "value; a SQL NULL type means the path was not returned, including absent keys "
                 "or SQL NULL/non-object roots. Arrays/objects are SQLite-returned JSON text, "
                 "not the original lexical JSON bytes. Every matched main is read in encounter "
                 "order; the artifact source still names the last main, so combined-input row "
                 "provenance remains unresolved. Existing date conversions are unchanged.",
        "paths": ('*/data/com.adhoclabs.burner/databases/burnerDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "credit-card",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.adhoclabs.burner vc 2104 | 1 row",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


@artifact_processor
def get_burnerSubscription(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('burnerDatabase.db'):
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT
            json_extract(SubscriptionEntity.value, '$.burnerIds') as 'User ID',
            json_extract(SubscriptionEntity.value, '$.creationDate') as 'Date Created',
            json_extract(SubscriptionEntity.value, '$.renewalDate') as 'Renewal Date',
            json_extract(SubscriptionEntity.value, '$.sku') as 'SKU',
            json_extract(SubscriptionEntity.value, '$.store') as 'Store',
            json_extract(SubscriptionEntity.value, '$.trial') as 'Trial Extracted Value',
            json_type(SubscriptionEntity.value, '$.trial') as 'Trial JSON Type',
            json_extract(SubscriptionEntity.value, '$.state') as 'State'
            FROM SubscriptionEntity
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((_ms_to_utc(row[1]), _ms_to_utc(row[2]), row[0], row[3], row[4], row[5], row[6], row[7]))

    data_headers = (('Timestamp', 'datetime'), ('Renewal Date', 'datetime'), 'User ID', 'SKU', 'Store',
                    'Trial Extracted Value', 'Trial JSON Type', 'State')
    return data_headers, data_list, source_path
