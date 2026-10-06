__artifacts_v2__ = {
    "get_TripEvents": {
        "name": "Life360 Driver Behavior - Trip Events",
        "description": "Parses Events from Life360 DriverBehavior/trips JSON files",
        "author": "Heather Charpentier; @AlexisBrignoni, Codex",
        "creation_date": "2024-09-17",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Life360DriverBehavior",
        "notes": "Reads the events list of each JSON file under "
                 "the exact com.life360.android.safetymapd/files/DriverBehavior/trips path under "
                 "legacy data, data/data, numeric user/user_de and data_mirror CE/DE namespaces. "
                 "Each selected input occurrence is retained, including equal or conflicting aliases; "
                 "rows are not unique trips. Files without an events key are skipped. Source File "
                 "is added only when multiple distinct files contribute rows to this artifact. "
                 "Timestamp is the event's timestamp value read as Unix "
                 "seconds, which is an assumption. Speed and distance are reported as stored; "
                 "the JSON records no units for them. The MPH columns multiply the stored speed by "
                 "2.23694, which assumes the stored value is in metres per second.",
        "paths": ('*/trips/*.json',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    },
    "get_TripWaypoints": {
        "name": "Life360 Driver Behavior - Trip Waypoints",
        "description": "Parses Waypoints from Life360 DriverBehavior/trips JSON files",
        "author": "Heather Charpentier; @AlexisBrignoni, Codex",
        "creation_date": "2024-09-17",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Life360DriverBehavior",
        "notes": "Reads the waypoints list of each event in the JSON files under "
                 "the exact com.life360.android.safetymapd/files/DriverBehavior/trips path under "
                 "legacy data, data/data, numeric user/user_de and data_mirror CE/DE namespaces. "
                 "Each selected input occurrence is retained, including equal or conflicting aliases; "
                 "rows are not unique trips. Files without an events key are skipped. Source File "
                 "is added only when multiple distinct files contribute rows to this artifact. "
                 "Accuracy is reported as stored; the "
                 "JSON records no unit for it.",
        "paths": ('*/trips/*.json',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "map-pin",
    }
}

import datetime
import json
import re

from scripts.ilapfuncs import artifact_processor

TARGET_DIRECTORY = 'com.life360.android.safetymapd/files/DriverBehavior/trips'
_TRIP_PATH_RE = re.compile(
    r'(?:^|/)(?:data/(?:data/|user(?:_de)?/\d+/)?|data_mirror/data_(?:ce|de)/[^/]+/\d+/)'
    + re.escape(TARGET_DIRECTORY) + r'/.+\.json$')


def _mps_to_mph(value):
    if value != '' and value is not None:
        return round(float(value) * 2.23694, 2)
    return ''


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


def _iter_trip_files(context):
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if file_found.startswith('\\\\?\\'):
            file_found = file_found[4:]
        relative_path = context.get_relative_path(file_found).replace('\\', '/')
        if _TRIP_PATH_RE.search(relative_path):
            try:
                with open(file_found, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                continue
            if 'events' in data:
                yield file_found, data


def _trip_result(context, headers, rows, row_sources):
    """Keep occurrence rows and identify only their actual contributing files."""
    sources = list(dict.fromkeys(row_sources))
    if len(sources) > 1:
        headers += ('Source File',)
        rows = [row + (context.get_relative_path(source),)
                for row, source in zip(rows, row_sources)]
    return headers, rows, '\n'.join(sources)


@artifact_processor
def get_TripEvents(context):
    data_list = []
    row_sources = []
    for file_found, data in _iter_trip_files(context):
        for event in data.get('events', []):
            timestamp = _sec_to_utc(event.get('timestamp', 0))
            speed = event.get('speed', '')
            top_speed = event.get('topSpeed', '')
            avg_speed = event.get('averageSpeed', '')
            data_list.append((
                timestamp,
                event.get('eventType', ''),
                event.get('location', {}).get('lat', ''),
                event.get('location', {}).get('lon', ''),
                speed,
                _mps_to_mph(speed),
                top_speed,
                _mps_to_mph(top_speed),
                avg_speed,
                _mps_to_mph(avg_speed),
                event.get('distance', ''),
                event.get('tripId', ''),
            ))
            row_sources.append(file_found)

    data_headers = (('Timestamp', 'datetime'), 'Event Type', 'Latitude', 'Longitude',
                    'Speed (as stored)', 'Speed MPH (assumes m/s)',
                    'Top Speed (as stored)', 'Top Speed MPH (assumes m/s)',
                    'Average Speed (as stored)', 'Average Speed MPH (assumes m/s)',
                    'Distance (as stored)', 'Trip ID')
    return _trip_result(context, data_headers, data_list, row_sources)


@artifact_processor
def get_TripWaypoints(context):
    data_list = []
    row_sources = []
    for file_found, data in _iter_trip_files(context):
        for event in data.get('events', []):
            trip_id = event.get('tripId', '')
            for waypoint in event.get('waypoints', []):
                data_list.append((waypoint.get('lat', ''), waypoint.get('lon', ''), waypoint.get('accuracy', ''), trip_id))
                row_sources.append(file_found)

    data_headers = ('Latitude', 'Longitude', 'Accuracy (as stored)', 'Trip ID')
    return _trip_result(context, data_headers, data_list, row_sources)
