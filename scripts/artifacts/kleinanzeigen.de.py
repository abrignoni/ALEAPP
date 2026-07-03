# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_kleinanzeigenaccount": {
        "name": "kleinanzeigen.de App - Account Details",
        "description": "Extracts Account Details",
        "author": "@BrunoFischerGermany",
        "creation_date": "2024-04-02",
        "last_update_date": "2024-04-02",
        "requirements": "none",
        "category": "kleinanzeigen.de App",
        "notes": "",
        "paths": ('*/com.ebay.kleinanzeigen/shared_prefs/com.ebay.kleinanzeigen_preferences.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "shopping-bag",
    },
    "get_kleinanzeigenrecentsearchescache": {
        "name": "kleinanzeigen.de - Recent Searches Cache",
        "description": "Extracts Recent Searches Cache",
        "author": "@BrunoFischerGermany",
        "creation_date": "2024-04-02",
        "last_update_date": "2024-04-02",
        "requirements": "none",
        "category": "kleinanzeigen.de App",
        "notes": "",
        "paths": ('*/com.ebay.kleinanzeigen/files/RECENT_SEARCHES_CACHE',),
        "output_types": "standard",
        "artifact_icon": "shopping-bag",
    },
    "get_kleinanzeigennonresettablerecentsearchescache": {
        "name": "kleinanzeigen.de - Non resettable Recent Searches Cache",
        "description": "Extracts Recent Searches Cache",
        "author": "@BrunoFischerGermany",
        "creation_date": "2024-04-08",
        "last_update_date": "2024-04-08",
        "requirements": "none",
        "category": "kleinanzeigen.de App",
        "notes": "",
        "paths": ('*/com.ebay.kleinanzeigen/files/NON_RESETTABLE_RECENT_SEARCHES_CACHE',),
        "output_types": "standard",
        "artifact_icon": "shopping-bag",
    },
    "get_kleinanzeigenmessagebox": {
        "name": "kleinanzeigen.de - Messagebox",
        "description": "Extracts conversation summaries from the message database",
        "author": "@BrunoFischerGermany",
        "creation_date": "2024-04-13",
        "last_update_date": "2024-04-13",
        "requirements": "none",
        "category": "kleinanzeigen.de App",
        "notes": "",
        "paths": ('*com.ebay.kleinanzeigen/databases/messageBoxDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "shopping-bag",
    },
    "get_kleinanzeigenmessages": {
        "name": "kleinanzeigen.de - Messages",
        "description": "Extracts individual messages from the message database",
        "author": "@BrunoFischerGermany",
        "creation_date": "2024-04-13",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "kleinanzeigen.de App",
        "notes": "",
        "paths": ('*com.ebay.kleinanzeigen/databases/messageBoxDatabase.db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Counterparty",
                "conversationLabelColumn": "Counterparty",
                "textColumn": "Message Text",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Counterparty",
                "sentMessageStaticLabel": "Local User"
            }
        },
    }
}

import datetime
import json

import xmltodict

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _iso_to_utc(value):
    if not value:
        return ''
    try:
        dt = datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt.astimezone(datetime.timezone.utc)
    except (ValueError, TypeError):
        return value


def _recent_searches(files_found, marker):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if marker not in file_found:
            continue
        source_path = file_found
        with open(file_found, encoding='utf-8') as fd:
            json_data = json.load(fd)
        for entry in json_data:
            data_list.append((entry.get('searchTerm', ''),
                              entry.get('category', {}).get('localizedName', ''),
                              _ms_to_utc(entry.get('termSearchTimestamp'))))
    return data_list, source_path


@artifact_processor
def get_kleinanzeigenrecentsearchescache(files_found, report_folder, seeker, wrap_text):
    data_list, source_path = _recent_searches(files_found, 'RECENT_SEARCHES_CACHE')
    data_headers = ('Search Term', 'Category', ('Search Timestamp', 'datetime'))
    return data_headers, data_list, source_path


