__artifacts_v2__ = {
    "truecaller_call_history": {
        "name": "Truecaller - Call History",
        "description": "Parses the call history recorded by the Truecaller Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Truecaller",
        "notes": "Read from the history table of tc.db. The timestamp column is Unix "
                 "milliseconds. The type, action and feature columns are integers with no "
                 "mapping recoverable from the extraction, so they are reported as stored; "
                 "type held 1, 2 and 3 in the tested sample and action held 0 and 4. The "
                 "duration and ringing duration columns carry no unit in the schema and "
                 "none was established here, so they are also reported as stored: duration "
                 "ranged 0 to 3792 and ringing duration 0 to 584062 in the tested sample. "
                 "cached_name is the name the app had cached for the number at the time, "
                 "which is not necessarily a name from the phonebook. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/com.truecaller/databases/tc.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "phone"
    },
    "truecaller_contacts": {
        "name": "Truecaller - Contacts",
        "description": "Parses the contacts cached by the Truecaller Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Truecaller",
        "notes": "One row per raw_contact. Numbers come from the data table where "
                 "data_type is 4 and the value is in data1: that pairing is data-proven "
                 "rather than assumed, because contact_default_number equalled data1 on all "
                 "1093 such rows of the tested sample. The remaining data_type values are "
                 "undocumented and are not interpreted here. contact_search_time is Unix "
                 "milliseconds while insert_timestamp in the same row is Unix seconds; the "
                 "two resolved to the same instant on the tested sample, which is what "
                 "established each unit. Spam score, spam type, badges, source and gender "
                 "are reported as stored. A cached contact is not evidence the user knows "
                 "the person: the app caches results of its own lookups. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/com.truecaller/databases/tc.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users"
    },
    "truecaller_im_users": {
        "name": "Truecaller - Messaging Users",
        "description": "Parses the messaging user directory cached by the Truecaller Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Truecaller",
        "notes": "Read from the msg_im_users table of tc.db. The date column is Unix "
                 "milliseconds and registration_timestamp in the same row is Unix seconds; "
                 "the two units were established from their values in the tested sample. "
                 "The table records numbers the app resolved to a messaging peer. It is not "
                 "a record of messages: the message tables in the same database held no "
                 "rows in the tested sample, so no message artifact is offered here. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": ('*/com.truecaller/databases/tc.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-circle"
    },
    "truecaller_sms_senders": {
        "name": "Truecaller - SMS Senders",
        "description": "Parses the SMS sender information cached by the Truecaller Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Truecaller",
        "notes": "Read from the sender_info table of insights.db, which records senders the "
                 "app classified. The table carries no timestamp. Sender type, source type, "
                 "smart features status and enabled grammars are reported as stored. The "
                 "same database also holds a categorizer_probability table, which is model "
                 "data rather than a record of the user's messages, and is not parsed. "
                 "Field mapping was done against a private sample provided by Mattia; no "
                 "sample data is recorded for it.",
        "paths": ('*/com.truecaller/databases/insights.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-square"
    },
    "truecaller_call_cache": {
        "name": "Truecaller - Call Cache",
        "description": "Parses the call lookup cache of the Truecaller Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Truecaller",
        "notes": "Read from the call_cache table of calling-cache.db. The timestamp column "
                 "is Unix milliseconds. The state column is reported as stored. The max age "
                 "column is a cache lifetime rather than an event time. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": ('*/com.truecaller/databases/calling-cache.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "database"
    },
    "truecaller_settings": {
        "name": "Truecaller - Settings",
        "description": "Parses the app and account settings of the Truecaller Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Truecaller",
        "notes": "Every entry of the app's own preference files is reported as stored, with "
                 "its declared preference type. Values are not interpreted and absence of a "
                 "key is not evidence a feature was unused. Entries whose value is a Unix "
                 "second or millisecond timestamp are additionally rendered in the "
                 "Timestamp column, chosen by magnitude, and that column is empty for "
                 "everything else. Field mapping was done against a private sample provided "
                 "by Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.truecaller/shared_prefs/tc.settings.xml',
            '*/com.truecaller/shared_prefs/core_settings.xml',
            '*/com.truecaller/shared_prefs/tc_premium_state_settings.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
}

import os
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Values at or above this are milliseconds, below are seconds. 10**12 ms is 2001 and
# 10**12 s is far outside any plausible record, so the split is unambiguous for both the
# columns this module reads and the preference values it renders opportunistically.
_MS_THRESHOLD = 10 ** 12


def _rows(source_path, sql):
    '''Rows for sql. Empty on any SQLite error, which is logged.'''
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if not db:
        return []
    cursor = db.cursor()
    try:
        rows = cursor.execute(sql).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Could not query {os.path.basename(source_path)}: {ex}')
        rows = []
    db.close()
    return rows


def _from_ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _from_seconds(value):
    '''A Unix second value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(seconds=value)


def _by_magnitude(value):
    '''A Unix timestamp as a UTC datetime, reading it as seconds or milliseconds.

    Used only where the column is not one whose unit was established from the data, so
    the choice is made per value from its magnitude rather than asserted for the column.
    '''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _from_ms(value) if abs(value) >= _MS_THRESHOLD else _from_seconds(value)


def _files_named(context, *names):
    '''The matched files whose basename is one of names, one per storage view.'''
    return [path for path in unique_files(context)
            if os.path.basename(path) in names]


@artifact_processor
def truecaller_call_history(context):
    data_list = []
    sources = []

    query = '''
        SELECT timestamp, duration, ringing_duration, normalized_number, raw_number,
               cached_name, country_code, number_type, type, action, feature,
               filter_source, is_important_call, important_call_note, assistant_state,
               subscription_id, tc_id, event_id, call_log_id
        FROM history
        ORDER BY timestamp DESC
    '''

    for source_path in _files_named(context, 'tc.db'):
        relative_path = context.get_relative_path(source_path)
        for row in _rows(source_path, query):
            data_list.append((
                _from_ms(row[0]),
                row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17],
                row[18],
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Timestamp', 'datetime'),
        'Duration (as stored)',
        'Ringing Duration (as stored)',
        ('Normalized Number', 'phonenumber'),
        ('Raw Number', 'phonenumber'),
        'Cached Name',
        'Country Code',
        'Number Type (as stored)',
        'Type (as stored)',
        'Action (as stored)',
        'Feature (as stored)',
        'Filter Source (as stored)',
        'Is Important Call (as stored)',
        'Important Call Note',
        'Assistant State (as stored)',
        'Subscription ID',
        'Truecaller ID',
        'Event ID',
        'Call Log ID',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def truecaller_contacts(context):
    data_list = []
    sources = []

    # data_type 4 with the value in data1 is the contact's number. Proven on the tested
    # sample by contact_default_number equalling data1 on every one of those rows.
    query = '''
        SELECT rc.contact_search_time, rc.insert_timestamp, rc.contact_name,
               rc.contact_default_number,
               (SELECT group_concat(d.data1, ', ') FROM data d
                 WHERE d.data_raw_contact_id = rc._id AND d.data_type = 4),
               rc.contact_alt_name, rc.contact_transliterated_name, rc.contact_company,
               rc.contact_job_title, rc.contact_about, rc.contact_gender,
               rc.contact_spam_score, rc.contact_spam_type, rc.spam_categories,
               rc.is_suspected_fraud, rc.contact_badges, rc.contact_is_favorite,
               rc.contact_source, rc.contact_image_url, rc.search_query, rc.tc_id,
               rc.contact_phonebook_id
        FROM raw_contact rc
        ORDER BY rc.contact_search_time DESC
    '''

    for source_path in _files_named(context, 'tc.db'):
        relative_path = context.get_relative_path(source_path)
        for row in _rows(source_path, query):
            data_list.append((
                _from_ms(row[0]),
                _from_seconds(row[1]),
                row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10],
                row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
                row[19], row[20], row[21],
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Search Time', 'datetime'),
        ('Insert Timestamp', 'datetime'),
        'Contact Name',
        ('Default Number', 'phonenumber'),
        'Numbers',
        'Alt Name',
        'Transliterated Name',
        'Company',
        'Job Title',
        'About',
        'Gender (as stored)',
        'Spam Score (as stored)',
        'Spam Type (as stored)',
        'Spam Categories (as stored)',
        'Is Suspected Fraud (as stored)',
        'Badges (as stored)',
        'Is Favorite (as stored)',
        'Contact Source (as stored)',
        'Image URL',
        'Search Query',
        'Truecaller ID',
        'Phonebook ID',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def truecaller_im_users(context):
    data_list = []
    sources = []

    query = '''
        SELECT date, registration_timestamp, normalized_number, fallback_name,
               im_peer_id, tc_id, join_im_notification
        FROM msg_im_users
        ORDER BY date DESC
    '''

    for source_path in _files_named(context, 'tc.db'):
        relative_path = context.get_relative_path(source_path)
        for row in _rows(source_path, query):
            data_list.append((
                _from_ms(row[0]),
                _from_seconds(row[1]),
                row[2], row[3], row[4], row[5], row[6],
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Date', 'datetime'),
        ('Registration Timestamp', 'datetime'),
        ('Normalized Number', 'phonenumber'),
        'Fallback Name',
        'IM Peer ID',
        'Truecaller ID',
        'Join Notification (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def truecaller_sms_senders(context):
    data_list = []
    sources = []

    query = '''
        SELECT sender, sender_name, sender_type, country_code, source_type,
               smart_features_status, grammars_enabled
        FROM sender_info
        ORDER BY sender
    '''

    for source_path in _files_named(context, 'insights.db'):
        relative_path = context.get_relative_path(source_path)
        for row in _rows(source_path, query):
            data_list.append(row + (relative_path,))
            sources.append(source_path)

    data_headers = (
        'Sender',
        'Sender Name',
        'Sender Type (as stored)',
        'Country Code',
        'Source Type (as stored)',
        'Smart Features Status (as stored)',
        'Grammars Enabled (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def truecaller_call_cache(context):
    data_list = []
    sources = []

    query = 'SELECT timestamp, number, state, maxAgeSeconds FROM call_cache ORDER BY timestamp DESC'

    for source_path in _files_named(context, 'calling-cache.db'):
        relative_path = context.get_relative_path(source_path)
        for row in _rows(source_path, query):
            data_list.append((_from_ms(row[0]), row[1], row[2], row[3], relative_path))
            sources.append(source_path)

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Number', 'phonenumber'),
        'State (as stored)',
        'Max Age Seconds',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def truecaller_settings(context):
    data_list = []
    sources = []

    for source_path in unique_files(context):
        relative_path = context.get_relative_path(source_path)
        try:
            root = ET.parse(source_path).getroot()
        except (ET.ParseError, OSError) as ex:
            logfunc(f'Could not parse {os.path.basename(source_path)}: {ex}')
            continue

        for element in root:
            name = element.get('name')
            if not name:
                continue
            value = element.get('value') if element.get('value') is not None else element.text
            timestamp = _by_magnitude(value) if element.tag == 'long' else ''
            data_list.append((
                timestamp,
                os.path.basename(source_path),
                name,
                element.tag,
                value,
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Timestamp', 'datetime'),
        'Preference File',
        'Setting',
        'Type',
        'Value (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
