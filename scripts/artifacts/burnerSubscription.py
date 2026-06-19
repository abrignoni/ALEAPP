# pylint: disable=W0613
__artifacts_v2__ = {
    "get_burnerSubscription": {
        "name": "Burner: Second Phone Number",
        "description": "Parses Burner Subscription Information",
        "author": "Heather Charpentier (With Tons of Help from Alexis Brignoni!)",
        "version": "0.0.1",
        "creation_date": "2024-02-15",
        "last_update_date": "2024-02-15",
        "requirements": "none",
        "category": "Burner",
        "notes": "",
        "paths": ('*/data/com.adhoclabs.burner/databases/burnerDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "credit-card",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


@artifact_processor
def get_burnerSubscription(files_found, report_folder, seeker, wrap_text):

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
            CASE json_extract(SubscriptionEntity.value, '$.trial')
                WHEN 1 THEN 'True'
                WHEN 2 THEN 'False'
                ELSE 'Unknown'
            END as Trial,
            json_extract(SubscriptionEntity.value, '$.state') as 'State'
            FROM SubscriptionEntity
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((row[0], _ms_to_utc(row[1]), _ms_to_utc(row[2]), row[3], row[4], row[5], row[6]))

    data_headers = ('User ID', ('Timestamp', 'datetime'), ('Renewal Date', 'datetime'), 'SKU', 'Store', 'Trial', 'State')
    return data_headers, data_list, source_path
