__artifacts_v2__ = {
    "tutanota_accounts": {
        "name": "Tutanota - Accounts",
        "description": "Parses the Tutanota (Tuta Mail) accounts the Android client holds credentials for.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "ccl_chromium_reader",
        "category": "Tutanota",
        "notes": "The client keeps its account list in three different shapes depending on release, and "
                 "all three are read. Newer releases store it in the PersistedCredentials table of the Room "
                 "database databases/tuta-db. Older releases store it in the web app's own configuration "
                 "under the tutanotaConfig key of the WebView Local Storage, where _credentials is keyed "
                 "by user id and each entry carries a credentialInfo holding login, userId and type. Older "
                 "still, at configuration version 2, _credentials is a list rather than a mapping and "
                 "its entries carry mailAddress, accessToken, encryptedPassword and userId with no "
                 "credentialInfo and no type. Those are decoded the way the app converts them itself in "
                 "migrateConfigV2to3 (src/applications/common/misc/DeviceConfig.ts at tutao/tutanota "
                 "80c8e4cb): the login is the mailAddress where it contains an @ and the type is "
                 "internal, and otherwise the login is the user id and the type is external, because at "
                 "that version an external user's address was their user id. On "
                 "the three tested images all three shapes appear: the Android 11 image holds the version 2 "
                 "list, the Android 12 image holds the version 3 mapping, and both carried no "
                 "PersistedCredentials table at all so their accounts were readable only from the "
                 "WebView configuration, while the Android 14 image had migrated to the table and left "
                 "_credentials empty. The Stored In column records which of the two a row came from. The "
                 "client records that migration itself in the isCredentialsMigratedToNative and "
                 "hasParticipatedInCredentialsMigration flags, reported by the App Configuration "
                 "artifact. Credential Type is decoded from the app's own CredentialType enum, whose "
                 "members are internal and external (app-android/tutashared/src/main/java/de/tutao/"
                 "tutashared/CredentialType.kt at tutao/tutanota 80c8e4cb). Credential Encryption Mode "
                 "is read from the credentialEncryptionMode key of the same database and decoded from "
                 "CredentialEncryptionMode, whose members are DEVICE_LOCK, SYSTEM_PASSWORD and "
                 "BIOMETRICS; the app's own comments state that DEVICE_LOCK does not require immediate "
                 "user interaction to access the key while the other two do (app-android/tutashared/src/"
                 "main/java/de/tutao/tutashared/credentials/CredentialEncryptionMode.kt at the same "
                 "commit). The encryptedPassword, databaseKey, accessToken and encryptedPassphraseKey "
                 "columns of that table are ciphertext wrapped by a key held in the Android Keystore, so "
                 "they are not reported and are not recoverable from a filesystem extraction. A row "
                 "records that the client held credentials for that account and does not by itself "
                 "establish who used it. WebView Local Storage retains superseded copies of the "
                 "configuration, and every copy is read; on both tested images the superseded copies "
                 "held no account the newest copy did not, so no account was recovered from them alone. "
                 "Rows are de-duplicated on login and user id within a container. Every container in the "
                 "extraction is read, so a second Android user's account is reported rather than "
                 "replacing the first. The app was present on 2 of the 19 registered Android corpora "
                 "when this was written. The other stores in the app's directory were examined and are "
                 "not parsed here, for the reasons given. databases/offline_<userid>.sqlite is the "
                 "offline mail cache and is encrypted: its header is not the SQLite magic, and the key "
                 "that would open it is the databaseKey column of PersistedCredentials, which is itself "
                 "wrapped by a key held in the Android Keystore, so mail content is not recoverable from "
                 "a filesystem extraction alone. The WebView IndexedDB store under app_webview holds the "
                 "app's own search index, whose indexed words and suggestion entries are ciphertext; its "
                 "readable parts are index bookkeeping, and one of them, the per group indexTimestamp, "
                 "is not a wall clock time but an internal id range marker that was 0 or 4398046511103 "
                 "on the tested images, so it is not reported as a date. That store also carries a "
                 "lastEventIndexTimeMs value that does decode as Unix milliseconds on both tested "
                 "images, which is a candidate for a separate artifact and is not covered here. The "
                 "app's app_webview Cookies and Web Data stores are already read by the Chrome artifacts, "
                 "whose path patterns are not anchored to a package, so they are not duplicated here. "
                 "The app's shared_prefs hold only theme and battery optimisation prompt state.",
        "paths": ('*/de.tutao.tutanota/databases/tuta-db*',
                  '*/de.tutao.tutanota/app_webview/Default/Local Storage/leveldb/*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | de.tutao.tutanota vc 396351 | 1 rows",
            "pixel3_a12": "Android 12 | 1 rows",
            "pixel3_a11": "Android 11 | de.tutao.tutanota vc 376070 | 1 rows",
        }
    },
    "tutanota_configuration": {
        "name": "Tutanota - App Configuration",
        "description": "Parses the Tutanota (Tuta Mail) Android client's server, notification and credential settings.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "ccl_chromium_reader",
        "category": "Tutanota",
        "notes": "One row per container, combining the KeyValue table of databases/tuta-db with the "
                 "newest tutanotaConfig record in the WebView Local Storage. The KeyValue key names are "
                 "the app's own constants in app-android/tutashared/src/main/java/de/tutao/tutashared/"
                 "push/SseStorage.kt at tutao/tutanota 80c8e4cb: deviceIdentifier is the push "
                 "identifier, sseOrigin is the server the client opens its event stream against, and "
                 "lastMissedNotificationCheckTime is stored through getLong and set from a Java Date, so "
                 "it is Unix milliseconds. That key is spelled with literal single quote characters "
                 "around the name in the app's own constant, and both that spelling and the unquoted one "
                 "are accepted here. Server Origin is worth reading because Tutanota can be self hosted: "
                 "on the two tested images it held the vendor's own hosts, which differed between them "
                 "as the product was renamed. Connect Timeout, Extended Notification Mode and Config "
                 "Version are reported as stored because no mapping for their values was sourced. "
                 "Theme is read from _themeId, or from _theme on configuration version 2 where that key "
                 "carried the name instead. Credentials Migrated To Native Store and Setup Complete are "
                 "the client's own booleans "
                 "and are what explains which store the Accounts artifact found a given account in. "
                 "A row draws on both stores, so each is cited in its own column: Source File is the "
                 "database the KeyValue settings came from and Configuration Source File is the WebView "
                 "Local Storage the remaining columns came from. Columns are blank where the release did "
                 "not write that key: the Android 12 image "
                 "carried no credentialEncryptionMode and no extendedNotificationMode, and its "
                 "configuration record predates the migration flags, so Credential Encryption Mode is "
                 "empty, Extended Notification Mode is empty, Credentials Migrated To Native Store is "
                 "empty, Participated In Credentials Migration is empty and Setup Complete is empty for "
                 "it. The app's own shared_prefs hold only theme and battery optimisation "
                 "prompt state and are not read. The language, hidden calendars, expanded mail folders "
                 "and offline time range values in the same configuration record were empty on both "
                 "tested images and are not reported.",
        "paths": ('*/de.tutao.tutanota/databases/tuta-db*',
                  '*/de.tutao.tutanota/app_webview/Default/Local Storage/leveldb/*'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "pixel7a_a14": "Android 14 | de.tutao.tutanota vc 396351 | 1 rows",
            "pixel3_a12": "Android 12 | 1 rows",
            "pixel3_a11": "Android 11 | de.tutao.tutanota vc 376070 | 1 rows",
        }
    },
    "tutanota_calendar_alarms": {
        "name": "Tutanota - Calendar Alarms",
        "description": "Parses the calendar alarm notifications scheduled by the Tutanota (Tuta Mail) Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Tutanota",
        "notes": "Read from the AlarmNotification table of databases/tuta-db. The table stores the "
                 "encrypted form of the alarm, so most of it is not readable: the app's own entity is "
                 "named EncryptedAlarmNotificationEntity and its decrypt function passes summary, "
                 "eventStart and eventEnd through decryptString and decryptDate with a session key, so "
                 "the event title and both event times are ciphertext and are not reported. The repeat "
                 "rule columns frequency, interval, timeZone, endType, endValue and excludedDates belong "
                 "to EncryptedRepeatRule and are ciphertext for the same reason, so only whether a "
                 "repeat rule is present is reported. The alarm identifier and the user id are not "
                 "encrypted: the same decrypt function assigns alarmIdentifier straight from the stored "
                 "identifier and assigns user directly, while the trigger beside it is decrypted "
                 "(app-android/tutashared/src/main/java/de/tutao/tutashared/alarms/"
                 "EncryptedAlarmInfo.kt and EncryptedAlarmNotificationEntity.kt at tutao/tutanota "
                 "80c8e4cb). Operation is stored as the ordinal of the app's OperationType enum, whose "
                 "members are declared CREATE, UPDATE, DELETE in that order, giving 0, 1 and 2 "
                 "(app-android/tutashared/src/main/java/de/tutao/tutashared/ModelTypes.kt line 18 at "
                 "the same commit); the conversion is the app's own OperationTypeConverter, which reads "
                 "the value as an index into that enum. Any value outside that range is reported as "
                 "stored. The push identifier list id and element id are the IdTuple the alarm's "
                 "notification session key belongs to. This artifact is code present and was not "
                 "exercised: the table was empty on both tested images, so the operation decoding and "
                 "the repeat rule flag have not been run against real rows and are sourced from the "
                 "app's code rather than proven from data.",
        "paths": ('*/de.tutao.tutanota/databases/tuta-db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "pixel7a_a14": "Android 14 | de.tutao.tutanota vc 396351 | 0 rows; AlarmNotification "
                            "table present and empty, confirmed by reading the table directly both "
                            "with and without its write ahead log",
            "pixel3_a12": "Android 12 | 0 rows; AlarmNotification table present and empty, "
                           "confirmed by reading the table directly both with and without its "
                           "write ahead log",
            "pixel3_a11": "Android 11 | de.tutao.tutanota vc 376070 | 0 rows; AlarmNotification "
                           "table present and empty, confirmed by reading the table directly",
        }
    }
}

