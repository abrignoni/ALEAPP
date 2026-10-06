__artifacts_v2__ = {
    "jitsi_meet_recent_meetings": {
        "name": "Jitsi Meet - Recent Meetings",
        "description": "Parses the recent meeting list stored by the Jitsi Meet Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Jitsi Meet",
        "notes": "One row per entry in the app's recent-meeting list. The list holds at most 30 "
                 "entries and keeps one entry per conference URL, the latest (reducer.ts lines 32 "
                 "and 87 to 100 at the commit below), so it is not a full history. Jitsi Meet is "
                 "a React Native app and keeps its state in the AsyncStorage database "
                 "databases/RKStorage, in the catalystLocalStorage table, one JSON document per "
                 "key. This artifact reads the key @jitsi-meet/features/recent-list, whose "
                 "entries the app defines as conference, date and duration (the IRecent type in "
                 "react/features/recent-list/reducer.ts at jitsi/jitsi-meet "
                 "98de6219cc7ddbe07ace9fde045aff90a242ba01). Conference URL is the full meeting "
                 "URL as stored, which carries both the server host and the room name, and Room "
                 "Name is the last path segment of that URL. The Date column is the date field, "
                 "set from Date.now() when the entry is added, so it is Unix milliseconds and is "
                 "reported as UTC; on the tested device 18:26 UTC matched the device's 2:26 PM "
                 "local clock. Duration is the duration field, which the same source computes as "
                 "Date.now() minus date when the conference ends, so it is milliseconds and is "
                 "reported here in seconds. A row records that the app stored that conference URL "
                 "in its recent list on this device. The entry is added when the room is set, "
                 "before a join is confirmed (reducer.ts lines 84 to 103 and middleware.ts lines "
                 "130 to 137 at the same commit), so a row alone does not show the conference was "
                 "joined. A row does not show who else attended, and the app does not store the "
                 "participants or the chat here. A zero Duration is reported as stored; the app "
                 "creates the entry with duration 0 and updates it when the conference is left "
                 "(reducer.ts line 96 and the _updateConferenceDuration function from line 112, "
                 "at the same commit).",
        "paths": ('*/org.jitsi.meet/databases/RKStorage*',),
        "output_types": "standard",
        "artifact_icon": "video",
        "sample_data": {
            "emu_a15_oss_v2": "Android 15 | org.jitsi.meet vc 26000002 | 1 rows",
        },
    },
    "jitsi_meet_settings": {
        "name": "Jitsi Meet - Settings",
        "description": "Parses the profile and server settings stored by the Jitsi Meet Android app.",
        "author": "@AlexisBrignoni, Claude; @AlexisBrignoni, Codex",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Jitsi Meet",
        "notes": "One row per reported setting read from the catalystLocalStorage table of "
                 "databases/RKStorage. Display Name and Email come from the "
                 "@jitsi-meet/features/base/settings document; on the tested device the display "
                 "name entered at the join screen was stored here and no email was set. Install "
                 "ID is @jitsi-meet/jitsiMeetId and Call Stats Username is "
                 "@jitsi-meet/callStatsUserName, both reported as stored; how the app produces "
                 "them was not sourced. Known Domains is @jitsi-meet/features/base/known-domains, "
                 "reported as stored; the presence of a domain in the list is not evidence a "
                 "meeting used it, and how the app populates the list was not sourced. Only the "
                 "settings named here are reported; the remaining keys in the table hold the "
                 "fetched server configuration, feature toggles and interface preferences. The "
                 "existing nonempty Value display is retained. Present empty, NULL and false/zero "
                 "values are retained with explicit status and reversible Raw Value JSON; missing "
                 "named keys have no row. Stored Root Value preserves the source SQL value "
                 "(BLOB bytes use tagged hexadecimal JSON). Invalid, NULL or non-object settings "
                 "documents produce a neutral Settings Document row, without inferred nested keys. "
                 "Known Domains retains its joined display only for lists of strings; raw JSON "
                 "retains list structure. Duplicate table keys still follow the existing last-key "
                 "dictionary behavior. These settings do not establish meeting use or ownership.",
        "paths": ('*/org.jitsi.meet/databases/RKStorage*',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "emu_a15_oss_v2": "Android 15 | org.jitsi.meet vc 26000002 | 4 rows",
        },
    }
}

import json

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, logfunc
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/RKStorage'

