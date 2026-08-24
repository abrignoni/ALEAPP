"""
Parses Android Facebook application (com.facebook.katana) artifacts.

These are stores belonging to the Facebook app itself. The messaging mailbox the app
shares with Messenger is read by FacebookMessenger.py and is not repeated here.
"""

import base64
import datetime
import os
import re
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import unique_files

__artifacts_v2__ = {
    "facebookAppContacts": {
        "name": "Facebook - Contacts",
        "description": "Contacts held in the Facebook app's own contacts store "
                       "(android_facebook_contacts_db, contacts table), with the Facebook id, "
                       "name fields and profile picture links the app recorded for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Facebook",
        "notes": "This is the app's own contacts store and is separate from the msys mailbox "
                 "contacts reported by the Facebook Messenger artifacts. The store is populated "
                 "by a server sync, so a row records a contact the app held for this account "
                 "rather than one entered on the device. The companion Contact Sync artifact "
                 "reports when that sync last ran.",
        "paths": ('*/com.facebook.katana/databases/*android_facebook_contacts_db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "cookbook_a11": "Android 11 | 126 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsungs20_a13": "Android 13 | 1 row",
            "sharon_a13": "Android 13 | 11 rows",
            "userb2_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 33 rows",
            "anne_a15": "Android 15 | 11 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
        },
    },
    "facebookAppContactSync": {
        "name": "Facebook - Contact Sync State",
        "description": "Contact synchronisation state from the Facebook app's contacts store: "
                       "the recorded sync times and locale, and the per-contact hashes the app "
                       "kept as its upload snapshot.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Facebook",
        "notes": "Two sources are combined. Rows labelled Sync Property come from "
                 "contacts_db_properties, where last_contacts_sync_client_time_ms and "
                 "last_full_contacts_sync_client_time_ms are Unix milliseconds and are converted "
                 "at this call site; contacts_delta_cursor is base64 and, where it decodes to "
                 "text, the decoded value is reported beside it. Rows labelled Upload Snapshot "
                 "come from contacts_upload_snapshot, which stores a local contact id and "
                 "hashes rather than contact details, so the names behind them are not "
                 "recoverable from this table. The presence of snapshot rows records that the "
                 "app kept an upload snapshot for that many local contacts; this artifact does "
                 "not establish what was transmitted.",
        "paths": ('*/com.facebook.katana/databases/*android_facebook_contacts_db*',),
        "output_types": "standard",
        "artifact_icon": "refresh",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "cookbook_a11": "Android 11 | 5 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsungs20_a13": "Android 13 | 5 rows",
            "sharon_a13": "Android 13 | 17 rows",
            "userb2_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 17 rows",
            "anne_a15": "Android 15 | 5 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 5 rows",
            "hc_pixel8pro_a17": "Android 17 | 5 rows",
        },
    },
    "facebookAppFeedCache": {
        "name": "Facebook - Cached Feed Stories",
        "description": "Metadata for news feed stories the app cached "
                       "(android_facebook_newsfeed_db, home_stories), with the feed the story "
                       "belonged to, when it was fetched, and the stored seen state.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Facebook",
        "notes": "The table holds cache bookkeeping, not story content: there is no author or "
                 "message column, and this artifact reports the keys and state the app stored. "
                 "The rows are server-supplied feed items the app downloaded, so their presence "
                 "does not establish that the user viewed them. seen_state and image_seen_state "
                 "are the app's own record of that and are reported as stored; on sharon_a13 "
                 "seen_state was 0 on 67 rows and 1 on 19. fetched_at is Unix "
                 "milliseconds, converted at this call site. Media Count is the number of "
                 "home_stories_media rows sharing the story's dedup_key.",
        "paths": ('*/com.facebook.katana/databases/*android_facebook_newsfeed_db*',),
        "output_types": "standard",
        "artifact_icon": "news",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "cookbook_a11": "Android 11 | 245 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsungs20_a13": "Android 13 | 149 rows",
            "sharon_a13": "Android 13 | 86 rows",
            "userb2_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 295 rows",
            "anne_a15": "Android 15 | 269 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 159 rows",
            "hc_pixel8pro_a17": "Android 17 | 214 rows",
        },
    },
    "facebookAppMentionEntities": {
        "name": "Facebook - Mention Typeahead Entities",
        "description": "Entities the app downloaded for the mention typeahead "
                       "(search_bootstrap_db_uid, mentions_entities): the Facebook id, display "
                       "name, entity type and friendship status of each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Facebook",
        "notes": "This is a bootstrap list the app fetched so it can offer suggestions while "
                 "the user types a mention. A row records an entity the app held for this "
                 "account; it is not a record that the user searched for, mentioned or "
                 "interacted with that entity. type and friendship_status are reported as "
                 "stored. On sharon_a13 the 182 rows were 181 of type User and 1 of type "
                 "Place, and friendship_status was CANNOT_REQUEST on 162, OUTGOING_REQUEST on "
                 "18, CAN_REQUEST on 1 and UNSET_OR_UNRECOGNIZED_ENUM_VALUE on 1. The "
                 "companion bootstrap_db_properties table recorded only an api version, so no "
                 "fetch time for this list was available.",
        "paths": ('*/com.facebook.katana/databases/*search_bootstrap_db*',),
        "output_types": "standard",
        "artifact_icon": "at",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "cookbook_a11": "Android 11 | 377 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 182 rows",
            "userb2_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 422 rows",
            "anne_a15": "Android 15 | 61 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
        },
    },
    "facebookAppTimeInApp": {
        "name": "Facebook - Time In App",
        "description": "App usage intervals from the intervals table of "
                       "time_in_app_<user id>.db, with the start and end times and the stored "
                       "event codes.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Facebook",
        "notes": "One row per intervals table entry. start_walltime and end_walltime are stored "
                 "as epoch seconds. The start_event and end_event integers are reported as "
                 "stored; nothing in the extraction maps them. The user id in the User ID "
                 "column is taken from the database file name. An interval is a record the app "
                 "wrote about its own foreground time; this artifact does not interpret what "
                 "activity occurred within it. The store has the same shape as the Instagram "
                 "one read by instagramTimeInApp.",
        "paths": ('*/com.facebook.katana/databases/time_in_app_*.db*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "cookbook_a11": "Android 11 | 19 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsungs20_a13": "Android 13 | 10 rows",
            "sharon_a13": "Android 13 | 43 rows",
            "userb2_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 39 rows",
            "anne_a15": "Android 15 | 23 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 11 rows",
            "hc_pixel8pro_a17": "Android 17 | 11 rows",
        },
    },
    "facebookAppPreferences": {
        "name": "Facebook - Preferences",
        "description": "Key and value pairs from the Facebook app preference store "
                       "(prefs_db, preferences table).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Facebook",
        "notes": "Every row in the table is reported rather than a selected subset, so nothing "
                 "is filtered out by this module's choices. Most keys are configuration: on "
                 "sharon_a13 896 rows carried 327 keys under logged_in_user_scoped, 116 under "
                 "config and 88 under ras_blobs, and the remainder were spread across smaller "
                 "groups. The stored type integer is reported as stored. Values are reported as "
                 "written by the app and are not interpreted.",
        "paths": ('*/com.facebook.katana/databases/prefs_db*',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 203 rows",
            "cookbook_a11": "Android 11 | 1018 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 75 rows",
            "samsungs20_a13": "Android 13 | 216 rows",
            "sharon_a13": "Android 13 | 896 rows",
            "userb2_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 1130 rows",
            "anne_a15": "Android 15 | 1039 rows",
            "kevin_pocox7_a15": "Android 15 | 215 rows",
            "hc_pixel8pro_a16": "Android 16 | 1172 rows",
            "hc_pixel8pro_a17": "Android 17 | 1069 rows",
        },
    },
}

