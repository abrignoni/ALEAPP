# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_mmw_activities": {
        "name": "Map My Walk - Activities",
        "description": "Map My Walk activities with GPS routes (workout.db)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "none",
        "category": "Map My Walk",
        "notes": "Interactive folium map and online reverse-geocoding removed; route shown as an "
                 "offline image (media) + a downloadable route KML.",
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
def get_mmw_activities(files_found, report_folder, seeker, wrap_text):
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
            data_list.append((lid, start_t, end_t, distance, mean_speed, duration_min, start_lat,
                              start_lon, end_lat, end_lon, route_map, route_kml))
        db.close()

    data_headers = ('ID', ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Distance (km)',
                    'Mean Speed', 'Duration (min)', 'Latitude', 'Longitude', 'End Latitude',
                    'End Longitude', ('Route Map', 'media'), ('Route KML', 'media'))
    return data_headers, data_list, source_path
