# pylint: disable=W0612
__artifacts_v2__ = {
    "googlevoice_accounts": {
        "name": "Google Voice - User Accounts",
        "description": "Parses the account entries of the Google Voice AccountData.pb and two phone numbers from the VoiceAccountCache database",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek)",
        "creation_date": "2025-08-08",
        "last_update_date": "2025-10-29",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "The authors report testing on app version 2025.07.20.788599304 (October 29th, "
                 "2025) on Samsung and Motorola devices; no count or image from that testing is "
                 "recorded. The registered image with rows is pixel7a_a14. Account number, name "
                 "and email address come from field 2 of AccountData.pb. Linked Phone Number is "
                 "field 3.2.1.1 and Current Google Voice Number is field 3.1.1.1 of the cached "
                 "response in the VoiceAccountCache database; the names are the authors' and no "
                 "source for them is cited.",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/AccountData.pb', '*/data/com.google.android.apps.googlevoice/files/accounts/*/SqliteKeyValueCache:VoiceAccountCache.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.google.android.apps.googlevoice vc 3579017 | 1 row",
        },
    },
    "googlevoice_calls": {
        "name": "Google Voice - Calls",
        "description": "Parses call records from the Google Voice LegacyMsgDbInstance.db message_t table",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek); @AlexisBrignoni, Codex",
        "creation_date": "2025-08-20",
        "last_update_date": "2026-10-06",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "The authors report testing on app version 2025.07.20.788599304 (October 29th, "
                 "2025) on Samsung and Motorola devices; no count or image from that testing is "
                 "recorded. The registered image with rows is pixel7a_a14. Direction, Call Status "
                 "and Voicemail Left are assigned by the module from field 13 of message_blob (0, "
                 "1, 2 or 3) and from whether field 22 is present. The mapping is the module's "
                 "own and no source is cited. Call Status reads Missed for value 0, for value 3 "
                 "and for any record carrying field 22; the module's comments say value 0 covers "
                 "a call that was declined as well as one that was not answered. Duration is "
                 "field 9 read as a 32-bit float of seconds. Call Status is explicitly the existing "
                 "parser classification, not a verified outcome. Raw Field 13 JSON and Raw Field "
                 "22 JSON retain decoded protobuf decision values using typed JSON nodes: integer "
                 "decimal text, bytes hexadecimal, list items, and dictionary key/value entries. "
                 "All nodes are tagged, so a dictionary cannot be confused with a byte tag. "
                 "Field 22 Present tests membership, including stored zero/empty values; absent "
                 "field 22 has blank raw output. This representation preserves decoded values, "
                 "not the original protobuf wire encoding. Existing record selection, account "
                 "iteration and unsupported/malformed record handling remain unchanged.",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/accounts/*/LegacyMsgDbInstance.db*', '*/data/com.google.android.apps.googlevoice/cache/audio/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "phone",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.google.android.apps.googlevoice vc 3579017 | 4 rows",
        },
    },
    "googlevoice_voicemails": {
        "name": "Google Voice - Voicemails",
        "description": "Parses voicemail records (field 13 = 3) from the Google Voice LegacyMsgDbInstance.db message_t table",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek)",
        "creation_date": "2025-09-03",
        "last_update_date": "2025-10-29",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "The authors report testing on app version 2025.07.20.788599304 (October 29th, "
                 "2025) on Samsung and Motorola devices; no count or image from that testing is "
                 "recorded. The registered image with rows is pixel7a_a14. Read Status is field 6 "
                 "of the record, 0 shown as Unread and 1 as Read. What sets it is not "
                 "established, and it does not show that a person listened to the voicemail. "
                 "Transcript is the text segments stored in field 7.2 joined with spaces; it "
                 "reads Transcript Not Available when field 7 is absent.",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/accounts/*/LegacyMsgDbInstance.db*', '*/data/com.google.android.apps.googlevoice/cache/audio/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "record-mail",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.google.android.apps.googlevoice vc 3579017 | 1 row",
        },
    },
    "googlevoice_messages": {
        "name": "Google Voice - Messages",
        "description": "Parses message records from the Google Voice LegacyMsgDbInstance.db message_t table",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek)",
        "creation_date": "2025-10-22",
        "last_update_date": "2026-07-03",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "The authors report testing on app version 2025.07.20.788599304 (October 29th, "
                 "2025) on Samsung and Motorola devices; no count or image from that testing is "
                 "recorded. The registered image with rows is pixel7a_a14. Rows are the message_t "
                 "records whose conversation_id starts with t or g. Direction is assigned by the "
                 "module, from field 13 (5 Incoming, 6 Outgoing) for t conversations and from "
                 "whether field 15.5 is present for g conversations; the mapping is the module's "
                 "own and no source is cited. Read Status is field 6 on incoming rows, 0 shown as "
                 "Unread and 1 as Read, and is blank on outgoing rows; what sets it is not "
                 "established. An image is shown only when the message text contains MMS and a "
                 "cached file named for the message id is present.",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/accounts/*/LegacyMsgDbInstance.db*', '*/data/com.google.android.apps.googlevoice/cache/Photo MMS images/*', '*/data/com.samsung.android.providers.contacts/databases/contact*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.providers.contacts | 0 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.providers.contacts | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.googlevoice vc 3579017 | 14 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.providers.contacts | 0 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.providers.contacts | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.android.providers.contacts | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender",
                "mediaColumn": "Image"
            }
        },
    }
}

