# pylint: disable=W0718
__artifacts_v2__ = {
    "get_mmw_activities": {
        "name": "Map My Walk - Activities",
        "description": "One row per localId in the timeSeries table of workout.db, with the first and last stored time and position, the last stored distance value and a route drawn from the stored coordinates",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}, @AlexisBrignoni, Codex",
        "creation_date": "2023-02-24",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Map My Walk",
        "notes": "Samples are ordered by interpreted integer Unix milliseconds, with eligible "
                 "timestamps first; zero and negative timestamps are eligible when representable. "
                 "NULL, empty, nonnumeric, nonfinite and unrepresentable timestamps remain in an "
                 "undated tail. Equal-time and undated samples use typed source-field ordering, "
                 "which does not establish event precedence. Raw Samples JSON preserves source "
                 "types, values, query positions, eligibility and ordered positions without "
                 "dropping duplicates. Start/End/Duration use eligible timestamps only. Last "
                 "Ordered Distance (as stored) is the last non-NULL distance in that order, "
                 "not a maximum; distance/speed units and vendor timestamp meanings remain "
                 "unverified. Routes retain coordinate-bearing undated samples at the tail, "
                 "which is not proven chronological. Only the first workout.db is read. "
                 "Positive genuine coverage remains unavailable.",
        "paths": ('*com.mapmywalk.android2/databases/workout.db*',),
        "output_types": "all",
        "artifact_icon": "activity",
    }
}

import base64
import datetime
import json
import math
import sqlite3

from scripts.geo_utils import render_gps_track_png, build_track_kml
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_embedded_media


def _timestamp(value):
    """Retain existing integer-millisecond interpretation, with explicit eligibility."""
    if value is None or value == '':
        return None, '', 'missing'
    if isinstance(value, float) and not math.isfinite(value):
        return None, '', 'nonfinite'
    try:
        milliseconds = int(value)
    except (ValueError, OverflowError, TypeError):
        return None, '', 'nonnumeric'
    try:
        date = datetime.datetime.fromtimestamp(milliseconds / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return None, '', 'unrepresentable'
    return milliseconds, date, 'eligible'


def _typed_value(value):
    """Encode SQLite values without losing text/numeric/BLOB distinctions."""
    if value is None:
        return {'type': 'null', 'value': None}
    if isinstance(value, bytes):
        return {'type': 'blob', 'base64': base64.b64encode(value).decode('ascii')}
    if isinstance(value, int):
        return {'type': 'integer', 'value': value}
    if isinstance(value, float):
        return {'type': 'real', 'hex': value.hex()}
    return {'type': 'text', 'value': value}


def _ordered_samples(points):
    observations = []
    for position, point in enumerate(points):
        milliseconds, date, status = _timestamp(point[0])
        fields = [_typed_value(value) for value in point]
        canonical = json.dumps(fields, ensure_ascii=True, sort_keys=True, separators=(',', ':'))
        observations.append((milliseconds, date, status, fields, canonical, position, point))
    observations.sort(key=lambda item: (item[0] is None, item[0] if item[0] is not None else 0, item[4]))
    inventory = [{'query_position': item[5], 'ordered_position': index,
                  'timestamp_status': item[2], 'interpreted_timestamp_ms': item[0],
                  'fields': dict(zip(('timestamp', 'distance', 'speed', 'latitude', 'longitude'), item[3]))}
                 for index, item in enumerate(observations)]
    return observations, json.dumps(inventory, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('workout.db'):
            return file_found
    return ''


def _q(cursor, sql, params=()):
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    except sqlite3.Error:
        return []


def _route_media(source, coords, title, subtitle, base):
    route_map = ''
    png = render_gps_track_png(coords, title=title, subtitle=subtitle)
    if png:
        route_map = check_in_embedded_media(source, png, f'{base}.png', force_type='image/png',
                                            force_extension='png') or ''
    route_kml = ''
    kml = build_track_kml(coords, name=base)
    if kml:
        route_kml = check_in_embedded_media(source, kml, f'{base}.kml',
                                            force_type='application/vnd.google-earth.kml+xml',
                                            force_extension='kml') or ''
    return route_map, route_kml


@artifact_processor
def get_mmw_activities(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        for (lid,) in _q(cursor, 'SELECT localId FROM timeSeries GROUP BY localId'):
            pts = _q(cursor, '''SELECT timestamp, distance, speed, latitude, longitude
                FROM timeSeries WHERE localId = ?''', (lid,))
            observations, raw_samples = _ordered_samples(pts)
            pts = [item[6] for item in observations]
            eligible = [item for item in observations if item[0] is not None]
            coords = [(p[3], p[4]) for p in pts if p[3] is not None and p[4] is not None]
            speeds = [p[2] for p in pts if p[2] is not None]
            dists = [p[1] for p in pts if p[1] is not None]
            start_t = eligible[0][1] if eligible else ''
            end_t = eligible[-1][1] if eligible else ''
            distance = dists[-1] if dists else ''
            mean_speed = round(sum(speeds) / len(speeds), 2) if speeds else ''
            duration_min = round((eligible[-1][0] - eligible[0][0]) / 60000, 2) if len(eligible) >= 2 else ''
            start_lat, start_lon = coords[0] if coords else ('', '')
            end_lat, end_lon = coords[-1] if coords else ('', '')
            title = f'Map My Walk {lid}'
            subtitle = start_t.strftime('%Y-%m-%d %H:%M UTC') if start_t else ''
            route_map, route_kml = _route_media(source_path, coords, title, subtitle, f'{lid}_route')
            data_list.append((start_t, end_t, lid, distance, mean_speed, duration_min, start_lat,
                              start_lon, end_lat, end_lon, raw_samples, route_map, route_kml))
        db.close()

    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'ID', 'Last Ordered Distance (as stored)',
                    'Mean Speed', 'Duration (min)', 'Latitude', 'Longitude', 'End Latitude',
                    'End Longitude', 'Raw Samples JSON', ('Route Map', 'media'), ('Route KML', 'media'))
    return data_headers, data_list, source_path
