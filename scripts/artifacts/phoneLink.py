__artifacts_v2__ = {
    "phonelink_accounts": {
        "name": "Phone Link - Linked Accounts",
        "description": "The accounts the Phone Link app stored on the phone, with the account "
                       "name and the account type as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Phone Link",
        "notes": "Read from the app's ACCOUNT_NAME Preferences DataStore file, a protobuf key and "
                 "value store. Each key is the account name joined to its type by a colon, and "
                 "each value is a small JSON object holding the same type and a username, which "
                 "is reported as Username.\n"
                 "The DataStore layout is Android's PreferencesProto: field 1 repeats an entry of "
                 "a key at 1 and a value at 2, and the value's field number gives its type, with "
                 "5 for a string. Reference: Android Jetpack (androidx), "
                 "datastore/datastore-preferences-proto/src/main/proto/preferences.proto, "
                 "https://github.com/androidx/androidx/blob/88f6829b8e444cc83280547803309dfb7741b214/datastore/datastore-preferences-proto/src/main/proto/preferences.proto#L9-L19."
                 "\n"
                 "A sibling ACCOUNT_DATA_NAME file holds one or more opaque encoded blobs per "
                 "account, keyed by the account key with an attribute name appended. The values "
                 "are encoded envelopes rather than plain text, and some attribute names "
                 "indicate credential material "
                 "such as a private key or an identity token, so no value from that file is "
                 "reported. The attribute names are reported as Stored Attributes, with their "
                 "count, so an examiner knows what the app held for each account.\n"
                 "Phone Link pairs the phone with a Windows computer through the Microsoft "
                 "account signed in on both, so a row names an account the app stored. Whether "
                 "that account was used for a pairing is not established by this file. Account "
                 "Type is the type string as stored. A row does not establish that "
                 "a computer is still linked, and the file carries no timestamp. Reference: "
                 "Microsoft Support, 'Phone Link requirements and setup', "
                 "https://support.microsoft.com/en-us/topic/phone-link-requirements-and-setup-cd2a1ee7-75a7-66a6-9d4e-bf22e735f9e3",
        "paths": ('*/com.microsoft.appmanager/files/datastore/ACCOUNT_NAME.preferences_pb',
                  '*/com.microsoft.appmanager/files/datastore/ACCOUNT_DATA_NAME.preferences_pb'),
        "output_types": "standard",
        "artifact_icon": "user-check",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 2 rows",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
    "phonelink_content_access": {
        "name": "Phone Link - Content Access Events",
        "description": "Rows from the content_access_event table of the app's eventstore, each "
                       "with a start time, a stored content type and a stored duration, including "
                       "rows that another state in the write-ahead log holds and the current state "
                       "does not",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Phone Link",
        "notes": "com.microsoft.appmanager is the phone side of Microsoft Phone Link, which pairs "
                 "a phone with a Windows PC. content_access_event is the only table in this "
                 "package holding dated event rows in the current state on the corpora below. start_time is Unix "
                 "milliseconds and duration is stored alongside it without a recorded unit, so "
                 "Duration (as stored) is reported unconverted. Content Type (as stored) and "
                 "Access Was Useful (as stored) are the schema's own integer columns; no source "
                 "for their code lists was located, so they are not expanded into labels. "
                 "Content Type was 22 on every row of seven of the eight corpora below and "
                 "carried 18 different values on samsunga53_a14. The states of the database hold "
                 "different row sets: this artifact reports the current state's rows and, through "
                 "scripts/sqlite_wal.py, rows another state holds that the current state does not, "
                 "read as in Snapchat - Messages (arroyo.db): each earlier committed state of the "
                 "log that SQLite can still read exactly, the previous log generation's left-over frames where every gate passes, and "
                 "frames after the last commit. Reading names where each row was found, and "
                 "Recovery Location the committed states and any previous-generation commits it "
                 "was read in, with first and last numbers, or the frames after the last commit "
                 "for an event read only there; a recovered event is "
                 "reported once, as the newest committed state holding it stored it, else the "
                 "previous generation's newest left-over commit, and an event "
                 "read only in frames after the last commit is labelled so. On the corpora below "
                 "the recovered share was 33 of 35 rows on anne_a15, 34 of 44 on falken_a326u_a13, "
                 "49 of 52 on kevin_pocox7_a15, 20 of 48 on s20fe_a13, 42 of 43 on samsunga53_a14, "
                 "7 of 26 on samsungs20_a13, 27 of 36 on sharon_a14 and 31 of 31 on userb2_a13, "
                 "where comparing the database file without its log against the file with it "
                 "applied recovered 1, 17, 7, 0, 16, 7, 5 and 9, all among them. 25 on "
                 "kevin_pocox7_a15 and 22 on userb2_a13 were read only in the previous log "
                 "generation; no tested log had frames after its last commit. Reading held one "
                 "value on all 31 rows of userb2_a13, whose current state holds no "
                 "content_access_event rows. The same "
                 "eventstore holds FcmNotificationEvent and agent_service_event, the latter with a "
                 "timestamp column. Both were empty in the current state on every corpus below; in "
                 "other states of the log they held up to 2 and 10 rows on samsunga53_a14, and "
                 "agent_service_event up to 10 on userb2_a13. They have no artifact here.",
        "paths": ('*/com.microsoft.appmanager/databases/eventstore*',),
        "output_types": "standard",
        "artifact_icon": "link",
        "sample_data": {
            "s20fe_a13": "Android 13 | com.microsoft.appmanager | 48 rows (28 current, 20 recovered)",
            "samsunga53_a14": "Android 14 | com.microsoft.appmanager | 43 rows (1 current, 42 recovered)",
            "sharon_a14": "Android 14 | com.microsoft.appmanager | 36 rows (9 current, 27 recovered)",
            "kevin_pocox7_a15": "Android 15 | com.microsoft.appmanager | 52 rows (3 current, 49 recovered)",
            "anne_a15": "Android 15 | com.microsoft.appmanager | 35 rows (2 current, 33 recovered)",
            "falken_a326u_a13": "Android 13 | com.microsoft.appmanager | 44 rows (10 current, 34 recovered)",
            "samsungs20_a13": "Android 13 | com.microsoft.appmanager | 26 rows (19 current, 7 recovered)",
            "userb2_a13": "Android 13 | com.microsoft.appmanager | 31 rows (0 current, 31 recovered)",
        },
    },
    "phonelink_phone_apps": {
        "name": "Phone Link - Linked Phone Apps",
        "description": "Rows from the phoneAppsTable of PhoneAppsDatabase, a list of "
                       "applications the Phone Link app keeps, with each one's "
                       "package name and version",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Phone Link",
        "notes": "phoneAppsTable holds one row per application the Phone Link app listed, with a "
                 "name, package name and version; how the app builds or uses the list is not "
                 "sourced here. Whether every row names an application installed on the phone "
                 "was not measured here; the rows can be compared against packages.xml. Last "
                 "Updated is Unix milliseconds and held the same value "
                 "on all 75 rows of the corpus below, so on that corpus it dates the inventory "
                 "as a whole rather than each application; what event it marks is not "
                 "established. Favorite Rank was 0 on every row there and is reported as stored; "
                 "what a non-zero value marks was not exercised here. The same database holds "
                 "browserHistoryTable, whose columns include a web address and a favicon, and "
                 "recentAppsTable, whose columns include a task id and an intent action; both "
                 "were present and empty on every corpus below and neither has an artifact here, "
                 "so their absence is a checked result rather than an omission. A corpus with "
                 "rows in browserHistoryTable would close a real gap, since its columns name a "
                 "web address and a favicon. content.db in the same package holds a content_view "
                 "table, 183 rows on the corpus below, carrying only a content type, an id, two "
                 "sequence numbers and a checksum; its purpose is not established here and it "
                 "names nothing an examiner could act "
                 "on, so it is not reported.",
        "paths": ('*/com.microsoft.appmanager/databases/PhoneAppsDatabase*',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "samsunga53_a14": "Android 14 | com.microsoft.appmanager | 75 rows",
            "cookbook_a11": "Android 11 | com.microsoft.appmanager | 0 rows",
        },
    },
}

import json
import os

from scripts import blackboxprotobuf
from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    get_sqlite_db_path,
    get_sqlite_db_records,
    logfunc,
)
from scripts.sqlite_wal import KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED, rows_not_in_current