from scripts.ilapfuncs import decode_protobuf
import os
import time
import struct
import inspect
import json
from scripts.ilapfuncs import artifact_processor, get_binary_file_content, open_sqlite_db_readonly, does_table_exist_in_db, check_in_media


def _decode_text(value):
    '''Message body (protobuf field 10) is normally bytes, but can be a nested message
    (dict) for structured/MMS content. Decode bytes; otherwise stringify so the record
    still parses instead of raising AttributeError on .decode.'''
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return str(value)

@artifact_processor
def googlevoice_accounts(context):
    files_found = context.get_files_found()
    data_headers = ('Account Number', 'Full Name', 'Email Address', 'Linked Phone Number', 'Current Google Voice Number')
    data_list = []
    source_paths = []

    account_number = ""
    full_name = ""
    email_address = ""
    linked_number = ""
    voice_number = ""

    accounts = []
    for file in files_found:
        if os.path.basename(file).endswith("VoiceAccountCache.db"):
            parts = file.split(os.sep)
            user_index = parts.index("accounts") + 1
            accounts.append(int(parts[user_index]))

    for i in range(len(accounts)):
        for file in files_found:
            if os.path.basename(file) == 'AccountData.pb':
                source_paths.append(file)
                pb = get_binary_file_content(file)

                message = decode_protobuf(pb)

                # check for data in the account
                if '2' in message[0]:
                    if len(accounts) == 1:
                        account_number = message[0]['2']['1']
                        full_name = message[0]['2']['2']['2']['2'].decode('utf-8')
                        email_address = message[0]['2']['2']['2']['3'].decode('utf-8')
                    elif len(accounts) > 1:
                        account_number = message[0]['2'][i]['1']
                        full_name = message[0]['2'][i]['2']['2']['2'].decode('utf-8')
                        email_address = message[0]['2'][i]['2']['2']['3'].decode('utf-8')
                else:
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
                message = decode_protobuf(pb)

                # check account data exists
                if '3' in message[0]:
                    if '2' in message[0]['3']:
                        linked_number = message[0]['3']['2']['1']['1'].decode('utf-8')
                    else:
                        linked_number = ""
                    if '1' in message[0]['3']:
                        voice_number = message[0]['3']['1']['1']['1'].decode('utf-8')
                    else:
                        voice_number = ""

        if account_number:
            data_list.append((account_number,full_name,email_address,linked_number,voice_number))

    return data_headers, data_list, '\n'.join(source_paths)

