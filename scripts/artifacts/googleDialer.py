__artifacts_v2__ = {
    "googleDialerAnnotatedCallLog": {
        "name": "Google Dialer Annotated Call Log",
        "description": "Call log kept by the Google Phone app (annotated_call_log.db). "
                       "Call types follow the Android CallLog.Calls constants.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Google Dialer",
        "notes": "",
        "paths": ('*/com.google.android.dialer/databases/annotated_call_log.db*',
                  '*/com.google.android.apps.messaging/databases/annotated_call_log.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.dialer vc 19806568 | 705 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.dialer vc 19106378 | 12 rows",
            "pixel7a_a14": "Android 14 | com.google.android.dialer vc 15435008 | 501 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.dialer vc 11945968 | 42 rows",
        },
    },
    "googleDialerPhoneLookupHistory": {
        "name": "Google Dialer Phone Lookup History",
        "description": "Caller-id information cached per phone number by the Google Phone "
                       "app (phone_lookup_history.db). The contact name, label and lookup "
                       "URI come from the device contacts (Cp2Info) and the CNAP name from "
                       "the carrier, per the app's phone_lookup_info protobuf.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Google Dialer",
        "notes": "",
        "paths": ('*/com.google.android.dialer/databases/phone_lookup_history.db*',
                  '*/com.google.android.apps.messaging/databases/phone_lookup_history.db*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.dialer vc 19806568 | 3 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.dialer vc 19106378 | 5 rows",
            "pixel7a_a14": "Android 14 | com.google.android.dialer vc 15435008 | 446 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.dialer vc 11945968 | 22 rows",
        },
    },
    "googleDialerSmartdial": {
        "name": "Google Dialer Smartdial",
        "description": "Contacts indexed for smart dialing by the Google Phone app "
                       "(dialer.db, smartdial_table).",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Google Dialer",
        "notes": "",
        "paths": ('*/com.google.android.dialer/databases/dialer.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.dialer vc 19806568 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.dialer vc 19106378 | 14 rows",
            "pixel7a_a14": "Android 14 | com.google.android.dialer vc 15435008 | 11 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.dialer vc 11945968 | 2 rows",
        },
    },
    "googleDialerCachedNumberContacts": {
        "name": "Google Dialer Cached Number Contacts",
        "description": "Caller-id lookups cached per phone number by the Google Phone app "
                       "(dialer.db, cached_number_contacts).",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Google Dialer",
        "notes": "",
        "paths": ('*/com.google.android.dialer/databases/dialer.db*',),
        "output_types": "standard",
        "artifact_icon": "user-check",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.dialer vc 19806568 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.dialer vc 19106378 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.dialer vc 15435008 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.dialer vc 11945968 | 0 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc, decode_protobuf
from scripts.artifacts.storagePathViews import unique_files

# Android CallLog.Calls type constants
CALL_TYPES = {
    1: 'Incoming',
    2: 'Outgoing',
    3: 'Missed',
    4: 'Voicemail',
    5: 'Rejected',
    6: 'Blocked',
    7: 'Answered Externally',
}

# Android CallLog.Calls presentation constants
PRESENTATIONS = {
    1: 'Allowed',
    2: 'Restricted',
    3: 'Unknown',
    4: 'Payphone',
    5: 'Unavailable',
}


def _db_files(context):
    '''The db globs also match -journal/-wal/-shm sidecars; keep only the databases.'''
    return [str(x) for x in unique_files(context) if str(x).endswith('.db')]


def _ms_to_utc(value):
    if not value:
        return ''
    return convert_unix_ts_to_utc(int(value) / 1000)


def _pb_str(node, *path):
    '''Defensively walk a blackboxprotobuf dict and return the value at path as text.'''
    cur = node
    for key in path:
        if isinstance(cur, list):
            cur = cur[0] if cur else None
        if not isinstance(cur, dict):
            return ''
        cur = cur.get(key)
    if isinstance(cur, list):
        cur = cur[0] if cur else None
    if isinstance(cur, bytes):
        return cur.decode('utf-8', 'replace')
    if isinstance(cur, str):
        return cur
    return ''


@artifact_processor
def googleDialerAnnotatedCallLog(context):
    data_list = []
    source_path = ''

    for file_found in _db_files(context):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT timestamp, formatted_number, raw_number, call_type, presentation,
                   duration, geocoded_location, phone_account_id, is_read, new,
                   is_voicemail_call, voicemail_transcription
            FROM AnnotatedCallLog
            ORDER BY timestamp DESC
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                _ms_to_utc(row[0]),
                row[1],
                row[2],
                CALL_TYPES.get(row[3], row[3]),
                PRESENTATIONS.get(row[4], row[4]),
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[11],
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Formatted Number', 'phonenumber'),
        ('Raw Number', 'phonenumber'),
        'Call Type',
        'Presentation',
        'Duration (Seconds)',
        'Geocoded Location',
        'Phone Account ID',
        'Is Read',
        'New',
        'Is Voicemail Call',
        'Voicemail Transcription',
    )
    return data_headers, data_list, source_path


@artifact_processor
def googleDialerPhoneLookupHistory(context):
    data_list = []
    source_path = ''

    for file_found in _db_files(context):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT normalized_number, phone_lookup_info, last_modified
            FROM PhoneLookupHistory
            ORDER BY last_modified DESC
        ''')

        for row in db_records:
            source_path = file_found
            name = label = lookup_uri = cnap_name = location = ''
            try:
                info, _ = decode_protobuf(row[1])
                # PhoneLookupInfo: 1 = default_cp2_info (Cp2ContactInfo: 1 name,
                # 5 label, 7 lookup_uri), 7 = cnap_info (1 name)
                name = _pb_str(info, '1', '1', '1')
                label = _pb_str(info, '1', '1', '5')
                lookup_uri = _pb_str(info, '1', '1', '7')
                cnap_name = _pb_str(info, '7', '1')
                location = _pb_str(info, '13', '1')
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # unparseable protobuf blob; keep the row with empty lookup fields
            data_list.append((
                _ms_to_utc(row[2]),
                row[0],
                name,
                label,
                cnap_name,
                location,
                lookup_uri,
            ))

    data_headers = (
        ('Last Modified', 'datetime'),
        ('Number', 'phonenumber'),
        'Contact Name',
        'Number Label',
        'CNAP Name',
        'Location Info',
        'Contact Lookup URI',
    )
    return data_headers, data_list, source_path


@artifact_processor
def googleDialerSmartdial(context):
    data_list = []
    source_path = ''

    for file_found in _db_files(context):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT display_name, phone_number, normalized_number, contact_id,
                   last_smartdial_update_time, last_time_used, times_used, starred
            FROM smartdial_table
            ORDER BY display_name
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                row[0],
                row[1],
                row[2],
                row[3],
                _ms_to_utc(row[4]),
                _ms_to_utc(row[5]),
                row[6],
                row[7],
            ))

    data_headers = (
        'Display Name',
        ('Phone Number', 'phonenumber'),
        ('Normalized Number', 'phonenumber'),
        'Contact ID',
        ('Last Update Time', 'datetime'),
        ('Last Time Used', 'datetime'),
        'Times Used',
        'Starred',
    )
    return data_headers, data_list, source_path


@artifact_processor
def googleDialerCachedNumberContacts(context):
    data_list = []
    source_path = ''

    for file_found in _db_files(context):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT time_last_updated, number, normalized_number, display_name,
                   phone_label, source_name, photo_uri, lookup_key
            FROM cached_number_contacts
            ORDER BY time_last_updated DESC
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                _ms_to_utc(row[0]),
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
            ))

    data_headers = (
        ('Time Last Updated', 'datetime'),
        ('Number', 'phonenumber'),
        ('Normalized Number', 'phonenumber'),
        'Display Name',
        'Phone Label',
        'Source Name',
        'Photo URI',
        'Lookup Key',
    )
    return data_headers, data_list, source_path