UNIX_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


def _rows(source_path, sql, params=()):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return []
    try:
        return db.execute(sql, params).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Facebook: query failed on {source_path}: {ex}')
        return []


def _matching(context, pattern):
    """Files whose base name matches, with duplicate storage views removed."""
    return [p for p in unique_files(context) if re.search(pattern, os.path.basename(str(p)))]


def _unix_seconds(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    return UNIX_EPOCH + datetime.timedelta(seconds=value)


def _unix_millis(value):
    """Unix milliseconds. Converted here because the column's unit is known, rather than
    handing the value to a converter that infers the unit from magnitude."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    return UNIX_EPOCH + datetime.timedelta(milliseconds=value)


@artifact_processor
def facebookAppContacts(context):
    data_list = []
    source_path = ''
    for path in _matching(context, r'android_facebook_contacts_db$'):
        source_path = path
        for row in _rows(path, '''
                SELECT contact_id, fbid, display_name, first_name, last_name,
                       small_picture_url, big_picture_url
                FROM contacts
                ORDER BY display_name'''):
            data_list.append((row[1], row[2], row[3], row[4], row[0], row[5], row[6]))
    data_headers = ('Facebook ID', 'Display Name', 'First Name', 'Last Name', 'Contact ID',
                    'Small Picture URL', 'Big Picture URL')
    return data_headers, data_list, source_path


@artifact_processor
def facebookAppContactSync(context):
    data_list = []
    source_path = ''
    for path in _matching(context, r'android_facebook_contacts_db$'):
        source_path = path
        for key, value in _rows(path, 'SELECT key, value FROM contacts_db_properties'):
            converted = ''
            if isinstance(key, str) and key.endswith('_time_ms'):
                converted = _unix_millis(value)
            elif isinstance(key, str) and key.endswith('delta_cursor') and value:
                try:
                    decoded = base64.b64decode(str(value)).decode('utf-8')
                    converted = decoded if decoded.isprintable() else ''
                except (ValueError, UnicodeDecodeError):
                    converted = ''
            data_list.append((converted, 'Sync Property', key, value))
        for local_id, contact_hash, extra_hash in _rows(path, '''
                SELECT local_contact_id, contact_hash, contact_extra_fields_hash
                FROM contacts_upload_snapshot
                ORDER BY local_contact_id'''):
            data_list.append(('', 'Upload Snapshot', f'local_contact_id {local_id}',
                              f'{contact_hash} / {extra_hash}'))
    data_headers = (('Converted Value', 'datetime'), 'Record Type', 'Key', 'Stored Value')
    return data_headers, data_list, source_path


@artifact_processor
def facebookAppFeedCache(context):
    data_list = []
    source_path = ''
    for path in _matching(context, r'android_facebook_newsfeed_db$'):
        source_path = path
        media = {}
        for dedup_key, count in _rows(path, '''
                SELECT dedup_key, COUNT(*) FROM home_stories_media GROUP BY dedup_key'''):
            media[dedup_key] = count
        for row in _rows(path, '''
                SELECT fetched_at, feed_type, seen_state, image_seen_state, dedup_key,
                       sort_key, ranking_weight, cursor
                FROM home_stories
                ORDER BY fetched_at DESC'''):
            data_list.append((_unix_millis(row[0]), row[1], row[2], row[3],
                              media.get(row[4], 0), row[4], row[5], row[6], row[7]))
    data_headers = (('Fetched At', 'datetime'), 'Feed Type', 'Seen State (as stored)',
                    'Image Seen State (as stored)', 'Media Count', 'Dedup Key', 'Sort Key',
                    'Ranking Weight', 'Cursor')
    return data_headers, data_list, source_path


@artifact_processor
def facebookAppMentionEntities(context):
    data_list = []
    source_path = ''
    for path in _matching(context, r'search_bootstrap_db'):
        source_path = path
        for row in _rows(path, '''
                SELECT fbid, name, subtext, type, friendship_status, profile_picture_uri
                FROM mentions_entities
                ORDER BY name'''):
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
    data_headers = ('Facebook ID', 'Name', 'Subtext', 'Type (as stored)',
                    'Friendship Status (as stored)', 'Profile Picture URI')
    return data_headers, data_list, source_path


@artifact_processor
def facebookAppTimeInApp(context):
    data_list = []
    source_path = ''
    for path in _matching(context, r'^time_in_app_\d+\.db$'):
        source_path = path
        match = re.fullmatch(r'time_in_app_(\d+)\.db', os.path.basename(str(path)))
        user_id = match.group(1) if match else ''
        for start_wall, end_wall, start_event, end_event, seq in _rows(path, '''
                SELECT start_walltime, end_walltime, start_event, end_event, seq_num
                FROM intervals
                ORDER BY start_walltime DESC'''):
            data_list.append((_unix_seconds(start_wall), _unix_seconds(end_wall),
                              start_event, end_event, seq, user_id))
    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'),
                    'Start Event (as stored)', 'End Event (as stored)', 'Sequence Number',
                    'User ID')
    return data_headers, data_list, source_path


@artifact_processor
def facebookAppPreferences(context):
    data_list = []
    source_path = ''
    for path in _matching(context, r'^prefs_db$'):
        source_path = path
        for key, value, stored_type in _rows(path, '''
                SELECT key, value, type FROM preferences ORDER BY key'''):
            data_list.append((key, value, stored_type))
    data_headers = ('Key', 'Value', 'Type (as stored)')
    return data_headers, data_list, source_path
