__artifacts_v2__ = {
    "get_sms_mms": {
        "name": "SMS Messages",
        "description": "SMS messages from mmssms.db (incl. LG extended types and Samsung spam_sms)",
        "author": "@ydkhatri",
        "creation_date": "2020-03-10",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "SMS & MMS",
        "notes": "SMS date values are in milliseconds and MMS pdu.date values are in seconds, per the AOSP telephony provider. LG extended type mappings were established through testing and are not vendor-documented.",
        "paths": ('*/com.android.providers.telephony/databases/mmssms*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.providers.telephony | 25 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.telephony | 32 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.telephony | 62 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.telephony | 87 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.telephony | 1031 rows",
            "samsunga53_a14": "Android 14 | com.android.providers.telephony | 41 rows",
            "samsungs20_a13": "Android 13 | com.android.providers.telephony | 35 rows",
            "sharon_a14": "Android 14 | com.android.providers.telephony | 308 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.telephony | 12 rows",
            "userb2_a13": "Android 13 | com.android.providers.telephony | 19 rows",
            "adams_ss135dl_a13": "Android 13 | com.android.providers.telephony | 51 rows",
            "cookbook_a11": "Android 11 | com.android.providers.telephony | 59 rows",
            "falken_a326u_a13": "Android 13 | com.android.providers.telephony | 16 rows",
            "hc_pixel8pro_a17": "Android 17 | com.android.providers.telephony | 68 rows",
            "pixel3_a11": "Android 11 | com.android.providers.telephony | 27 rows",
            "pixel3_a12": "Android 12 | com.android.providers.telephony | 32 rows",
            "russell_a14": "Android 14 | com.android.providers.telephony | 139 rows",
            "s20fe_a13": "Android 13 | com.android.providers.telephony | 0 rows",
            "sharon_a13": "Android 13 | com.android.providers.telephony | 107 rows",
            "emu_a15_oss_v1": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v2": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v3": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v4": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v5": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v6": "Android 15 | com.android.providers.telephony | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Body",
                "directionColumn": "Type",
                "directionSentValue": "Sent",
                "timeColumn": "Date",
                "senderColumn": "Address",
                "sentMessageStaticLabel": "Local User"
            }
        },
    },
    "get_sms_mms_mms": {
        "name": "MMS Messages",
        "description": "MMS messages and attachments from mmssms.db",
        "author": "@ydkhatri",
        "creation_date": "2020-03-10",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "SMS & MMS",
        "notes": "SMS date values are in milliseconds and MMS pdu.date values are in seconds, per the AOSP telephony provider. Attachment files are matched to part rows on the recorded _data path (storage class, Android user, package and file name), never on the file name alone; a part whose file is not in the extraction shows its stored path in Body. Reference: AOSP, 'Telephony.BaseMmsColumns MESSAGE_BOX constants (ALL=0, INBOX=1, SENT=2, DRAFTS=3, OUTBOX=4, FAILED=5)', https://developer.android.com/reference/android/provider/Telephony.BaseMmsColumns",
        "paths": ('*/com.android.providers.telephony/databases/mmssms*',
                  '*/com.android.providers.telephony/app_parts/*',
                  '*/com.android.providers.telephony/parts/*'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.providers.telephony | 67 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.telephony | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.telephony | 17 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.telephony | 219 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.telephony | 91 rows",
            "samsunga53_a14": "Android 14 | com.android.providers.telephony | 4 rows",
            "samsungs20_a13": "Android 13 | com.android.providers.telephony | 6 rows",
            "sharon_a14": "Android 14 | com.android.providers.telephony | 20 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.telephony | 6 rows",
            "userb2_a13": "Android 13 | com.android.providers.telephony | 2 rows",
            "adams_ss135dl_a13": "Android 13 | com.android.providers.telephony | 47 rows",
            "cookbook_a11": "Android 11 | com.android.providers.telephony | 14 rows",
            "falken_a326u_a13": "Android 13 | com.android.providers.telephony | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.android.providers.telephony | 24 rows",
            "pixel3_a11": "Android 11 | com.android.providers.telephony | 2 rows",
            "pixel3_a12": "Android 12 | com.android.providers.telephony | 4 rows",
            "russell_a14": "Android 14 | com.android.providers.telephony | 65 rows",
            "s20fe_a13": "Android 13 | com.android.providers.telephony | 0 rows",
            "sharon_a13": "Android 13 | com.android.providers.telephony | 2 rows",
            "emu_a15_oss_v1": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v2": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v3": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v4": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v5": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v6": "Android 15 | com.android.providers.telephony | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Body",
                "directionColumn": "Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Date",
                "senderColumn": "From Address",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Media"
            }
        },
    },
    "get_sms_mms_combined": {
        "name": "SMS and MMS Messages",
        "description": "SMS and MMS messages from mmssms.db in one table, with a Message Type column stating which each row is. Complements the separate SMS Messages and MMS Messages artifacts rather than replacing them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "SMS & MMS",
        "notes": "The rows of the SMS Messages and MMS Messages artifacts in one table, sorted by Date, so a thread that carries both transports reads in one place. Both tables key on the same thread_id and the provider itself tells the two apart in its unified queries with a transport_type discriminator column. Reference: AOSP, 'Telephony.MmsSms.TYPE_DISCRIMINATOR_COLUMN', https://developer.android.com/reference/android/provider/Telephony.MmsSms#TYPE_DISCRIMINATOR_COLUMN. Message Type is SMS or MMS, and Source Table names the table each row was read from (sms, spam_sms or pdu); both are uniform on an image holding only one transport. Address is sms.address for SMS rows (the other party, per Telephony.TextBasedSmsColumns.ADDRESS) and the From (PduHeaders.FROM, 0x89) addr entry for MMS rows. To Address, Cc and Bcc are filled for MMS rows only; Contact ID, Service Center and Error Code are filled for SMS rows only. MMS rows are one per non-SMIL part, so a multi-part MMS repeats its MSG ID, and MSG ID is sms._id or pdu._id, unique only together with Message Type. Media renders the part file when it is in the extraction, matched on the part's recorded _data path (storage class, Android user, package and file name) rather than on the file name alone, and is blank for SMS rows, for text parts, and for parts whose file is not in the image (the part's stored path is then shown in Body). Direction maps sms.type and pdu.msg_box through the same words from the AOSP constants (Received, Sent, Draft, Outbox, Failed; Queued exists for SMS only), with the LG extended sms.type values handled as in the SMS Messages artifact. References: AOSP, 'Telephony.TextBasedSmsColumns MESSAGE_TYPE constants', https://developer.android.com/reference/android/provider/Telephony.TextBasedSmsColumns; AOSP, 'Telephony.BaseMmsColumns MESSAGE_BOX constants', https://developer.android.com/reference/android/provider/Telephony.BaseMmsColumns. SMS date values are in milliseconds and MMS pdu.date values are in seconds; the provider's own union query multiplies pdu.date by 1000 to line the two up. Reference: AOSP, 'MmsSmsProvider.java, getConversations and buildConversationQuery', https://android.googlesource.com/platform/packages/providers/TelephonyProvider/+/bca387f553a4493c88e24455172225fd1049c91f/src/com/android/providers/telephony/MmsSmsProvider.java",
        "paths": ('*/com.android.providers.telephony/databases/mmssms*',
                  '*/com.android.providers.telephony/app_parts/*',
                  '*/com.android.providers.telephony/parts/*'),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.providers.telephony | 92 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.telephony | 32 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.telephony | 79 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.telephony | 306 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.telephony | 1122 rows",
            "samsunga53_a14": "Android 14 | com.android.providers.telephony | 45 rows",
            "samsungs20_a13": "Android 13 | com.android.providers.telephony | 41 rows",
            "sharon_a14": "Android 14 | com.android.providers.telephony | 328 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.telephony | 18 rows",
            "userb2_a13": "Android 13 | com.android.providers.telephony | 21 rows",
            "adams_ss135dl_a13": "Android 13 | com.android.providers.telephony | 98 rows",
            "cookbook_a11": "Android 11 | com.android.providers.telephony | 73 rows",
            "falken_a326u_a13": "Android 13 | com.android.providers.telephony | 16 rows",
            "hc_pixel8pro_a17": "Android 17 | com.android.providers.telephony | 92 rows",
            "pixel3_a11": "Android 11 | com.android.providers.telephony | 29 rows",
            "pixel3_a12": "Android 12 | com.android.providers.telephony | 36 rows",
            "russell_a14": "Android 14 | com.android.providers.telephony | 204 rows",
            "s20fe_a13": "Android 13 | com.android.providers.telephony | 0 rows",
            "sharon_a13": "Android 13 | com.android.providers.telephony | 109 rows",
            "emu_a15_oss_v1": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v2": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v3": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v4": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v5": "Android 15 | com.android.providers.telephony | 0 rows",
            "emu_a15_oss_v6": "Android 15 | com.android.providers.telephony | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Body",
                "directionColumn": "Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Date",
                "senderColumn": "Address",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Media",
                "extraColumns": ["Message Type"]
            }
        },
    },
    "get_sms_mms_attachments": {
        "name": "MMS Attachments",
        "description": "MMS attachment files from the telephony provider's app_parts and parts folders, with the message a part row links each file to, and the files no part row references.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "SMS & MMS",
        "notes": "One row per part row that records a file path (part._data), joined to its pdu row for Date, Direction and From Address, plus one row per file found under app_parts or parts that no part row references. Status says which case a row is: 'Referenced by message', 'Referenced by a part row with no message row' (the part's mid names a pdu row that is not in the table, so Date, Direction, MSG ID and Thread ID are blank), 'Referenced, file not in extraction', or 'Not referenced by any part row'. Files are matched to part rows on the recorded _data path (storage class, Android user, package and file name), never on the file name alone. Content Type is part.ct as stored and Detected Type is sniffed independently from the file's own bytes; an ISO base media file (MP4, M4A, 3GP, HEIC, AVIF) is reported by its ftyp brand, because the container does not say whether its tracks are audio or video. On the 25 tested images the two agreed on every file that had both. Media is blank for zero-byte files and for files not in the extraction; Size is the file's length in bytes. On 17 of the 25 tested images the database held one part row with no message row pointing at a zero-byte file, and three images carried between one and ten unreferenced files of real size (JPEG, PNG, GIF, HEIC and MP4-family). Date, Direction and From Address are blank on rows with no message row, so on an image with few referenced attachments the table can lead with blanks. Why a file is on disk without a part row is not recorded in the database and is not asserted here. Reference: AOSP, 'Telephony.Mms.Part' (_DATA, CONTENT_TYPE, MSG_ID), https://developer.android.com/reference/android/provider/Telephony.Mms.Part",
        "paths": ('*/com.android.providers.telephony/databases/mmssms*',
                  '*/com.android.providers.telephony/app_parts/*',
                  '*/com.android.providers.telephony/parts/*'),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.providers.telephony | 11 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.telephony | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.telephony | 3 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.telephony | 45 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.telephony | 29 rows",
            "samsunga53_a14": "Android 14 | com.android.providers.telephony | 3 rows",
            "samsungs20_a13": "Android 13 | com.android.providers.telephony | 1 rows",
            "sharon_a14": "Android 14 | com.android.providers.telephony | 17 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.telephony | 3 rows",
            "userb2_a13": "Android 13 | com.android.providers.telephony | 2 rows",
            "adams_ss135dl_a13": "Android 13 | com.android.providers.telephony | 5 rows",
            "cookbook_a11": "Android 11 | com.android.providers.telephony | 19 rows",
            "falken_a326u_a13": "Android 13 | com.android.providers.telephony | 1 rows",
            "hc_pixel8pro_a17": "Android 17 | com.android.providers.telephony | 4 rows",
            "pixel3_a11": "Android 11 | com.android.providers.telephony | 4 rows",
            "pixel3_a12": "Android 12 | com.android.providers.telephony | 4 rows",
            "russell_a14": "Android 14 | com.android.providers.telephony | 21 rows",
            "s20fe_a13": "Android 13 | com.android.providers.telephony | 0 rows",
            "sharon_a13": "Android 13 | com.android.providers.telephony | 1 rows",
            "emu_a15_oss_v1": "Android 15 | com.android.providers.telephony | 2 rows",
            "emu_a15_oss_v2": "Android 15 | com.android.providers.telephony | 2 rows",
            "emu_a15_oss_v3": "Android 15 | com.android.providers.telephony | 2 rows",
            "emu_a15_oss_v4": "Android 15 | com.android.providers.telephony | 2 rows",
            "emu_a15_oss_v5": "Android 15 | com.android.providers.telephony | 2 rows",
            "emu_a15_oss_v6": "Android 15 | com.android.providers.telephony | 2 rows",
        },
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly, does_table_exist_in_db,
                               does_column_exist_in_db, check_in_media)
