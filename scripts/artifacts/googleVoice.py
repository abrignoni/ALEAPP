__artifacts_v2__ = {
    "googlevoice_accounts": {
        "name": "Google Voice - User Accounts",
        "description": "Parses Google Voice User Accounts",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek)",
        "creation_date": "2025-08-08",
        "last_update_date": "2025-08-15",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "Tested on version 2025.07.20.788599304 (August 15th, 2025)",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/AccountData.pb', '*/data/com.google.android.apps.googlevoice/files/accounts/*/SqliteKeyValueCache:VoiceAccountCache.db'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "function": "googlevoice_accounts"
    }
}

import blackboxprotobuf
import os
from scripts.ilapfuncs import artifact_processor, get_binary_file_content, open_sqlite_db_readonly

@artifact_processor
def googlevoice_accounts(files_found, report_folder, seeker, wrap_text):
    data_headers = ('Account Number','Full Name','Email Address','Linked Phone Number','Google Voice Number') 
    data_list = []
    source_path = ""

    accounts = []
    for file in files_found:
        if os.path.basename(file).endswith("VoiceAccountCache.db"):
            parts = file.split(os.sep)
            user_index = parts.index("accounts") + 1
            accounts.append(int(parts[user_index]))
    
    for i in range(len(accounts)):
        for file in files_found:
            if os.path.basename(file) == 'AccountData.pb':
                source_path = file 
                pb = get_binary_file_content(file)

                message = blackboxprotobuf.decode_message(pb)

                try:
                    if len(accounts) == 1:
                        account_number = message[0]['2']['1']
                        full_name = message[0]['2']['2']['2']['2'].decode('utf-8')
                        email_address = message[0]['2']['2']['2']['3'].decode('utf-8')
                    elif len(accounts) > 1:
                        account_number = message[0]['2'][i]['1']
                        full_name = message[0]['2'][i]['2']['2']['2'].decode('utf-8')
                        email_address = message[0]['2'][i]['2']['2']['3'].decode('utf-8')
                except:
                    account_number = ""
                    full_name = ""
                    email_address = ""

            if os.path.basename(file).endswith("VoiceAccountCache.db"):
                parts = file.split(os.sep)
                user_index = parts.index("accounts") + 1

                if accounts[i] == int(parts[user_index]):
                    db = open_sqlite_db_readonly(file)
                    cursor = db.cursor()
                    cursor.execute('''
                    SELECT
                    response_data
                    FROM
                    cache_table
                    ''')

                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    for row in all_rows:
                        pb = row[0]
                message = blackboxprotobuf.decode_message(pb)

                try:
                    linked_number = message[0]['3']['2']['1']['1'].decode('utf-8')
                    voice_number = message[0]['3']['1']['1']['1'].decode('utf-8')
                except:
                    linked_number = ""
                    voice_number = ""

        if account_number:
            data_list.append((account_number,full_name,email_address,linked_number,voice_number))

    return data_headers, data_list, source_path