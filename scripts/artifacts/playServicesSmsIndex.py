import datetime
import hashlib
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

__artifacts_v2__ = {
    "playServicesSmsIndex": {
        "name": "Play Services SMS Index",
        "description": "Rows of the mmssms table of Google Play services' icing_mmssms.db: messages with their "
                       "address, body, type, thread and date, and whether the SMS provider database in the same "
                       "data folder holds a message with that ID and body.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Messaging",
        "notes": "One row per row of the mmssms table of each icing_mmssms.db in Google Play services' databases folder. The database is in Play services' private data folder. Play services' source is not published, so the column names are the database's own and no meaning is asserted beyond what is named below. Values are reported as stored except where named below. An empty cell is a NULL or empty value in the index. Tested only with known data: emu_a11_icing_sms_known_20261116 (Android 11 emulator, Play services 20.18.17), where three SMS were received, one conversation was deleted in Google Messages and one SMS was sent. All 4 messages were in the index. The 3 still in the SMS provider had the same _id, thread, address, body, type and date in both. The deleted message had no provider row left to compare. The deleted message was still in the index after the deletion, after the Play services SMS indexer start broadcast was sent again, after forced idle maintenance and after Google Messages' IcingMonitoringJobService job was forced to run, about seven minutes in all. How long the index keeps a deleted message is not established. The mint record says the same steps on two Android 15 emulators, one signed in to a Google account, created no icing_mmssms.db. Their Play services versions were not recorded and no image of them is in the corpus. Which Play services versions write it is not established. Of the other 58 registered Android images, searched by file listing on 2026-11-15, the file was on galaxys10_a10 and pixel3_a11 only. mmssms had no rows on either, while the SMS provider on each held messages. On the three images that held it, its tables were mmssms, mmssms_tag, sms_seqno_table_appdatasearch, incarnation_appdatasearch, version_appdatasearch, android_metadata and sqlite_sequence. Date (UTC) is date read as milliseconds since 1970. That unit is not documented by Play services. On the known data it equalled the SMS provider's date on the 3 rows the provider still held and the received times matched the mint record. Android User is n for a database under data/user/<n>, 0 under data/data and blank otherwise. It is read from the path. Type is type named from Telephony.TextBasedSmsColumns MESSAGE_TYPE_* (https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/provider/Telephony.java#L139-L157) for rows whose Kind is sms. The index type equalled the provider's type on the 3 comparable known-data rows. Values 0 and 3 to 6 are unexercised. An unlisted value and the type of an mms row are shown as stored. INBOX (1) for the three received and SENT (2) for the sent message on the known data. Kind is msg_type as stored. Read (as stored) is read as stored. Read (as stored) held 0 on all 4 rows of the known data while the SMS provider held 1 on the 3 rows it still had. Whether Play services updates this column is not established, so a 0 here is not evidence that a message was unread. Subject and Media URI had no value on any known-data row, Content Type held text_plain on all 4 rows, Kind held sms on all 4 rows and Android User held 0 on all 4 rows; no MMS was tested, so the mms rows and those columns are unexercised. In SMS Provider compares the row with the SMS provider database (com.android.providers.telephony/databases/mmssms.db) in the same data folder, data/user/0 read as data/data: Yes when its sms table has a row with that _id and the same body, No when it has no row with that _id, Different body under this ID when the body differs (the Different body value is unexercised). For mms rows it is Yes or No by whether the pdu table has that _id. That the two IDs correspond is assumed and unexercised. It is not checked when no such database is beside the index or it cannot be read or has no sms table (the run log says which), or when Kind is neither sms nor mms. No means only that the provider database in the extraction does not hold that ID; on the known data the one No was the deleted message. The provider's sms table declares _id without AUTOINCREMENT, so SQLite can give a deleted message's _id to a later one. The body comparison is there for that case. It did not occur on the known data. Not reported: the score column (it equalled the date in seconds on all 4 known-data rows), mmssms_tag (1 row on the known data: an unread tag with a date, on the deleted message) and the sms_seqno_table_appdatasearch change log. Byte-identical copies of icing_mmssms.db are read once (the main file is compared, not its journal). The first path in sort order is kept and Android User and In SMS Provider describe that copy.",
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
    norm = '/' + path.replace(os.sep, '/').lstrip('/')
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
        if 'sms' not in tables:
            logfunc(f'Play Services SMS Index: no sms table in {path}; In SMS Provider not checked')
            return None
        sms = dict(db.execute('SELECT _id, body FROM sms'))
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
        user = _android_user(context.get_relative_path(db_path))
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

    data_headers = (('Date (UTC)', 'datetime'), 'Android User', 'Type', 'Address', 'Body', 'Subject', 'Thread ID', 'Read (as stored)',
                    'Kind', 'Content Type', 'Media URI', 'URI', 'In SMS Provider')
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
