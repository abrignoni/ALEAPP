# pylint: disable=W0718
__artifacts_v2__ = {
    "get_googleInitiatedNav": {
        "name": "Google Maps - Navigated Cache Entries",
        "description": "Entries decoded from Google Maps' new_recent_history_cache_navigated.cs: protobuf field 2 read as Unix microseconds and the text of field 4.1. No source for the field meanings is cited. What the timestamp marks, and whether navigation was started, is not established.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2023-10-16",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "Field 4.1 Text is the UTF-8 text projection returned by the existing schemaless protobuf decoder from a decoded field 1 entry's field 4.1. Navigated in the artifact name follows the source cache filename new_recent_history_cache_navigated.cs; it does not establish that navigation was started. Timestamp preserves the module's existing interpretation of field 2 as Unix microseconds; the field meanings and the event the timestamp marks remain unestablished. Input is decoded after skipping its first 8 bytes. Preferred storage-path views are selected by the existing unique_files rules; other views are not compared. The report-level source is the last processed selected file, including one that contributes no row; individual rows are not associated with files. Existing decode, filtering, UTF-8 and malformed-shape limits remain. Original artifact contribution: @abrignoni.",
        "paths": ('*/new_recent_history_cache_navigated.cs',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.maps vc 1068243484 | 2 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.maps vc 1067057900 | 7 rows",
        },
    }
}

import datetime

from scripts.ilapfuncs import decode_protobuf

from scripts.ilapfuncs import artifact_processor
from scripts.artifacts.storagePathViews import unique_files


def _us_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_googleInitiatedNav(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        try:
            with open(file_found, 'rb') as f:
                data = f.read()
            values, _ = decode_protobuf(data[8:])
        except Exception:
            continue
        if not isinstance(values, dict):
            continue
        entry = values.get('1')
        if isinstance(entry, list):
            items = entry
        elif isinstance(entry, dict):
            items = [entry]
        else:
            items = []
        for item in items:
            try:
                data_list.append((_us_to_utc(item['2']), item['4']['1'].decode()))
            except (KeyError, TypeError, AttributeError):
                continue

    data_headers = (('Timestamp', 'datetime'), 'Field 4.1 Text')
    return data_headers, data_list, source_path
