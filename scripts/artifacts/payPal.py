__artifacts_v2__ = {
    "paypal_app_sessions": {
        "name": "PayPal - App Sessions",
        "description": "Parses the app sessions the PayPal Android app recorded in its "
                       "tracking store, with the first and last event time of each.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "PayPal",
        "notes": "One row per session recorded in the tracking store. The store holds one "
                 "row per event, and events are grouped onto their session rather than "
                 "listed, because every event payload is encrypted: each row carries a flag "
                 "marking it encrypted and that flag was set on every row of both tested "
                 "samples, so no event content is available. First Event and Last Event are "
                 "reported as stored and Session Date as a date, because the stored value "
                 "carries no time zone and nothing in the extraction establishes which one "
                 "the app used; a millisecond timestamp elsewhere in the app was months "
                 "away from these values and could not settle it, so the values are not "
                 "converted and are not offered as a UTC datetime. Events counts the rows "
                 "in the session and API Versions lists the versions those rows carry, as "
                 "stored. Field mapping was done against two private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.paypal.android.p2pmobile/databases/tracking*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "clock"
    },
    "paypal_device": {
        "name": "PayPal - Device and Encrypted Stores",
        "description": "Parses the device and installation identifiers the PayPal Android "
                       "app records, with a count of the encrypted account stores it holds.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "PayPal",
        "notes": "One row per app data directory. Configuration Cached is Unix "
                 "milliseconds. The account itself is not reported because it is not "
                 "readable: the app keeps its account state in AndroidX "
                 "EncryptedSharedPreferences files, whose entry names and values are both "
                 "encrypted under a Tink keyset that is itself wrapped by an Android "
                 "Keystore key the extraction does not contain, and it holds its tokens in "
                 "separately encrypted values beside them. Encrypted Preference Files and "
                 "Encrypted Entries count what is present and unreadable, so an examiner "
                 "can see how much account state the device holds rather than inferring it "
                 "from an empty report; the keyset entry itself is not counted as an entry. "
                 "Keep Me Logged In Opt Out is the one account state value stored in the "
                 "clear beside the encrypted ones, as stored. The app's home and hub "
                 "databases are not reported: they hold the server supplied templates that "
                 "lay out the app's home screen rather than anything the account holder "
                 "did. Field mapping was done against two private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.paypal.android.p2pmobile/shared_prefs/PayPal.xml',
            '*/com.paypal.android.p2pmobile/shared_prefs/version.6.shared.keys.xml',
            '*/com.paypal.android.p2pmobile/shared_prefs/FoundationAccount.AccountState.xml',
            '*/com.paypal.android.p2pmobile/shared_prefs/*_encrypted.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "smartphone"
    },
}

import os
import re
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_path,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_PACKAGE = 'com.paypal.android.p2pmobile'
_KEYSET = '__androidx_security_crypto'
_DATE = re.compile(r'^(\d{4}-\d{2}-\d{2})')


def _container(context, path):
    '''A key for the app data directory a matched file belongs to.

    Matched on a path segment equal to the package name rather than on a substring, so a
    directory that merely contains the name cannot be taken for the container. The key is
    canonicalised through storagePathViews, so the /data/data and /data/user/0 spellings
    of one directory collapse to one key while a second Android user stays separate.
    '''
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    parts = relative.split('/')
    for position, part in enumerate(parts):
        if part == _PACKAGE:
            return canonical_path('/'.join(parts[:position + 1]))[0]
    return canonical_path(relative)[0]


def _by_container(context):
    '''{container key: [path]} for the files this artifact matched.'''
    grouped = {}
    for file_found in unique_files(context):
        grouped.setdefault(_container(context, file_found), []).append(str(file_found))
    return grouped


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _prefs(source_path):
    '''{name: text} for an Android shared preferences file.'''
    values = {}
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'PayPal: could not parse {os.path.basename(source_path)}: {ex}')
        return values
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        values[name] = element.get('value') if element.tag != 'string' else (element.text or '')
    return values


def _rows(database, statement):
    '''The rows a statement returns, or nothing when the table is absent.'''
    try:
        cursor = database.cursor()
        cursor.execute(statement)
        return cursor.fetchall()
    except sqlite3.Error as ex:
        logfunc(f'PayPal: could not read from the tracking store: {ex}')
        return []


@artifact_processor
def paypal_app_sessions(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for path in paths:
            if os.path.basename(path) != 'tracking':
                continue
            try:
                database = open_sqlite_db_readonly(get_sqlite_db_path(path))
            except sqlite3.Error as ex:
                logfunc(f'PayPal: could not open the tracking store: {ex}')
                continue
            relative = context.get_relative_path(path)
            for row in _rows(database, '''SELECT session_id, MIN(create_timestamp),
                                                 MAX(create_timestamp), COUNT(*),
                                                 GROUP_CONCAT(DISTINCT api_version),
                                                 MAX(is_encrypted)
                                          FROM session_event GROUP BY session_id'''):
                session, first, last, count, versions, encrypted = row
                match = _DATE.match(str(first or ''))
                source_files.append(relative)
                data_list.append((
                    match.group(1) if match else '',
                    str(first or ''),
                    str(last or ''),
                    count,
                    str(session or ''),
                    str(versions or ''),
                    str(encrypted if encrypted is not None else ''),
                    relative,
                ))
            database.close()

    data_list.sort(key=lambda row: (str(row[1]), str(row[4])), reverse=True)

    data_headers = (
        ('Session Date', 'date'),
        'First Event (as stored)',
        'Last Event (as stored)',
        'Events',
        'Session ID',
        'API Versions (as stored)',
        'Events Encrypted (as stored)',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def paypal_device(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        general = {}
        keys = {}
        account = {}
        encrypted_files = 0
        encrypted_entries = 0
        relative_paths = []

        for path in paths:
            name = os.path.basename(path)
            relative_paths.append(context.get_relative_path(path))
            if name == 'PayPal.xml':
                general = _prefs(path)
            elif name == 'version.6.shared.keys.xml':
                keys = _prefs(path)
            elif name == 'FoundationAccount.AccountState.xml':
                account = _prefs(path)
            elif name.endswith('_encrypted.xml'):
                entries = _prefs(path)
                encrypted_files += 1
                # The stored keyset is not an account value, so it is not counted as one.
                encrypted_entries += len([entry for entry in entries
                                          if not entry.startswith(_KEYSET)])

        if not any((general, keys, account, encrypted_files)):
            continue

        source_files.extend(relative_paths)
        data_list.append((
            _ms(general.get('elmo_cache_time')),
            str(general.get('shared_pref_device_id', '')),
            str(keys.get('app_installation_guid', '')),
            str(general.get('shared_pref_app_version', '')),
            encrypted_files,
            encrypted_entries,
            str(account.get('kmliOptOutFlag', '')),
            '; '.join(sorted(relative_paths)),
        ))

    data_headers = (
        ('Configuration Cached', 'datetime'),
        'Device ID',
        'App Installation GUID',
        'App Version',
        'Encrypted Preference Files',
        'Encrypted Entries',
        'Keep Me Logged In Opt Out (as stored)',
        'Source Files',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