@artifact_processor
def get_kleinanzeigennonresettablerecentsearchescache(files_found, report_folder, seeker, wrap_text):
    data_list, source_path = _recent_searches(files_found, 'NON_RESETTABLE_RECENT_SEARCHES_CACHE')
    data_headers = ('Search Term', 'Category', ('Search Timestamp', 'datetime'))
    return data_headers, data_list, source_path


@artifact_processor
def get_kleinanzeigenaccount(files_found, report_folder, seeker, wrap_text):
    keys = ['USERPROFILE_NAME_KEY', 'USERPROFILE_INITIALS', 'LAST_EMAIL_USED', 'AUTH_USER_EMAIL', 'AUTH_USER_ID',
            'USERPROFILE_PHONE_NUMBER_KEY', 'USERPROFILE_ACCOUNT_TYPE_KEY', 'USERPROFILE_USER_SINCE_DATE_KEY',
            'USERPROFILE_LOCATION_LONGITUDE_KEY', 'USERPROFILE_LOCATION_LATITUDE_KEY']
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if 'com.ebay.kleinanzeigen_preferences.xml' not in file_found:
            continue
        source_path = file_found
        with open(file_found, encoding='utf-8') as fd:
            xml_dict = xmltodict.parse(fd.read())
        string_dict = xml_dict.get('map', {}).get('string', [])
        values = {item.get('@name'): item.get('#text', '') for item in string_dict}
        row = [values.get(k, '') for k in keys]
        row[7] = _iso_to_utc(row[7])  # USERPROFILE_USER_SINCE_DATE_KEY (ISO 8601)
        data_list.append(tuple(row))

    data_headers = ('Account Profile Name', 'Account Profile Initials', 'Account Last Used Email Address',
                    'Account Authenticated Email Address', 'Account User Id', ('Account Phone Number', 'phonenumber'),
                    'Account Type', ('Account Registered since', 'datetime'), 'Saved Location Longitude', 'Saved Location Latitude')
    return data_headers, data_list, source_path


def _messagebox_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('messageBoxDatabase.db'):
            return file_found
    return ''


@artifact_processor
def get_kleinanzeigenmessagebox(files_found, report_folder, seeker, wrap_text):
    source_path = _messagebox_db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT json_extract(conversations.counterParty, '$.name'),
                json_extract(conversations.ad, '$.displayTitle'),
                json_extract(conversations.ad, '$.identifier'),
                json_array_length(conversations.messages),
                conversations.sortByDate,
                json_extract(conversations.counterParty, '$.identifier')
                FROM conversations ORDER BY sortByDate DESC
            ''')
            rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            rows = []
        db.close()
        for r in rows:
            data_list.append((r[0], r[1], r[2], r[3], _ms_to_utc(r[4]), r[5]))

    data_headers = ('Counterparty', 'Ad Title', 'Ad Number', 'Number of Messages', ('Last Message Time', 'datetime'), 'Counterparty Identifier')
    return data_headers, data_list, source_path


@artifact_processor
def get_kleinanzeigenmessages(files_found, report_folder, seeker, wrap_text):
    source_path = _messagebox_db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT json_extract(conversations.counterParty, '$.name'),
                json_extract(conversations.ad, '$.displayTitle'),
                json_extract(conversations.ad, '$.identifier'),
                messages
                FROM conversations ORDER BY sortByDate DESC
            ''')
            rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            rows = []
        db.close()
        for r in rows:
            try:
                messages = json.loads(r[3]) if r[3] else []
            except (ValueError, TypeError):
                messages = []
            for message in messages:
                direction = 'Outgoing' if message.get('sender') == 'ME' else 'Incoming'
                data_list.append((_iso_to_utc(message.get('sortByDate')), r[0], r[1], r[2],
                                  message.get('text', ''), direction, str(message.get('state', '')).lower()))

    data_headers = (('Timestamp', 'datetime'), 'Counterparty', 'Ad Title', 'Ad Number', 'Message Text', 'Direction', 'Message State')
    return data_headers, data_list, source_path
