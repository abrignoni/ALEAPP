# pylint: disable=W0613
__artifacts_v2__ = {
    "get_TripEvents": {
        "name": "Life360 Driver Behavior - Trip Events",
        "description": "Parses Events from Life360 DriverBehavior/trips JSON files",
        "author": "Heather Charpentier",
        "creation_date": "2024-09-17",
        "last_update_date": "2024-09-17",
        "requirements": "none",
        "category": "Life360DriverBehavior",
        "notes": "Processes event data from trip JSON files",
        "paths": ('*/trips/*.json',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    },
    "get_TripWaypoints": {
        "name": "Life360 Driver Behavior - Trip Waypoints",
        "description": "Parses Waypoints from Life360 DriverBehavior/trips JSON files",
        "author": "Heather Charpentier",
        "creation_date": "2024-09-17",
        "last_update_date": "2024-09-17",
        "requirements": "none",
        "category": "Life360DriverBehavior",
        "notes": "Processes waypoint data from trip JSON files",
        "paths": ('*/trips/*.json',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "map-pin",
    }
}

import datetime
import json

from scripts.ilapfuncs import artifact_processor

TARGET_DIRECTORY = 'data/com.life360.android.safetymapd/files/DriverBehavior/trips'


def _mps_to_mph(value):
    if value != '' and value is not None:
        return round(float(value) * 2.23694, 2)
    return ''


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


def _iter_trip_files(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.startswith('\\\\?\\'):
            file_found = file_found[4:]
        if file_found.endswith('.json') and TARGET_DIRECTORY in file_found.replace('\\', '/'):
            try:
                with open(file_found, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                continue
            if 'events' in data:
                yield file_found, data


@artifact_processor
def get_TripEvents(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found, data in _iter_trip_files(files_found):
        source_path = file_found
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

    data_headers = (('Timestamp', 'datetime'), 'Event Type', 'Latitude', 'Longitude', 'Speed (m/s)', 'Speed (mph)',
                    'Top Speed (m/s)', 'Top Speed (mph)', 'Average Speed (m/s)', 'Average Speed (mph)',
                    'Distance (m)', 'Trip ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_TripWaypoints(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found, data in _iter_trip_files(files_found):
        source_path = file_found
        for event in data.get('events', []):
            trip_id = event.get('tripId', '')
            for waypoint in event.get('waypoints', []):
                data_list.append((waypoint.get('lat', ''), waypoint.get('lon', ''), waypoint.get('accuracy', ''), trip_id))

    data_headers = ('Latitude', 'Longitude', 'Accuracy (m)', 'Trip ID')
    return data_headers, data_list, source_path
