__artifacts_v2__ = {
    "get_googleTasks": {
        "name": "GoogleTasks",
        "description": ('One row per task in the data.db Google Tasks store that several Google apps keep in a '
                        'files/tasks/<folder> or files/tasks-<folder> folder of their app data directory, read from the '
                        "Tasks table and its EffectiveTask protobuf, with the task list's EffectiveTaskList text. App is "
                        'the package folder that holds the store.'),
        "author": "@bolisettynihith, @AlexisBrignoni, Claude",
        "creation_date": "2021-08-21",
        "last_update_date": "2026-11-25",
        "requirements": "none",
        "category": "Productivity",
        "notes": ('The store is data.db at files/tasks/<folder>/data.db (seen under com.google.android.gm, '
                  'com.google.android.calendar and com.google.android.keep) or files/tasks-<folder>/data.db (seen '
                  'under com.google.android.gm and com.google.android.apps.dynamite). The artifact also keeps the '
                  'com.google.android.apps.tasks path it read before; no registered image holds that package. A '
                  'data.db is read only when the path segment above files is one of these five packages, the file '
                  'sits directly in the folder named by that layout, and the store has a Tasks table with an '
                  'EffectiveTask column; any other data.db is logged and skipped. App is that package folder name. '
                  'Store Folder is the name of the folder holding data.db, as stored. On the 36 stores seen it was '
                  'a 21-digit number or a UUID under files/tasks, and tasks- and a 21-digit number in the other '
                  "layout. What it identifies is not established. Android User is taken from the store's evidence "
                  'path: the number after data/user/ or userdata/user/ or the data_mirror user folder, or 0 for a '
                  'store under data/data or userdata/data. It is blank for a path in none of those. The data/data, '
                  'data/user/0 and data_mirror spellings of one store are read once. A task present in two stores '
                  'is reported once per store; rows are not de-duplicated. Due Date and the ids are Tasks table '
                  'columns as stored. Completed is the Tasks.Completed column, an INTEGER: 0 is shown as No, any '
                  'other value as Yes, and NULL as blank. The one Android row seen held 0. No published definition '
                  'of the protobuf is known to the author, so the columns are named by field position and what each'
                  ' field records is not established. Fields 11 and 3 held two integers, read as seconds in field 1'
                  ' and nanoseconds in field 2, the shape of google.protobuf.Timestamp, and are converted to UTC on'
                  ' that basis. Field 2.5 is read the same way; it was not present on Android data. Field 9.1.6.1 '
                  "is an integer converted as Unix seconds to UTC. Fields 2.2, 2.3 and 9.1.4 and the task list's "
                  'field 2.1 are read as bytes and decoded as UTF-8 text. A protobuf blob starting with the bytes '
                  "FE FF is not decoded, leaving that row's protobuf columns blank; no such blob was seen. The task"
                  ' list is joined by Tasks.TaskListId to TaskLists.TaskListIdWithoutShard within the same ShardId;'
                  ' a task list with no tasks gets no row. On the 19 registered Android images listed in '
                  'sample_data, checked on 2026-11-25, 36 stores were found once the duplicate spellings were '
                  'collapsed: 16 Gmail, 13 Calendar, 3 Keep and 4 com.google.android.apps.dynamite, two of the '
                  'Calendar stores under data/user/10. One store, Gmail on adams_ss135dl_a13, held a task, and its '
                  'row was only in the -wal. On that row field 2.2 was absent, so Text (field 2.2) had no value, '
                  'and field 2.3 held text, field 11 was earlier than field 3, field 2.4 held the same date as Due '
                  'Date, and field 9.1.6.1 equalled the date in field 9.1.2 and the hour and minute in field 9.1.3 '
                  'read in the zone named by field 9.1.4. Its Completed column was 0, so field 2.5 on a row whose '
                  'Completed column is set was not exercised on Android data and Time (field 2.5) had no value. The'
                  ' other 35 stores held no tasks, so the Calendar, Keep and com.google.android.apps.dynamite '
                  'stores, and every store in the files/tasks-<folder> layout, were exercised only with empty Tasks'
                  ' tables. In 13 of the 36 stores the tables were only in the -wal; without the -wal such a store '
                  'reads as having no tables. Of the task fields on the Android row seen, 1, 2.4, 4, 8, 9.1.2, '
                  "9.1.3 and 13 are not reported, nor are the task list's fields other than 2.1 or the Task and "
                  'OriginalTask blobs. Not reported: TaskRecurrenceId (empty on the one task row seen), '
                  'TaskRecurrences (no rows in any store seen), HasDirtyState (0 on every task and task list row '
                  'seen), Operations, UserActions, Rooms, RoomsTable, DocumentsTable, GlobalMetadata and '
                  'UserExperimental (no rows in any store seen), and ClientSyncState, UserMetadata, UserPrefs and '
                  'GlobalMetadataTable (not decoded; GlobalMetadataTable has an ObfuscatedGaiaId column in 28 of '
                  'the 36 stores, holding a value in 25).'),
        "paths": ('*/com.google.android.apps.tasks/files/tasks*/data.db*',
                  '*/com.google.android.gm/files/tasks*/data.db*',
                  '*/com.google.android.calendar/files/tasks*/data.db*',
                  '*/com.google.android.apps.dynamite/files/tasks*/data.db*',
                  '*/com.google.android.keep/files/tasks*/data.db*'),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 1 row (Gmail store, task row only in the -wal)",
            "anne_a15": "Android 15 | 0 rows (Gmail store, one task list and no tasks)",
            "dragna_pixel9a_a16": "Android 16 | 0 rows (Gmail, Calendar and Keep stores, one task list and no tasks in each)",
            "falken_a326u_a13": "Android 13 | 0 rows (Gmail store, one task list and no tasks)",
            "hc_pixel8pro_a16": "Android 16 | 0 rows (Gmail, Calendar and Keep stores, one task list and no tasks in each)",
            "hc_pixel8pro_a17": "Android 17 | 0 rows (Gmail, Calendar and Keep stores, one task list and no tasks in each)",
            "hickman_a13": "Android 13 | 0 rows (Calendar store with one task list, com.google.android.apps.dynamite store with none; no tasks)",
            "kevin_pocox7_a15": "Android 15 | 0 rows (Gmail and Calendar stores, one task list and no tasks in each)",
            "pixel3_a11": "Android 11 | 0 rows (Calendar store, one task list and no tasks)",
            "pixel3_a12": "Android 12 | 0 rows (Gmail tasks- store and Calendar store, one task list and no tasks in each)",
            "pixel7a_a14": "Android 14 | 0 rows (Calendar store with one task list, com.google.android.apps.dynamite store with none; no tasks)",
            "russell_a14": "Android 14 | 0 rows (Calendar stores for users 0 and 10, one task list and no tasks in each)",
            "russell_pixel6a_a13": "Android 13 | 0 rows (Calendar stores for users 0 and 10 with one task list each, Gmail tasks- store with none; no tasks)",
            "s20fe_a13": "Android 13 | 0 rows (Gmail store, one task list and no tasks)",
            "samsung_a166u_a16_known_20261116": "Android 16 | 0 rows (Gmail store, one task list and no tasks)",
            "samsung_a166u_a16_known_20261117": "Android 16 | 0 rows (Gmail store, one task list and no tasks)",
            "samsunga53_a14": "Android 14 | 0 rows (two Gmail stores with one task list each, two com.google.android.apps.dynamite stores with none; no tasks)",
            "samsungs20_a13": "Android 13 | 0 rows (Gmail store, one task list and no tasks)",
            "userb2_a13": "Android 13 | 0 rows (Gmail and Calendar stores, one task list and no tasks in each)",
        },
    }
}

