# pylint: disable=W0702
__artifacts_v2__ = {
    "get_mewe_chat": {
        "name": "MeWe - Chat",
        "description": "Parses MeWe chat messages (timestamp, thread, user, message text, direction, type and attachments) from the MeWe chat database (app_database on older builds, app_v3.db on newer ones).",
        "author": "",
        "creation_date": "2021-11-10",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "MeWe",
        "notes": ("MeWe moved its chat store from 'app_database' to 'app_v3.db'; both are read. "
                  "Newer builds leave an empty 'mewe_old' database behind, which is skipped."),
        "paths": ('*/com.mewe/databases/app_database',
                  '*/com.mewe/databases/app_v3.db'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.mewe vc 90017000 | app_v3.db | 13 rows",
            "pixel7a_a14": "Android 14 | com.mewe vc 80116099 | app_v3.db | 18 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread Id",
                "conversationLabelColumn": "Thread Name",
                "textColumn": "Message Text",
                "directionColumn": "Message Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "User Name"
            }
        },
    },
    "get_mewe_session": {
        "name": "MeWe - SGSession",
        "description": "Parses MeWe session preferences (key and value) from the SGSession.xml file.",
        "author": "",
        "creation_date": "2021-11-10",
        "last_update_date": "2021-11-10",
        "requirements": "none",
        "category": "MeWe",
        "notes": "",
        "paths": ('*/com.mewe/shared_prefs/SGSession.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "key",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.mewe vc 90017000 | 27 rows",
            "pixel7a_a14": "Android 14 | com.mewe vc 80116099 | 25 rows",
        },
    }
}

import datetime
import re
import sqlite3
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc, \
    does_column_exist_in_db, does_table_exist_in_db

# Module-level constants (kept for backwards-compatibility; snapchat.py imports APP_NAME)
APP_NAME = 'MeWe'
DB_NAME = 'app_database'
# MeWe renamed the chat store to app_v3.db. Both carry the same CHAT_MESSAGE /
# CHAT_THREAD shape, so one query serves both; only the filename changed. Newer
# builds also leave a 'mewe_old' database in place, but it holds no chat tables.
DB_NAME_V3 = 'app_v3.db'
DB_NAMES = (DB_NAME, DB_NAME_V3)
SGSESSION_FILE = 'SGSession.xml'

# Column availability is probed rather than assumed: the two database
# generations were seen in the wild years apart, and only app_v3.db is covered
# by a test image, so a missing column must degrade to a blank cell instead of
# failing the whole artifact.
OPTIONAL_COLUMNS = {
    'threadName': ('CHAT_THREAD', 'name'),
    'groupId': ('CHAT_THREAD', 'groupId'),
    'chatType': ('CHAT_THREAD', 'chatType'),
    'ownerId': ('CHAT_MESSAGE', 'ownerId'),
    'ownerName': ('CHAT_MESSAGE', 'ownerName'),
    'textPlain': ('CHAT_MESSAGE', 'textPlain'),
    'attachmentType': ('CHAT_MESSAGE', 'attachmentType'),
    'attachmentName': ('CHAT_MESSAGE', 'attachmentName'),
    'deleted': ('CHAT_MESSAGE', 'deleted'),
    'currentUserMessage': ('CHAT_MESSAGE', 'currentUserMessage'),
}


def _column_or_null(db_path, key):
    """Qualified column reference if the schema has it, else a NULL placeholder."""
    table, column = OPTIONAL_COLUMNS[key]
    if does_column_exist_in_db(db_path, table, column):
        return f'{table}.{column}'
    return 'NULL'


def _build_chat_query(db_path):
    """Assemble the chat query for whichever schema generation this database is."""
    threadName = _column_or_null(db_path, 'threadName')
    groupId = _column_or_null(db_path, 'groupId')
    chatType = _column_or_null(db_path, 'chatType')
    ownerId = _column_or_null(db_path, 'ownerId')
    ownerName = _column_or_null(db_path, 'ownerName')
    textPlain = _column_or_null(db_path, 'textPlain')
    attachmentType = _column_or_null(db_path, 'attachmentType')
    attachmentName = _column_or_null(db_path, 'attachmentName')
    deleted = _column_or_null(db_path, 'deleted')
    currentUserMessage = _column_or_null(db_path, 'currentUserMessage')

    return f'''
    SELECT
        CHAT_MESSAGE.createdAt,
        CHAT_MESSAGE.threadId,
        {threadName},
        {groupId},
        {chatType},
        {ownerId},
        {ownerName},
        {textPlain},
        CASE {currentUserMessage} WHEN 1 THEN 'Sent' ELSE 'Received' END,
        CASE {attachmentType} WHEN 'UNSUPPORTED' THEN '' ELSE {attachmentType} END,
        {attachmentName},
        CASE {deleted} WHEN 1 THEN 'YES' ELSE 'NO' END
    FROM CHAT_MESSAGE
    JOIN CHAT_THREAD ON CHAT_MESSAGE.threadId = CHAT_THREAD.id
    ORDER BY CHAT_MESSAGE.createdAt
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
def get_mewe_chat(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith(DB_NAMES):
            continue
        # Newer installs keep an empty 'mewe_old' alongside app_v3.db, and a
        # database can be present without ever having held a chat.
        if not does_table_exist_in_db(file_found, 'CHAT_MESSAGE'):
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute(_build_chat_query(file_found))
            rows = cursor.fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Could not read MeWe chats from {file_found}: {ex}')
            rows = []
        db.close()

        if rows:
            sources.append(file_found)
        for row in rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]), datetime.timezone.utc) if row[0] else ''
            # Columns absent from this schema generation come back as NULL; report
            # them as empty cells rather than the string "None".
            values = tuple('' if value is None else value for value in row[1:])
            data_list.append((timestamp,) + values)

    source_path = ', '.join(sources)
    data_headers = (('Timestamp', 'datetime'), 'Thread Id', 'Thread Name', 'Group Id', 'Chat Type',
                    'User Id', 'User Name', 'Message Text', 'Message Direction', 'Message Type',
                    'Attachment Name', 'Deleted')
    return data_headers, data_list, source_path


@artifact_processor
def get_mewe_session(context):
    files_found = context.get_files_found()
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