def _raw_call_value_json(value):
    """Represent decoded protobuf values with collision-safe, recursively typed nodes."""
    def node(item):
        if isinstance(item, (bytes, bytearray)):
            return {'type': type(item).__name__, 'hex': item.hex()}
        if isinstance(item, dict):
            return {'type': 'dict', 'entries': [[node(key), node(val)] for key, val in item.items()]}
        if isinstance(item, list):
            return {'type': 'list', 'items': [node(val) for val in item]}
        if item is None:
            return {'type': 'null'}
        if isinstance(item, bool):
            return {'type': 'bool', 'value': item}
        if isinstance(item, int):
            return {'type': 'int', 'decimal': str(item)}
        if isinstance(item, float):
            return {'type': 'float', 'hex': item.hex()}
        if isinstance(item, str):
            return {'type': 'str', 'value': item}
        raise TypeError(f'Unsupported decoded protobuf value type: {type(item).__name__}')
    return json.dumps(node(value), ensure_ascii=False, separators=(',', ':'))


@artifact_processor
def googlevoice_calls(context):
    files_found = context.get_files_found()
    data_headers = (('Timestamp', 'datetime'), 'Account Number', 'Direction', 'Caller', 'Recipient', 'Call Status (existing parser classification)', 'Raw Field 13 JSON', 'Field 22 Present', 'Raw Field 22 JSON', 'Voicemail Left', 'Duration', ('Call Recording', 'media'))
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

                account_number = ""
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
                        message = decode_protobuf(pb)

                        # check if the entry is a call (answered, missed, outgoing)
                        # 13 = 0 for a missed or declined call without a voicemail
                        # 13 = 1 for an answered call
                        # 13 = 2 for an outgoing call
                        # 22 has a value if a call was missed or declined
                        # 13 = 3 for a received voicemail
                        # The Google Voice welcome voicemail does not call the phone but leaves a voicemail
                        if message[0]['13'] == 0 or message[0]['13'] == 1 or message[0]['13'] == 2 or ('22' in message[0]) or (message[0]['13'] == 3 and "welcome_voicemail" not in message[0]['1'].decode('utf-8')):

                            # Timestamp
                            timestamp = ""
                            if '2' in message[0]:
                                timestamp = message[0]['2'] / 1000 # convert to seconds
                                timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timestamp)) # convert to UTC time

                            # Direction
                            direction = ""
                            from_num = ""
                            to_num = ""
                            voicemail = ""
                            if message[0]['13'] == 0 or message[0]['13'] == 1 or ('22' in message[0]) or message[0]['13'] == 3:
                                direction = "Incoming"
                                from_num = str(message[0]['4']['1'].decode('utf-8'))
                                to_num = message[0]['3'].decode('utf-8') # GV number

                                # Voicemail
                                if message[0]['13'] == 3:
                                    voicemail = "Yes"
                                elif message[0]['13'] != 1:
                                    voicemail = "No"

                            elif message[0]['13'] == 2:
                                direction = "Outgoing"
                                from_num = message[0]['3'].decode('utf-8') # GV number
                                to_num = message[0]['4']['1'].decode('utf-8')

                            # Call Status
                            call_status = ""
                            if ('22' in message[0]) or message[0]['13'] == 3 or message[0]['13'] == 0:
                                call_status = "Missed"
                            elif message[0]['13'] == 1:
                                call_status = "Answered"

                            raw13 = _raw_call_value_json(message[0]['13'])
                            present22 = 'Yes' if '22' in message[0] else 'No'
                            raw22 = _raw_call_value_json(message[0]['22']) if '22' in message[0] else ''

                            # Duration
                            duration = ""
                            if '9' in message[0]:
                                duration = message[0]['9']
                                duration = struct.unpack('f', struct.pack('I', duration))[0] # convert int32 value to a float
                                duration = time.strftime("%H:%M:%S", time.gmtime(duration)) # convert seconds to Hours:Minutes:Seconds

                            # Recording
                            # 23 has values if an incoming call was recorded
                            recording = ""
                            if '23' in message[0]:
                                artifact_info = inspect.stack()[0]
                                message_id = message[0]['1'].decode('utf-8')
                                recording = ""

                                # get the audio file
                                for audio_file in files_found:
                                    if "audio" in audio_file and message_id in audio_file:
                                        recording = check_in_media(audio_file)
                                        break
                                
                                data_list.append((timestamp,account_number,direction,from_num,to_num,call_status,raw13,present22,raw22,voicemail,duration,recording))

                            else:
                                data_list.append((timestamp,account_number,direction,from_num,to_num,call_status,raw13,present22,raw22,voicemail,duration,recording))

    return data_headers, data_list, source_path

