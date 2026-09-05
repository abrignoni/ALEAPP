__artifacts_v2__ = {
    "easyvoicerecorder_library": {
        "name": "Easy Voice Recorder Library",
        "description": "Audio files listed in the Easy Voice Recorder library",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Easy Voice Recorder",
        "sample_data": {
            "emu_a15_oss_v10": "Easy Voice Recorder 2.10.3 | 4 rows",
        },
        "notes": "One row per row of the files table in "
                 "com.coffeebeanventures.easyvoicerecorder/databases/evr.db, which is the app's "
                 "own list of the audio in its recordings folder. The path column holds a Storage "
                 "Access Framework document URI rather than a filesystem path, so Folder and File "
                 "Name are decoded from that URI: the tree and document parts are percent-encoded "
                 "and the volume is named before a colon, which is why a URI ending "
                 "primary%3ARecordings%2Fnote.m4a is reported as the Recordings folder and the "
                 "file note.m4a. Document URI keeps the value exactly as stored so the decoding "
                 "can be checked. Duration is the app's own length_in_seconds column. A duration "
                 "of -1 is reported as blank and is what the app leaves when it could not read the "
                 "length; one such row was present on the tested device, from a recording the app "
                 "started and did not finish. There is no timestamp in this table, so a row says "
                 "the file was in the library and not when it was recorded; the file's own times "
                 "carry that. The row survives the audio file being deleted: one recording was "
                 "removed from the folder and the app reopened, and its row was still present, so "
                 "an entry whose path no longer resolves is a record that the file was once in the "
                 "folder. That was measured on this app rather than assumed, and it does not "
                 "generalise. MX Player, tested the same way on the same device, dropped its row "
                 "on the next scan. "
                 "Pinned is the should_be_stickied column and was No on every row of the tested "
                 "image, because nothing was pinned to the top of the app's list there. "
                 "**Validation limit:** the tested device is an emulator with no working "
                 "microphone, so no recording was made through the app. The rows were produced by "
                 "placing known audio in the recordings folder and letting the app index it, plus "
                 "the app's own incomplete-recording row. The parsing is proven against a real "
                 "store; the recording flow itself is not exercised here, and a sample from a "
                 "device that actually recorded would close that gap.",
        "paths": ('*/com.coffeebeanventures.easyvoicerecorder/databases/evr.db*',),
        "output_types": "standard",
        "artifact_icon": "mic",
    },
    "easyvoicerecorder_settings": {
        "name": "Easy Voice Recorder Settings",
        "description": "Where Easy Voice Recorder saves audio, and how much it has recorded",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Easy Voice Recorder",
        "sample_data": {
            "emu_a15_oss_v10": "Easy Voice Recorder 2.10.3 | 8 rows",
        },
        "notes": "One row per setting read from "
                 "com.coffeebeanventures.easyvoicerecorder/shared_prefs/"
                 "com.coffeebeanventures.easyvoicerecorder_preferences.xml. Only the keys an "
                 "examiner can act on are reported, and each is named in the Setting column as the "
                 "app stores it. saved_recordings_folder_key is the folder the app writes "
                 "recordings to, which matters because the user can point it anywhere and the "
                 "default is not the only place to look; most_recent_saved_recordings_folder_key "
                 "is the app's list of folders it has used, so a folder that appears there and is "
                 "not the current one was a previous destination. total_num_recordings_key and "
                 "num_recordings_key are the app's own counters and keep counting recordings that "
                 "have since been deleted, so a count higher than the number of rows in the Easy "
                 "Voice Recorder Library artifact is the gap worth following. install_info_key is "
                 "a JSON value holding the app's first install and last update times in Unix "
                 "milliseconds, and those two are reported as their own rows in UTC. Timestamp is "
                 "blank on every other row, because the rest of these settings carry no time. The "
                 "remaining keys in the file are theme, advertising and consent settings and are "
                 "not reported. Values are shown as stored.",
        "paths": ('*/com.coffeebeanventures.easyvoicerecorder/shared_prefs/'
                  'com.coffeebeanventures.easyvoicerecorder_preferences.xml',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
}

import json
import xml.etree.ElementTree as ET
from urllib.parse import unquote

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, \
    logfunc
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/evr.db'
PREFS_SUFFIX = 'com.coffeebeanventures.easyvoicerecorder_preferences.xml'

REPORTED_KEYS = (
    'saved_recordings_folder_key',
    'most_recent_saved_recordings_folder_key',
    'total_num_recordings_key',
    'num_recordings_key',
    '__v2_encoder_preference_key',
    'wave_sample_rate',
)


def _files(context, suffix):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(suffix)]


def _ms(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value // 1000)
    except (OverflowError, OSError, ValueError):
        return ''


def _saf_parts(uri):
    """Split a SAF document URI into (folder, file name). Blank when it is not one."""
    if not uri:
        return '', ''
    text = unquote(str(uri))
    marker = '/document/'
    if marker not in text:
        return '', ''
    document = text.split(marker, 1)[1]
    if ':' in document:
        document = document.split(':', 1)[1]
    document = document.strip('/')
    if '/' in document:
        folder, name = document.rsplit('/', 1)
        return folder, name
    return '', document


@artifact_processor
def easyvoicerecorder_library(context):
    query = ('SELECT path, length_in_seconds, should_be_stickied, _id '
             'FROM files ORDER BY _id')
    data_list = []
    sources = []
    for db_path in _files(context, DB_SUFFIX):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            folder, name = _saf_parts(r[0])
            duration = r[1] if r[1] is not None and r[1] >= 0 else ''
            data_list.append((
                name, folder, duration,
                'Yes' if r[2] else 'No', r[0] or '', r[3],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'File Name', 'Folder', 'Duration (seconds)', 'Pinned', 'Document URI',
        'Row ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def easyvoicerecorder_settings(context):
    data_list = []
    sources = []
    for prefs_path in _files(context, PREFS_SUFFIX):
        try:
            root = ET.parse(prefs_path).getroot()
        except (ET.ParseError, OSError) as error:
            logfunc(f'Could not read Easy Voice Recorder settings from {prefs_path}: {error}')
            continue

        found = False
        for element in root:
            key = element.attrib.get('name', '')
            if key not in REPORTED_KEYS:
                continue
            value = element.attrib.get('value')
            if value is None:
                value = (element.text or '').strip()
            found = True
            data_list.append((key, value, '', context.get_relative_path(prefs_path)))

        for element in root:
            if element.attrib.get('name') != 'install_info_key':
                continue
            raw = element.attrib.get('value')
            if raw is None:
                raw = (element.text or '').strip()
            try:
                info = json.loads(raw)
            except (ValueError, TypeError):
                continue
            if not isinstance(info, dict):
                continue
            for field, label in (('first_install_time', 'install_info_key first_install_time'),
                                 ('last_update_time', 'install_info_key last_update_time')):
                if field in info:
                    found = True
                    data_list.append((label, info[field], _ms(info[field]),
                                      context.get_relative_path(prefs_path)))

        if found and prefs_path not in sources:
            sources.append(prefs_path)

    data_headers = ('Setting', 'Value', ('Timestamp', 'datetime'), 'Source File')
    return data_headers, data_list, '\n'.join(sources)