import sqlite3

SIDECARS = ('-wal', '-shm', '-journal')

CURRENT_STATE = 'Current state'
OTHER_STATE = 'Recovered from another state of the log'
UNCOMMITTED_ONLY = 'Only in uncommitted frames'
WAL_KINDS = (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED)


def _stores(context, name):
    """The named database files, storage views collapsed and sidecars dropped."""
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or file_found.endswith(SIDECARS):
            continue
        if os.path.basename(file_found) == name:
            found.append(file_found)
    return found


def _wal_location(db_path, item):
    """Where in the write-ahead log a row was read, from an EarlierRow."""
    name = os.path.basename(db_path)
    parts = []
    if item.first_state is not None:
        first, last = item.first_state, item.last_state
        if last == 0:
            parts.append(f'{name} without its log, state 0')
        elif first == 0:
            parts.append(f'{name} and {name}-wal, committed states 0 to {last}')
        else:
            states = f'state {first}' if first == last else f'states {first} to {last}'
            parts.append(f'{name}-wal, committed {states}')
    if item.earlier_generation:
        first, last = item.earlier_generation
        commits = f'commit {first}' if first == last else f'commits {first} to {last}'
        parts.append(f'{name}-wal, previous log generation, left-over {commits}')
    if not parts:
        parts.append(f'{name}-wal, frames after the last commit')
    return '; '.join(parts)


