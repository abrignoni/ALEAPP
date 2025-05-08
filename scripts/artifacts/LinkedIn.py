# LinkedIn App (com.linkedin.android)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2024-08-16: Android 14, App: 4.1966

# Requirements:  json, xml


__artifacts_v2__ = {

    
    "get_linkedin_account": {
        "name": "LinkedIn - Account",
        "description": "Existing account in LinkedIn App. The Public Identifier can be used to visit the public profile on the LinkedIn Website (https://www.linkedin.com/in/[Public Identifier]).",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2025-04-26",
        "requirements": "xml",
        "category": "LinkedIn",
        "notes": "",
        "paths": ('*/com.linkedin.android/shared_prefs/linkedInPrefsName.xml'),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "get_linkedin_messages": {
        "name": "LinkedIn - Messages",
        "description": "Messages sent and received from LinkedIn App",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2025-04-26",
        "requirements": "",
        "category": "LinkedIn",
        "notes": "",
        "paths": ('*/com.linkedin.android/databases/messenger-sdk*'),
        "output_types": "standard",
        "artifact_icon": "message-square"
    }
}


import json
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records

@artifact_processor
def get_linkedin_account(files_found, report_folder, seeker, wrap_text):
    
    # Get data from xml into a dict to work with
    xml_dict = {}
    with open(files_found[0], 'rb') as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for elem in root:
            name = elem.attrib.get('name')

            if elem.tag == 'set':
                # Gather all child elements' text into a list
                values = [child.text for child in elem if child.text is not None]
                xml_dict[name] = values
            else:
                # Prefer value attribute, fallback to text
                value = elem.attrib.get('value') if 'value' in elem.attrib else elem.text
                xml_dict[name] = value

    # Now get the data from the dict and put it into the data_list
    last_login =  convert_unix_ts_to_utc(int(xml_dict['lastLoggedInTimestamp']))
    account_mail = xml_dict['memberEmail']
    temp_meModel = json.loads(xml_dict['meModel'])
    member_id = temp_meModel['plainId']
    last_name = temp_meModel['miniProfile']['lastName']
    first_name = temp_meModel['miniProfile']['firstName']
    headline = temp_meModel['miniProfile']['occupation']
    public_identifier = temp_meModel['miniProfile']['publicIdentifier']
    data_list = [(last_login, member_id, last_name, first_name, headline, public_identifier)]

    data_headers = ('Last Login', 'Member ID', 'Last Name', 'First Name', 'Headline', 'Public Identifier')

    return data_headers, data_list, files_found[0]



@artifact_processor
def get_linkedin_messages(files_found, report_folder, seeker, wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    query = ('''
            SELECT
            strftime('%Y-%m-%d %H:%M:%S.', "md"."deliveredAt"/1000, 'unixepoch') || ("md"."deliveredAt"%1000) [deliveredAt],
            CASE WHEN md.status = '5' 
                THEN 'Delivered'
                ELSE 'Unknown'
            END[Status],
            json_extract(pd.entityData, '$.participantType.member.firstName.text') [sender_firstname],
            json_extract(pd.entityData, '$.participantType.member.lastName.text') [sender_lastname],
            json_extract(pd.entityData, '$.participantType.member.headline.text') [sender_headline],
            json_extract(pd.entityData, '$.participantType.member.profileUrl') [sender_profile_url],
            json_extract(pd.entityData, '$.participantType.member.distance') [sender_distance],
            json_extract(md.entityData, '$.subject') [subject],
            json_extract(md.entityData, '$.body.text') [message],
            md.conversationUrn [conversationUrn]
            FROM MessagesData md
            JOIN ConversationsData cd ON cd.entityUrn = md.conversationUrn
            LEFT JOIN ParticipantsData pd on pd.entityUrn = md.senderUrn
    ''')
    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        delivery_date = row[0]
        delivery_status = row[1]
        sender_firstname = row[2]
        sender_lastname = row[3]
        sender_headline = row[4]
        sender_profile_url = row[5]
        sender_distance = row[6]
        subject = row[7]
        message = row[8]
        conversationurn = row[9]

        data_list.append((delivery_date, delivery_status, sender_firstname, sender_lastname, sender_headline, sender_profile_url, sender_distance, subject, message, conversationurn))

    data_headers = ('Delivery Date', 'Delivery Status', 'Sender First Name', 'Sender Last Name', 'Sender Headline', 'Sender Profile Url', 'Sender Distance', 'Subject', 'Message', 'Conversation Urn')

    return data_headers, data_list, files_found[0]