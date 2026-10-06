__artifacts_v2__ = {
    "dropbox_files": {
        "name": "Dropbox - Files",
        "description": "Cloud files and folders listed in the Dropbox app database, with the path, "
                       "size, MIME type and the four stored time columns (server_modified_millis, modified_millis, local_modified, accessed_millis)",
        "author": "@AlexisBrignoni, Claude; @AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Dropbox",
        "notes": "Read from the dropbox table of the account database, whose file name carries a "
                 "prefix before -db.db, so the path allows for it. Whether that prefix is the "
                 "account id was not established. Only the first database matched is read. This is "
                 "the listing the app had cached, not necessarily the full account contents. "
                 "Shared folder id and is_dir, is_favorite, read_only and is_vault_folder are "
                 "reported as stored, retaining NULL, zero and other values without assigning "
                 "boolean meanings.",
        "paths": ('*/com.dropbox.android/databases/*-db.db*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.dropbox.android | 15 rows",
        },
    },
    "dropbox_account": {
        "name": "Dropbox - Account",
        "description": "Text candidates and selected preferences from the Dropbox account preferences database",
        "author": "@AlexisBrignoni, Claude; @AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Dropbox",
        "notes": "Read from the DropboxAccountPrefs table of the first matched preferences database. "
                 "ACCOUNT_INFO, FULL_ACCOUNT_INFO_V2 and PLAN_INFO_V2 are base64 wrapped protobuf; "
                 "printable ASCII runs are extracted without binding them to protobuf fields. "
                 "The first email-shaped and dbid:-prefixed regex matches and each cleaned run "
                 "starting with 'Dropbox ' produce text candidates, not verified identity or plan "
                 "values. Value / Derived Display keeps the existing display, including stripped "
                 "wrapping characters for Dropbox-prefixed candidates. Raw Matched Candidate Text "
                 "(JSON) lists each accepted match and its source preference in encounter order: "
                 "exact regex substrings for email/dbid candidates, full pre-clean printable runs "
                 "for Dropbox-prefixed candidates. Equal display candidates remain aggregated; "
                 "repeats are retained in the raw list. This is not a lossless protobuf decoder. "
                 "Repeated preference names keep the last row read. Source Preference names the "
                 "preferences used. Timestamp preferences retain the existing Unix milliseconds "
                 "conversion to UTC; direct preferences have no raw candidate cell.",
        "paths": ('*/com.dropbox.android/databases/*-prefs.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.dropbox.android | 11 rows",
        },
    },
    "dropbox_thumbnails": {
        "name": "Dropbox - Thumbnails",
        "description": "Rows of the thumbnail_info table of the Dropbox app database, with the cloud path, size and format each names",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Dropbox",
        "notes": "Read from the thumbnail_info table of the account database. A row is a "
                 "thumbnail_info record naming a cloud path, a size and a format. This artifact "
                 "does not locate or show any image file, and whether a cached image exists for "
                 "a row was not checked.",
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
import json
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
            record[8],
            record[9],
            record[10],
            record[11],
            record[12],
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
        'is_dir (as stored)',
        'is_favorite (as stored)',
        'Shared Folder ID',
        'read_only (as stored)',
        'is_vault_folder (as stored)',
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
    raw_matches = {}

    def _record(prop, value, pref_name, raw_text):
        if not value:
            return
        matched.setdefault((prop, value), []).append(pref_name)
        raw_matches.setdefault((prop, value), []).append({
            'source_preference': pref_name, 'matched_text': raw_text})

    for pref_name in ('ACCOUNT_INFO', 'FULL_ACCOUNT_INFO_V2', 'PLAN_INFO_V2'):
        strings = _protobuf_strings(prefs.get(pref_name))
        if not strings:
            continue
        joined = ' '.join(strings)
        email = _EMAIL_RE.search(joined)
        dbid = _DBID_RE.search(joined)
        if email:
            _record('Email', email.group(0), pref_name, email.group(0))
        if dbid:
            _record('Dropbox ID', dbid.group(0), pref_name, dbid.group(0))
        for value in strings:
            cleaned = value.strip('"*() ')
            if cleaned and cleaned.startswith('Dropbox '):
                _record('Plan', cleaned, pref_name, value)

    candidate_labels = {
        'Email': 'Email-shaped Text Candidate',
        'Dropbox ID': 'dbid:-prefixed Text Candidate',
        'Plan': 'Dropbox-prefixed Text Candidate',
    }
    for (prop, value), pref_names in matched.items():
        raw_text = json.dumps(raw_matches[(prop, value)], ensure_ascii=False,
                              separators=(',', ':'))
        data_list.append((candidate_labels[prop], value, raw_text, ', '.join(pref_names)))

    for pref_name, label in _TEXT_PREFS.items():
        if prefs.get(pref_name):
            data_list.append((label, prefs[pref_name], '', pref_name))

    for pref_name, label in _TIME_PREFS.items():
        value = prefs.get(pref_name)
        if not value:
            continue
        try:
            data_list.append((label, convert_unix_ts_to_utc(int(value)), '', pref_name))
        except (TypeError, ValueError):
            data_list.append((label, value, '', pref_name))

    data_headers = (
        'Property / Candidate',
        'Value / Derived Display',
        'Raw Matched Candidate Text (JSON)',
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
