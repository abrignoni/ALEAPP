__artifacts_v2__ = {
    "get_kijijiConversations": {
        "name": "kijijiConversations",
        "description": "Kijiji messages from the conversations table of messageBoxDatabase, one row per message.",
        "author": "Terry Chabot (Krypterry), @AlexisBrignoni, Codex",
        "creation_date": "2022-05-13",
        "last_update_date": "2026-10-04",
        "requirements": "None",
        "category": "Kijiji",
        "notes": "Each conversations row stores its messages as a JSON list; one row is reported per list item. "
                 "sortByDate (as stored) is the message's sortByDate value, unchanged; its unit, its time zone and "
                 "what it marks are not established here, so it is not converted. "
                 "Sender (as stored) is the message's sender value, unchanged. Sender Is ME is Yes when that value "
                 "is the text ME and No otherwise. No source was found for what ME or any other sender value means, "
                 "so the module does not name a sender or a recipient. Counterparty ID and Counterparty Name come "
                 "from the conversation row's counterParty value and are the same on every message of a "
                 "conversation; they do not say who sent a message. State is the message's state value as stored. "
                 "No registered Android corpus holds this database (44 checked on 2026-10-04), so the columns are "
                 "described from the code and were not measured on data.",
        "paths": ('*/com.ebay.kijiji.ca/databases/messageBoxDatabase.*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
    }
}

import json
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, does_table_exist_in_db

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
        # The sender value is reported as stored. Only the value 'ME' is flagged; what any
        # other value means is not established, so no sender or recipient is named.
        sender = message['sender']
        senderIsMe = 'Yes' if sender == LOCAL_USER_INDICATOR else 'No'

        data_list.append((message['sortByDate'], conversationId, advertId, advertTitle, message['identifier'],
                          sender, senderIsMe, conversationPartyId, conversationPartyName,
                          message['state'], message['text']))


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

    data_headers = ('sortByDate (as stored)', 'Conversation ID', 'Ad ID', 'Ad Title', 'Message ID', 'Sender (as stored)', 'Sender Is ME', 'Counterparty ID', 'Counterparty Name', 'State', 'Message')
    return data_headers, data_list, source_path
