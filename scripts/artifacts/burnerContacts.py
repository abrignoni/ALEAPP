# pylint: disable=W0613
__artifacts_v2__ = {
    "get_burnerContacts": {
        "name": "Burner: Second Phone Number",
        "description": "Parses Burner Contacts",
        "author": "Heather Charpentier (With Tons of Help from Alexis Brignoni!)",
        "version": "0.0.1",
        "creation_date": "2024-02-15",
        "last_update_date": "2024-02-15",
        "requirements": "none",
        "category": "Burner",
        "notes": "",
        "paths": ('*/data/com.adhoclabs.burner/databases/burnerDatabase.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_burnerContacts(files_found, report_folder, seeker, wrap_text):

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
            SELECT id, phoneNumber
            FROM ContactEntity
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((row[0], row[1]))

    data_headers = ('User ID', ('Phone Number', 'phonenumber'))
    return data_headers, data_list, source_path