@artifact_processor
def googlevoice_voicemails(context):
    files_found = context.get_files_found()
    data_headers = (('Timestamp', 'datetime'), 'Account Number', 'Caller', 'Recipient', 'Duration', 'Read Status', 'Transcript', ('Audio File', 'media'))
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

                account_number = ""
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
                        message = decode_protobuf(pb)

                        # check if the entry is a voicemail
                        # 13 = 3 for a voicemail is received
                        if message[0]['13'] == 3:

                            # Timestamp
                            timestamp = ""
                            if '2' in message[0]:
                                timestamp = message[0]['2'] / 1000 # convert to seconds
                                timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timestamp)) # convert to UTC time

                            # Caller
                            from_num = ""
                            if '4' in message[0] and '1' in message[0]['4']:
                                from_num = str(message[0]['4']['1'].decode('utf-8'))

                            # Recipient
                            to_num = ""
                            if '3' in message[0]:
                                to_num = message[0]['3'].decode('utf-8') # GV number

                            # Duration
                            duration = ""
                            if '9' in message[0]:
                                duration = message[0]['9']
                                duration = struct.unpack('f', struct.pack('I', duration))[0] # convert int32 value to a float
                                duration = time.strftime("%H:%M:%S", time.gmtime(duration)) # convert seconds to Hours:Minutes:Seconds

                            # Read Status
                            read_status = ""
                            if message[0]['6'] == 0:
                                read_status = "Unread"
                            elif message[0]['6'] == 1:
                                read_status = "Read"

                            # Transcript
                            # 7[2] holds the transcript of the voicemail broken into word and special character segments
                            if '7' in message[0]:
                                transcript = ""
                                num_words = len(message[0]['7']['2'])
                                if isinstance(message[0]['7']['2'], list): # check to see if the voicemail is longer than one word
                                    for j in range(num_words):
                                        word = message[0]['7']['2'][j]['1'].decode('utf-8')
                                        if word != "":
                                            transcript += word + " "
                                else:
                                    transcript = message[0]['7']['2']['1'].decode('utf-8')
                            else:
                                transcript = "Transcript Not Available"

                            # Audio File
                            audio = ""
                            artifact_info = inspect.stack()[0]
                            message_id = message[0]['1'].decode('utf-8')
                            # get the voicemail audio file
                            for audio_file in files_found:
                                if "audio" in audio_file and message_id in audio_file:
                                    audio = check_in_media(audio_file)
                                    break

                            data_list.append((timestamp,account_number,from_num,to_num,duration,read_status,transcript,audio))

    return data_headers, data_list, source_path

