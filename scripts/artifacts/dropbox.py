__artifacts_v2__ = {
    "dropbox_files": {
        "name": "Dropbox - Files",
        "description": "Cloud files and folders listed in the Dropbox app database, with the path, "
                       "size, MIME type and the modification times the service recorded",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Dropbox",
        "notes": "Read from the dropbox table of the account database, which the app names with the "
                 "account id, for example <account id>-db.db, so the path allows for the prefix. "
                 "This is the listing the app had cached, not necessarily the full account "
                 "contents. Shared folder id and the vault and read-only flags are reported as the "
                 "app stored them.",
        "paths": ('*/com.dropbox.android/databases/*-db.db*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.dropbox.android | 15 rows",
        },
    },
    "dropbox_account": {
        "name": "Dropbox - Account",
        "description": "The signed-in Dropbox account, with the email, display name, account id and "
                       "plan read from the account preference values",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Dropbox",
        "notes": "Read from the DropboxAccountPrefs table of the account preferences database. The "
                 "ACCOUNT_INFO, FULL_ACCOUNT_INFO_V2 and PLAN_INFO_V2 values are base64 wrapped "
                 "protobuf; the readable strings are extracted from them rather than decoded field "
                 "by field, so each is reported as the value it was matched from. Timestamp "
                 "preferences are reported as epoch milliseconds converted to UTC.",
        "paths": ('*/com.dropbox.android/databases/*-prefs.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.dropbox.android | account reported",
        },
    },
    "dropbox_thumbnails": {
        "name": "Dropbox - Thumbnails",
        "description": "Thumbnails the Dropbox app cached, with the cloud path they belong to and "
                       "the size and format that was cached",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Dropbox",
        "notes": "Read from the thumbnail_info table of the account database. A row shows a "
                 "thumbnail was cached for that path; the image bytes are held elsewhere in the "
                 "app cache.",
        "paths": ('*/com.dropbox.android/databases/*-db.db*',),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.dropbox.android | 23 rows",
        },
    },
}

import base64
import binascii
import re

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records

# Preference names whose value is an epoch milliseconds timestamp.
_TIME_PREFS = {
    'USER_SIGN_UP_DATE': 'User Sign Up Date',
    'LAST_USER_LOGIN_TIME': 'Last User Login Time',
    'NOTIFICATION_PERMISSION_REQUEST_TIMESTAMP': 'Notification Permission Requested',
    'LAST_TIME_OVER_QUOTA_WARNING_PAGE_SHOWN': 'Over Quota Warning Shown',
}

# Preference names reported as stored text.
_TEXT_PREFS = {
    'PHOTO_UPLOAD_LAST_DESTINATION': 'Photo Upload Last Destination',
    'LAST_URI': 'Last URI',
    'IS_SIGN_UP': 'Is Sign Up',
    'UPGRADE_SOURCE_FOR_JTBD': 'Upgrade Source',
}

_EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
_DBID_RE = re.compile(r'dbid:[A-Za-z0-9_-]+')


def _db_by_suffix(files_found, suffix):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if file_found.endswith(suffix):
            return file_found
    return ''


def _protobuf_strings(value):
    """Readable strings from a base64 wrapped protobuf preference value."""
    if not value:
        return []
    try:
        raw = base64.b64decode(value + '==')
    except (binascii.Error, ValueError):
        return []
    return [match.decode('utf-8', 'replace')
            for match in re.findall(rb'[ -~]{4,}', raw)]


@artifact_processor
def dropbox_files(context):
    source_path = _db_by_suffix(context.get_files_found(), '-db.db')
    data_list = []

    query = '''
    SELECT server_modified_millis, modified_millis, local_modified, accessed_millis,
           _display_name, path, bytes, mime_type, is_dir, is_favorite, shared_folder_id,
           read_only, is_vault_folder, revision
    FROM dropbox
    ORDER BY server_modified_millis
    '''
    for record in get_sqlite_db_records(source_path, query):
        data_list.append((
            convert_unix_ts_to_utc(record[0]) if record[0] else '',
            convert_unix_ts_to_utc(record[1]) if record[1] else '',
            convert_unix_ts_to_utc(record[2]) if record[2] else '',
            convert_unix_ts_to_utc(record[3]) if record[3] else '',
            record[4],
            record[5],
            record[6],
            record[7],
            'Yes' if record[8] else 'No',
            'Yes' if record[9] else 'No',
            record[10],
            'Yes' if record[11] else 'No',
            'Yes' if record[12] else 'No',
            record[13],
        ))

    data_headers = (
        ('Server Modified', 'datetime'),
        ('Modified', 'datetime'),
        ('Local Modified', 'datetime'),
        ('Accessed', 'datetime'),
        'Name',
        'Path',
        'Size (bytes)',
        'MIME Type',
        'Is Directory',
        'Favourite',
        'Shared Folder ID',
        'Read Only',
        'Vault Folder',
        'Revision',
    )
    return data_headers, data_list, source_path


@artifact_processor
def dropbox_account(context):
    source_path = _db_by_suffix(context.get_files_found(), '-prefs.db')
    data_list = []

    prefs = {}
    for record in get_sqlite_db_records(
            source_path, 'SELECT pref_name, pref_value FROM DropboxAccountPrefs'):
        prefs[record[0]] = record[1]

    # Identity values live in the base64 protobuf blobs. The same value appears in more than
    # one preference, so each (property, value) pair is reported once with every preference it
    # was matched from, rather than repeated per preference.
    matched = {}

    def _record(prop, value, pref_name):
        if not value:
            return
        matched.setdefault((prop, value), []).append(pref_name)

    for pref_name in ('ACCOUNT_INFO', 'FULL_ACCOUNT_INFO_V2', 'PLAN_INFO_V2'):
        strings = _protobuf_strings(prefs.get(pref_name))
        if not strings:
            continue
        joined = ' '.join(strings)
        email = _EMAIL_RE.search(joined)
        dbid = _DBID_RE.search(joined)
        if email:
            _record('Email', email.group(0), pref_name)
        if dbid:
            _record('Dropbox ID', dbid.group(0), pref_name)
        for value in strings:
            cleaned = value.strip('"*() ')
            if cleaned and cleaned.startswith('Dropbox '):
                _record('Plan', cleaned, pref_name)

    for (prop, value), pref_names in matched.items():
        data_list.append((prop, value, ', '.join(pref_names)))

    for pref_name, label in _TEXT_PREFS.items():
        if prefs.get(pref_name):
            data_list.append((label, prefs[pref_name], pref_name))

    for pref_name, label in _TIME_PREFS.items():
        value = prefs.get(pref_name)
        if not value:
            continue
        try:
            data_list.append((label, convert_unix_ts_to_utc(int(value)), pref_name))
        except (TypeError, ValueError):
            data_list.append((label, value, pref_name))

    data_headers = (
        'Property',
        'Value',
        'Source Preference',
    )
    return data_headers, data_list, source_path


@artifact_processor
def dropbox_thumbnails(context):
    source_path = _db_by_suffix(context.get_files_found(), '-db.db')
    data_list = []

    query = '''
    SELECT dropbox_canon_path, thumb_size, format, revision
    FROM thumbnail_info
    ORDER BY dropbox_canon_path
    '''
    for record in get_sqlite_db_records(source_path, query):
        data_list.append((record[0], record[1], record[2], record[3]))

    data_headers = (
        'Cloud Path',
        'Thumbnail Size',
        'Format',
        'Revision',
    )
    return data_headers, data_list, source_path