RECENT_KEY = '@jitsi-meet/features/recent-list'
SETTINGS_KEY = '@jitsi-meet/features/base/settings'
DOMAINS_KEY = '@jitsi-meet/features/base/known-domains'
INSTALL_ID_KEY = '@jitsi-meet/jitsiMeetId'
CALLSTATS_KEY = '@jitsi-meet/callStatsUserName'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _values(db_path):
    query = 'SELECT key, value FROM catalystLocalStorage'
    records = get_sqlite_db_records(db_path, query)
    return {r[0]: r[1] for r in records} if records else {}


def _loads(raw):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def _room_name(url):
    if not url:
        return ''
    return url.rstrip('/').rsplit('/', 1)[-1]


@artifact_processor
def jitsi_meet_recent_meetings(context):
    data_list = []
    sources = []
    for db_path in _db_files(context):
        entries = _loads(_values(db_path).get(RECENT_KEY))
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            url = entry.get('conference') or ''
            duration = entry.get('duration')
            seconds = round(duration / 1000, 1) if isinstance(duration, (int, float)) else ''
            data_list.append((_ms(entry.get('date')), _room_name(url), url, seconds,
                              context.get_relative_path(db_path)))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (('Date', 'datetime'), 'Room Name', 'Conference URL',
                    'Duration (seconds)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


def _sql_json(value):
    """Tag source SQL values without treating stored strings as decoded JSON."""
    if isinstance(value, bytes):
        return json.dumps({'storage_kind': 'blob', 'hex': value.hex()})
    kind = 'null' if value is None else ('integer' if isinstance(value, int)
                                       else 'real' if isinstance(value, float) else 'text')
    return json.dumps({'storage_kind': kind, 'value': value}, ensure_ascii=False)


def _setting_status(value):
    if value is None:
        return 'JSON null'
    if value == '' and isinstance(value, str):
        return 'Empty string'
    if isinstance(value, (list, dict)) and not value:
        return 'Empty list' if isinstance(value, list) else 'Empty object'
    return 'Present value'


@artifact_processor
def jitsi_meet_settings(context):
    data_list = []
    sources = []
    for db_path in _db_files(context):
        values = _values(db_path)
        if not values:
            continue
        rel = context.get_relative_path(db_path)

        def append(name, value, raw, status=None, decoded=True, display=None, source=rel):
            raw_json = (json.dumps(value, ensure_ascii=False) if decoded else _sql_json(value))
            root_value = _sql_json(raw) if isinstance(raw, bytes) else raw
            shown = str(value) if display is None and value is not None else display
            data_list.append((name, shown, status or _setting_status(value), raw_json,
                              root_value, source))

        if SETTINGS_KEY in values:
            raw = values[SETTINGS_KEY]
            try:
                settings = json.loads(raw)
            except (TypeError, ValueError, UnicodeDecodeError):
                append('Settings Document', raw, raw,
                       'SQL NULL' if raw is None else 'Invalid JSON', decoded=False,
                       display='' if isinstance(raw, bytes) else None)
                logfunc(f'Jitsi settings document is NULL or invalid JSON: {rel}')
            else:
                if isinstance(settings, dict):
                    for name, key in [('Display Name', 'displayName'), ('Email', 'email')]:
                        if key in settings:
                            append(name, settings[key], raw)
                else:
                    append('Settings Document', settings, raw,
                           'JSON null' if settings is None else 'Unsupported settings shape')
                    logfunc(f'Jitsi settings document is not an object: {rel}')
        for name, key in [('Install ID', INSTALL_ID_KEY), ('Call Stats Username', CALLSTATS_KEY)]:
            if key in values:
                value = values[key]
                status = 'SQL NULL' if value is None else _setting_status(value)
                append(name, value, value, status, decoded=False,
                       display='' if isinstance(value, bytes) else None)
        if DOMAINS_KEY in values:
            raw = values[DOMAINS_KEY]
            try:
                domains = json.loads(raw)
            except (TypeError, ValueError, UnicodeDecodeError):
                append('Known Domains', raw, raw,
                       'SQL NULL' if raw is None else 'Invalid JSON', decoded=False,
                       display='' if isinstance(raw, bytes) else None)
                logfunc(f'Jitsi known-domains value is NULL or invalid JSON: {rel}')
            else:
                if isinstance(domains, list) and all(isinstance(v, str) for v in domains):
                    append('Known Domains', domains, raw, display=', '.join(domains))
                else:
                    append('Known Domains', domains, raw,
                           _setting_status(domains) if domains is None else 'Unsupported domain shape')
                    logfunc(f'Jitsi known-domains value is not a string list: {rel}')
        if db_path not in sources:
            sources.append(db_path)

    data_headers = ('Setting', 'Value', 'Value Status', 'Raw Value JSON',
                    'Stored Root Value', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
