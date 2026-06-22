# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_run_activities": {
        "name": "Runkeeper - Activities",
        "description": "Runkeeper activities with GPS routes (RunKeeper.sqlite)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-03-25",
        "last_update_date": "2023-03-25",
        "requirements": "none",
        "category": "Runkeeper",
        "notes": "Interactive folium map and online reverse-geocoding removed; route shown as an "
                 "offline image (media) + a downloadable route KML.",
        "paths": ('*com.fitnesskeeper.runkeeper.pro/databases/RunKeeper.sqlite*',),
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
        if file_found.endswith('RunKeeper.sqlite'):
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
def get_run_activities(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        trips = _q(cursor, '''SELECT _id, start_date, device_sync_time, distance, elapsed_time,
            activity_type, calories, heart_rate, totalClimb, uuid, nickname FROM trips''')
        for t in trips:
            tid = t[0]
            pts = _q(cursor, 'SELECT latitude, longitude FROM points WHERE trip_id = ?', (tid,))
            coords = [(p[0], p[1]) for p in pts if p[0] is not None and p[1] is not None]
            start_lat, start_lon = coords[0] if coords else ('', '')
            end_lat, end_lon = coords[-1] if coords else ('', '')
            start_t = _ms_to_utc(t[1])
            title = f'{t[5] or "Runkeeper"} {tid}'
            subtitle = start_t.strftime('%Y-%m-%d %H:%M UTC') if start_t else ''
            route_map, route_kml = _route_media(source_path, coords, title, subtitle, f'{tid}_route')
            data_list.append((tid, start_t, _ms_to_utc(t[2]), t[3], t[4], t[5], t[6], t[7], t[8], t[9],
                              t[10], start_lat, start_lon, end_lat, end_lon, route_map, route_kml))
        db.close()

    data_headers = ('ID', ('Start Time', 'datetime'), ('Device Sync Time', 'datetime'), 'Distance',
                    'Duration', 'Activity Type', 'Calories', 'Heart Rate', 'Total Climb', 'UUID',
                    'Nickname', 'Latitude', 'Longitude', 'End Latitude', 'End Longitude',
                    ('Route Map', 'media'), ('Route KML', 'media'))
    return data_headers, data_list, source_path
