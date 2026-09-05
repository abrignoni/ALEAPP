__artifacts_v2__ = {
    "vinted_items": {
        "name": "Vinted - Cached Listings",
        "description": "Parses the Vinted listings the Android app cached, including the "
                       "title, description, price, seller and the address of the listing.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Vinted",
        "notes": "One row per cached listing. The row holds the listing as a stored document "
                 "and the columns are read from it. Listing Created is the date string the "
                 "listing carries, reported as a date because it has no time part. Cache "
                 "Expires is Unix milliseconds and is the app's own expiry for the cached "
                 "copy, not an action by the account holder. Favourited is the flag the "
                 "listing carries for the viewing account. View Count and Favourite Count "
                 "are the counts the listing carries, which are the service's figures rather "
                 "than anything measured on the device. A cached listing records that the "
                 "app held it, not that the account holder looked at it. Field mapping was "
                 "done against three private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": (
            '*/fr.vinted/databases/vinted_database_2.db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "tag"
    },
    "vinted_favorites": {
        "name": "Vinted - Favourited Listings",
        "description": "Parses the listings in the Vinted Android app's favourites store, with the favourited flag as "
                       "stored and the listing title where the app also cached the listing.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Vinted",
        "notes": "One row per recorded listing. Favourited is the flag the row carries, "
                 "reported as stored, so a row marked false records that the app tracked the "
                 "listing rather than that it was favourited. Cache Expires is Unix "
                 "milliseconds and is the app's own expiry rather than an action by the "
                 "account holder; the table carries no time for when a listing was "
                 "favourited. Title and Address are filled from the cached listing of the "
                 "same identifier in the same app data directory, and are empty where the "
                 "app did not also cache that listing. On the tested device 16 rows were "
                 "recorded against 11 cached listings and 8 of the 16 matched one, so a row "
                 "without a title is one whose listing the app did not keep. Field "
                 "mapping was done against three private samples provided by Mattia; no "
                 "sample data is recorded for them.",
        "paths": (
            '*/fr.vinted/databases/vinted_database_2.db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "heart"
    },
    "vinted_feedbacks": {
        "name": "Vinted - Feedback",
        "description": "Parses the Vinted feedback entries the Android app cached, with the "
                       "rating, the text and the account that left it.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Vinted",
        "notes": "One row per feedback entry. Row Created is Unix milliseconds and records "
                 "when the app wrote the row, not when the feedback was left; the feedback's "
                 "own date is a date string with no time part and is reported separately. "
                 "Owner is the account the feedback belongs to, taken from the row rather "
                 "than from the document. Author is the account that left the feedback and "
                 "Reply Author is the account that replied, both read from the stored "
                 "document. Rating is the value the document carries, as stored. System "
                 "Feedback marks entries the service generated rather than a person. Field "
                 "mapping was done against three private samples provided by Mattia; no "
                 "sample data is recorded for them.",
        "paths": (
            '*/fr.vinted/databases/vinted_database_2.db*',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "star"
    },
    "vinted_session": {
        "name": "Vinted - Session and Locale",
        "description": "Parses the session counters and locale the Vinted Android app "
                       "records for itself.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Vinted",
        "notes": "One row per app data directory. Help Session Time is Unix milliseconds. "
                 "Sessions is the running count the app keeps, so it describes the whole "
                 "life of the install rather than one session. Locale and Currency are the "
                 "values the app recorded for itself. The tested samples carried no signed "
                 "in account name or identifier in this store; where an account can be named "
                 "at all it is named on the feedback rows instead. Field mapping was done "
                 "against three private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": (
            '*/fr.vinted/shared_prefs/user_session.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
}

import json
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
_PACKAGE = 'fr.vinted'
_DATABASE = 'vinted_database_2.db'


def _container(context, path):
    '''A key for the app data directory a matched file belongs to.

    Matched on a path segment equal to the package name rather than on a substring, so a
    directory that merely contains the name cannot be taken for the container. The key is
    canonicalised through storagePathViews, so the /data/data and /data/user/0 spellings
    of one directory collapse to one key while a second Android user stays separate. The
    listing index the favourites artifact builds is keyed on it, because a listing
    identifier is not unique across two app data directories.
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
        logfunc(f'Vinted: could not parse {os.path.basename(source_path)}: {ex}')
        return values
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        values[name] = element.get('value') if element.tag != 'string' else (element.text or '')
    return values


def _databases(context, paths):
    '''[(relative path, open database)] for each Vinted database in one container.'''
    opened = []
    for path in paths:
        if os.path.basename(path) != _DATABASE:
            continue
        try:
            opened.append((context.get_relative_path(path),
                           open_sqlite_db_readonly(get_sqlite_db_path(path))))
        except sqlite3.Error as ex:
            logfunc(f'Vinted: could not open {_DATABASE}: {ex}')
    return opened


def _rows(database, statement):
    '''The rows a statement returns, or nothing when the table is absent.

    The tested samples carried two schema versions, one without the listing and
    favourite tables, so a missing table is logged and yields nothing rather than costing
    the artifact every row it would have returned.
    '''
    try:
        cursor = database.cursor()
        cursor.execute(statement)
        return cursor.fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Vinted: could not read from the database: {ex}')
        return []


def _document(stored):
    '''The JSON document held in a column, or {} when it does not parse.'''
    if isinstance(stored, (bytes, bytearray)):
        stored = bytes(stored).decode('utf-8', 'replace')
    try:
        parsed = json.loads(stored)
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _amount(price):
    '''A price document rendered as amount and currency, or ''.'''
    if not isinstance(price, dict):
        return ''
    amount = price.get('amount')
    currency = price.get('currency_code') or ''
    if amount is None:
        return ''
    return f'{amount} {currency}'.strip()


def _listings(database):
    '''{listing id: document} for the cached listings in one database.'''
    index = {}
    for identifier, stored in _rows(database, 'SELECT id, json FROM items'):
        index[str(identifier)] = _document(stored)
    return index


@artifact_processor
def vinted_items(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for relative, database in _databases(context, paths):
            for identifier, stored, expires in _rows(
                    database, 'SELECT id, json, expires_at FROM items'):
                document = _document(stored)
                user = document.get('user') if isinstance(document.get('user'), dict) else {}
                brand = document.get('brand_dto') if isinstance(document.get('brand_dto'), dict) else {}
                source_files.append(relative)
                data_list.append((
                    str(document.get('created_at_ts') or ''),
                    _ms(expires),
                    str(document.get('title') or ''),
                    str(document.get('description') or ''),
                    _amount(document.get('price')),
                    str(document.get('status') or ''),
                    str(brand.get('title') or ''),
                    str(user.get('login') or ''),
                    str(user.get('id') or ''),
                    str(document.get('view_count', '')),
                    str(document.get('favourite_count', '')),
                    str(document.get('is_favourite', '')),
                    str(document.get('is_closed', '')),
                    str(document.get('is_reserved', '')),
                    str(document.get('url') or ''),
                    str(identifier or ''),
                    relative,
                ))
            database.close()

    data_headers = (
        ('Listing Created', 'date'),
        ('Cache Expires', 'datetime'),
        'Title',
        'Description',
        'Price',
        'Condition (as stored)',
        'Brand',
        'Seller Login',
        'Seller ID',
        'View Count (as stored)',
        'Favourite Count (as stored)',
        'Favourited (as stored)',
        'Closed (as stored)',
        'Reserved (as stored)',
        'Listing Address',
        'Listing ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def vinted_favorites(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for relative, database in _databases(context, paths):
            # Built from the listings in this database only, so one app data directory
            # cannot supply another's listing title against this one's rows.
            listings = _listings(database)
            for identifier, is_favorite, expires in _rows(
                    database, 'SELECT id, isFavorite, expires_at FROM favorites'):
                listing = listings.get(str(identifier), {})
                source_files.append(relative)
                data_list.append((
                    _ms(expires),
                    str(identifier or ''),
                    str(is_favorite if is_favorite is not None else ''),
                    str(listing.get('title') or ''),
                    _amount(listing.get('price')),
                    str(listing.get('url') or ''),
                    relative,
                ))
            database.close()

    data_headers = (
        ('Cache Expires', 'datetime'),
        'Listing ID',
        'Favourited (as stored)',
        'Title',
        'Price',
        'Listing Address',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def vinted_feedbacks(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for relative, database in _databases(context, paths):
            for identifier, stored, owner, created in _rows(
                    database, 'SELECT id, json, owner_id, created_at FROM feedbacks'):
                document = _document(stored)
                author = document.get('user') if isinstance(document.get('user'), dict) else {}
                comment = document.get('comment') if isinstance(document.get('comment'), dict) else {}
                replier = comment.get('user') if isinstance(comment.get('user'), dict) else {}
                source_files.append(relative)
                data_list.append((
                    _ms(created),
                    str(document.get('created_at_ts') or ''),
                    str(owner or ''),
                    str(author.get('login') or ''),
                    str(author.get('id') or ''),
                    str(document.get('rating', '')),
                    str(document.get('feedback') or ''),
                    str(comment.get('comment') or comment.get('feedback') or ''),
                    str(replier.get('login') or ''),
                    str(replier.get('id') or ''),
                    str(document.get('system_feedback', '')),
                    str(document.get('localization') or ''),
                    str(document.get('feedback_url') or ''),
                    str(identifier or ''),
                    relative,
                ))
            database.close()

    data_list.sort(key=lambda row: (str(row[0]), str(row[13])), reverse=True)

    data_headers = (
        ('Row Created', 'datetime'),
        ('Feedback Date', 'date'),
        'Owner ID',
        'Author Login',
        'Author ID',
        'Rating (as stored)',
        'Feedback',
        'Reply',
        'Reply Author Login',
        'Reply Author ID',
        'System Feedback (as stored)',
        'Localization (as stored)',
        'Feedback Address',
        'Feedback ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def vinted_session(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for path in paths:
            if os.path.basename(path) != 'user_session.xml':
                continue
            values = _prefs(path)
            if not values:
                continue
            relative = context.get_relative_path(path)
            source_files.append(relative)
            data_list.append((
                _ms(values.get('help_session_timestamp')),
                str(values.get('number_of_sessions', '')),
                str(values.get('iso_locale', '')),
                str(values.get('user_currency_code', '')),
                str(values.get('ab_anon_id', '')),
                str(values.get('help_session_uuid', '')),
                str(values.get('version_code', '')),
                str(values.get('push_notifications_toggle', '')),
                str(values.get('last_stored_bundle_id', '')),
                relative,
            ))

    data_headers = (
        ('Help Session Time', 'datetime'),
        'Sessions',
        'Locale',
        'Currency',
        'Anonymous ID',
        'Help Session UUID',
        'Version Code',
        'Push Notifications (as stored)',
        'Last Stored Bundle ID (as stored)',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
