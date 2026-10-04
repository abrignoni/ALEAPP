__artifacts_v2__ = {
    "magisk_superuser_log": {
        "name": "Magisk - Superuser Log",
        "description": "Rows from the logs table of sulogs.db, each recording a request for "
                       "superuser rights with the requesting package, the command and the time",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Magisk",
        "notes": "com.topjohnwu.magisk is a root management app; this database sits in that "
                 "package's data directory. Each row names the package and app label "
                 "that asked for superuser rights, the command string recorded for the request, "
                 "and the requesting and target user ids. App Name, Package Name, From UID and To "
                 "UID are reported as stored. The commands "
                 "recorded were shell commands. time is Unix milliseconds. Action (as stored) is "
                 "reported as stored and not expanded into allowed or denied, because its "
                 "meaning depends on the Magisk version that wrote the row. In the SuLog entity "
                 "at tags v23.0 and v25.2, which has no target, context or gids fields, like the "
                 "tested database, action is a Boolean "
                 "(https://github.com/topjohnwu/Magisk/blob/97c1e181c5a96217021d96bcdc4d4e31fbfce2ac/app/src/main/java/com/topjohnwu/magisk/core/model/su/SuLog.kt#L19 "
                 "and "
                 "https://github.com/topjohnwu/Magisk/blob/6066b5cf86703512451a021cf1aaf1a877530af7/app/src/main/java/com/topjohnwu/magisk/core/model/su/SuLog.kt#L17), "
                 "and at v25.2 it is set from policy == SuPolicy.ALLOW (line 38 of the same "
                 "file). At tags v26.4 and v27.0 it is an Int set from the policy value "
                 "(https://github.com/topjohnwu/Magisk/blob/6c807d35b241c6a22b35534af8b6fe447a66f073/app/src/main/java/com/topjohnwu/magisk/core/model/su/SuLog.kt#L17 "
                 "and "
                 "https://github.com/topjohnwu/Magisk/blob/2c6adbc69ba0e5dce09cd13c6d9aca5de30efe76/app/src/main/java/com/topjohnwu/magisk/core/model/su/SuLog.kt#L17), "
                 "and SuPolicy.kt at both tags declares INTERACTIVE 0, DENY 1 and ALLOW 2 "
                 "(https://github.com/topjohnwu/Magisk/blob/2c6adbc69ba0e5dce09cd13c6d9aca5de30efe76/app/src/main/java/com/topjohnwu/magisk/core/model/su/SuPolicy.kt#L5-L7). "
                 "Which version wrote the tested rows was not established; Action (as stored) "
                 "held 1 on all 8 "
                 "rows below, so the column is uniform "
                 "there. The entity in current Magisk carries target, context and gids columns "
                 "that the tested database does not have, so those are selected only where the "
                 "table actually declares them and are blank otherwise; they were absent on the "
                 "corpus below and those three columns are empty there. On the tested image "
                 "sulogs.db was under data/user_de (device-encrypted storage), not data/data.",
        "paths": ('*/com.topjohnwu.magisk/databases/sulogs.db*',),
        "output_types": "standard",
        "artifact_icon": "terminal",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.topjohnwu.magisk | 8 rows",
        },
    },
    "magisk_configuration": {
        "name": "Magisk - Configuration",
        "description": "Entries of the app's preferences file and su_timeout.xml, by name and value as stored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Magisk",
        "notes": "Reads com.topjohnwu.magisk_preferences.xml and su_timeout.xml. Every entry in "
                 "both files is reported so settings added by later versions still appear. The "
                 "values are as stored: the numeric settings, including root_access, "
                 "multiuser_mode and mnt_ns, are integers whose meaning was not traced to a "
                 "source, so they are not expanded into labels. On the tested image "
                 "su_timeout.xml held entries named for packages. What the app writes them for "
                 "was not traced to a source, so an entry is not read as a request or a grant; "
                 "the Superuser Log "
                 "artifact is where the requests themselves are. Store names which of the two "
                 "files each row came from.",
        "paths": ('*/com.topjohnwu.magisk/shared_prefs/com.topjohnwu.magisk_preferences.xml',
                  '*/com.topjohnwu.magisk/shared_prefs/su_timeout.xml'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "pixel3_a12": "Android 12 | com.topjohnwu.magisk | 9 rows",
        },
    },
}