import json
import os
import sqlite3

from scripts.ilapfuncs import (artifact_processor, convert_unix_ts_to_utc, logfunc,
                              open_sqlite_db_readonly)
from scripts.artifacts.storagePathViews import unique_files

PACKAGE = 'de.tutao.tutanota'
DB_SUFFIX = 'databases/tuta-db'
LOCALSTORAGE_MARKER = 'app_webview/Default/Local Storage/leveldb/'
CONFIG_SCRIPT_KEY = 'tutanotaConfig'

# app-android/tutashared/src/main/java/de/tutao/tutashared/ModelTypes.kt line 18,
# tutao/tutanota 80c8e4cb. Stored as the enum ordinal by OperationTypeConverter.
OPERATION_TYPES = {0: 'CREATE', 1: 'UPDATE', 2: 'DELETE'}

# app-android/tutashared/src/main/java/de/tutao/tutashared/push/SseStorage.kt, same commit.
# The app's own constant for this key includes the single quote characters.
LAST_CHECK_KEYS = ("'lastMissedNotificationCheckTime'", 'lastMissedNotificationCheckTime')


def _container_root(path):
    """The app data directory a matched file sits in, or None."""
    path = str(path).replace('\\', '/')
    marker = f'/{PACKAGE}/'
    index = path.find(marker)
    if index == -1:
        return None
    return path[:index + len(marker)]


