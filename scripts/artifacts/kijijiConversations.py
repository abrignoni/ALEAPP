__artifacts_v2__ = {
    "get_kijijiConversations": {
        "name": "kijijiConversations",
        "description": "Kijiji Conversations",
        "author": "Terry Chabot (Krypterry)",
        "creation_date": "2022-05-13",
        "last_update_date": "2022-05-13",
        "requirements": "None",
        "category": "Kijiji",
        "notes": "",
        "paths": ('*/com.ebay.kijiji.ca/databases/messageBoxDatabase.*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
    }
}

import json
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, does_table_exist_in_db

LOCAL_USER = 'Local User'
LOCAL_USER_INDICATOR = 'ME'

conversations_query = '''
    SELECT
        identifier,
        ad,
        counterParty,
        messages
    FROM conversations
    ORDER BY sortByDate ASC;
'''


def AppendMessageRowsToDataList(data_list, conversationId, advertId, advertTitle,
                                conversationPartyId, conversationPartyName, messagesJson):
    messages = json.loads(messagesJson)
    for message in messages:
        if message['sender'] == LOCAL_USER_INDICATOR:
            senderId = ''
            senderName = LOCAL_USER
            recipientId = conversationPartyId
            recipientName = conversationPartyName
        else:
            senderId = conversationPartyId
            senderName = conversationPartyName
            recipientId = ''
            recipientName = LOCAL_USER

        data_list.append((message['sortByDate'], conversationId, advertId, advertTitle, message['identifier'],
                          senderId, senderName, recipientId, recipientName, message['state'], message['text']))


@artifact_processor
def get_kijijiConversations(context):
    files_found = context.get_files_found()
    source_path = str(files_found[0])
    logfunc(f'Database file {source_path} is being interrogated...')

    data_list = []
    if does_table_exist_in_db(source_path, 'conversations'):
        db = open_sqlite_db_readonly(source_path)
        db.row_factory = sqlite3.Row  # For fetching columns by name
        cursor = db.cursor()
        cursor.execute(conversations_query)
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            conversationId = row['identifier']
            counterPartyInfo = json.loads(row['counterParty'])
            counterPartyId = counterPartyInfo["identifier"]
            counterPartyName = counterPartyInfo["name"]
            advertInfo = json.loads(row['ad'])
            advertId = advertInfo["identifier"]
            advertTitle = advertInfo["displayTitle"]

            AppendMessageRowsToDataList(data_list, conversationId, advertId, advertTitle,
                                        counterPartyId, counterPartyName, row['messages'])
    else:
        logfunc('The conversations table was not found in the database!')

    data_headers = ('Date Sent', 'Conversation ID', 'Ad ID', 'Ad Title', 'Message ID', 'Sender ID', 'Sender Name', 'Recipient ID', 'Recipient Name', 'State', 'Message')
    return data_headers, data_list, source_path
