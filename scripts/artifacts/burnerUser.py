# pylint: disable=W0613
__artifacts_v2__ = {
    "get_burnerUser": {
        "name": "Burner: Second Phone Number",
        "description": "Parses Burner User Information",
        "author": "Heather Charpentier (With Tons of Help from Alexis Brignoni!)",
        "version": "0.0.1",
        "creation_date": "2024-02-15",
        "last_update_date": "2024-02-15",
        "requirements": "none",
        "category": "Burner",
        "notes": "",
        "paths": ('*/data/com.adhoclabs.burner/databases/burnerDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_burnerUser(files_found, report_folder, seeker, wrap_text):

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
            json_extract(BurnerEntity.value, '$.dateCreated') as 'Date Created',
            id as 'User ID',
            json_extract(BurnerEntity.value, '$.phoneNumberId') as 'Phone Number',
            json_extract(BurnerEntity.value, '$.autoReplyText') as 'Auto Reply Message'
            FROM BurnerEntity
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            created = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((created, row[1], row[2], row[3]))

    data_headers = (('Timestamp', 'datetime'), 'User ID', ('Phone Number', 'phonenumber'), 'Auto Reply Message')
    return data_headers, data_list, source_path