def _containers(files_found):
    """{container root: {'db': path or None, 'localstorage': dir or None}}.

    An extraction can hold the app's data for more than one Android user, and each
    container holds a different account, so every one is kept rather than the first.
    """
    containers = {}
    for file_found in files_found:
        file_found = str(file_found).replace('\\', '/')
        if os.path.isdir(file_found):
            continue
        root = _container_root(file_found)
        if root is None:
            continue
        entry = containers.setdefault(root, {'db': None, 'localstorage': None})
        # The glob also matches the -wal and -shm sidecars. Only the database itself is
        # opened, so a sidecar can never become the path this artifact reports.
        if file_found.endswith(DB_SUFFIX):
            entry['db'] = file_found
        elif LOCALSTORAGE_MARKER in file_found:
            entry['localstorage'] = file_found[:file_found.index(LOCALSTORAGE_MARKER)
                                               + len(LOCALSTORAGE_MARKER)].rstrip('/')
    return containers


def _table_names(cursor):
    return {row[0] for row in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}


def _key_values(db_path):
    """{key: value} from the KeyValue table, or {} when it cannot be read."""
    values = {}
    connection = open_sqlite_db_readonly(db_path)
    if connection is None:
        return values
    try:
        cursor = connection.cursor()
        if 'KeyValue' not in _table_names(cursor):
            logfunc(f'Tutanota: {db_path} has no KeyValue table, skipped')
            return values
        for key, value in cursor.execute('SELECT key, value FROM KeyValue'):
            values[key] = value
    except sqlite3.Error as error:
        logfunc(f'Tutanota: could not read KeyValue from {db_path}: {error}')
    finally:
        connection.close()
    return values


