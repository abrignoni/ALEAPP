__artifacts_v2__ = {
    "get_samsung_message_logs": {
        "name": "Samsung Message Logs",
        "description": "SMS and MMS log rows that the Samsung contacts provider keeps in the calls table of "
                       "calllog.db beside the call log, with whether the telephony provider still holds the "
                       "message each row names",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Messaging",
        "notes": "One row per row of the calls table in com.samsung.android.providers.contacts/databases/"
                 "calllog.db whose logtype is 300 or 200. The Call logs artifact leaves these rows out. "
                 "Message Type maps logtype 300 to SMS and 200 to MMS, and Direction maps type 1 and 2 to "
                 "Received and Sent; any other type is shown as stored, and no row on the images checked "
                 "had another type. No Samsung source for these values is cited. They are data-proven by a "
                 "recorded join: messageid names a telephony provider row, SMS rows in mmssms.db sms (date "
                 "in milliseconds) and MMS rows in pdu (date in seconds, times 1000). On the seven images "
                 "with rows, 100 of the sharon_a13 rows are also in sharon_a14 (same _id, date and "
                 "messageid); counted once, 440 of 481 rows named a provider row with the same id and the "
                 "same date, and on every one of those the provider's sms.type or pdu.msg_box equalled "
                 "type (1 or 2, which AOSP names inbox and sent: https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/provider/Telephony.java#L139-L157, https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/provider/Telephony.java#L1477-L1487). By image: "
                 "samsung_a166u_a16_known_20261116 3 of 3, sharon_a14 324 of 324, sharon_a13 108 of 108, "
                 "galaxys10_a10 19 of 19, samsungs20_a13 9 of 10, cookbook_a11 62 of 81, falken_a326u_a13 "
                 "15 of 36. On the known-data image the 3 rows are the 2 SMS and 1 MMS sent from Samsung "
                 "Messages; the 2 SMS and 1 MMS sent the same day from Google Messages, before Samsung "
                 "Messages was installed, added no row. Which apps write these rows on other devices is "
                 "not established. "
                 "Telephony Provider Row says whether mmssms.db of the same Android user holds a row with "
                 "the id messageid names and the same date (Matched), does not (No provider row with this "
                 "id and date), or no readable mmssms.db was found for that Android user (Not checked). "
                 "The credential-encrypted and device-encrypted copies of mmssms.db are read together. The "
                 "artifact does not say why a provider row is absent, and some ids named provider rows "
                 "with a different date (12 rows on falken_a326u_a13, 3 on cookbook_a11), so an id alone "
                 "is not treated as a match. Telephony Provider Row held Matched on all 324 rows of "
                 "sharon_a14 and all 3 of the known-data image. Content held a value on 40 of the 41 rows "
                 "with no provider row. "
                 "Date is calls.date and Last Modified is calls.last_modified, both read as Unix "
                 "milliseconds; Last Modified was after Date on all 481 rows, and what updates it is not "
                 "established. Number and Name are calls.number and calls.name as stored; a NULL is shown "
                 "blank. On the known-data image Direction held Sent and Number and Name held one value on "
                 "all 3 rows, one test thread. Content is calls.m_content; it held a value on 448 of the "
                 "449 SMS rows and on none of the 32 MMS rows. Subject is calls.m_subject. Subject held a "
                 "value on 9 of the 17 MMS rows of sharon_a14, and Subject had no value on any row of the "
                 "other images. "
                 "Message Type held SMS on all 36 rows of falken_a326u_a13. Provider Message ID is "
                 "messageid as stored (text on the images seen). sec_msg_id (as stored) is "
                 "calls.sec_msg_id; what it identifies is not established, and the calls table has no "
                 "sec_msg_id column on cookbook_a11 and galaxys10_a10, so it is blank on their 81 and 19 "
                 "rows. Log ID is calls._id. Only the columns named above are read; among those not "
                 "reported are the SIM and account columns (subscription_id, subscription_component_name, "
                 "sec_icc_id), geocoded_location, the read and new flags, and the contact and number "
                 "normalisation columns. The logs_group, memo (where present), roaming, sec_duration, "
                 "debug, properties and voicemail_status tables of calllog.db are not reported. "
                 "calllog_shadow.db in device-encrypted storage is not read; it held no calls rows on the "
                 "known-data image.",
        "paths": (
            '*/com.samsung.android.providers.contacts/databases/calllog.db*',
            '*/com.android.providers.telephony/databases/mmssms.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.providers.contacts | 3 rows",
            "adams_ss135dl_a13": "Android 13 | com.samsung.android.providers.contacts | 0 rows",
            "anne_a15": "Android 15 | com.samsung.android.providers.contacts | 0 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.providers.contacts | 81 rows",
            "falken_a326u_a13": "Android 13 | com.samsung.android.providers.contacts | 36 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.providers.contacts | 19 rows",
            "s20fe_a13": "Android 13 | com.samsung.android.providers.contacts | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.providers.contacts | 0 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.providers.contacts | 10 rows",
            "sharon_a13": "Android 13 | com.samsung.android.providers.contacts | 108 rows",
            "sharon_a14": "Android 14 | com.samsung.android.providers.contacts | 324 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Number",
                "textColumn": "Content",
                "directionColumn": "Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Date",
                "senderColumn": "Number",
                "sentMessageStaticLabel": "Local User"
            }
        },
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import canonical_path, unique_files

# logtype values whose rows name a telephony provider message in messageid
_LOGTYPES = {300: 'SMS', 200: 'MMS'}
_DIRECTIONS = {1: 'Received', 2: 'Sent'}
_LOG_COLUMNS = ('_id', 'logtype', 'type', 'date', 'last_modified', 'number', 'name', 'm_subject',
                'm_content', 'messageid', 'sec_msg_id')

_MATCHED = 'Matched (same id and date)'
_NO_ROW = 'No provider row with this id and date'
_NOT_CHECKED = 'Not checked (no readable mmssms.db for this Android user)'


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return ''


def _as_int(value):
    """messageid is stored as text on the images seen; the provider ids are integers."""
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _user(context, file_found):
    """'<storage prefix>|<Android user>' of a file, or None outside a known storage layout."""
    key, _rank = canonical_path(context.get_relative_path(file_found))
    if '\x00' not in key:
        return None
    prefix, storage, _rest = key.split('\x00', 2)
    return f'{prefix}|{storage.split(":", 1)[-1]}'


def _select(db, table, wanted):
    present = {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
    columns = ', '.join(f'"{name}"' if name in present else f'NULL AS "{name}"' for name in wanted)
    return present, db.execute(f'SELECT {columns} FROM "{table}"').fetchall()


def _provider_ids(db_path):
    """({sms _id: date ms}, {pdu _id: date ms}) of one mmssms.db, or None when unreadable."""
    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return None
    try:
        sms = dict(db.execute('SELECT _id, date FROM sms').fetchall())
        pdu = {pid: date * 1000 for pid, date in db.execute('SELECT _id, date FROM pdu').fetchall()
               if isinstance(date, int)}
        return sms, pdu
    except sqlite3.Error as ex:
        logfunc(f'Samsung Message Logs: provider rows not read from {db_path}: {ex}')
        return None
    finally:
        db.close()


@artifact_processor
def get_samsung_message_logs(context):
    files_found = [str(f) for f in unique_files(context) if not os.path.isdir(str(f))]

    providers = {}
    provider_paths = []
    for file_found in files_found:
        if not file_found.endswith('mmssms.db'):
            continue
        ids = _provider_ids(file_found)
        user = _user(context, file_found)
        if ids is None or user is None:
            continue
        provider_paths.append(file_found)
        merged = providers.setdefault(user, ({}, {}))
        merged[0].update(ids[0])
        merged[1].update(ids[1])

    data_list = []
    source_paths = []
    for file_found in files_found:
        if not file_found.endswith('calllog.db'):
            continue
        source_paths.append(file_found)
        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        db.row_factory = sqlite3.Row
        try:
            present, rows = _select(db, 'calls', _LOG_COLUMNS)
        except sqlite3.Error as ex:
            logfunc(f'Samsung Message Logs: could not read {file_found}: {ex}')
            rows, present = [], set()
        finally:
            db.close()
        if 'logtype' not in present:
            continue
        provider = providers.get(_user(context, file_found))
        for row in rows:
            kind = _LOGTYPES.get(row['logtype'])
            if kind is None:
                continue
            message_id = _as_int(row['messageid'])
            if provider is None:
                status = _NOT_CHECKED
            elif message_id is None:
                status = _NO_ROW
            else:
                table = provider[0] if kind == 'SMS' else provider[1]
                status = _MATCHED if table.get(message_id) == row['date'] else _NO_ROW
            data_list.append((
                _ms_to_utc(row['date']),
                _ms_to_utc(row['last_modified']),
                _DIRECTIONS.get(row['type'], row['type']),
                row['number'] or '',
                row['m_content'] or '',
                kind,
                row['name'] or '',
                row['m_subject'] or '',
                status,
                row['messageid'],
                row['sec_msg_id'] or '',
                row['_id'],
            ))

    data_list.sort(key=lambda r: (r[0] == '', str(r[0])))
    data_headers = (
        ('Date', 'datetime'), ('Last Modified', 'datetime'), 'Direction', ('Number', 'phonenumber'),
        'Content', 'Message Type', 'Name', 'Subject', 'Telephony Provider Row', 'Provider Message ID',
        'sec_msg_id (as stored)', 'Log ID',
    )
    return data_headers, data_list, '\n'.join(source_paths + provider_paths)
