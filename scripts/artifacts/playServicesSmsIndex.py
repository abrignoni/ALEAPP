import datetime
import hashlib
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

__artifacts_v2__ = {
    "playServicesSmsIndex": {
        "name": "Play Services SMS Index",
        "description": "Rows of the mmssms table of Google Play services' icing_mmssms.db: messages with their "
                       "address, body, type, thread and date as the index stores them, and whether the SMS "
                       "provider database in the same data folder still holds a message with that ID and body.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "SMS & MMS",
        "notes": "One row per row of the mmssms table of each icing_mmssms.db in Google Play services' databases folder. The database is written by Play services, whose source is not published; the column names are its own and the values are reported as stored except where named below. Its tables were mmssms, mmssms_tag, sms_seqno_table_appdatasearch, incarnation_appdatasearch and version_appdatasearch. Tested only with known data: emu_a11_icing_sms_known_20261116 (Android 11 emulator, Play services 20.18.17), where three SMS were received, one conversation was deleted in Google Messages and one SMS was sent. All 4 messages were in the index with _id, thread, address, body, type and date equal to the SMS provider's rows; the deleted message was still in the index after the deletion, after the Play services SMS indexer was started again, after forced idle maintenance and after Google Messages' own index job was forced, about seven minutes in all. How long the index keeps a deleted message is not established. On the same steps an Android 15 emulator (Play services of 2024 and later), signed in or not, created no icing_mmssms.db; which Play services versions write it is not established. On the corpus the file was on galaxys10_a10 and pixel3_a11 only, with no rows in mmssms on either. Date (UTC) is date read as milliseconds since 1970; on the known data it equalled the SMS provider's date on all 4 rows. Android User is n for a database under data/user/<n> and 0 under data/data. Type is type named from Telephony.TextBasedSmsColumns MESSAGE_TYPE_* (https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/provider/Telephony.java#L139-L157) for rows whose Kind is sms; INBOX for the three received and SENT for the sent message on the known data. Kind is msg_type as stored. Read is read as stored. Read held 0 on all 4 rows of the known data while the SMS provider had marked them read, so the index value can lag the provider. Subject and Media URI had no value on any known-data row, Content Type held text_plain on all 4 rows, Kind held sms on all 4 rows and Android User held 0 on all 4 rows; no MMS was tested, so the mms rows and those columns are unexercised. In SMS Provider compares the row with the SMS provider database (com.android.providers.telephony/databases/mmssms.db) in the same data folder, data/user/0 read as data/data: Yes when its sms table has a row with that _id and the same body, No when it has no row with that _id, Different body under this ID when the body differs, and for mms rows Yes or No by the pdu table's _id; not checked when no such database is beside the index (the run log says so). No means only that the provider database in the extraction does not hold that ID; on the known data the one No was the deleted message. SMS provider _id values can be reused after deletion, which the body comparison is there to catch. Not reported: the score column (it equalled the date in seconds on all 4 known-data rows), mmssms_tag (an unread tag with a date per message on the known data) and the sms_seqno_table_appdatasearch change log. Byte-identical copies of icing_mmssms.db are read once.",
        "paths": (
            '*/com.google.android.gms/databases/icing_mmssms.db*',
            '*/com.android.providers.telephony/databases/mmssms.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "emu_a11_icing_sms_known_20261116": "Android 11 | 4 rows (known data; one deleted message, In SMS Provider No)",
            "galaxys10_a10": "Android 10 | 0 rows (mmssms table empty)",
            "pixel3_a11": "Android 11 | 0 rows (mmssms table empty)",
            "pixel7a_a14": "Android 14 | 0 rows (no icing_mmssms.db)",
        },
    }
}

# Telephony.TextBasedSmsColumns MESSAGE_TYPE_* (Telephony.java L139-L157)
_SMS_TYPES = {0: 'ALL', 1: 'INBOX', 2: 'SENT', 3: 'DRAFT', 4: 'OUTBOX', 5: 'FAILED', 6: 'QUEUED'}
_INDEX = '/com.google.android.gms/databases/icing_mmssms.db'
_PROVIDER = '/com.android.providers.telephony/databases/mmssms.db'


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return None
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return None


def _label(mapping, value):
    if value is None or value == '':
        return ''
    name = mapping.get(value)
    return f'{name} ({value})' if name else str(value)