def _persisted_credentials(db_path):
    """[(login, userId, type)] from PersistedCredentials.

    Absent on releases that kept credentials in the web app configuration instead, which
    is a schema difference rather than an error, so it logs and yields nothing.
    """
    rows = []
    connection = open_sqlite_db_readonly(db_path)
    if connection is None:
        return rows
    try:
        cursor = connection.cursor()
        if 'PersistedCredentials' not in _table_names(cursor):
            logfunc(f'Tutanota: {db_path} has no PersistedCredentials table, so this '
                    f'release kept credentials in the WebView configuration')
            return rows
        for login, credential_type, user_id in cursor.execute(
                'SELECT login, type, userId FROM PersistedCredentials'):
            rows.append((login or '', user_id or '', credential_type or ''))
    except sqlite3.Error as error:
        logfunc(f'Tutanota: could not read PersistedCredentials from {db_path}: {error}')
    finally:
        connection.close()
    return rows


def _config_records(localstorage_dir):
    """Every tutanotaConfig value in the WebView Local Storage, newest last.

    Chromium keeps superseded values, so more than one record is normal and each is a
    state the configuration passed through.
    """
    records = []
    if not localstorage_dir:
        return records
    try:
        from pathlib import Path
        from ccl_chromium_reader import ccl_chromium_localstorage
    except ImportError as error:
        logfunc(f'Tutanota: ccl_chromium_reader is not available, so the WebView '
                f'configuration was not read: {error}')
        return records
    try:
        store = ccl_chromium_localstorage.LocalStoreDb(Path(localstorage_dir))
    # A truncated or partly overwritten LevelDB raises from inside the reader, and the
    # exception type is the library's business. A container that cannot be read must not
    # abort the artifact for the containers that can.
    except Exception as error:  # pylint: disable=broad-exception-caught
        logfunc(f'Tutanota: could not open Local Storage at {localstorage_dir}: {error}')
        return records
    try:
        for record in store.iter_all_records():
            if record.script_key != CONFIG_SCRIPT_KEY or not record.value:
                continue
            try:
                loaded = json.loads(record.value)
            except ValueError:
                logfunc(f'Tutanota: a {CONFIG_SCRIPT_KEY} record in {localstorage_dir} '
                        f'is not the JSON expected, skipped')
                continue
            if isinstance(loaded, dict):
                records.append((getattr(record, 'leveldb_seq_number', 0), loaded))
    except Exception as error:  # pylint: disable=broad-exception-caught
        logfunc(f'Tutanota: could not read Local Storage at {localstorage_dir}: {error}')
    records.sort(key=lambda item: item[0])
    return records


