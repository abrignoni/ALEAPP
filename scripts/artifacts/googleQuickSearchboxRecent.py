# pylint: disable=W0718
__artifacts_v2__ = {
    "get_quicksearch_recent": {
        "name": "Google Quick Search Recent",
        "description": "Recently searched terms and pages read from the Google app (Google Now)",
        "author": "",
        "creation_date": "2020-03-22",
        "last_update_date": "2020-03-22",
        "requirements": "none",
        "category": "Google Now & QuickSearch",
        "notes": "",
        "paths": ('*/com.google.android.googlequicksearchbox/files/recently/*',
                  '*/com.google.android.googlequicksearchbox/files/accounts/*/RecentsDataStore.pb',
                  '*/com.google.android.googlequicksearchbox/databases/accounts.notifications.db'),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "galaxys10_a10": "Android 10 | com.google.android.googlequicksearchbox vc 301139116 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.googlequicksearchbox vc 301302075 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.googlequicksearchbox vc 301639434 | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.googlequicksearchbox vc 301671258 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.googlequicksearchbox vc 301381725 | 0 rows",
        },
    }
}

import datetime
import json
import os
import sqlite3

import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media

_TYPES = {'1': {'type': 'message', 'message_typedef': {
    '1': {'type': 'uint', 'name': 'id'},
    '4': {'type': 'uint', 'name': 'timestamp1'},
    '5': {'type': 'str', 'name': 'search-query'},
    '7': {'type': 'message', 'message_typedef': {
        '1': {'type': 'str', 'name': 'url'},
        '2': {'type': 'str', 'name': 'url-domain'},
        '3': {'type': 'str', 'name': 'title'}}, 'name': 'page'},
    '8': {'type': 'message', 'message_typedef': {
        '1': {'type': 'str', 'name': 'category'},
        '2': {'type': 'str', 'name': 'engine'}}, 'name': 'search'},
    '9': {'type': 'int', 'name': 'screenshot-id'},
    '17': {'type': 'uint', 'name': 'timestamp2'}}, 'name': ''}}


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _recursive_bytes_to_str(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = _recursive_bytes_to_str(v)
        return obj
    if isinstance(obj, list):
        return [_recursive_bytes_to_str(v) for v in obj]
    if isinstance(obj, bytes):
        return obj.decode('utf8', 'backslashreplace')
    return obj


@artifact_processor
def get_quicksearch_recent(context):
    files_found = context.get_files_found()
    account_name = ''
    screenshots = {}
    pb_files = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('accounts.notifications.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            try:
                cursor.execute('SELECT account_name FROM accounts')
                for row in cursor.fetchall():
                    account_name = row[0]
            except sqlite3.Error:
                pass
            db.close()
        elif file_found.endswith('.jpg'):
            screenshots[os.path.basename(file_found)] = file_found
        elif '/mirror/' in file_found.replace('\\', '/') or os.path.isdir(file_found):
            continue
        else:
            pb_files.append(file_found)

    data_list = []
    source_path = ''
    for file_found in pb_files:
        source_path = file_found
        try:
            with open(file_found, 'rb') as f:
                values, _ = blackboxprotobuf.decode_message(f.read(), _TYPES)
        except Exception:
            continue
        items = values.get('1')
        if isinstance(items, dict):
            items = [items]
        elif not isinstance(items, list):
            continue
        for item in items:
            screenshot_id = str(item.get('screenshot-id', ''))
            search_query = str(item.get('search-query', ''))
            name = f'{account_name}-{screenshot_id}.jpg'
            screenshot = check_in_media(screenshots[name], name) if name in screenshots else ''
            _recursive_bytes_to_str(item)
            data_list.append((_ms_to_utc(item.get('timestamp1')), search_query, screenshot,
                              json.dumps(item, ensure_ascii=False), context.get_relative_path(file_found)))

    data_headers = (('Timestamp', 'datetime'), 'Search Query', ('Screenshot', 'media'),
                    'Protobuf Data', 'Source File')
    return data_headers, data_list, context.get_relative_path(source_path)
