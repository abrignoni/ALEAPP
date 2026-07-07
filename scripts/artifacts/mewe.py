# pylint: disable=W0613,W0702
__artifacts_v2__ = {
    "get_mewe_chat": {
        "name": "MeWe - Chat",
        "description": "",
        "author": "",
        "creation_date": "2021-11-10",
        "last_update_date": "2026-07-07",
        "requirements": "none",
        "category": "MeWe",
        "notes": "",
        "paths": ('*/com.mewe/databases/app_v3.db',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "get_mewe_session": {
        "name": "MeWe - SGSession",
        "description": "",
        "author": "",
        "creation_date": "2021-11-10",
        "last_update_date": "2021-11-10",
        "requirements": "none",
        "category": "MeWe",
        "notes": "",
        "paths": ('*/com.mewe/shared_prefs/SGSession.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "key",
    }
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc

# Module-level constants (kept for backwards-compatibility; snapchat.py imports APP_NAME)
APP_NAME = 'MeWe'
DB_NAME = 'app_v3.db'
SGSESSION_FILE = 'SGSession.xml'

CHAT_MESSAGES_QUERY = '''
    SELECT
        createdAt,
        threadId,
        groupId,
        ownerId,
        ownerName,
        textPlain,
        CASE currentUserMessage WHEN 1 THEN "Sent" ELSE "Received" END currentUserMessage,
        CASE attachmentType WHEN "UNSUPPORTED" THEN '' ELSE attachmentType END attachmentType,
        attachmentName,
        CASE deleted WHEN 1 THEN "YES" ELSE "NO" END deleted
    FROM CHAT_MESSAGE
    JOIN CHAT_THREAD ON threadId = CHAT_THREAD.id
'''


INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_xml(file_found):
    """Parse XML, recovering from invalid tokens / unescaped ampersands; empty element if unparseable."""
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


@artifact_processor
def get_mewe_chat(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(DB_NAME):
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute(CHAT_MESSAGES_QUERY)
            rows = cursor.fetchall()
        except:
            rows = []
        db.close()

        for row in rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]), datetime.timezone.utc) if row[0] else ''
            data_list.append((timestamp, row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                              row[8] if row[8] else '', row[9]))

    data_headers = (('Timestamp', 'datetime'), 'Thread Id', 'Thread Name', 'User Id', 'User Name',
                    'Message Text', 'Message Direction', 'Message Type', 'Attachment Name', 'Deleted')
    return data_headers, data_list, source_path


@artifact_processor
def get_mewe_session(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(SGSESSION_FILE):
            continue

        source_path = file_found
        root = _parse_xml(file_found)
        for node in root:
            if '.' in node.attrib['name']:
                continue  # skip not relevant keys
            try:
                value = node.attrib['value']
            except:
                value = node.text
            data_list.append((node.attrib['name'], value))

    data_headers = ('Key', 'Value')
    return data_headers, data_list, source_path