@artifact_processor
def googlevoice_messages(context):
    files_found = context.get_files_found()
    data_headers = (('Timestamp', 'datetime'), 'Direction', 'Sender', 'Message', ('Image', 'media'), 'Account Number', 'Conversation ID', 'Recipient(s)', 'Read Status')
    data_list = []
    source_path = ""

    # get a list of accounts
    accounts = []
    for file in files_found:
        if os.path.basename(file).endswith("LegacyMsgDbInstance.db"):
            parts = file.split(os.sep)
            user_index = parts.index("accounts") + 1
            accounts.append(int(parts[user_index]))

    # get the message data
    source_path_found = False
    for i in range(len(accounts)):
        for file in files_found:
            if os.path.basename(file) == 'LegacyMsgDbInstance.db':

                account_number = ""
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
                        message_blob,
                        conversation_id
                        FROM
                        message_t
                        ''')
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    for row in all_rows:
                        # conversation_id starts with "t" for individual messages
                        if row[1].startswith("t"):
                            pb = row[0]
                            message = decode_protobuf(pb)

                            # Conversation ID
                            conversation_id = row[1]

                            # Timestamp
                            timestamp = ""
                            if '2' in message[0]:
                                timestamp = message[0]['2'] / 1000 # convert to seconds
                                timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timestamp)) # convert to UTC time

                            # Direction
                            # 13 = 5 when a message is received
                            # 13 = 6 when a message is sent
                            direction = ""
                            from_num = ""
                            to_num = ""
                            read_status = ""
                            if message[0]['13'] == 5:
                                direction = "Incoming"
                                from_num = message[0]['4']['1'].decode('utf-8')
                                to_num = message[0]['3'].decode('utf-8') # GV number

                                # Read Status
                                if message[0]['6'] == 0:
                                    read_status = "Unread"
                                elif message[0]['6'] == 1:
                                    read_status = "Read"

                            elif message[0]['13'] == 6:
                                direction = "Outgoing"
                                from_num = message[0]['3'].decode('utf-8') # GV number
                                to_num = message[0]['4']['1'].decode('utf-8')

                            # Message
                            message_content = ""
                            if '10' in message[0]:
                                message_content = _decode_text(message[0]['10'])

                            # Image
                            if "MMS" in message_content:
                                artifact_info = inspect.stack()[0]
                                message_id = message[0]['1'].decode('utf-8')

                                # get image file
                                thumb = ""
                                for image in files_found:
                                    # image file resides in Photo MMS images folder
                                    # filename: message_id + "-14" + extension
                                    if "Photo MMS images" in image and message_id in image and "-14" in image:
                                        thumb = check_in_media(image)
                                        data_list.append((timestamp, direction, from_num, message_content, thumb, account_number, conversation_id, to_num, read_status))
                                        break

                                # if no image file is cached for the message
                                if thumb == "":
                                    data_list.append((timestamp, direction, from_num, message_content, "", account_number, conversation_id, to_num, read_status))

                            else:
                                data_list.append((timestamp, direction, from_num, message_content, "", account_number, conversation_id, to_num, read_status))

                        # conversation_id starts with "g" for group chat messages
                        elif row[1].startswith("g"):
                            pb = row[0]
                            message = decode_protobuf(pb)

                            # Conversation ID
                            conversation_id = row[1]

                            # Timestamp
                            timestamp = ""
                            if '2' in message[0]:
                                timestamp = message[0]['2'] / 1000 # convert to seconds
                                timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timestamp)) # convert to UTC time

                            # Direction
                            # 5 exists in 15 when the message is received
                            direction = ""
                            from_num = ""
                            to_nums_list = []
                            read_status = ""
                            if '5' in message[0]['15']:
                                direction = "Incoming"
                                from_num = message[0]['15']['5'].decode('utf-8')

                                # GV number & other group chat members in to_nums_list
                                to_nums_list.append(message[0]['3'].decode('utf-8')) # GV number
                                for j in range(len(message[0]['15']['4'])):
                                    if message[0]['15']['4'][j]['1'].decode('utf-8') != from_num:
                                        to_nums_list.append(message[0]['15']['4'][j]['1'].decode('utf-8'))

                                # Read Status
                                if message[0]['6'] == 0:
                                    read_status = "Unread"
                                elif message[0]['6'] == 1:
                                    read_status = "Read"

                            # 5 does not exist in 15 when the message is sent
                            elif '5' not in message[0]['15']:
                                direction = "Outgoing"
                                from_num = message[0]['3'].decode('utf-8') # GV number

                                # other group chat members in to_nums_list
                                for j in range(len(message[0]['15']['4'])):
                                    to_nums_list.append(message[0]['15']['4'][j]['1'].decode('utf-8'))

                            to_nums = ', '.join(to_nums_list)

                            # Message
                            message_content = ""
                            if '15' in message[0] and '1' in message[0]['15']:
                                message_content = message[0]['15']['1'].decode('utf-8')

                            # Image
                            if "MMS" in message_content:
                                artifact_info = inspect.stack()[0]
                                message_id = message[0]['1'].decode('utf-8')

                                # get the image file
                                thumb = ""
                                for image in files_found:
                                    # image file resides in Photo MMS images folder
                                    # filename: message_id + "-14" + extension
                                    if "Photo MMS images" in image and message_id in image and "-14" in image:
                                        thumb = check_in_media(image)
                                        data_list.append((timestamp, direction, from_num, message_content, thumb, account_number, conversation_id, to_nums, read_status))
                                        break
                                
                                # if no image file is cached for the message
                                if thumb == "":
                                    data_list.append((timestamp, direction, from_num, message_content, "", account_number, conversation_id, to_nums, read_status))

                            else:
                                data_list.append((timestamp, direction, from_num, message_content, "", account_number, conversation_id, to_nums, read_status))

    return data_headers, data_list, source_path