def _config_credentials(config):
    """[(login, user_id, credential_type)] from a tutanotaConfig record.

    Two shapes exist. From configuration version 3 onward _credentials is a mapping keyed
    by user id whose entries carry a credentialInfo. At version 2 it is a list whose
    entries carry mailAddress instead, and the app converts one to the other in
    migrateConfigV2to3 (src/applications/common/misc/DeviceConfig.ts at tutao/tutanota
    80c8e4cb): the login is the mailAddress when it contains an @, and otherwise the user
    id, because at that version an external user's address was their user id. The same
    rule is applied here rather than a guess at the field's meaning.
    """
    credentials = config.get('_credentials')
    rows = []
    if isinstance(credentials, dict):
        for stored in credentials.values():
            if not isinstance(stored, dict):
                continue
            info = stored.get('credentialInfo')
            if not isinstance(info, dict):
                continue
            rows.append((info.get('login', '') or '', info.get('userId', '') or '',
                         info.get('type', '') or ''))
    elif isinstance(credentials, list):
        for stored in credentials:
            if not isinstance(stored, dict):
                continue
            user_id = stored.get('userId', '') or ''
            mail_address = stored.get('mailAddress', '') or ''
            if '@' in mail_address:
                rows.append((mail_address, user_id, 'internal'))
            else:
                rows.append((user_id, user_id, 'external'))
    return rows


def _newest_config(records):
    return records[-1][1] if records else {}


def _flag(value):
    """A stored boolean as Yes/No, blank when the release did not write the key."""
    if value is None:
        return ''
    return 'Yes' if value else 'No'