from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.filetype import guess_mime

_SMS_QUERY = '''
    SELECT _id as msg_id, thread_id, address, person, date, date_sent, read,
        CASE WHEN type=1 THEN 'Received' WHEN type=2 THEN 'Sent' WHEN type=3 THEN 'Draft'
             WHEN type=4 THEN 'Outbox' WHEN type=5 THEN 'Failed' WHEN type=6 THEN 'Queued'
             {extendedType} ELSE type END as type,
        body, service_center, error_code
    FROM {smsTableName}
    ORDER BY date
'''

_LG_EXTENDED_TYPES = '''
    WHEN type=7 THEN 'Blocked Number' WHEN type=8 THEN 'Scheduled Send'
    WHEN type=19 THEN 'Broadcast Alert'
'''

_MMS_QUERY = '''
    SELECT pdu._id as mms_id, thread_id, pdu.date as date, pdu.date_sent as date_sent, read, pdu.msg_box as msg_box,
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x89) as "FROM",
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x97) as "TO",
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x82) as "CC",
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x81) as "BCC",
        part._id as part_id, seq, ct, cl, _data, text
    FROM pdu LEFT JOIN part ON part.mid=pdu._id
    ORDER BY pdu._id, date, part_id
'''


_PARTS_QUERY = '''
    SELECT part._id as part_id, part.ct, part._data, pdu._id as mms_id, pdu.thread_id, pdu.date as date,
        pdu.msg_box as msg_box,
        (SELECT address FROM addr WHERE pdu._id=addr.msg_id and addr.type=0x89) as "FROM"
    FROM part LEFT JOIN pdu ON pdu._id=part.mid
    WHERE part._data IS NOT NULL
    ORDER BY part._id
'''