def _read_states(db_path, query, key_index):
    """Rows from the database with its log applied, plus rows only another state holds.

    The table this reads is a rolling buffer the application trims, so the write
    ahead log can carry deletions: an earlier state then holds rows the current state
    no longer has. Every state scripts/sqlite_wal.py can read is compared with the
    current one on the table's own primary key, and a key the current state lacks is
    reported once, as the newest committed state holding it stored it. Which reading a
    row came from is reported rather than hidden, because a row absent from the current
    state is a different claim than one present in it.
    """
    rows = {}
    try:
        connection = sqlite3.connect(f'file:{get_sqlite_db_path(db_path)}?mode=ro', uri=True)
        for row in connection.cursor().execute(query):
            rows.setdefault(row[key_index], (row, CURRENT_STATE, ''))
        connection.close()
    except sqlite3.Error as error:
        logfunc(f'Phone Link: could not read {os.path.basename(db_path)}: {error}')
    try:
        _columns, found, wal = rows_not_in_current(str(db_path), query,
                                                   key_columns=[key_index], include=WAL_KINDS)
    except (OSError, sqlite3.Error) as error:
        logfunc(f'Phone Link: could not read the states of {os.path.basename(db_path)}: {error}')
        return rows
    logfunc(f'Phone Link {wal.summary()}')
    best = {}
    for item in found:
        key = item.values[key_index]
        if key in rows:
            continue
        rank = ((2, item.last_state) if item.first_state is not None else
                (1, item.earlier_generation[1]) if item.earlier_generation else (0, 0))
        if key not in best or rank > best[key][0]:
            best[key] = (rank, item)
    for key, (rank, item) in best.items():
        label = UNCOMMITTED_ONLY if rank[0] == 0 else OTHER_STATE
        rows[key] = (item.values, label, _wal_location(db_path, item))
    return rows


