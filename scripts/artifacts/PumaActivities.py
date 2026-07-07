# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_puma_activities": {
        "name": "Puma - Activities",
        "description": "Pumatrac activities with GPS routes (pumatrac-db)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "none",
        "category": "Puma",
        "notes": "Interactive folium map and online reverse-geocoding removed; route shown as an "
                 "offline image (media) + a downloadable route KML.",
        "paths": ('*com.pumapumatrac/databases/pumatrac-db*',),
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
        if file_found.endswith('pumatrac-db'):
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
def get_puma_activities(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        acts = _q(cursor, '''SELECT id, startTime, endTime, duration, score, calories, city, country,
            distance, maxAltitude, meanAltitude, maxSpeed, meanSpeed, averageTimePerKm,
            runLocationType, currentPace FROM completed_exercises''')
        for a in acts:
            aid = a[0]
            pts = _q(cursor, 'SELECT lat, lng FROM positions WHERE completedExerciseId = ?', (aid,))
            coords = [(p[0], p[1]) for p in pts if p[0] is not None and p[1] is not None]
            start_lat, start_lon = coords[0] if coords else ('', '')
            end_lat, end_lon = coords[-1] if coords else ('', '')
            start_t = _ms_to_utc(a[1])
            title = f'Puma activity {aid}'
            subtitle = start_t.strftime('%Y-%m-%d %H:%M UTC') if start_t else ''
            route_map, route_kml = _route_media(source_path, coords, title, subtitle, f'{aid}_route')
            data_list.append((aid, start_t, _ms_to_utc(a[2]), a[3], a[4], a[5], a[6], a[7], a[8], a[9],
                              a[10], a[11], a[12], a[13], a[14], a[15], start_lat, start_lon, end_lat,
                              end_lon, route_map, route_kml))
        db.close()

    data_headers = ('ID', ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Duration', 'Score',
                    'Calories', 'City', 'Country', 'Distance', 'Max Altitude', 'Mean Altitude',
                    'Max Speed', 'Mean Speed', 'Average Time Per Km', 'Run Location Type',
                    'Current Pace', 'Latitude', 'Longitude', 'End Latitude', 'End Longitude',
                    ('Route Map', 'media'), ('Route KML', 'media'))
    return data_headers, data_list, source_path
