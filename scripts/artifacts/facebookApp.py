"""
Parses Android Facebook application (com.facebook.katana) artifacts.

These are stores belonging to the Facebook app itself. The messaging mailbox the app
shares with Messenger is read by FacebookMessenger.py and is not repeated here. Two
exceptions are the contacts store, android_facebook_contacts_db, and the preference store,
prefs_db, which also exist under the same names in Messenger's (com.facebook.orca)
databases directory, with every column read here; the contacts and preferences artifacts
read both copies and report which app each row came from.
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
        "description": "Contacts held in the contacts store of the Facebook app and of "
                       "Messenger (android_facebook_contacts_db, contacts table), with the app "
                       "the store belongs to, the Facebook id, name fields and profile picture "
                       "links recorded for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Facebook",
        "notes": "This is each app's own contacts store and is separate from the msys mailbox "
                 "contacts reported by the Facebook Messenger artifacts. A row records a contact "
                 "the app held for this account; it does not establish that the contact was "
                 "entered on the device. The companion Contact Sync artifact reports the sync "
                 "times the store recorded. Messenger (com.facebook.orca) holds a database "
                 "of the same name under its own databases directory, with every column this "
                 "artifact reads, and both are read. The App column holds the "
                 "package directory the database was found in. On the nine corpus images "
                 "checked that hold a Messenger copy (cookbook_a11, hickman_a13, "
                 "samsungs20_a13, sharon_a13, pixel7a_a14, sharon_a14, anne_a15, "
                 "hc_pixel8pro_a16, hc_pixel8pro_a17), its contacts table was empty, so the "
                 "Messenger half of this artifact has not produced a row on them. On "
                 "sharon_a14 App held com.facebook.katana on all 33 rows for that reason. "
                 "Small Picture URL and Big Picture URL held the same link on all 186 rows of "
                 "the seven Facebook app stores with contacts on those images.",
        "paths": ('*/com.facebook.katana/databases/*android_facebook_contacts_db*',
                  '*/com.facebook.orca/databases/*android_facebook_contacts_db*'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "cookbook_a11": "Android 11 | 126 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "hickman_a13": "Android 13 | 0 rows",
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
        "description": "Contact synchronisation state from the contacts store of the Facebook "
                       "app and of Messenger: the recorded sync times and locale, and the "
                       "per-contact hashes each app kept as its upload snapshot.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-10-25",
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
                 "not establish what was transmitted. Messenger (com.facebook.orca) holds a "
                 "database of the same name under its own databases directory, with every "
                 "column this artifact reads, and both are read. The App column "
                 "holds the package directory the database was found in, and is needed "
                 "because the two apps keep separate snapshots: on sharon_a14 the Facebook "
                 "app held 12 snapshot rows and Messenger 19, and 10 local_contact_id values "
                 "appeared in both. A NULL hash is reported as empty. On the same nine corpus "
                 "images checked for the Contacts artifact that hold a Messenger copy, its contacts_db_properties table "
                 "was empty, so Messenger rows have so far been Upload Snapshot rows only. "
                 "Converted Value is filled only for keys ending in _time_ms (two on those "
                 "images) and for a delta cursor that decodes to text, so it is empty on every Upload Snapshot "
                 "row. On pixel7a_a14 and hickman_a13 only a Messenger copy was present, "
                 "so on each Record Type held Upload Snapshot on all 5 rows, App held "
                 "com.facebook.orca on all 5 rows and Converted Value held no value.",
        "paths": ('*/com.facebook.katana/databases/*android_facebook_contacts_db*',
                  '*/com.facebook.orca/databases/*android_facebook_contacts_db*'),
        "output_types": "standard",
        "artifact_icon": "refresh",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "cookbook_a11": "Android 11 | 5 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "hickman_a13": "Android 13 | 5 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsungs20_a13": "Android 13 | 5 rows",
            "sharon_a13": "Android 13 | 17 rows",
            "userb2_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 5 rows",
            "russell_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 36 rows",
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
                 "The rows are feed items the app cached, so their presence does not establish "
                 "that the user viewed them. seen_state and image_seen_state are reported as "
                 "stored and their meaning beyond the column name is not established; on "
                 "sharon_a13 "
                 "seen_state was 0 on 67 rows and 1 on 19. fetched_at is read as Unix "
                 "milliseconds. What event the column marks beyond its name is not established. "
                 "Media Count is the number of "
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
        "description": "Entities held in the mentions_entities table of the app's search "
                       "bootstrap database (search_bootstrap_db_uid): the Facebook id, display "
                       "name, entity type and friendship status of each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Facebook",
        "notes": "This is the list held in the mentions_entities table of the app's search "
                 "bootstrap database. A row records an entity the app held for this "
                 "account; it is not a record that the user searched for, mentioned or "
                 "interacted with that entity. type and friendship_status are reported as "
                 "stored. On sharon_a13 the 182 rows were 181 of type User and 1 of type "
                 "Place, and friendship_status was CANNOT_REQUEST on 162, OUTGOING_REQUEST on "
                 "18, CAN_REQUEST on 1 and UNSET_OR_UNRECOGNIZED_ENUM_VALUE on 1. On "
                 "sharon_a13 the bootstrap_db_properties table held only an api version, so no "
                 "fetch time for this list was found there.",
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
        "description": "Rows of the intervals table of "
                       "time_in_app_<user id>.db, with the start and end times and the stored "
                       "event codes.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Facebook",
        "notes": "One row per intervals table entry. start_walltime and end_walltime are read "
                 "as Unix seconds. The start_event and end_event integers are reported as "
                 "stored; nothing in the extraction maps them. The user id in the User ID "
                 "column is taken from the database file name. An interval is a record the app "
                 "wrote in its time_in_app store; what it measures beyond the table and column "
                 "names is not established, and this artifact does not interpret what "
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
        "description": "Key and value pairs from the preference store of the Facebook app "
                       "and of Messenger (prefs_db, preferences table), with the app the "
                       "store belongs to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Facebook",
        "notes": "Every row of each store's preferences table is reported rather than a "
                 "selected subset, so nothing is filtered out by this module's choices. Messenger "
                 "(com.facebook.orca) holds a database of the same name and schema under its "
                 "own databases directory, and both are read. The App column holds the "
                 "package directory the database was found in, and is needed because the two "
                 "apps keep separate stores that share key names: on sharon_a14 272 keys "
                 "appeared in both, and 142 of them held a different value in each. On the "
                 "eleven corpus images checked that hold a Messenger copy, it held 420 to 661 "
                 "rows. On pixel3_a11, pixel3_a12, pixel7a_a14 and hickman_a13 only a "
                 "Messenger copy was present, so App held com.facebook.orca on every row; on "
                 "galaxys10_a10, s20fe_a13, kevin_pocox7_a15 and adams_ss135dl_a13 only a "
                 "Facebook app copy was present, so App held com.facebook.katana on every row. "
                 "App does not tell Android users apart: on samsungs20_a13 a second Facebook "
                 "app copy under user 150 added 216 rows that also carry com.facebook.katana. "
                 "On sharon_a13 the Facebook app's 896 rows carried 327 keys under "
                 "logged_in_user_scoped, 116 under config and 88 under ras_blobs, and the "
                 "remainder were spread across smaller groups. The stored type integer is "
                 "reported as stored. Values are reported as written by the app and are not "
                 "interpreted.",
        "paths": ('*/com.facebook.katana/databases/prefs_db*',
                  '*/com.facebook.orca/databases/prefs_db*'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 203 rows",
            "cookbook_a11": "Android 11 | 1499 rows",
            "pixel3_a11": "Android 11 | 661 rows",
            "pixel3_a12": "Android 12 | 556 rows",
            "adams_ss135dl_a13": "Android 13 | 78 rows",
            "hickman_a13": "Android 13 | 494 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 75 rows",
            "samsungs20_a13": "Android 13 | 1548 rows",
            "sharon_a13": "Android 13 | 1414 rows",
            "userb2_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 607 rows",
            "russell_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 1674 rows",
            "anne_a15": "Android 15 | 1556 rows",
            "kevin_pocox7_a15": "Android 15 | 215 rows",
            "hc_pixel8pro_a16": "Android 16 | 1720 rows",
            "hc_pixel8pro_a17": "Android 17 | 1559 rows",
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


# The globs end in * so the seeker stages each database's sidecars alongside it, which is
# what lets SQLite apply a write ahead log on open. The artifact itself must not treat one
# as a database: opening it fails, and the failure is silent because the path still lands
# in source_path, which is what the report prints as the row's location.
_SIDECARS = ('-journal', '-wal', '-shm')


def _matching(context, pattern):
    """Databases whose base name matches, with duplicate storage views and sidecars removed."""
    return [p for p in unique_files(context)
            if not str(p).endswith(_SIDECARS)
            and re.search(pattern, os.path.basename(str(p)))]


_FB_APPS = ('com.facebook.katana', 'com.facebook.orca')


def _app(context, path):
    """The package directory a database sits in, read from a segment of its evidence-relative
    path so a folder name above the extraction cannot be mistaken for it."""
    segments = re.split(r'[\\/]', str(context.get_relative_path(str(path))))
    for segment in reversed(segments):
        if segment in _FB_APPS:
            return segment
    return ''


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
    source_paths = []
    for path in _matching(context, r'android_facebook_contacts_db$'):
        source_paths.append(str(path))
        app = _app(context, path)
        for row in _rows(path, '''
                SELECT contact_id, fbid, display_name, first_name, last_name,
                       small_picture_url, big_picture_url
                FROM contacts
                ORDER BY display_name'''):
            data_list.append((row[1], row[2], row[3], row[4], app, row[0], row[5], row[6]))
    data_headers = ('Facebook ID', 'Display Name', 'First Name', 'Last Name', 'App',
                    'Contact ID', 'Small Picture URL', 'Big Picture URL')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def facebookAppContactSync(context):
    data_list = []
    source_paths = []
    for path in _matching(context, r'android_facebook_contacts_db$'):
        source_paths.append(str(path))
        app = _app(context, path)
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
            data_list.append((converted, 'Sync Property', app, key, value))
        for local_id, contact_hash, extra_hash in _rows(path, '''
                SELECT local_contact_id, contact_hash, contact_extra_fields_hash
                FROM contacts_upload_snapshot
                ORDER BY local_contact_id'''):
            data_list.append(('', 'Upload Snapshot', app, f'local_contact_id {local_id}',
                              f'{contact_hash or ""} / {extra_hash or ""}'))
    data_headers = (('Converted Value', 'datetime'), 'Record Type', 'App', 'Key',
                    'Stored Value')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def facebookAppFeedCache(context):
    data_list = []
    source_paths = []
    for path in _matching(context, r'android_facebook_newsfeed_db$'):
        source_paths.append(str(path))
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
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def facebookAppMentionEntities(context):
    data_list = []
    source_paths = []
    for path in _matching(context, r'search_bootstrap_db'):
        source_paths.append(str(path))
        for row in _rows(path, '''
                SELECT fbid, name, subtext, type, friendship_status, profile_picture_uri
                FROM mentions_entities
                ORDER BY name'''):
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
    data_headers = ('Facebook ID', 'Name', 'Subtext', 'Type (as stored)',
                    'Friendship Status (as stored)', 'Profile Picture URI')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def facebookAppTimeInApp(context):
    data_list = []
    source_paths = []
    for path in _matching(context, r'^time_in_app_\d+\.db$'):
        source_paths.append(str(path))
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
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def facebookAppPreferences(context):
    data_list = []
    source_paths = []
    for path in _matching(context, r'^prefs_db$'):
        source_paths.append(str(path))
        app = _app(context, path)
        for key, value, stored_type in _rows(path, '''
                SELECT key, value, type FROM preferences ORDER BY key'''):
            data_list.append((app, key, value, stored_type))
    data_headers = ('App', 'Key', 'Value', 'Type (as stored)')
    return data_headers, data_list, '\n'.join(source_paths)