import copy
import re
import sqlite3
import struct
from datetime import datetime, timedelta, timezone

from google.protobuf.message import DecodeError

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import (artifact_processor, decode_protobuf, is_sqlite_sidecar, logfunc,
                               open_sqlite_db_readonly)

_PACKAGES = ('com.google.android.apps.tasks', 'com.google.android.gm',
             'com.google.android.calendar', 'com.google.android.apps.dynamite',
             'com.google.android.keep')
# <package>/files/tasks-<folder>/data.db or <package>/files/tasks/<folder>/data.db, matched on
# whole path segments so a folder that merely contains a package name is not taken for it.
_STORE_RE = re.compile(r'(?:^|/)([^/]+)/files/(?:tasks-[^/]+|tasks/[^/]+)/data\.db$')
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_DECODE_ERRORS = (DecodeError, struct.error, KeyError, ValueError, TypeError, IndexError)
# The decoder guesses a field's type from its bytes, and short UTF-8 text can also parse as a
# nested message. The text fields the artifact reports are pinned to bytes; the rest are guessed.
_BYTES = {'type': 'bytes', 'name': ''}
_TASK_TYPES = {
    '2': {'type': 'message', 'name': '', 'message_typedef': {'2': _BYTES, '3': _BYTES}},
    '9': {'type': 'message', 'name': '', 'message_typedef': {
        '1': {'type': 'message', 'name': '', 'message_typedef': {'4': _BYTES}}}},
}
_TASK_LIST_TYPES = {'2': {'type': 'message', 'name': '', 'message_typedef': {'1': _BYTES}}}


