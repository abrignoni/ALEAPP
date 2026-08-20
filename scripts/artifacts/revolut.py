__artifacts_v2__ = {
    "revolut_payment_recipients": {
        "name": "Revolut - Recent Payment Recipients",
        "description": "Parses the recipients the Revolut Android app recorded as recently "
                       "paid, with the type of each recipient and the item it links to.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Revolut",
        "notes": "One row per recipient. Recipient Type is the value the row carries and was "
                 "BANK, CONTACT_CODE or CRYPTO on the tested device, where a contact code "
                 "row carries a readable handle and the others carry an identifier only; all "
                 "are reported as stored. Item ID and Item Type name the record the row "
                 "links to, which was a transaction on every row, but the transactions "
                 "themselves are not in this store and the app's own transaction and chat "
                 "databases are encrypted, so no amount, currency or date of a payment is "
                 "available here. Unread Sync is Unix milliseconds and is the app's own sync "
                 "marker for the unread counter beside it, not the time of a payment; it was "
                 "zero on some rows. The row records that the app listed the recipient, "
                 "which is not the same as a payment having been made. Field mapping was "
                 "done against three private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": (
            '*/com.revolut.revolut/databases/payments_recent_db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "credit-card"
    },
    "revolut_app_state": {
        "name": "Revolut - App State",
        "description": "Parses the times the Revolut Android app last refreshed its "
                       "configuration and its rate and help caches, with the size of each "
                       "cache.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Revolut",
        "notes": "One row per app data directory. Every timestamp is Unix milliseconds. The "
                 "three caches this row counts hold content the service supplied rather than "
                 "anything the account holder produced, so they are counted rather than "
                 "listed: the rate cache holds exchange rates, the help cache holds the "
                 "app's help articles in the language the app was using, and the device "
                 "cache holds a catalogue of device models that ran to tens of thousands of "
                 "rows on the tested devices. Their fetch times are reported because the "
                 "time the device last refreshed each one is a dated fact about the device. "
                 "Help Language is the language recorded on the help rows. The app's chat "
                 "and main data stores are encrypted with no key recoverable from the "
                 "extraction, so no message or transaction content is reported by this "
                 "module. Field mapping was done against three private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.revolut.revolut/databases/rates_database*',
            '*/com.revolut.revolut/databases/revolut_support_db*',
            '*/com.revolut.revolut/databases/android-devices.db*',
            '*/com.revolut.revolut/shared_prefs/configuration_storage.pref.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
}

import os
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
_PACKAGE = 'com.revolut.revolut'


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
        logfunc(f'Revolut: could not parse {os.path.basename(source_path)}: {ex}')
        return values
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        values[name] = element.get('value') if element.tag != 'string' else (element.text or '')
    return values


def _open(paths, name):
    '''The named database in one container, opened read only, or (None, None).'''
    for path in paths:
        if os.path.basename(path) == name:
            try:
                return path, open_sqlite_db_readonly(get_sqlite_db_path(path))
            except sqlite3.Error as ex:
                logfunc(f'Revolut: could not open {name}: {ex}')
    return None, None


def _rows(database, statement):
    '''The rows a statement returns, or nothing when the table is absent.'''
    if database is None:
        return []
    try:
        cursor = database.cursor()
        cursor.execute(statement)
        return cursor.fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Revolut: could not read from the database: {ex}')
        return []


def _single(database, statement):
    '''The first value the statement returns, or ''.'''
    rows = _rows(database, statement)
    if not rows or rows[0][0] is None:
        return ''
    return rows[0][0]


@artifact_processor
def revolut_payment_recipients(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        source_path, database = _open(paths, 'payments_recent_db')
        if database is None:
            continue
        relative = context.get_relative_path(source_path)
        for row in _rows(database, '''SELECT unreadSyncTimestamp, recipientId, recipientType,
                                             itemId, itemType, unreadCounter
                                      FROM payments_recent_v2'''):
            stamp, recipient, recipient_type, item, item_type, unread = row
            source_files.append(relative)
            data_list.append((
                _ms(stamp),
                str(recipient or ''),
                str(recipient_type or ''),
                str(item_type or ''),
                str(item or ''),
                str(unread if unread is not None else ''),
                relative,
            ))
        database.close()

    data_list.sort(key=lambda row: (str(row[0]), str(row[1])), reverse=True)

    data_headers = (
        ('Unread Sync', 'datetime'),
        'Recipient',
        'Recipient Type (as stored)',
        'Item Type (as stored)',
        'Item ID',
        'Unread Counter',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def revolut_app_state(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        rates_path, rates = _open(paths, 'rates_database')
        support_path, support = _open(paths, 'revolut_support_db')
        devices_path, devices = _open(paths, 'android-devices.db')

        configuration = {}
        for path in paths:
            if os.path.basename(path) == 'configuration_storage.pref.xml':
                configuration = _prefs(path)

        if rates is None and support is None and devices is None and not configuration:
            continue

        rate_fetched = _single(rates, 'SELECT MAX(time_stamp) FROM rates_cache') if rates else ''
        rate_rows = _single(rates, 'SELECT COUNT(*) FROM mid_rates_cache') if rates else ''
        help_rows = _single(support, 'SELECT COUNT(*) FROM light_faq') if support else ''
        help_language = _single(support, 'SELECT language FROM light_faq LIMIT 1') if support else ''
        node_rows = _single(support, 'SELECT COUNT(*) FROM pigeon_tree_node') if support else ''
        device_rows = _single(devices, 'SELECT COUNT(*) FROM devices') if devices else ''

        relative_paths = sorted({context.get_relative_path(path)
                                 for path in (rates_path, support_path, devices_path) if path})
        for path in paths:
            if os.path.basename(path) == 'configuration_storage.pref.xml':
                relative_paths.append(context.get_relative_path(path))
        source_files.extend(relative_paths)
        data_list.append((
            _ms(configuration.get('COMMON_CONFIG_LAST_MODIFIED_DATE')),
            _ms(rate_fetched),
            str(rate_rows if rate_rows != '' else ''),
            str(help_rows if help_rows != '' else ''),
            str(help_language or ''),
            str(node_rows if node_rows != '' else ''),
            str(device_rows if device_rows != '' else ''),
            str(configuration.get('file_version', '')),
            '; '.join(relative_paths),
        ))
        for database in (rates, support, devices):
            if database is not None:
                database.close()

    data_headers = (
        ('Configuration Last Modified', 'datetime'),
        ('Rates Last Fetched', 'datetime'),
        'Cached Rate Rows',
        'Cached Help Articles',
        'Help Language',
        'Cached Help Nodes',
        'Cached Device Catalogue Rows',
        'Configuration File Version',
        'Source Files',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
