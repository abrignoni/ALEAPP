# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_blueskymessages": {
        "name": "Bluesky - Messages",
        "description": "Bluesky direct messages",
        "author": "Alexis Brignoni",
        "creation_date": "2024-11-19",
        "last_update_date": "2024-11-19",
        "requirements": "none",
        "category": "Bluesky",
        "notes": "",
        "paths": ('*/xyz.blueskyweb.app/databases/RKStorage*',
                  '*/xyz.blueskyweb.app/cache/http-cache/*.*'),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "get_blueskymessages_actors": {
        "name": "Bluesky - Actors",
        "description": "Bluesky actors (accounts) seen in storage and the http-cache",
        "author": "Alexis Brignoni",
        "creation_date": "2024-11-19",
        "last_update_date": "2024-11-19",
        "requirements": "none",
        "category": "Bluesky",
        "notes": "",
        "paths": ('*/xyz.blueskyweb.app/databases/RKStorage*',
                  '*/xyz.blueskyweb.app/cache/http-cache/*.*'),
        "output_types": "standard",
        "artifact_icon": "users",
    }
}

import datetime
import json
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, utf8_in_extended_ascii

_ACTORS_CACHE = {}


def _iso_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(
            datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _s(value):
    if value is None:
        return ''
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _fix(value):
    if not value:
        return ''
    try:
        return utf8_in_extended_ascii(value)[1]
    except Exception:
        return value


def _load_json(file_found):
    try:
        with open(file_found, 'r', encoding='utf-8') as handle:
            return json.load(handle)
    except (ValueError, OSError, UnicodeDecodeError):
        return None


def _build_actors(files_found):
    cache_key = tuple(sorted(str(f) for f in files_found))
    if cache_key in _ACTORS_CACHE:
        return _ACTORS_CACHE[cache_key]
    actors = []
    seen = set()

    def add(row):
        if row not in seen:
            seen.add(row)
            actors.append(row)

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('RKStorage'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            try:
                cursor.execute("SELECT value FROM catalystLocalStorage WHERE key = 'BSKY_STORAGE'")
                rows = cursor.fetchall()
            except sqlite3.Error:
                rows = []
            db.close()
            for row in rows:
                try:
                    account = json.loads(row[0])['session']['accounts'][0]
                except (ValueError, KeyError, IndexError, TypeError):
                    continue
                add(('', account.get('did'), account.get('handle'), '', '', '', '', '', account.get('email')))
            continue

        data = _load_json(file_found)
        if not isinstance(data, dict):
            continue
        for item in data.get('actors') or []:
            add((_iso_to_utc(item.get('createdAt')), item.get('did'), item.get('handle'),
                 _fix(item.get('displayName')), _s(item.get('avatar')), _s(item.get('viewer')),
                 _s(item.get('labels')), '', ''))
        if data.get('did') is not None and len(data) > 1:
            add((_iso_to_utc(data.get('createdAt')), data.get('did'), data.get('handle'),
                 _fix(data.get('displayName')), _s(data.get('avatar')), _s(data.get('viewer')),
                 _s(data.get('labels')), _fix(data.get('description')), ''))

    _ACTORS_CACHE[cache_key] = actors
    return actors


@artifact_processor
def get_blueskymessages_actors(files_found, report_folder, seeker, wrap_text):
    actors = _build_actors(files_found)
    source_path = next((str(f) for f in files_found if not str(f).endswith('RKStorage')), '')
    data_headers = ('Created At', 'DID', 'Handle', 'Display Name', 'Avatar', 'Viewer', 'Labels',
                    'Description', 'Email')
    return data_headers, actors, source_path


@artifact_processor
def get_blueskymessages(files_found, report_folder, seeker, wrap_text):
    actors = _build_actors(files_found)
    data_list = []
    seen = set()
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('RKStorage'):
            continue
        data = _load_json(file_found)
        if not isinstance(data, dict):
            continue
        source_path = file_found
        for message in data.get('messages') or []:
            try:
                sender_id = message['sender']['did']
            except (KeyError, TypeError):
                continue
            username = ''
            actor_url = ''
            for actor in actors:
                if sender_id == actor[1]:
                    username = actor[3]
                    actor_url = actor[2]
                    break
            row = (_iso_to_utc(message.get('sentAt')), actor_url, username, _fix(message.get('text')),
                   sender_id, message.get('id'))
            if row not in seen:
                seen.add(row)
                data_list.append(row)

    data_headers = (('Timestamp Sent', 'datetime'), 'Actor URL', 'Username', 'Message', 'Sender ID',
                    'Message ID')
    return data_headers, data_list, source_path