_STATUS_LINKED = 'Referenced by message'
_STATUS_NO_PDU = 'Referenced by a part row with no message row'
_STATUS_MISSING = 'Referenced, file not in extraction'
_STATUS_ORPHAN = 'Not referenced by any part row'


# Telephony.Mms msg_box values; wording mirrors the SMS type CASE
_MMS_BOX_DIRECTION = {0: 'All messages', 1: 'Received', 2: 'Sent', 3: 'Draft', 4: 'Outbox', 5: 'Failed'}

# rows with no Date sort after every dated row in the combined table
_UNDATED = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _rows(source_path, sql):
    db = open_sqlite_db_readonly(source_path)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _sms_tables(source_path):
    """(table, extended CASE text) pairs to read from one mmssms.db."""
    extended = _LG_EXTENDED_TYPES if does_column_exist_in_db(source_path, 'sms', 'lgeSiid') else ''
    tables = [('sms', extended)]
    if does_table_exist_in_db(source_path, 'spam_sms'):
        tables.append(('spam_sms', ''))
    return tables


def _storage_key(relative_path):
    """The storage class, Android user and in-package path of a file, or None.

    Every spelling of one file (data/user_de/0/..., data_mirror/data_de/null/0/...) and
    the absolute path the provider records in part._data all reduce to the same key.
    """
    key, _rank = canonical_path(relative_path)
    if '\x00' not in key:
        return None
    return key.split('\x00', 1)[1]