@artifact_processor
def tutanota_accounts(context):
    files_found = unique_files(context)
    containers = _containers(files_found)

    data_list = []
    sources = []
    for root in sorted(containers):
        entry = containers[root]
        seen = set()
        rows = []

        db_path = entry['db']
        if db_path:
            key_values = _key_values(db_path)
            encryption_mode = key_values.get('credentialEncryptionMode') or ''
            for login, user_id, credential_type in _persisted_credentials(db_path):
                rows.append((login, user_id, credential_type, encryption_mode,
                             'PersistedCredentials table', db_path))
        else:
            encryption_mode = ''

        # Every stored copy is read, because Chromium keeps superseded values and an
        # account can be present in one and absent from the newest.
        localstorage_dir = entry['localstorage']
        for _, config in _config_records(localstorage_dir):
            mode = config.get('_credentialEncryptionMode') or encryption_mode or ''
            for login, user_id, credential_type in _config_credentials(config):
                rows.append((login, user_id, credential_type, mode,
                             'WebView configuration', localstorage_dir))

        for login, user_id, credential_type, mode, stored_in, source in rows:
            identity = (login, user_id)
            if identity in seen:
                continue
            seen.add(identity)
            data_list.append((login, user_id, credential_type, mode, stored_in,
                              context.get_relative_path(source)))
            if source not in sources:
                sources.append(source)

    data_headers = ('Login', 'User ID', 'Credential Type (as stored)',
                    'Credential Encryption Mode', 'Stored In', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tutanota_configuration(context):
    files_found = unique_files(context)
    containers = _containers(files_found)

    data_list = []
    sources = []
    for root in sorted(containers):
        entry = containers[root]
        db_path = entry['db']
        key_values = _key_values(db_path) if db_path else {}
        records = _config_records(entry['localstorage'])
        config = _newest_config(records)

        if not key_values and not config:
            continue

        last_check = ''
        for key in LAST_CHECK_KEYS:
            raw = key_values.get(key)
            if raw not in (None, '', '0'):
                try:
                    # SseStorage stores this through getLong from a Java Date, so the
                    # value is Unix milliseconds.
                    last_check = convert_unix_ts_to_utc(int(raw) / 1000)
                except (TypeError, ValueError):
                    logfunc(f'Tutanota: {key} in {db_path} is not the number expected, '
                            f'reported blank')
                break

        extended = ''
        for key, value in key_values.items():
            if key.startswith('extendedNotificationMode'):
                extended = value or ''
                break

        used = [path for path in (db_path, entry['localstorage']) if path]
        for path in used:
            if path not in sources:
                sources.append(path)

        data_list.append((
            last_check,
            key_values.get('sseOrigin', '') or '',
            key_values.get('credentialEncryptionMode', '') or '',
            key_values.get('deviceIdentifier', '') or '',
            key_values.get('lastProcessedNotificationId', '') or '',
            extended,
            key_values.get('connectTimeoutSec', '') or '',
            config.get('_version', ''),
            _flag(config.get('isCredentialsMigratedToNative')),
            _flag(config.get('hasParticipatedInCredentialsMigration')),
            _flag(config.get('isSetupComplete')),
            config.get('_themeId') or config.get('_theme') or '',
            len(records),
            context.get_relative_path(db_path) if db_path else '',
            context.get_relative_path(entry['localstorage']) if entry['localstorage'] else '',
        ))

    data_headers = (
        ('Last Missed Notification Check', 'datetime'),
        'Server Origin', 'Credential Encryption Mode', 'Push Device Identifier',
        'Last Processed Notification ID', 'Extended Notification Mode (as stored)',
        'Connect Timeout Seconds (as stored)', 'Config Version (as stored)',
        'Credentials Migrated To Native Store', 'Participated In Credentials Migration',
        'Setup Complete', 'Theme (as stored)', 'Stored Configuration Copies',
        'Source File', 'Configuration Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def tutanota_calendar_alarms(context):
    files_found = unique_files(context)
    containers = _containers(files_found)

    data_list = []
    sources = []
    for root in sorted(containers):
        db_path = containers[root]['db']
        if not db_path:
            continue
        connection = open_sqlite_db_readonly(db_path)
        if connection is None:
            continue
        try:
            cursor = connection.cursor()
            if 'AlarmNotification' not in _table_names(cursor):
                logfunc(f'Tutanota: {db_path} has no AlarmNotification table, skipped')
                continue
            columns = {row[1] for row in cursor.execute(
                'PRAGMA table_info(AlarmNotification)')}
            # excludedDates is absent on older releases, so the repeat rule check uses
            # only the columns every tested schema carries.
            repeat_columns = [name for name in
                              ('frequency', 'interval', 'timeZone', 'endType', 'endValue')
                              if name in columns]
            selected = ['operation', 'identifier', 'user', 'keylistId', 'keyelementId']
            selected = [name for name in selected if name in columns]
            query = f'SELECT {", ".join(selected + repeat_columns)} FROM AlarmNotification'
            for row in cursor.execute(query):
                values = dict(zip(selected + repeat_columns, row))
                operation = values.get('operation')
                if operation in OPERATION_TYPES:
                    operation_label = OPERATION_TYPES[operation]
                elif operation is None:
                    operation_label = ''
                else:
                    operation_label = f'{operation} (as stored)'
                has_repeat = any(values.get(name) not in (None, '')
                                 for name in repeat_columns)
                data_list.append((
                    operation_label,
                    values.get('identifier', '') or '',
                    values.get('user', '') or '',
                    values.get('keylistId', '') or '',
                    values.get('keyelementId', '') or '',
                    'Yes' if has_repeat else 'No',
                    context.get_relative_path(db_path),
                ))
            if db_path not in sources:
                sources.append(db_path)
        except sqlite3.Error as error:
            logfunc(f'Tutanota: could not read AlarmNotification from {db_path}: {error}')
        finally:
            connection.close()

    data_headers = ('Operation', 'Alarm Identifier', 'User ID',
                    'Push Identifier List ID', 'Push Identifier Element ID',
                    'Has Repeat Rule', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