import os
import xml.etree.ElementTree as ET

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    get_sqlite_db_records,
    logfunc,
)

SIDECARS = ('-wal', '-shm', '-journal')

# Columns the logs table has carried. The three at the end were added to the app's
# SuLog entity after the schema in the tested extraction, so each is selected only
# when the table declares it.
BASE_COLUMNS = ('time', 'appName', 'packageName', 'command', 'action',
                'fromUid', 'toUid', 'fromPid', 'id')
LATER_COLUMNS = ('target', 'context', 'gids')


def _files(context, wanted):
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or file_found.endswith(SIDECARS):
            continue
        if wanted(os.path.basename(file_found)):
            found.append(file_found)
    return found


def _columns(db_path):
    """The column names the logs table declares, or an empty set."""
    rows = get_sqlite_db_records(db_path, 'PRAGMA table_info(logs)')
    return {row[1] for row in rows}


@artifact_processor
def magisk_superuser_log(context):
    data_list = []
    source_paths = []

    for db_path in _files(context, lambda n: n == 'sulogs.db'):
        present = _columns(db_path)
        if not present:
            logfunc(f'Magisk: no logs table in {db_path}, skipping')
            continue
        selected = [name for name in BASE_COLUMNS if name in present]
        if not selected:
            logfunc(f'Magisk: logs table in {db_path} declared none of the expected columns')
            continue
        later = [name for name in LATER_COLUMNS if name in present]
        order = ' ORDER BY time' if 'time' in present else ''
        columns = ', '.join(f'"{name}"' for name in selected + later)
        rows = list(get_sqlite_db_records(
            db_path, f'SELECT {columns} FROM logs{order}'))
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            values = dict(zip(selected + later, row))
            stamp = values.get('time')
            data_list.append((
                convert_unix_ts_to_utc(stamp / 1000) if stamp else '',
                values.get('appName') or '',
                values.get('packageName') or '',
                values.get('command') or '',
                values.get('action') if values.get('action') is not None else '',
                values.get('fromUid') if values.get('fromUid') is not None else '',
                values.get('toUid') if values.get('toUid') is not None else '',
                values.get('fromPid') if values.get('fromPid') is not None else '',
                values.get('target') if values.get('target') is not None else '',
                values.get('context') or '',
                values.get('gids') or '',
                values.get('id') if values.get('id') is not None else '',
            ))

    data_headers = (
        ('Request Time', 'datetime'),
        'App Name',
        'Package Name',
        'Command',
        'Action (as stored)',
        'From UID',
        'To UID',
        'From PID',
        'Target (as stored)',
        'Context',
        'GIDs',
        'Log ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def magisk_configuration(context):
    data_list = []
    source_paths = []

    def wanted(name):
        return name in ('com.topjohnwu.magisk_preferences.xml', 'su_timeout.xml')

    for prefs_path in _files(context, wanted):
        try:
            root = ET.parse(prefs_path).getroot()
        except (OSError, ET.ParseError) as error:
            logfunc(f'Magisk: could not parse {prefs_path}: {error}')
            continue
        source_paths.append(context.get_relative_path(prefs_path))
        store = os.path.basename(prefs_path)
        for entry in root:
            name = entry.get('name', '')
            if entry.tag == 'set':
                value = ', '.join((child.text or '') for child in entry)
            elif entry.tag == 'string':
                value = entry.text or ''
            else:
                value = entry.get('value', '')
            data_list.append((name, value, entry.tag, store))

    data_list.sort(key=lambda row: (row[3], row[0]))
    data_headers = ('Setting', 'Value (as stored)', 'Stored Type', 'Store')
    return data_headers, data_list, '\n'.join(source_paths)