@artifact_processor
def phonelink_content_access(context):
    data_list = []
    source_paths = []
    query = ('SELECT uid, start_time, duration, content_type, access_was_useful '
             'FROM content_access_event')

    for db_path in _stores(context, 'eventstore'):
        rows = _read_states(db_path, query, 0)
        if not rows:
            continue
        source_paths.append(context.get_relative_path(db_path))
        for uid, (row, label, location) in sorted(rows.items(),
                                                   key=lambda item: item[1][0][1] or 0):
            _, start_time, duration, content_type, useful = row
            data_list.append((
                convert_unix_ts_to_utc(start_time / 1000) if start_time else '',
                duration if duration is not None else '',
                content_type if content_type is not None else '',
                useful if useful is not None else '',
                label,
                location,
                uid,
            ))

    data_headers = (
        ('Access Time', 'datetime'),
        'Duration (as stored)',
        'Content Type (as stored)',
        'Access Was Useful (as stored)',
        'Reading',
        'Recovery Location',
        'Event ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def phonelink_phone_apps(context):
    data_list = []
    source_paths = []

    for db_path in _stores(context, 'PhoneAppsDatabase'):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT lastUpdatedTime, appName, appPackageName, appVersion, favoriteRank, id
            FROM phoneAppsTable ORDER BY appName, phoneAppsTable.rowid
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for updated, app_name, package, version, favorite, app_id in rows:
            data_list.append((
                convert_unix_ts_to_utc(updated / 1000) if updated else '',
                app_name or '',
                package or '',
                version or '',
                favorite if favorite is not None else '',
                app_id if app_id is not None else '',
            ))

    data_headers = (
        ('Last Updated', 'datetime'),
        'App Name',
        'Package Name',
        'App Version',
        'Favorite Rank',
        'App ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


# Android Jetpack Preferences DataStore, preferences.proto: field 1 repeats an entry whose key
# is field 1 and whose value is field 2; the value's own field number carries its type.
_PREF_ENTRIES = '1'
_PREF_KEY = '1'
_PREF_VALUE = '2'
_PREF_STRING = '5'


def _preference_strings(path):
    """The string entries of a Preferences DataStore file, as {key: value}."""
    with open(path, 'rb') as handle:
        raw = handle.read()
    if not raw:
        return {}
    message, _ = blackboxprotobuf.decode_message(raw)
    entries = message.get(_PREF_ENTRIES)
    if isinstance(entries, dict):
        entries = [entries]
    out = {}
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        key = entry.get(_PREF_KEY)
        value = entry.get(_PREF_VALUE)
        if isinstance(key, (bytes, bytearray)):
            key = key.decode('utf-8', 'replace')
        if not isinstance(value, dict):
            continue
        text = value.get(_PREF_STRING)
        if isinstance(text, (bytes, bytearray)):
            out[str(key)] = text.decode('utf-8', 'replace')
    return out


@artifact_processor
def phonelink_accounts(context):
    data_headers = (
        'Account',
        'Username',
        'Account Type',
        'Stored Attributes',
        'Attribute Count',
        'Source File',
    )
    data_list = []
    sources = []

    names = {}
    blobs = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        base = os.path.basename(file_found)
        if base not in ('ACCOUNT_NAME.preferences_pb', 'ACCOUNT_DATA_NAME.preferences_pb'):
            continue
        try:
            entries = _preference_strings(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Phone Link: could not read {base}: {error}')
            continue
        if base == 'ACCOUNT_NAME.preferences_pb':
            for key, value in entries.items():
                names[key] = (value, file_found)
        else:
            for key in entries:
                account_key, _, attribute = key.rpartition(':')
                blobs.setdefault(account_key, []).append(attribute)

    for key, (value, file_found) in sorted(names.items()):
        account, _, account_type = key.partition(':')
        username = ''
        try:
            username = str(json.loads(value).get('username', ''))
        except (ValueError, AttributeError):
            username = ''
        data_list.append((
            account,
            username,
            account_type,
            ', '.join(sorted(blobs.get(key, []))),
            len(blobs.get(key, [])),
            context.get_relative_path(file_found),
        ))
        sources.append(file_found)

    return data_headers, data_list, '\n'.join(sorted(set(sources)))