def _part_files(context, files_found):
    """Index the attachment files the seeker found by recorded identity.

    Returns (by_key, by_tail): by_key maps the storage key of each file under app_parts
    or parts to its staged path; by_tail maps 'app_parts/<name>' to the staged path only
    where exactly one file carries that tail, and to None where the tail is ambiguous.
    """
    by_key = {}
    by_tail = {}
    for file_found in files_found:
        file_found = str(file_found)
        posix = file_found.replace('\\', '/')
        parent = posix.rsplit('/', 2)
        if len(parent) < 3 or parent[-2] not in ('app_parts', 'parts') or os.path.isdir(file_found):
            continue
        key = _storage_key(context.get_relative_path(file_found))
        if key is not None:
            by_key.setdefault(key, file_found)
        tail = f'{parent[-2]}/{parent[-1]}'
        by_tail[tail] = None if tail in by_tail else file_found
    return by_key, by_tail


def _find_part_file(data_path, part_files):
    """The staged file a part row's recorded _data path names, or None."""
    by_key, by_tail = part_files
    posix = str(data_path).replace('\\', '/')
    key = _storage_key(posix.lstrip('/'))
    if key is not None and key in by_key:
        return by_key[key]
    if key is None:
        # a storage layout canonical_path does not know: accept the in-package tail when
        # exactly one found file carries it, and refuse to guess between several
        parent = posix.rsplit('/', 2)
        if len(parent) == 3:
            return by_tail.get(f'{parent[-2]}/{parent[-1]}')
    return None


