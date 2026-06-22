# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_googleInitiatedNav": {
        "name": "Google Initiated Navigation",
        "description": "Recent navigation destinations (new_recent_history_cache_navigated.cs)",
        "author": "",
        "creation_date": "2023-10-16",
        "last_update_date": "2023-10-16",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "",
        "paths": ('*/com.google.android.apps.maps/files/new_recent_history_cache_navigated.cs',
                  '*/new_recent_history_cache_navigated.cs'),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    }
}

import datetime

import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor


def _us_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_googleInitiatedNav(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        try:
            with open(file_found, 'rb') as f:
                data = f.read()
            values, _ = blackboxprotobuf.decode_message(data[8:])
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

    data_headers = (('Timestamp', 'datetime'), 'Initiated Navigation Destination')
    return data_headers, data_list, source_path
