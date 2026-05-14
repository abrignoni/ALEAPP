# Tested with the following versions:
# 2024-08-16: Android 14, App: 4.1.966
# 2025-02-07: Android 16, App: 4.1.1166

# Requirements:  json, xml


__artifacts_v2__ = {

    
    "linkedin_account": {
        "name": "LinkedIn - Account",
        "description": "Existing account in LinkedIn App. The Public Identifier can be used to visit the public profile on the LinkedIn Website (https://www.linkedin.com/in/[Public Identifier]).",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.1",
        "creation_date": "2025-04-26",
        'last_update_date': '2026-02-07',
        "requirements": "xml, json",
        "category": "LinkedIn",
        "notes": "",
        "paths": ('*/com.linkedin.android/shared_prefs/linkedInPrefsName.xml'),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "linkedin_messages": {
        "name": "LinkedIn - Messages",
        "description": "Messages sent and received from LinkedIn App",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.2",
        'creation_date': '2025-04-26',
        'last_update_date': '2026-05-14',
        "requirements": "",
        "category": "LinkedIn",
        "notes": "",
        "paths": ('*/com.linkedin.android/databases/messenger-sdk*'),
        "output_types": "standard",
        "data_views": {
            "chat": {
                "directionSentValue": 1,
                "threadDiscriminatorColumn": "Conversation Urn",
                "textColumn": "Message",
                "directionColumn": "Sent",
                "timeColumn": "Delivery Date",
                "senderColumn": "Sender Name",
                "threadLabelColumn": "Conversation Label"
            }
        },
        "artifact_icon": "message-square"
    }
}



import json
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records

@artifact_processor
def linkedin_account(files_found, _report_folder, _seeker, _wrap_text):
    
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
    data_list = [(last_login, member_id, account_mail, last_name, first_name, headline, public_identifier)]

    data_headers = (    
                        ('Last Login', 'datetime'),
                        'Member ID',
                        'Account Mail',
                        'Last Name',
                        'First Name',
                        'Headline',
                        'Public Identifier'
                    )

    return data_headers, data_list, files_found[0]



@artifact_processor
def linkedin_messages(files_found, _report_folder, _seeker, _wrap_text):
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]

    query = ('''
            SELECT
            md.deliveredAt[deliveredAt],
            CASE WHEN md.status = '5' 
                THEN 'Delivered'
                ELSE 'Unknown'
            END[Status],
            concat(json_extract(pd.entityData, '$.participantType.member.firstName.text'), ' ',  json_extract(pd.entityData, '$.participantType.member.lastName.text')) [Sender Name],
            json_extract(pd.entityData, '$.participantType.member.headline.text') [Sender Headline],
            json_extract(pd.entityData, '$.participantType.member.profileUrl') [Sender Profile URL],
            json_extract(pd.entityData, '$.participantType.member.distance') [Sender Distance],
            json_extract(md.entityData, '$.subject') [Subject],
            json_extract(md.entityData, '$.body.text') [Message],
            md.conversationUrn [Conversation Urn],
            CASE WHEN json_extract(pd.entityData, '$.participantType.member.distance') = 'SELF'
                THEN 1
                ELSE 0
            END [SENT],
            CASE 
                WHEN json_extract(cd.entityData, '$.groupChat') = 1
                THEN COALESCE(
                    json_extract(cd.entityData, '$.name'),
                    (
                        SELECT 
                            json_extract(p2.entityData, '$.participantType.member.firstName.text') || ' ' ||
                            json_extract(p2.entityData, '$.participantType.member.lastName.text') ||
                            ' +' || (COUNT(*) - 1) || ' others'
                        FROM ConversationParticipantCrossRef cp2
                        JOIN ParticipantsData p2 ON p2.entityUrn = cp2.participantUrn
                        WHERE cp2.conversationUrn = md.conversationUrn
                        AND json_extract(p2.entityData, '$.participantType.member.distance') != 'SELF'
                    )
                )
                ELSE (
                    SELECT 
                        json_extract(p2.entityData, '$.participantType.member.firstName.text') || ' ' ||
                        json_extract(p2.entityData, '$.participantType.member.lastName.text')
                    FROM ConversationParticipantCrossRef cp2
                    JOIN ParticipantsData p2 ON p2.entityUrn = cp2.participantUrn
                    WHERE cp2.conversationUrn = md.conversationUrn
                    AND json_extract(p2.entityData, '$.participantType.member.distance') != 'SELF'
                    LIMIT 1
                )
            END [Conversation Label]
            FROM MessagesData md
            JOIN ConversationsData cd ON cd.entityUrn = md.conversationUrn
            LEFT JOIN ParticipantsData pd on pd.entityUrn = md.senderUrn
    ''')
    db_records = get_sqlite_db_records(str(files_found[0]), query)

    data_list = []
    for row in db_records:
        delivery_date = convert_unix_ts_to_utc(int(row[0])/1000)
        delivery_status = row[1]
        sender_name = row[2]
        sender_headline = row[3]
        sender_profile_url = row[4]
        sender_distance = row[5]
        subject = row[6]
        message = row[7]
        conversationurn = row[8]
        sent = row[9]
        conversation_label = row[10]

        data_list.append(   (delivery_date,
                            delivery_status,
                            sender_name,
                            sender_headline,
                            sender_profile_url,
                            sender_distance,
                            subject,
                            message,
                            conversationurn,
                            sent,
                            conversation_label)
                        )

    data_headers = (    ('Delivery Date', 'datetime'),
                        'Delivery Status',
                        'Sender Name',
                        'Sender Headline',
                        'Sender Profile Url',
                        'Sender Distance',
                        'Subject',
                        'Message',
                        'Conversation Urn',
                        'Sent',
                        'Conversation Label'
                    )

    return data_headers, data_list, files_found[0]