def _store_app(context, path):
    '''(package, store folder, Android user) for a data.db in a known package's layout, else None.'''
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    match = _STORE_RE.search(relative)
    if not match or match.group(1) not in _PACKAGES:
        return None
    folder = relative.rsplit('/', 2)[-2]
    return match.group(1), folder, android_user(relative)


def _yes_no(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _fetch(cursor, query, app):
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as error:
        logfunc(f'Google Tasks: query failed on the {app} data.db: {error}')
        return []


def _tables(cursor, app):
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return {row[0] for row in cursor.fetchall()}
    except sqlite3.Error as error:
        logfunc(f'Google Tasks: could not read the schema of the {app} data.db: {error}')
        return set()


def _columns(cursor, table):
    try:
        cursor.execute(f"PRAGMA table_info('{table}')")
        return {row[1] for row in cursor.fetchall()}
    except sqlite3.Error:
        return set()


def _pb(message, *keys):
    value = message
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _pb_text(message, *keys):
    value = _pb(message, *keys)
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    if isinstance(value, str):
        return value
    if value is not None:
        field = '.'.join(keys)
        logfunc(f'Google Tasks: protobuf field {field} did not decode as text; left blank')
    return ''


def _pb_time(message, *keys):
    '''A seconds/nanoseconds pair (google.protobuf.Timestamp shape) to UTC.'''
    value = _pb(message, *keys)
    if not isinstance(value, dict) or not isinstance(value.get('1'), int):
        return ''
    nanos = value.get('2') if isinstance(value.get('2'), int) else 0
    return _EPOCH + timedelta(seconds=value['1'], microseconds=nanos // 1000)


def _pb_seconds(message, *keys):
    value = _pb(message, *keys)
    if not isinstance(value, int) or isinstance(value, bool):
        return ''
    return _EPOCH + timedelta(seconds=value)


def _decode(blob, label, typedef):
    if not isinstance(blob, (bytes, bytearray)) or not blob or bytes(blob).startswith(b'\xfe\xff'):
        return {}
    try:
        message, _types = decode_protobuf(bytes(blob), copy.deepcopy(typedef))
        return message
    except _DECODE_ERRORS as error:
        logfunc(f'Google Tasks: could not decode a {label} protobuf: {error}')
        return {}


@artifact_processor
def get_googleTasks(context):
    data_list = []
    sources = []
    stores = []
    for found in unique_files(context):
        if is_sqlite_sidecar(found):
            continue
        owner = _store_app(context, found)
        if owner is None:
            logfunc('Google Tasks: skipping a data.db outside a known package layout')
            continue
        stores.append((found,) + owner)

    for store, app, folder, user in stores:
        db = open_sqlite_db_readonly(store)
        if db is None:
            continue
        cursor = db.cursor()
        tables = _tables(cursor, app)
        if 'Tasks' not in tables or 'EffectiveTask' not in _columns(cursor, 'Tasks'):
            logfunc(f'Google Tasks: no Tasks table with an EffectiveTask column in the {app} data.db')
            db.close()
            continue
        sources.append(store)
        lists = {}
        if 'TaskLists' in tables:
            for shard, list_id, blob in _fetch(
                    cursor, 'SELECT ShardId, TaskListIdWithoutShard, EffectiveTaskList FROM TaskLists',
                    app):
                lists[(shard, list_id)] = _pb_text(_decode(blob, 'task list', _TASK_LIST_TYPES), '2', '1')
        rows = _fetch(cursor, '''
            SELECT TaskId, TaskListId, DueDate, Completed, EffectiveTask, ShardId
            FROM Tasks ORDER BY rowid''', app)
        db.close()
        for task_id, list_id, due, completed, blob, shard in rows:
            message = _decode(blob, 'task', _TASK_TYPES)
            data_list.append((
                _pb_time(message, '11'), _pb_time(message, '3'), _pb_time(message, '2', '5'),
                _pb_seconds(message, '9', '1', '6', '1'), _pb_text(message, '9', '1', '4'),
                due or '', _yes_no(completed), _pb_text(message, '2', '2'), _pb_text(message, '2', '3'),
                lists.get((shard, list_id), ''), app, user, folder, task_id or '', list_id or ''))

    data_headers = (
        ('Time (field 11)', 'datetime'), ('Time (field 3)', 'datetime'), ('Time (field 2.5)', 'datetime'),
        ('Time (field 9.1.6.1)', 'datetime'), 'Zone (field 9.1.4)', 'Due Date (as stored)', 'Completed',
        'Text (field 2.2)', 'Text (field 2.3)', 'Task List Text (field 2.1)', 'App', 'Android User',
        'Store Folder',
        'Task ID', 'Task List ID')
    return data_headers, data_list, '\n'.join(sources)
