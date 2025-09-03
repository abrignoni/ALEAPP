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
        "function": "googlevoice_accounts",
    },
    "googlevoice_calls": {
        "name": "Google Voice - User Calls",
        "description": "Parses Google Voice Call History",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek)",
        "creation_date": "2025-08-20",
        "last_update_date": "2025-08-29",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "Tested on version 2025.07.20.788599304 (August 29th, 2025)",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/accounts/*/LegacyMsgDbInstance.db'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "phone",
        "function": "googlevoice_calls",
    },
    "googlevoice_voicemails": {
        "name": "Google Voice - Voicemails",
        "description": "Parses Google Voice Voicemails",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek)",
        "creation_date": "2025-09-03",
        "last_update_date": "2025-09-03",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "Tested on version 2025.07.20.788599304 (September 3rd, 2025)",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/accounts/*/LegacyMsgDbInstance.db'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "voicemail",
        "function": "googlevoice_voicemails",
    }
}

import blackboxprotobuf
import os
import time
import struct
from scripts.ilapfuncs import artifact_processor, get_binary_file_content, open_sqlite_db_readonly, does_column_exist_in_db, does_table_exist_in_db

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

@artifact_processor
def googlevoice_calls(files_found, report_folder, seeker, wrap_text):
    data_headers = ('Account Number', 'Timestamp','Direction','Caller','Recipient','Call Status','Voicemail Left','Duration','Read Status','Audio Recording') 
    data_list = []
    source_path = ""

    # get a list of accounts
    accounts = []
    for file in files_found:
        if os.path.basename(file).endswith("LegacyMsgDbInstance.db"):
            parts = file.split(os.sep)
            user_index = parts.index("accounts") + 1
            accounts.append(int(parts[user_index]))
    
    # get the call data
    source_path_found = False
    for i in range(len(accounts)):
        for file in files_found:
            if os.path.basename(file) == 'LegacyMsgDbInstance.db':

                parts = file.split(os.sep)
                user_index = parts.index("accounts") + 1

                # get the path of the first account's db
                if source_path_found == False:
                    source_path = file
                    source_path_found = True

                if accounts[i] == int(parts[user_index]):
                    account_number = accounts[i]
                    db = open_sqlite_db_readonly(file)
                    cursor = db.cursor()
                    if does_table_exist_in_db(file, 'message_t'):
                        cursor.execute('''
                        SELECT 
                        message_blob 
                        FROM 
                        message_t
                        ''')
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    for row in all_rows:
                        pb = row[0]
                        message = blackboxprotobuf.decode_message(pb)

                        # check if the entry is a call (answered, missed, outgoing)
                        # 13 = 1 for an answered call
                        # 13 = 2 for an outgoing call
                        # 22 has a value if a call was missed or declined
                        if message[0]['13'] == 1 or message[0]['13'] == 2 or ('22' in message[0]):

                            # Timestamp
                            timestamp = message[0]['2'] / 1000 # convert to seconds
                            timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timestamp)) # convert to UTC time

                            # Direction
                            if message[0]['13'] == 1 or ('22' in message[0]):
                                direction = "Incoming"
                                from_num = str(message[0]['4']['1'].decode('utf-8'))
                                to_num = message[0]['3'].decode('utf-8') # GV number

                            elif message[0]['13'] == 2:
                                direction = "Outgoing"
                                from_num = message[0]['3'].decode('utf-8') # GV number
                                to_num = message[0]['4']['1'].decode('utf-8')

                            # Call Status
                            call_status = ""
                            if '22' in message[0]:
                                call_status = "Missed"
                            elif message[0]['13'] == 1:
                                call_status = "Answered"

                            # Voicemail
                            # 13 = 3 if a voicemail was left
                            if message[0]['13'] == 3:
                                voicemail = "Yes"
                            else:
                                voicemail = "No"
                            
                            # Duration
                            duration = message[0]['9']
                            duration = struct.unpack('f', struct.pack('I', duration))[0] # convert int32 value to a float
                            duration = time.strftime("%H:%M:%S", time.gmtime(duration)) # convert seconds to Hours:Minutes:Seconds

                            # Read Status
                            if message[0]['6'] == 0:
                                read_status = "Unread"
                            elif message[0]['6'] == 1:
                                read_status = "Read"

                            # Recording
                            # show file which can be found at /data/data/com.google.android.apps.googlevoice/cache/audio
                            if '23' in message[0]:
                                recording = "/data/data/com.google.android.apps.googlevoice/cache/audio/" + message[0]['1'].decode('utf-8') + ".mp3"
                            else:
                                recording = ""


                            if timestamp:
                                data_list.append((account_number,timestamp,direction,from_num,to_num,call_status,voicemail, duration,read_status,recording))

    return data_headers, data_list, source_path

@artifact_processor
def googlevoice_voicemails(files_found, report_folder, seeker, wrap_text):
    data_headers = ('Account Number', 'Timestamp', 'Caller','Recipient','Duration','Read Status','Audio File') 
    data_list = []
    source_path = ""

    # get a list of accounts
    accounts = []
    for file in files_found:
        if os.path.basename(file).endswith("LegacyMsgDbInstance.db"):
            parts = file.split(os.sep)
            user_index = parts.index("accounts") + 1
            accounts.append(int(parts[user_index]))
    
    # get the voicemail data
    source_path_found = False
    for i in range(len(accounts)):
        for file in files_found:
            if os.path.basename(file) == 'LegacyMsgDbInstance.db':

                parts = file.split(os.sep)
                user_index = parts.index("accounts") + 1

                # get the path of the first account's db
                if source_path_found == False:
                    source_path = file
                    source_path_found = True

                if accounts[i] == int(parts[user_index]):
                    account_number = accounts[i]
                    db = open_sqlite_db_readonly(file)
                    cursor = db.cursor()
                    if does_table_exist_in_db(file, 'message_t'):
                        cursor.execute('''
                        SELECT 
                        message_blob 
                        FROM 
                        message_t
                        ''')
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    for row in all_rows:
                        pb = row[0]
                        message = blackboxprotobuf.decode_message(pb)

                        # check if the entry is a voicemail 
                        # 13 = 3 for a voicemail is received
                        if message[0]['13'] == 3:

                            # Timestamp
                            timestamp = message[0]['2'] / 1000 # convert to seconds
                            timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timestamp)) # convert to UTC time
                            
                            # Caller
                            from_num = str(message[0]['4']['1'].decode('utf-8'))
                            
                            # Recipient
                            to_num = message[0]['3'].decode('utf-8') # GV number
                            
                            # Duration
                            duration = message[0]['9']
                            duration = struct.unpack('f', struct.pack('I', duration))[0] # convert int32 value to a float
                            duration = time.strftime("%H:%M:%S", time.gmtime(duration)) # convert seconds to Hours:Minutes:Seconds

                            # Read Status
                            if message[0]['6'] == 0:
                                read_status = "Unread"
                            elif message[0]['6'] == 1:
                                read_status = "Read"

                            # Audio File
                            # show file which can be found at /data/data/com.google.android.apps.googlevoice/cache/audio
                            audio = "/data/data/com.google.android.apps.googlevoice/cache/audio/" + message[0]['1'].decode('utf-8') + ".mp3"
                            
                            if timestamp:
                                data_list.append((account_number,timestamp,from_num,to_num,duration,read_status,audio))

    return data_headers, data_list, source_path
