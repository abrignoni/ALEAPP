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
        "notes": "Start Time, End Time and the start and end coordinates are taken from the "
                 "first and last timeSeries rows of each localId in the order the database "
                 "returns them. The query has no ORDER BY, so they are the earliest and latest "
                 "points only where the rows come back in time order. Timestamps are read as "
                 "Unix milliseconds. Duration (min) is the difference between those two times. "
                 "Last Returned Distance (as stored) is the last non-NULL distance in returned "
                 "query order, not necessarily the latest-time or largest distance. Mean Speed is the "
                 "average of the stored speed values; the unit of neither was established, and "
                 "the unordered chronology defect remains unresolved. Positive genuine coverage "
                 "is unavailable. Only the first workout.db found "
                 "is read. Route Map is an image drawn from the row's stored coordinates and "
                 "Route KML holds the same points; neither uses an online service.",
        "paths": ('*com.mapmywalk.android2/databases/workout.db*',),
        "output_types": "all",
        "artifact_icon": "activity",
    }
}

import datetime
import sqlite3

from scripts.geo_utils import render_gps_track_png, build_track_kml
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_embedded_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


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
            coords = [(p[3], p[4]) for p in pts if p[3] is not None and p[4] is not None]
            times = [p[0] for p in pts if p[0]]
            speeds = [p[2] for p in pts if p[2] is not None]
            dists = [p[1] for p in pts if p[1] is not None]
            start_t = _ms_to_utc(times[0]) if times else ''
            end_t = _ms_to_utc(times[-1]) if times else ''
            distance = dists[-1] if dists else ''
            mean_speed = round(sum(speeds) / len(speeds), 2) if speeds else ''
            duration_min = round((times[-1] - times[0]) / 60000, 2) if len(times) >= 2 else ''
            start_lat, start_lon = coords[0] if coords else ('', '')
            end_lat, end_lon = coords[-1] if coords else ('', '')
            title = f'Map My Walk {lid}'
            subtitle = start_t.strftime('%Y-%m-%d %H:%M UTC') if start_t else ''
            route_map, route_kml = _route_media(source_path, coords, title, subtitle, f'{lid}_route')
            data_list.append((start_t, end_t, lid, distance, mean_speed, duration_min, start_lat,
                              start_lon, end_lat, end_lon, route_map, route_kml))
        db.close()

    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'ID', 'Last Returned Distance (as stored)',
                    'Mean Speed', 'Duration (min)', 'Latitude', 'Longitude', 'End Latitude',
                    'End Longitude', ('Route Map', 'media'), ('Route KML', 'media'))
    return data_headers, data_list, source_path
