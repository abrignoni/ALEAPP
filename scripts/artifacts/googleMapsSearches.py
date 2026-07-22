# pylint: disable=W0718
__artifacts_v2__ = {
    "get_googleMapsSearches": {
        "name": "Google Maps Searches",
        "description": "Recent Google Maps search history (new_recent_history_cache_search.cs)",
        "author": "",
        "creation_date": "2023-10-15",
        "last_update_date": "2023-10-15",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "",
        "paths": ('*/com.google.android.apps.maps/files/new_recent_history_cache_search.cs',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.apps.maps vc 1068243484 | 7 rows",
            "galaxys10_a10": "Android 10 | com.google.android.apps.maps vc 1064201040 | 10 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.maps vc 1067620099 | 6 rows",
            "samsungs20_a13": "Android 13 | com.google.android.apps.maps vc 1068347331 | 1 row",
            "sharon_a14": "Android 14 | com.google.android.apps.maps vc 1067648704 | 8 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.maps vc 1067057900 | 7 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.maps vc 1067804533 | 6 rows",
        },
    }
}

import datetime

from scripts.ilapfuncs import decode_protobuf

from scripts.ilapfuncs import artifact_processor

TYPEDEF = {'1': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'bytes', 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '4': {'type': 'bytes', 'name': ''}, '5': {'type': 'message', 'message_typedef': {'3': {'type': 'double', 'name': ''}, '4': {'type': 'double', 'name': ''}}, 'name': ''}, '10': {'type': 'int', 'name': ''}, '11': {'type': 'bytes', 'name': ''}, '12': {'type': 'int', 'name': ''}, '13': {'type': 'int', 'name': ''}, '14': {'type': 'int', 'name': ''}, '17': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'3': {'type': 'fixed64', 'name': ''}, '4': {'type': 'fixed64', 'name': ''}}, 'name': ''}, '5': {'type': 'bytes', 'name': ''}, '6': {'type': 'bytes', 'name': ''}, '8': {'type': 'fixed32', 'name': ''}, '9': {'type': 'int', 'name': ''}, '10': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'bytes', 'name': ''}}, 'name': ''}, '11': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'4': {'type': 'bytes', 'name': ''}, '5': {'type': 'message', 'message_typedef': {'3': {'type': 'int', 'name': ''}, '4': {'type': 'int', 'name': ''}, '5': {'type': 'int', 'name': ''}, '6': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '14': {'type': 'bytes', 'name': ''}, '16': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {}, 'name': ''}}, 'name': ''}, '21': {'type': 'bytes', 'name': ''}, '24': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '4': {'type': 'bytes', 'name': ''}, '5': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '6': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'double', 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}}, 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '4': {'type': 'fixed32', 'name': ''}}, 'name': ''}, '16': {'type': 'int', 'name': ''}}, 'name': ''}, '9': {'type': 'int', 'name': ''}, '1': {'type': 'bytes', 'name': ''}, '11': {'type': 'bytes', 'name': ''}}, 'name': ''}, '2': {'type': 'bytes', 'name': ''}}


def _us_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _extract_search(item):
    timeofsearch = item['2']
    place = item.get('4', '')
    latitude = ''
    longitude = ''
    if place != '':
        if item['4'].get('5', '') != '':
            latitude = item['4']['5']['3']
            longitude = item['4']['5']['4']
        elif item['4'].get('6', '') != '':
            latitude = item['4']['6']['1']['3']
            longitude = item['4']['6']['1']['2']
    url = item.get('11', 'No URL')
    place = place if isinstance(place, str) else place['1'].decode()
    url = url if isinstance(url, str) else url.decode()
    return (_us_to_utc(timeofsearch), place, latitude, longitude, url)


@artifact_processor
def get_googleMapsSearches(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        try:
            with open(file_found, 'rb') as f:
                data = f.read()
            values, _ = decode_protobuf(data[8:], TYPEDEF)
        except Exception:
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
                data_list.append(_extract_search(item))
            except (KeyError, TypeError, AttributeError):
                continue

    data_headers = (('Timestamp', 'datetime'), 'Place', 'Latitude', 'Longitude', 'URL')
    return data_headers, data_list, source_path
