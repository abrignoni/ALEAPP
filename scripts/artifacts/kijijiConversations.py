# Kijiji Conversations
# Author:  Terry Chabot (Krypterry)
# Version: 1.0.2
# Kijiji App Version Tested: v17.5.0b172 (2022-05-06)
# Requirements:  None
#
#   Description:
#   Obtains individual chat messages that were sent and received using the Kijiji application.
#
#   Additional Info:
#       Kijiji.ca is a Canadian online classified advertising website and part of eBay Classifieds Group, with over 16 million unique visitors per month.
#
#       Kijiji, May 2022 <https://help.kijiji.ca/helpdesk/basics/what-is-kijiji>
#       Wikipedia - The Free Encyclopedia, May 2022, <https://en.wikipedia.org/wiki/Kijiji>
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, open_sqlite_db_readonly, does_table_exist_in_db

LOCAL_USER = 'Local User'
LOCAL_USER_INDICATOR = 'ME'

conversations_query = \
'''
    SELECT
        identifier,
        ad,
        counterParty,
        messages
    FROM conversations
    ORDER BY sortByDate ASC;
'''

def get_kijijiConversations(files_found, report_folder, seeker, wrap_text):
    file_found = str(files_found[0])
    logfunc(f'Database file {file_found} is being interrogated...')
    db = open_sqlite_db_readonly(file_found)
    db.row_factory = sqlite3.Row # For fetching columns by name
    tabCheck = does_table_exist_in_db(file_found, 'conversations')
    if tabCheck == False:
        logfunc('The conversations table was not found in the database!')
        return False

    cursor = db.cursor()
    cursor.execute(conversations_query)
    all_rows = cursor.fetchall()
    if len(all_rows) > 0:
        report = ArtifactHtmlReport('Kijiji Conversations')
        report.start_artifact_report(report_folder, 'Kijiji Conversations')
        report.add_script()

        data_headers = ('Date Sent', 'Conversation ID', 'Ad ID', 'Ad Title', 'Message ID', 'Sender ID', 'Sender Name', 'Recipient ID', 'Recipient Name', 'State', 'Message')
        data_list = []
        for row in all_rows:
            # Each row is for a conversation thread, with JSON for the individual message data.
            conversationId = row['identifier']
            
            # Determine the counter party for the conversation thread.
            counterPartyJson = row['counterParty']
            counterPartyInfo = json.loads(counterPartyJson)
            counterPartyId = counterPartyInfo["identifier"]
            counterPartyName = counterPartyInfo["name"]
            messagesJson = row['messages']

            advertJson = row['ad']
            advertInfo = json.loads(advertJson)
            advertId = advertInfo["identifier"]
            advertTitle = advertInfo["displayTitle"]

            AppendMessageRowsToDataList(data_list,
                conversationId,
                advertId,
                advertTitle,
                counterPartyId,
                counterPartyName,
                messagesJson)

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Kijiji Conversations'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Kijiji Conversations data was found.')

    db.close()
    return True

# Appends a row for each message sent in a unique conversation thread.
#  Row ordinal: Date Sent, Message ID, Sender ID, Sender Name, Recipient ID, Recipient Name, State, Message
def AppendMessageRowsToDataList(data_list, 
    conversationId, 
    advertId,
    advertTitle,    
    conversationPartyId,
    conversationPartyName, 
    messagesJson):
    messages = json.loads(messagesJson)
    for message in messages:
        # Determine sender (local user or counter party)
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

        data_list.append((message['sortByDate'], conversationId, advertId, advertTitle, message['identifier'], senderId, senderName, recipientId, recipientName, message['state'], message['text']))

__artifacts__ = {
        "kijijiConversations": (
                "Kijiji Conversations",
                ('*/com.ebay.kijiji.ca/databases/messageBoxDatabase.*'),
                get_kijijiConversations)
}