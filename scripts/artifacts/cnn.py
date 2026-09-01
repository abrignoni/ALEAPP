__artifacts_v2__ = {
    "cnnAndroidSearches": {
        "name": "CNN - Searches",
        "description": "Search terms the CNN app kept in its recent search list.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "CNN",
        "notes": "Read from files/datastore/search.preferences_pb, an Android DataStore preferences "
                 "file. The file is a protobuf in which each entry pairs a key with a typed value; the "
                 "recent_search key holds a JSON array of strings, which is decoded and reported one "
                 "term per row. Position is the term's index in that array as stored. The store "
                 "records no timestamp for a search, so there is nothing here to say when a term was "
                 "entered, and the list order is reported as stored rather than asserted to be "
                 "chronological. Repeated terms are reported as they appear because the app stores "
                 "them that way. A term is evidence that the search was issued from this app; it does "
                 "not establish who typed it. The app keeps further DataStore files that are "
                 "deliberately not reported: com.cnn.storage holds advertising configuration, "
                 "tooltip_prefs holds interface state, the firebase_session files hold telemetry, and "
                 "data_migration_executor holds migration flags. The app's DataStore files were "
                 "present on 2 of the registered Android corpora swept for them and both carry rows, "
                 "so the counts recorded here come from two independent extractions.",
        "paths": ('*/com.cnn.mobile.android.phone/files/datastore/search.preferences_pb',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 5 rows",
            "falken_a326u_a13": "Android 13 | 4 rows",
        },
    },
    "cnnAndroidArticles": {
        "name": "CNN - Article Views",
        "description": "CNN articles the app recorded as viewed, with the article identifier "
                       "decoded from the form the app stores.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "CNN",
        "notes": "Read from files/datastore/article_meter.preferences_pb and "
                 "article_shown.preferences_pb, Android DataStore preferences files. The "
                 "article_meter_set key holds a JSON array of identifiers and current_article holds a "
                 "single one; each identifier is base64 of a path of the form /_pages/<id>, which is "
                 "decoded and reported beside the stored value so the decoding can be checked. Source "
                 "Key records which key a row came from, so a row from the metered set and the single "
                 "current article are distinguishable. The meter set is the app's own count-limiting "
                 "list rather than a complete reading history, and the store records no per-article "
                 "timestamp, so a row says the app registered a view of that article before the reset "
                 "date and nothing about when. Meter Reset Date is the value stored against "
                 "last_article_meter_reset_date, an eight digit YYYYMMDD value with no time or zone "
                 "recorded. The identifier is the publisher's internal page id; the store holds no "
                 "headline or URL, so none is reported. The app's DataStore files were present on 2 of "
                 "the registered Android corpora swept for them and both carry rows, so the counts "
                 "recorded here come from two independent extractions.",
        "paths": ('*/com.cnn.mobile.android.phone/files/datastore/article_meter.preferences_pb',
                  '*/com.cnn.mobile.android.phone/files/datastore/article_shown.preferences_pb'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "news",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 5 rows",
            "falken_a326u_a13": "Android 13 | 3 rows",
        },
    },
}

import base64
import json
import os

import scripts.blackboxprotobuf as blackboxprotobuf
from scripts.ilapfuncs import artifact_processor, logfunc

# An Android DataStore preferences file is a protobuf whose field 1 repeats one entry per
# stored preference: field 1 of the entry is the key and field 2 is a typed value, whose
# field 5 is the string variant. Only string values are read here.
_ENTRIES = '1'
_KEY = '1'
_VALUE = '2'
_STRING = '5'


def _as_text(value):
    return value.decode('utf-8', 'replace') if isinstance(value, (bytes, bytearray)) else value


def _preferences(path):
    """{key: string value} for a DataStore preferences file, or {} when unreadable."""
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except OSError as error:
        logfunc(f'CNN: could not read {os.path.basename(path)}: {error}')
        return {}
    try:
        message, _ = blackboxprotobuf.decode_message(raw)
    except Exception as error:  # pylint: disable=broad-exception-caught
        logfunc(f'CNN: {os.path.basename(path)} did not decode as protobuf: {error}')
        return {}
    entries = message.get(_ENTRIES)
    if entries is None:
        return {}
    if not isinstance(entries, list):
        entries = [entries]
    out = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        key = _as_text(entry.get(_KEY))
        value = entry.get(_VALUE)
        if key and isinstance(value, dict) and _STRING in value:
            out[key] = _as_text(value[_STRING])
    return out


def _json_list(value):
    """The members of a JSON array held as a string, or [] when it is not one."""
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return []
    return [item for item in parsed if isinstance(item, str)] if isinstance(parsed, list) else []


def _decoded_identifier(value):
    """The base64 identifier decoded to its path form, or '' when it does not decode."""
    if not value:
        return ''
    try:
        text = base64.b64decode(value + '=' * (-len(value) % 4)).decode('utf-8')
    except (ValueError, UnicodeDecodeError):
        return ''
    return text if text.startswith('/') else ''


def _files(files_found, basename):
    found = []
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isdir(file_found) and os.path.basename(file_found) == basename:
            found.append(file_found)
    return found


@artifact_processor
def cnnAndroidSearches(context):
    data_headers = (
        'Position',
        'Search Term',
        'Source File',
    )
    data_list = []
    source_files = []

    for path in _files(context.get_files_found(), 'search.preferences_pb'):
        terms = _json_list(_preferences(path).get('recent_search'))
        for index, term in enumerate(terms):
            data_list.append((index, term, context.get_relative_path(path)))
        if terms:
            source_files.append(path)

    return data_headers, data_list, '\n'.join(source_files)


@artifact_processor
def cnnAndroidArticles(context):
    data_headers = (
        'Article Path',
        'Article ID (as stored)',
        'Source Key',
        'Meter Reset Date (as stored, no zone recorded)',
        'Source File',
    )
    data_list = []
    source_files = []

    for basename, keys in (('article_meter.preferences_pb', ('article_meter_set',)),
                           ('article_shown.preferences_pb', ('current_article',))):
        for path in _files(context.get_files_found(), basename):
            preferences = _preferences(path)
            reset = preferences.get('last_article_meter_reset_date', '')
            rows = 0
            for key in keys:
                stored = preferences.get(key)
                if not stored:
                    continue
                identifiers = _json_list(stored) or [stored]
                for identifier in identifiers:
                    rows += 1
                    data_list.append((
                        _decoded_identifier(identifier),
                        identifier,
                        key,
                        reset,
                        context.get_relative_path(path),
                    ))
            if rows:
                source_files.append(path)

    return data_headers, data_list, '\n'.join(source_files)
