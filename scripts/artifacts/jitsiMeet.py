__artifacts_v2__ = {
    "jitsi_meet_recent_meetings": {
        "name": "Jitsi Meet - Recent Meetings",
        "description": "Parses the recent meeting list stored by the Jitsi Meet Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Jitsi Meet",
        "notes": "One row per entry in the app's recent-meeting list. Jitsi Meet is a React Native app "
                 "and keeps its state in the AsyncStorage database databases/RKStorage, in the "
                 "catalystLocalStorage table, one JSON document per key. This artifact reads the key "
                 "@jitsi-meet/features/recent-list, whose entries the app defines as conference, date "
                 "and duration (the IRecent type in react/features/recent-list/reducer.ts at "
                 "jitsi/jitsi-meet 98de6219cc7ddbe07ace9fde045aff90a242ba01). Conference URL is the full "
                 "meeting URL as stored, which carries both the server that hosted the meeting and the "
                 "room name, and Room Name is the last path segment of that URL. Joined is the date "
                 "field, set from Date.now() when the conference is added, so it is Unix milliseconds "
                 "and is reported as UTC; on the tested device 18:26 UTC matched the device's 2:26 PM "
                 "local clock. Duration is the duration field, which the same source computes as "
                 "Date.now() minus date when the conference ends, so it is milliseconds and is reported "
                 "here in seconds. A row records that the app joined that meeting from this device, not "
                 "who else attended, and the app does not store the participants or the chat here. An "
                 "entry that is still open, or a join that never completed, can carry a zero duration.",
        "paths": ('*/org.jitsi.meet/databases/RKStorage*',),
        "output_types": "standard",
        "artifact_icon": "video",
        "sample_data": {
            "emu_a15_oss_v2": "Android 15 | org.jitsi.meet vc 26000002 | 1 rows",
        },
    },
    "jitsi_meet_settings": {
        "name": "Jitsi Meet - Settings",
        "description": "Parses the account-free profile and server settings stored by the Jitsi Meet Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Jitsi Meet",
        "notes": "One row per reported setting read from the catalystLocalStorage table of "
                 "databases/RKStorage. Jitsi Meet needs no account, so the identifying values it keeps "
                 "are these. Display Name and Email come from the @jitsi-meet/features/base/settings "
                 "document and hold the self-chosen name and address the app presents to other "
                 "participants; on the tested device the display name entered at the join screen was "
                 "stored here and no email was set. Install ID is @jitsi-meet/jitsiMeetId, a "
                 "value the app generates and keeps across meetings, so the same value appearing "
                 "elsewhere ties activity to this installation. Call Stats Username is "
                 "@jitsi-meet/callStatsUserName, a name the app generates for its statistics service and "
                 "not one the user chose. Known Domains is @jitsi-meet/features/base/known-domains, the "
                 "list of servers the app has seen, which shows whether meetings used the public "
                 "meet.jit.si service or a self-hosted server; the list is seeded with the app's own "
                 "defaults, so the presence of a default entry is not evidence a meeting used it. Only "
                 "the settings named here are reported; the remaining keys in the table hold the fetched "
                 "server configuration, feature toggles and interface preferences. The value of each "
                 "setting is reported as stored and a setting the app never wrote is absent rather than "
                 "empty.",
        "paths": ('*/org.jitsi.meet/databases/RKStorage*',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "emu_a15_oss_v2": "Android 15 | org.jitsi.meet vc 26000002 | 4 rows",
        },
    }
}

import json

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
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

    data_headers = (('Joined', 'datetime'), 'Room Name', 'Conference URL',
                    'Duration (seconds)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def jitsi_meet_settings(context):
    data_list = []
    sources = []
    for db_path in _db_files(context):
        values = _values(db_path)
        if not values:
            continue
        settings = _loads(values.get(SETTINGS_KEY)) or {}
        domains = _loads(values.get(DOMAINS_KEY))
        rel = context.get_relative_path(db_path)

        reported = [
            ('Display Name', settings.get('displayName')),
            ('Email', settings.get('email')),
            ('Install ID', values.get(INSTALL_ID_KEY)),
            ('Call Stats Username', values.get(CALLSTATS_KEY)),
            ('Known Domains', ', '.join(domains) if isinstance(domains, list) else None),
        ]
        for name, value in reported:
            if value:
                data_list.append((name, str(value), rel))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = ('Setting', 'Value', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
