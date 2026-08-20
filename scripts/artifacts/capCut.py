__artifacts_v2__ = {
    "capcut_app_sessions": {
        "name": "CapCut - App Sessions",
        "description": "Parses the app sessions the CapCut Android app recorded, with the "
                       "time each began, its duration and the app version that ran.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "CapCut",
        "notes": "One row per recorded session. Start is Unix milliseconds and Duration is "
                 "the value the row carries, as stored, because nothing in the extraction "
                 "states its unit. Events counts the entries in the same store that name "
                 "this session, and First Event and Last Event bound them in time; the "
                 "entries themselves are the app's own SDK bookkeeping rather than user "
                 "actions, so they are counted rather than listed. The store recorded that "
                 "no account was signed in on every entry it holds. The app's editing "
                 "projects are not in this artifact and were not present in the tested "
                 "sample: its project and draft tables held no rows, and CapCut keeps "
                 "project files in external storage, which an app private extraction does "
                 "not contain. Field mapping was done against a private sample provided by "
                 "Mattia; no sample data is recorded for it.",
        "paths": (
            '*/com.lemon.lvoverseas/databases/ss_app_log.db*',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "clock"
    },
    "capcut_device": {
        "name": "CapCut - Device and Install",
        "description": "Parses the device, install and advertising identifiers the CapCut "
                       "Android app records, with the time it recorded its install.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "CapCut",
        "notes": "One row per app data directory. Install Recorded is Unix milliseconds. "
                 "The device identifier is written to three of the app's preference files "
                 "by different parts of it and all three held the same value on the tested "
                 "device, so the column names one value rather than comparing them. The "
                 "app stores two candidate device identifiers under the same name in two "
                 "different preference files and they differed on the tested device, so "
                 "both are reported rather than one being chosen. No signed in account was "
                 "recorded: the app's account store held no login rows. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": (
            '*/com.lemon.lvoverseas/shared_prefs/applog_stats.xml',
            '*/com.lemon.lvoverseas/shared_prefs/common_config.xml',
            '*/com.lemon.lvoverseas/shared_prefs/byte_sync_settings.xml',
            '*/com.lemon.lvoverseas/shared_prefs/applog_monitor.xml',
            '*/com.lemon.lvoverseas/shared_prefs/appsflyer-data.xml',
            '*/com.lemon.lvoverseas/shared_prefs/com.ss.android.deviceregister.utils.*.xml',
            '*/com.lemon.lvoverseas/databases/ss_app_log.db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "smartphone"
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
_PACKAGE = 'com.lemon.lvoverseas'


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
        logfunc(f'CapCut: could not parse {os.path.basename(source_path)}: {ex}')
        return values
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        values[name] = element.get('value') if element.tag != 'string' else (element.text or '')
    return values


def _preference(files, name, key):
    '''One preference value from the named file in this container, or ''.

    A module level helper rather than a closure over the loop variables, so the container
    a value is read from is the one passed in rather than whichever the loop last bound.
    '''
    for path in files.get(name, []):
        value = _prefs(path).get(key)
        if value:
            return value
    return ''


def _open(paths, name):
    '''The named database in one container, opened read only, or (None, None).'''
    for path in paths:
        if os.path.basename(path) == name:
            try:
                return path, open_sqlite_db_readonly(get_sqlite_db_path(path))
            except sqlite3.Error as ex:
                logfunc(f'CapCut: could not open {name}: {ex}')
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
        logfunc(f'CapCut: could not read from the database: {ex}')
        return []


@artifact_processor
def capcut_app_sessions(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        source_path, database = _open(paths, 'ss_app_log.db')
        if database is None:
            continue
        relative = context.get_relative_path(source_path)

        # Counted per session id inside this store, so a second app data directory's
        # events cannot be counted against this one's sessions.
        counts = {}
        for session_id, count, first, last in _rows(
                database, 'SELECT session_id, COUNT(*), MIN(timestamp), MAX(timestamp) '
                          'FROM event GROUP BY session_id'):
            counts[str(session_id)] = (count, first, last)

        for row in _rows(database, '''SELECT _id, value, timestamp, duration, app_version,
                                             version_code, non_page, event_index
                                      FROM session'''):
            identifier, value, stamp, duration, version, code, non_page, index = row
            count, first, last = counts.get(str(identifier), (0, None, None))
            source_files.append(relative)
            data_list.append((
                _ms(stamp),
                _ms(first),
                _ms(last),
                str(duration if duration is not None else ''),
                str(version or ''),
                str(code if code is not None else ''),
                count,
                str(value or ''),
                str(identifier if identifier is not None else ''),
                str(non_page if non_page is not None else ''),
                str(index if index is not None else ''),
                relative,
            ))
        database.close()

    data_list.sort(key=lambda row: (str(row[0]), str(row[8])), reverse=True)

    data_headers = (
        ('Start', 'datetime'),
        ('First Event', 'datetime'),
        ('Last Event', 'datetime'),
        'Duration (as stored)',
        'App Version',
        'Version Code',
        'Events',
        'Session UUID',
        'Session ID',
        'Non Page (as stored)',
        'Event Index (as stored)',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def capcut_device(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        files = {}
        for path in paths:
            files.setdefault(os.path.basename(path), []).append(path)

        stats = _preference(files, 'applog_stats.xml', 'device_id') \
            or _preference(files, 'common_config.xml', 'key_device_id') \
            or _preference(files, 'byte_sync_settings.xml', 'device_id')
        install = _preference(files, 'applog_stats.xml', 'install_id') \
            or _preference(files, 'common_config.xml', 'key_install_id')
        recorded = _preference(files, 'applog_monitor.xml', 'monitor_install_time3')
        android_id = _preference(files, 'appsflyer-data.xml', 'androidIdCached')

        # The app writes a candidate device identifier under one name in two different
        # preference files, and they differed on the tested device, so both are kept.
        candidates = []
        for name, values in files.items():
            if not name.startswith('com.ss.android.deviceregister.utils'):
                continue
            for path in values:
                value = _prefs(path).get('cdid')
                if value and value not in candidates:
                    candidates.append(value)

        version = code = ''
        _, database = _open(paths, 'ss_app_log.db')
        if database is not None:
            rows = _rows(database, 'SELECT app_version, version_code FROM session '
                                   'ORDER BY timestamp DESC LIMIT 1')
            if rows:
                version, code = rows[0]
            database.close()

        if not any((stats, install, recorded, android_id, candidates, version)):
            continue

        relative_paths = sorted({context.get_relative_path(path) for path in paths})
        source_files.extend(relative_paths)
        data_list.append((
            _ms(recorded),
            str(stats or ''),
            str(install or ''),
            '; '.join(candidates),
            str(android_id or ''),
            str(version or ''),
            str(code if code is not None else ''),
            '; '.join(relative_paths),
        ))

    data_headers = (
        ('Install Recorded', 'datetime'),
        'Device ID',
        'Install ID',
        'Candidate Device Identifiers',
        'Android ID',
        'App Version',
        'Version Code',
        'Source Files',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