def _mms_body_and_media(part_row, part_files):
    """Body text and media reference for one pdu/part row."""
    data_path = part_row['_data']
    media_ref = ''
    body = ''
    if data_path:
        match = _find_part_file(data_path, part_files)
        if match:
            media_ref = check_in_media(match, os.path.basename(str(data_path))) or ''
        else:
            body = str(data_path)
    else:
        body = part_row['text'] or ''
    return body, media_ref


def _mmssms_dbs(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('mmssms.db') and '/mirror/' not in file_found.replace('\\', '/'):
            yield file_found


@artifact_processor
def get_sms_mms(context):
    files_found = unique_files(context)
    data_list = []
    source_paths = []
    for source_path in _mmssms_dbs(files_found):
        source_paths.append(source_path)
        for table, ext in _sms_tables(source_path):
            for r in _rows(source_path, _SMS_QUERY.format(smsTableName=table, extendedType=ext)):
                data_list.append((
                    _ms_to_utc(r['date']),
                    _ms_to_utc(r['date_sent']),
                    r['type'],
                    r['address'],
                    r['body'],
                    r['msg_id'],
                    r['thread_id'],
                    r['person'],
                    r['read'],
                    r['service_center'],
                    r['error_code'],
                ))

    data_headers = (
        ('Date', 'datetime'),
        ('Date Sent', 'datetime'),
        'Type',
        'Address',
        'Body',
        'MSG ID',
        'Thread ID',
        'Contact ID',
        'Read',
        'Service Center',
        'Error Code',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_sms_mms_mms(context):
    files_found = unique_files(context)
    part_files = _part_files(context, files_found)
    data_list = []
    source_paths = []
    for source_path in _mmssms_dbs(files_found):
        source_paths.append(source_path)
        for r in _rows(source_path, _MMS_QUERY):
            if r['ct'] == 'application/smil':  # presentation layer, not content
                continue
            body, media_ref = _mms_body_and_media(r, part_files)
            direction = _MMS_BOX_DIRECTION.get(r['msg_box'], r['msg_box'])
            data_list.append((
                _sec_to_utc(r['date']),
                _sec_to_utc(r['date_sent']),
                direction,
                r['FROM'],
                body,
                media_ref,
                r['mms_id'],
                r['thread_id'],
                r['read'],
                r['TO'],
                r['CC'],
                r['BCC'],
            ))

    data_headers = (
        ('Date', 'datetime'),
        ('Date Sent', 'datetime'),
        'Direction',
        'From Address',
        'Body',
        ('Media', 'media'),
        'MSG ID',
        'Thread ID',
        'Read',
        'To Address',
        'Cc',
        'Bcc',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_sms_mms_combined(context):
    files_found = unique_files(context)
    part_files = _part_files(context, files_found)
    data_list = []
    source_paths = []
    for source_path in _mmssms_dbs(files_found):
        source_paths.append(source_path)
        for table, ext in _sms_tables(source_path):
            for r in _rows(source_path, _SMS_QUERY.format(smsTableName=table, extendedType=ext)):
                data_list.append((
                    _ms_to_utc(r['date']),
                    _ms_to_utc(r['date_sent']),
                    r['type'],
                    r['address'],
                    r['body'],
                    '',
                    'SMS',
                    r['msg_id'],
                    r['thread_id'],
                    r['read'],
                    '',
                    '',
                    '',
                    r['person'],
                    r['service_center'],
                    r['error_code'],
                    table,
                ))
        for r in _rows(source_path, _MMS_QUERY):
            if r['ct'] == 'application/smil':  # presentation layer, not content
                continue
            body, media_ref = _mms_body_and_media(r, part_files)
            data_list.append((
                _sec_to_utc(r['date']),
                _sec_to_utc(r['date_sent']),
                _MMS_BOX_DIRECTION.get(r['msg_box'], r['msg_box']),
                r['FROM'],
                body,
                media_ref,
                'MMS',
                r['mms_id'],
                r['thread_id'],
                r['read'],
                r['TO'],
                r['CC'],
                r['BCC'],
                '',
                '',
                '',
                'pdu',
            ))
    data_list.sort(key=lambda row: row[0] or _UNDATED)

    data_headers = (
        ('Date', 'datetime'),
        ('Date Sent', 'datetime'),
        'Direction',
        'Address',
        'Body',
        ('Media', 'media'),
        'Message Type',
        'MSG ID',
        'Thread ID',
        'Read',
        'To Address',
        'Cc',
        'Bcc',
        'Contact ID',
        'Service Center',
        'Error Code',
        'Source Table',
    )
    return data_headers, data_list, '\n'.join(source_paths)


def _sniff(file_found):
    """(size, detected type) of a staged file; the type is '' for an empty file.

    An ISO base media file (MP4, M4A, 3GP, HEIC) is reported by the brand its ftyp box
    records, because the container alone does not say whether its tracks are audio or
    video and a mime type would assert that.
    """
    size = os.path.getsize(file_found)
    if not size:
        return 0, ''
    with open(file_found, 'rb') as handle:
        data = handle.read()
    if data[4:8] == b'ftyp' and len(data) >= 12:
        return size, f"ISO media (ftyp brand {data[8:12].decode('ascii', 'replace').strip()})"
    return size, guess_mime(data) or ''


@artifact_processor
def get_sms_mms_attachments(context):
    files_found = unique_files(context)
    part_files = _part_files(context, files_found)
    referenced = set()
    data_list = []
    source_paths = []
    for source_path in _mmssms_dbs(files_found):
        source_paths.append(source_path)
        for r in _rows(source_path, _PARTS_QUERY):
            data_path = str(r['_data'])
            match = _find_part_file(data_path, part_files)
            if match:
                referenced.add(match)
                size, detected = _sniff(match)
                media_ref = (check_in_media(match, os.path.basename(data_path)) or '') if size else ''
                status = _STATUS_LINKED if r['mms_id'] is not None else _STATUS_NO_PDU
                file_path = context.get_relative_path(match)
            else:
                size, detected, media_ref, file_path = '', '', '', ''
                status = _STATUS_MISSING
            data_list.append((
                _sec_to_utc(r['date']),
                _MMS_BOX_DIRECTION.get(r['msg_box'], r['msg_box']) if r['mms_id'] is not None else '',
                r['FROM'],
                os.path.basename(data_path),
                media_ref,
                r['ct'],
                detected,
                status,
                size,
                r['mms_id'],
                r['thread_id'],
                r['part_id'],
                data_path,
                file_path,
            ))
    for file_found in sorted(set(part_files[0].values()) - referenced):
        size, detected = _sniff(file_found)
        media_ref = (check_in_media(file_found, os.path.basename(file_found)) or '') if size else ''
        data_list.append((
            '', '', '',
            os.path.basename(file_found),
            media_ref,
            '',
            detected,
            _STATUS_ORPHAN,
            size,
            '', '', '', '',
            context.get_relative_path(file_found),
        ))

    data_headers = (
        ('Date', 'datetime'),
        'Direction',
        'From Address',
        'File Name',
        ('Media', 'media'),
        'Content Type (as stored)',
        'Detected Type',
        'Status',
        'Size (bytes)',
        'MSG ID',
        'Thread ID',
        'Part ID',
        'Stored Path',
        'File Path',
    )
    return data_headers, data_list, '\n'.join(source_paths)
