__artifacts_v2__ = {
    "get_MSAuth_accounts": {
        "name": "Microsoft Authenticator - Accounts",
        "description": "Parses the existing Accounts out of the Microsoft Authenticator App.",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2024-05-11",
        "last_update_date": "2024-05-11",
        "requirements": "",
        "category": "MS Authenticator",
        "notes": "Get Account information from MS authenticator app.",
        "paths": ('*/com.azure.authenticator/databases/PhoneFactor*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "shield",
    }
}

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_MSAuth_accounts(context):
    files_found = context.get_files_found()
    logfunc("Processing data for Microsoft Authenticator - Accounts")

    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm')]

    data_list = []
    source_path = ''
    for file_found in files_found:
        source_path = str(file_found)
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
            SELECT name, username, oath_secret_key
            FROM accounts
        ''')
        data_rows = cursor.fetchall()
        db.close()

        for row in data_rows:
            data_list.append((row[0], row[1], row[2]))

    data_headers = ('Service Name', 'User Name', 'OATH Secret Key')
    return data_headers, data_list, source_path