def _parent(path, marker):
    '''The path before marker, with /data/user/0/ read as /data/data/, or None.'''
    norm = path.replace(os.sep, '/')
    if not norm.endswith(marker):
        return None
    return norm[:-len(marker)].replace('/data/user/0', '/data/data')


def _android_user(path):
    '''n from /data/user/<n>/, 0 from /data/data/, else blank.'''
    norm = path.replace(os.sep, '/')
    marker = '/data/user/'
    if marker in norm:
        part = norm.split(marker, 1)[1].split('/', 1)[0]
        return int(part) if part.isdigit() else ''
    return 0 if '/data/data/' in norm else ''


def _dedupe_identical(paths):
    by_hash = {}
    for path in sorted(paths):
        try:
            with open(path, 'rb') as handle:
                digest = hashlib.sha1(handle.read()).hexdigest()
        except OSError as ex:
            logfunc(f'Play Services SMS Index: could not hash {path}: {ex}')
            by_hash[path] = path
            continue
        by_hash.setdefault(digest, path)
    return list(by_hash.values())


def _provider_rows(path):
    '''({sms _id: body}, {pdu _id}) of an SMS provider database, or None when it cannot be read.'''
    db = open_sqlite_db_readonly(path)
    if db is None:
        return None
    try:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        sms = dict(db.execute('SELECT _id, body FROM sms')) if 'sms' in tables else {}
        pdu = {row[0] for row in db.execute('SELECT _id FROM pdu')} if 'pdu' in tables else set()
        return sms, pdu
    except sqlite3.Error as ex:
        logfunc(f'Play Services SMS Index: could not read {path}: {ex}')
        return None
    finally:
        db.close()


def _in_provider(provider, kind, msg_id, body):
    if provider is None:
        return 'not checked'
    sms, pdu = provider
    if kind == 'sms':
        if msg_id not in sms:
            return 'No'
        return 'Yes' if sms[msg_id] == body else 'Different body under this ID'
    if kind == 'mms':
        return 'Yes' if msg_id in pdu else 'No'
    return 'not checked'


@artifact_processor
def playServicesSmsIndex(context):
    files_found = context.get_files_found()
    providers = {}
    for path in sorted(files_found):
        parent = _parent(path, _PROVIDER)
        if parent is not None and parent not in providers:
            providers[parent] = path
    data_list = []
    sources = []
    for db_path in _dedupe_identical([p for p in files_found if _parent(p, _INDEX) is not None]):
        user = _android_user(db_path)
        provider_path = providers.get(_parent(db_path, _INDEX))
        provider = _provider_rows(provider_path) if provider_path else None
        if provider_path is None:
            logfunc(f'Play Services SMS Index: no SMS provider database beside {db_path}; In SMS Provider not checked')
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            logfunc(f'Play Services SMS Index: could not open {db_path}')
            continue
        try:
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            sources.append(db_path)
            if 'mmssms' not in tables:
                logfunc(f'Play Services SMS Index: no mmssms table in {db_path}')
                continue
            for msg_id, kind, uri, msg_type, thread, address, date, subject, body, content_type, media_uri, read \
                    in db.execute('SELECT _id, msg_type, uri, type, thread_id, address, date, subject, body, '
                                  'content_type, media_uri, read FROM mmssms ORDER BY date, _id'):
                data_list.append((
                    _ms_to_utc(date),
                    user,
                    _label(_SMS_TYPES, msg_type) if kind == 'sms' else (msg_type if msg_type is not None else ''),
                    address or '',
                    body or '',
                    subject or '',
                    thread if thread is not None else '',
                    read if read is not None else '',
                    kind,
                    content_type or '',
                    media_uri or '',
                    uri,
                    _in_provider(provider, kind, msg_id, body),
                ))
            if provider_path:
                sources.append(provider_path)
        except sqlite3.Error as ex:
            logfunc(f'Play Services SMS Index: could not read {db_path}: {ex}')
        finally:
            db.close()

    data_headers = (('Date (UTC)', 'datetime'), 'Android User', 'Type', 'Address', 'Body', 'Subject', 'Thread ID', 'Read',
                    'Kind', 'Content Type', 'Media URI', 'URI', 'In SMS Provider')
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
