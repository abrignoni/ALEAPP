__artifacts_v2__ = {
    "adobe_reader_account": {
        "name": "Adobe Acrobat Reader - Account",
        "description": "Parses the signed in Adobe account recorded by the Acrobat Reader "
                       "Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Adobe Acrobat Reader",
        "notes": "Read from the app's shared preferences. FoundationMigrated.xml holds the "
                 "account identity as plain text values. AccessTokenExpiration is a Unix "
                 "millisecond value stored as a string. Account type, service level and the "
                 "entitlement and subscription flags from the services account preferences "
                 "are reported as stored. An entitlement flag records what the account was "
                 "provisioned for and does not establish that the service was used. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": (
            '*/com.adobe.reader/shared_prefs/FoundationMigrated.xml',
            '*/com.adobe.reader/shared_prefs/Foundation.xml',
            '*/com.adobe.reader/shared_prefs/com.adobe.reader.account_type.xml',
            '*/com.adobe.reader/shared_prefs/com.adobe.libs.services.auth.SVServicesAccount.cloud.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "adobe_reader_recent_files": {
        "name": "Adobe Acrobat Reader - Recent Files",
        "description": "Parses the per path open history recorded by the Acrobat Reader "
                       "Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Adobe Acrobat Reader",
        "notes": "Read from ARRecentFileEntity in com.adobe.reader.ARRecentDatabase, which "
                 "keys one row per file path. lastOpenTime is Unix milliseconds: read as "
                 "seconds the column lands beyond the year 57000, and read as milliseconds "
                 "it lands in the same 2024 to 2026 range as the other stores in the sample. "
                 "fileOpenCount is the counter the app keeps for that path and is reported as "
                 "stored. The database is read twice, once with the write ahead log applied "
                 "and once with immutable=1 to ignore it, and rows whose primary key appears "
                 "only in the pre checkpoint read are reported with Record Source naming that "
                 "read. A row missing from the committed read may have been removed by the "
                 "app or rewritten; the reason is not recorded. A path listed here does not "
                 "establish that the file is still present on the device. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/com.adobe.reader/databases/com.adobe.reader.ARRecentDatabase*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "file-text"
    },
    "adobe_reader_documents": {
        "name": "Adobe Acrobat Reader - Documents",
        "description": "Parses the document list and per document view state recorded by the "
                       "Acrobat Reader Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Adobe Acrobat Reader",
        "notes": "Read from ARRecentsFileTable, joined to ARRecentsSharedTable on the row id "
                 "the schema declares as the foreign key. last_access is an ISO 8601 string "
                 "and appeared in three spellings in the tested sample, with and without a "
                 "trailing Z and with or without a fractional second, so it is parsed "
                 "tolerantly. The shared dates are also ISO 8601 and carried one, two or "
                 "three fractional digits. doc_source, viewMode and cloudSource are integers "
                 "with no mapping recoverable from the extraction, so they are reported as "
                 "stored; doc_source held 0 and 8 and viewMode held 0 and 1 in the tested "
                 "sample. Participant Count is the length of the mParticipantList JSON array, "
                 "which was an empty array on every shared row of the tested sample, so no "
                 "participant identities were available from this table. The pre checkpoint "
                 "read is compared against the committed read and rows found only in the "
                 "former are reported with Record Source naming that read. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/com.adobe.reader/databases/'
                  'com.adobe.reader.filebrowser.ARRecentsFileManager.ARRecentsFileDatabase*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "files"
    },
    "adobe_reader_thumbnails": {
        "name": "Adobe Acrobat Reader - Document Thumbnails",
        "description": "Parses the cached page thumbnails held by the Acrobat Reader Android "
                       "app and checks the images into the report.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Adobe Acrobat Reader",
        "notes": "Read from ARThumbnailTable. The thumbnail column holds a base64 encoded "
                 "image, PNG on every decoded row of the tested sample, and the decoded bytes "
                 "are checked in so the image renders in the report. The image is the "
                 "thumbnail the app cached and is not necessarily the current content of the "
                 "file. uniqueID is the key the app stores: it was a file system path on most "
                 "rows of the tested sample and a cloud asset identifier on the rest, and it "
                 "is reported as stored. Where that key matches a path in ARRecentFileEntity "
                 "the open count and last open time from that row are reported alongside, "
                 "which is a join on a recorded key rather than a correlation. Rows whose key "
                 "matches no such path are still reported, with those columns empty. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": (
            '*/com.adobe.reader/databases/com.adobe.reader.filebrowser.ARThumbnailDatabase*',
            '*/com.adobe.reader/databases/com.adobe.reader.ARRecentDatabase*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "photo"
    },
    "adobe_reader_comments": {
        "name": "Adobe Acrobat Reader - Comment Notifications",
        "description": "Parses the commenting notifications recorded by the Acrobat Reader "
                       "Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Adobe Acrobat Reader",
        "notes": "Read from ARBellNotificationEntity. Each row carries a JSON payload that "
                 "parsed on every row of the tested sample. timeStamp is Unix milliseconds. "
                 "The payload declares comment and comment_html members, and both were empty "
                 "strings on every row of the tested sample, so the Comment Text column is "
                 "blank there: these rows record that a comment was added or deleted, not the "
                 "text of the comment. The annotation type comes from the payload's "
                 "selector.subtype member and held highlight, underline and shape values. "
                 "Type, sub type and read state are reported as stored. The payload references "
                 "the document rendition as an https URL only, and no reproducible link to "
                 "cached bytes for these documents was found in the extraction, so no media is "
                 "checked in for this artifact. Author Name and Author User ID are the values "
                 "the notification payload carries for the account that acted. Field mapping "
                 "was done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/com.adobe.reader/databases/Notification.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-circle"
    },
    "adobe_reader_shared_documents": {
        "name": "Adobe Acrobat Reader - Shared Documents",
        "description": "Parses the shared document, review and send and track records held by "
                       "the Acrobat Reader Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Adobe Acrobat Reader",
        "notes": "Read from the app's services database, named database. Five tables are "
                 "reported and the Record Type column names the table each row came from. "
                 "modifiedDateAtDownload and updatedModifiedDate are Unix milliseconds and "
                 "both use -1 as an absent value, which is reported as an empty cell rather "
                 "than converted; 21 and 2 of the 48 rows of that table held -1 in the tested "
                 "sample. lastViewedPageNumber uses -1 the same way. Review type, asset type "
                 "and the favourite, shared, rooted and progress state flags are reported as "
                 "stored. The parcel records hold serialized JSON members for the resource, the "
                 "parcel and the privileges, which are not expanded here. Participant Count is "
                 "the length of the serialized participants member, which was NULL on every "
                 "parcel row of the tested sample, so that column is empty there. The parcel "
                 "table is also "
                 "read with immutable=1 and rows whose primary key appears only in that pre "
                 "checkpoint read are reported with Record Source naming it. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is recorded "
                 "for it.",
        "paths": ('*/com.adobe.reader/databases/database*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "share"
    },
    "adobe_reader_ai_conversations": {
        "name": "Adobe Acrobat Reader - AI Assistant Conversations",
        "description": "Parses the AI Assistant conversation records held by the Acrobat "
                       "Reader Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Adobe Acrobat Reader",
        "notes": "Read from DCMConversation in DCMQnAConversationDb, with the linked documents "
                 "resolved through DCMConversationAssetCrossRef into DCMAsset. The three "
                 "timestamp columns are Unix milliseconds, which their own column names state "
                 "and the decoded values agree with. The conversation name is the label the "
                 "app stored for the conversation. This database records conversation "
                 "identity, the documents attached to a conversation and asset change events; "
                 "every event row in the tested sample was of type ASSET_CHANGE_EVENT and none "
                 "carried question or answer text, so no message content is reported here and "
                 "the event count column counts those change events. Field mapping was done "
                 "against a private sample provided by Mattia; no sample data is recorded for "
                 "it.",
        "paths": ('*/com.adobe.reader/databases/DCMQnAConversationDb*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-2"
    },
    "adobe_reader_tool_usage": {
        "name": "Adobe Acrobat Reader - Tool Usage",
        "description": "Parses the in app tool invocations recorded by the Acrobat Reader "
                       "Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Adobe Acrobat Reader",
        "notes": "Read from tool_usage in nba_database. timestampInMs is Unix milliseconds. "
                 "toolId and eventType are stored as literal names rather than codes and are "
                 "reported as stored. docId is populated on some rows only and is the "
                 "identifier the app associated with the invocation. Field mapping was done "
                 "against a private sample provided by Mattia; no sample data is recorded for "
                 "it.",
        "paths": ('*/com.adobe.reader/databases/nba_database*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "tool"
    },
    "adobe_reader_document_cloud": {
        "name": "Adobe Acrobat Reader - Document Cloud",
        "description": "Parses the Document Cloud file, transfer, open document and share in "
                       "progress records held by the Acrobat Reader Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Adobe Acrobat Reader",
        "notes": "Four tables from three databases are reported and the Record Type column "
                 "names the table each row came from: ARFileInfo and ARCloudTransfer from "
                 "ARDatabase, OpenDocTable from the multi document database and "
                 "ARShareInProgressFileInfo from the share database. The transfer dates are "
                 "Unix milliseconds. Transfer type is stored as a literal name; transfer "
                 "status, document source and the upload and comment status integers have no "
                 "mapping recoverable from the extraction and are reported as stored. Each "
                 "database is read with the write ahead log applied and again with "
                 "immutable=1, and rows whose primary key appears only in the pre checkpoint "
                 "read are reported with Record Source naming that read; the open document and "
                 "share in progress tables were empty in the committed read of the tested "
                 "sample and their rows came from that comparison. Field mapping was done "
                 "against a private sample provided by Mattia; no sample data is recorded for "
                 "it.",
        "paths": (
            '*/com.adobe.reader/databases/ARDatabase*',
            '*/com.adobe.reader/databases/com.adobe.reader.multidoc.ARMultiDocDatabase*',
            '*/com.adobe.reader/databases/com.adobe.reader.share.ARShareDatabase*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud"
    },
}

import base64
import json
import os
import re
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    get_sqlite_db_path,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_FRACTION = re.compile(r'\.(\d+)')

_RECENT_DB = 'com.adobe.reader.ARRecentDatabase'
_RECENTS_DB = 'com.adobe.reader.filebrowser.ARRecentsFileManager.ARRecentsFileDatabase'
_THUMBNAIL_DB = 'com.adobe.reader.filebrowser.ARThumbnailDatabase'
_NOTIFICATION_DB = 'Notification.db'
_SERVICES_DB = 'database'
_QNA_DB = 'DCMQnAConversationDb'
_NBA_DB = 'nba_database'
_AR_DB = 'ARDatabase'
_MULTIDOC_DB = 'com.adobe.reader.multidoc.ARMultiDocDatabase'
_SHARE_DB = 'com.adobe.reader.share.ARShareDatabase'

_COMMITTED = 'Committed read'
_PRE_CHECKPOINT = 'Pre-checkpoint read only'


def _rows(source_path, sql):
    '''Rows for sql, with the write-ahead log applied. Empty on any SQLite error.'''
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if not db:
        return []
    cursor = db.cursor()
    try:
        rows = cursor.execute(sql).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Could not query {os.path.basename(source_path)}: {ex}')
        rows = []
    db.close()
    return rows


def _rows_pre_wal(source_path, sql):
    '''Rows for sql as of the file's last checkpoint, ignoring the write-ahead log.

    immutable=1 is strictly read-only. Unlike mode=ro it does not even create a -shm
    sidecar, so no evidence file is altered. Path handling goes through the same
    get_sqlite_db_path() that open_sqlite_db_readonly() uses, so Windows long paths and
    URI-special characters behave identically. A table created after the last checkpoint
    does not exist in this view, so an error here is expected rather than exceptional.
    '''
    if not source_path:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?immutable=1', uri=True)
    except sqlite3.Error:
        return []
    cursor = db.cursor()
    try:
        rows = cursor.execute(sql).fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _superseded(source_path, sql, key_indexes):
    '''Rows readable before the last checkpoint whose key is absent from the committed read.

    Keyed on the row's primary key rather than compared by count, because a table can hold
    the same number of rows in both reads with different rows in them.
    '''
    def key(row):
        return tuple(row[index] for index in key_indexes)

    committed = {key(row) for row in _rows(source_path, sql)}
    return [row for row in _rows_pre_wal(source_path, sql) if key(row) not in committed]


def _table_columns(source_path, table):
    '''The column names the file's own schema declares for table.'''
    return {row[1] for row in _rows(source_path, f'PRAGMA table_info(`{table}`)')}


def _select(source_path, table, columns, tail=''):
    '''A SELECT naming every column, substituting NULL for the ones this schema lacks.

    The app adds columns across releases, so a schema that predates one of them would
    otherwise fail the whole query. NULL AS <name> keeps the result shape and the column
    names identical either way, so callers can index by position.
    '''
    present = _table_columns(source_path, table)
    if not present:
        return ''
    select_list = ', '.join(
        f'`{column}`' if column in present else f'NULL AS `{column}`' for column in columns)
    return f'SELECT {select_list} FROM `{table}` {tail}'


def _databases(context, name, files=None):
    '''The matched files that are the named database itself, not its sidecars.'''
    return [path for path in unique_files(context, files)
            if os.path.basename(path) == name]


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent.

    Converted here rather than through convert_unix_ts_to_utc because these stores use -1
    and 0 as absent values. The shared helper sizes its input with math.log10, which raises
    on a value that is not positive, and it infers the unit from the value's magnitude
    rather than being told it. These columns are always milliseconds.
    '''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _iso(value):
    '''An ISO 8601 timestamp string as a UTC datetime, or '' when it will not parse.

    The fractional second is normalised to six digits first. These stores wrote one, two
    and three digits, and datetime.fromisoformat accepts an arbitrary count only from
    Python 3.11: on 3.10, which this repo still supports, a one or two digit fraction
    raises and the value would be silently dropped.
    '''
    if not value or not isinstance(value, str):
        return ''
    text = value.strip()
    if text.endswith(('Z', 'z')):
        text = f'{text[:-1]}+00:00'
    match = _FRACTION.search(text)
    if match:
        digits = match.group(1)[:6].ljust(6, '0')
        text = f'{text[:match.start()]}.{digits}{text[match.end():]}'
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return ''
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _json(value):
    '''value decoded as JSON, or None when it is absent or will not decode.'''
    if not value:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def _count(value):
    '''The length of a JSON array held in value, or '' when there is no array.'''
    decoded = _json(value)
    return len(decoded) if isinstance(decoded, list) else ''


def _prefs(source_path):
    '''name -> value for every entry in an Android shared preferences XML file.'''
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Could not parse {os.path.basename(source_path)}: {ex}')
        return {}
    values = {}
    for element in root:
        name = element.get('name')
        if not name:
            continue
        values[name] = element.text if element.tag == 'string' else element.get('value')
    return values


@artifact_processor
def adobe_reader_account(context):
    data_list = []
    sources = []
    prefs = {}

    for source_path in unique_files(context):
        name = os.path.basename(source_path)
        if not name.endswith('.xml'):
            continue
        entries = _prefs(source_path)
        if entries:
            prefs[name] = entries
            sources.append(source_path)

    identity = prefs.get('FoundationMigrated.xml', {})
    services = prefs.get(
        'com.adobe.libs.services.auth.SVServicesAccount.cloud.xml', {})
    account_type = prefs.get('com.adobe.reader.account_type.xml', {})
    device = prefs.get('Foundation.xml', {})

    if identity or services:
        entitlements = ', '.join(sorted(
            key for key, value in services.items()
            if str(value).lower() == 'true' and (
                key.endswith(('Entitlement_KEY', 'Subscribed_KEY', 'StatusKey')))))
        data_list.append((
            _ms(identity.get('AccessTokenExpiration')),
            identity.get('Email', ''),
            identity.get('DisplayName', ''),
            identity.get('FirstName', ''),
            identity.get('LastName', ''),
            identity.get('AdobeID', ''),
            identity.get('AuthID', ''),
            services.get('userID_KEY', ''),
            identity.get('AccountType', ''),
            identity.get('ServiceLevel', ''),
            identity.get('EmailVerified', ''),
            identity.get('CountryCode', '') or services.get('userCountryCode_KEY', ''),
            identity.get('OwnerOrg', ''),
            identity.get('EnterpriseInfo', ''),
            identity.get('Tags', ''),
            identity.get('idpFlow', ''),
            identity.get('DeviceName', ''),
            identity.get('DeviceId', '') or device.get('DeviceId', ''),
            account_type.get('accountRecordedSignIn', ''),
            services.get('totalSubscriptionCount', ''),
            entitlements,
            '\n'.join(dict.fromkeys(sources)),
        ))

    data_headers = (
        ('Access Token Expiration', 'datetime'),
        'Email',
        'Display Name',
        'First Name',
        'Last Name',
        'Adobe ID',
        'Auth ID',
        'Services User ID',
        'Account Type (as stored)',
        'Service Level (as stored)',
        'Email Verified (as stored)',
        'Country Code',
        'Owner Organisation',
        'Enterprise Info (as stored)',
        'Tags (as stored)',
        'Identity Provider Flow (as stored)',
        'Device Name',
        'Device ID',
        'Account Recorded Sign In (as stored)',
        'Total Subscription Count',
        'Entitlement Flags Set (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def adobe_reader_recent_files(context):
    data_list = []
    sources = []
    sql = 'SELECT `lastOpenTime`, `fileOpenCount`, `fileAddress` FROM `ARRecentFileEntity`'

    for source_path in _databases(context, _RECENT_DB):
        relative_path = context.get_relative_path(source_path)
        rows = [(row, _COMMITTED) for row in _rows(source_path, sql)]
        rows += [(row, _PRE_CHECKPOINT) for row in _superseded(source_path, sql, (2,))]
        for (last_open, open_count, file_address), record_source in rows:
            data_list.append((
                _ms(last_open),
                open_count,
                file_address,
                record_source,
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Last Opened', 'datetime'),
        'Open Count',
        'File Path',
        'Record Source',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def adobe_reader_documents(context):
    data_list = []
    sources = []
    file_columns = ('_id', 'fileName', 'filePath', 'fileMimeType', 'last_access',
                    'doc_source', 'cloudSource', 'cloudID', 'userID', 'favourite',
                    'readOnlyFile', 'pageNum', 'zoomLevel', 'viewMode',
                    'genAIConversationId', 'is_static')
    shared_columns = ('parentTableRowID', 'ownershipType', 'userStatus', 'state',
                      'parcelId', 'sharedDate', 'modifyDate', 'expireDate',
                      'mParticipantList', 'size', 'canEdit')

    for source_path in _databases(context, _RECENTS_DB):
        relative_path = context.get_relative_path(source_path)
        file_sql = _select(source_path, 'ARRecentsFileTable', file_columns)
        if not file_sql:
            continue
        shared_sql = _select(source_path, 'ARRecentsSharedTable', shared_columns)
        shared = {row[0]: row for row in _rows(source_path, shared_sql)} if shared_sql else {}

        rows = [(row, _COMMITTED) for row in _rows(source_path, file_sql)]
        rows += [(row, _PRE_CHECKPOINT) for row in _superseded(source_path, file_sql, (0,))]
        for row, record_source in rows:
            (row_id, file_name, file_path, mime_type, last_access, doc_source, cloud_source,
             cloud_id, user_id, favourite, read_only, page_num, zoom, view_mode,
             conversation_id, is_static) = row
            share = shared.get(row_id)
            data_list.append((
                _iso(last_access),
                _iso(share[6]) if share else '',
                _iso(share[5]) if share else '',
                _iso(share[7]) if share else '',
                file_name,
                file_path,
                mime_type,
                favourite,
                read_only,
                page_num,
                zoom,
                view_mode,
                doc_source,
                cloud_source,
                cloud_id,
                user_id,
                conversation_id,
                is_static,
                share[1] if share else '',
                share[2] if share else '',
                share[3] if share else '',
                share[4] if share else '',
                _count(share[8]) if share else '',
                share[9] if share else '',
                share[10] if share else '',
                record_source,
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Last Access', 'datetime'),
        ('Shared Modify Date', 'datetime'),
        ('Shared Date', 'datetime'),
        ('Share Expiry Date', 'datetime'),
        'File Name',
        'File Path',
        'MIME Type',
        'Favourite (as stored)',
        'Read Only (as stored)',
        'Page Number',
        'Zoom Level',
        'View Mode (as stored)',
        'Document Source (as stored)',
        'Cloud Source (as stored)',
        'Cloud ID',
        'User ID',
        'AI Conversation ID',
        'Is Static (as stored)',
        'Ownership Type (as stored)',
        'User Status (as stored)',
        'Share State (as stored)',
        'Parcel ID',
        'Participant Count',
        'Shared Size',
        'Can Edit (as stored)',
        'Record Source',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def adobe_reader_thumbnails(context):
    data_list = []
    sources = []
    files_found = unique_files(context)

    opened = {}
    for source_path in _databases(context, _RECENT_DB, files_found):
        for last_open, open_count, file_address in _rows(
                source_path,
                'SELECT `lastOpenTime`, `fileOpenCount`, `fileAddress` '
                'FROM `ARRecentFileEntity`'):
            opened[file_address] = (last_open, open_count)

    for source_path in _databases(context, _THUMBNAIL_DB, files_found):
        relative_path = context.get_relative_path(source_path)
        sql = _select(source_path, 'ARThumbnailTable',
                      ('uniqueID', 'thumbnail', 'thumbnailUrl'))
        if not sql:
            continue
        for unique_id, thumbnail, thumbnail_url in _rows(source_path, sql):
            media = ''
            if thumbnail:
                try:
                    # binascii.Error, which b64decode raises, subclasses ValueError.
                    decoded = base64.b64decode(thumbnail)
                except (ValueError, TypeError):
                    decoded = None
                    logfunc(f'Could not decode a thumbnail for {os.path.basename(source_path)}')
                if decoded:
                    name = os.path.basename(str(unique_id).rstrip('/')) or str(unique_id)
                    media = check_in_embedded_media(source_path, decoded, f'{name}.png')
            last_open, open_count = opened.get(unique_id, ('', ''))
            data_list.append((
                _ms(last_open) if last_open else '',
                media,
                unique_id,
                open_count,
                thumbnail_url or '',
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Last Opened', 'datetime'),
        ('Thumbnail', 'media'),
        'Document Identifier (as stored)',
        'Open Count',
        'Thumbnail URL',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def adobe_reader_comments(context):
    data_list = []
    sources = []

    for source_path in _databases(context, _NOTIFICATION_DB):
        relative_path = context.get_relative_path(source_path)
        sql = _select(source_path, 'ARBellNotificationEntity',
                      ('notificationID', 'timeStamp', 'type', 'subType', 'readState',
                       'payload'))
        if not sql:
            continue
        rows = [(row, _COMMITTED) for row in _rows(source_path, sql)]
        rows += [(row, _PRE_CHECKPOINT) for row in _superseded(source_path, sql, (0,))]
        for row, record_source in rows:
            notification_id, timestamp, kind, sub_type, read_state, payload = row
            body = _json(payload) or {}
            user = body.get('user') or {}
            asset = body.get('asset') or {}
            selector = body.get('selector') or {}
            data_list.append((
                _ms(timestamp),
                sub_type,
                selector.get('subtype', ''),
                body.get('comment', ''),
                user.get('name', ''),
                user.get('userId', ''),
                asset.get('name', ''),
                asset.get('mimeType', '') or body.get('mimetype', ''),
                asset.get('id', ''),
                read_state,
                kind,
                body.get('commentId', ''),
                notification_id,
                record_source,
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Timestamp', 'datetime'),
        'Event (as stored)',
        'Annotation Type (as stored)',
        'Comment Text',
        'Author Name',
        'Author User ID',
        'Document Name',
        'MIME Type',
        'Document ID',
        'Read State (as stored)',
        'Notification Type (as stored)',
        'Comment ID',
        'Notification ID',
        'Record Source',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def adobe_reader_shared_documents(context):
    data_list = []
    sources = []
    blank = ''

    for source_path in _databases(context, _SERVICES_DB):
        relative_path = context.get_relative_path(source_path)

        meta_sql = _select(source_path, 'SVSharedFileMetaInfoEntity',
                           ('assetID', 'fileName', 'filePath', 'pageNum', 'favourite',
                            'shared', 'progressState', 'viewMode'))
        for row in (_rows(source_path, meta_sql) if meta_sql else []):
            asset_id, file_name, file_path, page_num, favourite, shared, progress, view = row
            data_list.append((blank, blank, 'SVSharedFileMetaInfoEntity', asset_id, file_name, file_path,
                 blank, blank, blank, blank, blank, blank, page_num, favourite, shared,
                 progress, view, blank, blank, blank, blank, _COMMITTED, relative_path))
            sources.append(source_path)

        heron_sql = _select(source_path, 'SVBlueHeronEntity',
                            ('assetId', 'filePath', 'updatedModifiedDate',
                             'modifiedDateAtDownload', 'lastViewedPageNumber', 'type',
                             'favourite', 'shared', 'isRooted'))
        for row in (_rows(source_path, heron_sql) if heron_sql else []):
            (asset_id, file_path, updated, downloaded, page_num, asset_type, favourite,
             shared, rooted) = row
            data_list.append((_ms(updated), _ms(downloaded), 'SVBlueHeronEntity', asset_id, blank,
                 file_path, blank, blank, blank, blank, blank,
                 page_num if page_num not in (None, -1) else blank, blank, favourite,
                 shared, blank, blank, rooted, asset_type, blank, blank, _COMMITTED, relative_path))
            sources.append(source_path)

        review_sql = _select(source_path, 'SVReviewEntity',
                             ('assetID', 'name', 'filePath', 'reviewType', 'reviewID',
                              'invitationID', 'parcerID'))
        for row in (_rows(source_path, review_sql) if review_sql else []):
            asset_id, name, file_path, review_type, review_id, invitation_id, parcel_id = row
            data_list.append((blank, blank, 'SVReviewEntity', asset_id, name, file_path, review_type,
                 review_id, invitation_id, parcel_id, blank, blank, blank, blank, blank,
                 blank, blank, blank, blank, blank, blank, _COMMITTED, relative_path))
            sources.append(source_path)

        track_sql = _select(source_path, 'SVSendAndTrackEntity',
                            ('assetID', 'name', 'filePath', 'reviewType', 'invitationID',
                             'parcelID'))
        for row in (_rows(source_path, track_sql) if track_sql else []):
            asset_id, name, file_path, review_type, invitation_id, parcel_id = row
            data_list.append((blank, blank, 'SVSendAndTrackEntity', asset_id, name, file_path,
                 review_type, blank, invitation_id, parcel_id, blank, blank, blank, blank,
                 blank, blank, blank, blank, blank, blank, blank, _COMMITTED, relative_path))
            sources.append(source_path)

        parcel_sql = _select(source_path, 'SVParcelInfoEntity',
                             ('invitationId', 'assetId', 'reviewId',
                              'serializedReviewParticipants', 'isOriginalShared',
                              'isLegacyAsset'))
        parcel_rows = []
        if parcel_sql:
            parcel_rows = [(row, _COMMITTED) for row in _rows(source_path, parcel_sql)]
            parcel_rows += [(row, _PRE_CHECKPOINT)
                            for row in _superseded(source_path, parcel_sql, (0,))]
        for row, record_source in parcel_rows:
            invitation_id, asset_id, review_id, participants, original, legacy = row
            data_list.append((blank, blank, 'SVParcelInfoEntity', asset_id, blank, blank, blank,
                 review_id, invitation_id, blank, _count(participants), blank, blank, blank,
                 blank, blank, blank, blank, blank, original, legacy, record_source, relative_path))
            sources.append(source_path)

    data_headers = (
        ('Updated Modified Date', 'datetime'),
        ('Modified Date At Download', 'datetime'),
        'Record Type',
        'Asset ID',
        'File Name',
        'File Path',
        'Review Type (as stored)',
        'Review ID',
        'Invitation ID',
        'Parcel ID',
        'Participant Count',
        'Last Viewed Page Number',
        'Page Number',
        'Favourite (as stored)',
        'Shared (as stored)',
        'Progress State (as stored)',
        'View Mode (as stored)',
        'Is Rooted (as stored)',
        'Asset Type (as stored)',
        'Original Shared (as stored)',
        'Legacy Asset (as stored)',
        'Record Source',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def adobe_reader_ai_conversations(context):
    data_list = []
    sources = []

    for source_path in _databases(context, _QNA_DB):
        relative_path = context.get_relative_path(source_path)
        conversation_sql = _select(
            source_path, 'DCMConversation',
            ('id', 'conversationName', 'userId', 'sessionId', 'chatSessionId',
             'createdTimeInMs', 'modifiedTimeInMs', 'lastAccessTimeInMs'))
        if not conversation_sql:
            continue

        assets = {row[0]: row for row in _rows(
            source_path,
            _select(source_path, 'DCMAsset',
                    ('docId', 'fileName', 'mimeType', 'fileHash', 'assetId', 'docType')))}
        linked = {}
        for conversation_id, doc_id in _rows(
                source_path,
                'SELECT `conversationId`, `docId` FROM `DCMConversationAssetCrossRef`'):
            linked.setdefault(conversation_id, []).append(doc_id)
        events = {}
        for conversation_id, event_type in _rows(
                source_path,
                'SELECT `conversationId`, `type` FROM `DCMConversationEvent`'):
            events.setdefault(conversation_id, []).append(event_type)

        rows = [(row, _COMMITTED) for row in _rows(source_path, conversation_sql)]
        rows += [(row, _PRE_CHECKPOINT)
                 for row in _superseded(source_path, conversation_sql, (0,))]
        for row, record_source in rows:
            (conversation_id, name, user_id, session_id, chat_session_id, created, modified,
             last_access) = row
            doc_ids = linked.get(conversation_id, [])
            names = ', '.join(
                str(assets[doc_id][1]) for doc_id in doc_ids
                if doc_id in assets and assets[doc_id][1])
            types = events.get(conversation_id, [])
            data_list.append((
                _ms(last_access),
                _ms(created),
                _ms(modified),
                name,
                conversation_id,
                user_id,
                session_id,
                chat_session_id,
                len(doc_ids),
                names,
                len(types),
                ', '.join(sorted(set(types))),
                record_source,
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Last Access', 'datetime'),
        ('Created', 'datetime'),
        ('Modified', 'datetime'),
        'Conversation Name',
        'Conversation ID',
        'User ID',
        'Session ID',
        'Chat Session ID',
        'Linked Document Count',
        'Linked Document Names',
        'Event Count',
        'Event Types (as stored)',
        'Record Source',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def adobe_reader_tool_usage(context):
    data_list = []
    sources = []

    for source_path in _databases(context, _NBA_DB):
        relative_path = context.get_relative_path(source_path)
        sql = _select(source_path, 'tool_usage',
                      ('id', 'timestampInMs', 'toolId', 'eventType', 'docId'))
        if not sql:
            continue
        rows = [(row, _COMMITTED) for row in _rows(source_path, sql)]
        rows += [(row, _PRE_CHECKPOINT) for row in _superseded(source_path, sql, (0,))]
        for (_row_id, timestamp, tool_id, event_type, doc_id), record_source in rows:
            data_list.append((
                _ms(timestamp),
                tool_id,
                event_type,
                doc_id or '',
                record_source,
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Timestamp', 'datetime'),
        'Tool (as stored)',
        'Event Type (as stored)',
        'Document ID',
        'Record Source',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def adobe_reader_document_cloud(context):
    data_list = []
    sources = []
    files_found = unique_files(context)
    blank = ''

    def collect(source_path, sql, key_indexes):
        '''Committed rows, then rows readable only before the last checkpoint.'''
        if not sql:
            return []
        rows = [(row, _COMMITTED) for row in _rows(source_path, sql)]
        return rows + [(row, _PRE_CHECKPOINT)
                       for row in _superseded(source_path, sql, key_indexes)]

    for source_path in _databases(context, _AR_DB, files_found):
        relative_path = context.get_relative_path(source_path)
        file_sql = _select(source_path, 'ARFileInfo',
                           ('_fileID', '_fileName', '_filePath', '_assetID', '_userID',
                            '_docSource', '_source', '_fileSize', '_mimeType',
                            '_isPersistent'))
        for row, record_source in collect(source_path, file_sql, (0,)):
            (_file_id, file_name, file_path, asset_id, user_id, doc_source, source_kind,
             file_size, mime_type, persistent) = row
            data_list.append((blank, 'ARFileInfo', file_name, file_path, asset_id, user_id,
                              mime_type, file_size, doc_source, source_kind, persistent,
                              blank, blank, blank, blank, blank, blank, blank, blank, blank,
                              blank, record_source, relative_path))
            sources.append(source_path)

        transfer_sql = _select(source_path, 'ARCloudTransfer',
                               ('_transferID', '_fileID', '_transferType', '_transferStatus',
                                '_transferDate', '_transferErrorReason',
                                '_transferNumberAttempt'))
        for row, record_source in collect(source_path, transfer_sql, (0,)):
            (_transfer_id, _linked_file_id, transfer_type, status, transfer_date, error,
             attempts) = row
            data_list.append((_ms(transfer_date), 'ARCloudTransfer', blank, blank, blank,
                              blank, blank, blank, blank, blank, blank, transfer_type,
                              status, attempts, error or blank, blank, blank, blank, blank,
                              blank, blank, record_source, relative_path))
            sources.append(source_path)

    for source_path in _databases(context, _MULTIDOC_DB, files_found):
        relative_path = context.get_relative_path(source_path)
        sql = _select(source_path, 'OpenDocTable',
                      ('viewerWindowID', 'docPath', 'uniqueCloudIdentifier',
                       'notificationID'))
        for row, record_source in collect(source_path, sql, (0,)):
            window_id, doc_path, cloud_id, notification_id = row
            data_list.append((blank, 'OpenDocTable', blank, doc_path, cloud_id, blank, blank,
                              blank, blank, blank, blank, blank, blank, blank, blank,
                              window_id, notification_id or blank, blank, blank, blank,
                              blank, record_source, relative_path))
            sources.append(source_path)

    for source_path in _databases(context, _SHARE_DB, files_found):
        relative_path = context.get_relative_path(source_path)
        sql = _select(source_path, 'ARShareInProgressFileInfo',
                      ('dummyFilePath', 'assetId', 'invitationUri', 'backupFilePath',
                       'fileSize', 'uploadStatus', 'commentAddedStatus', 'isReview'))
        for row, record_source in collect(source_path, sql, (0,)):
            (_dummy_path, asset_id, invitation_uri, backup_path, file_size, upload_status,
             comment_status, is_review) = row
            data_list.append((blank, 'ARShareInProgressFileInfo', blank, backup_path,
                              asset_id, blank, blank, file_size, blank, blank, blank, blank,
                              blank, blank, blank, blank, blank, upload_status,
                              comment_status, is_review, invitation_uri or blank,
                              record_source, relative_path))
            sources.append(source_path)

    data_headers = (
        ('Transfer Date', 'datetime'),
        'Record Type',
        'File Name',
        'File Path',
        'Asset ID',
        'User ID',
        'MIME Type',
        'File Size',
        'Document Source (as stored)',
        'Source (as stored)',
        'Is Persistent (as stored)',
        'Transfer Type (as stored)',
        'Transfer Status (as stored)',
        'Transfer Attempts',
        'Transfer Error Reason',
        'Viewer Window ID',
        'Notification ID',
        'Upload Status (as stored)',
        'Comment Added Status (as stored)',
        'Is Review (as stored)',
        'Invitation URI',
        'Record Source',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
