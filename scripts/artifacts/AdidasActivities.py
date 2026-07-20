# pylint: disable=W0718
__artifacts_v2__ = {
    "get_adidas_activities": {
        "name": "Adidas Running - Activities",
        "description": "Adidas Running (Runtastic) activities with GPS routes",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "polyline",
        "category": "Adidas",
        "notes": "Interactive folium map and online reverse-geocoding removed; route shown as an "
                 "offline image (media) + a downloadable route KML.",
        "paths": ('*/com.runtastic.android/databases/db*',),
        "output_types": "all",
        "artifact_icon": "activity",
    }
}

import datetime
import sqlite3

import polyline

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
        if 'com.runtastic.android' in file_found and not file_found.endswith(('wal', 'shm', '-journal')):
            return file_found
    return ''


@artifact_processor
def get_adidas_activities(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT sampleId, userId, distance, startTime, endTime, runtime, maxSpeed, calories,
                       temperature, note, maxPulse, avgPulse, maxElevation, minElevation, humidity,
                       encodedTrace
                FROM session
            ''')
            rows = cursor.fetchall()
        except sqlite3.Error:
            rows = []
        db.close()

        for r in rows:
            try:
                coords = polyline.decode(r[15]) if r[15] else []
            except Exception:
                coords = []
            start_lat, start_lon = coords[0] if coords else ('', '')
            end_lat, end_lon = coords[-1] if coords else ('', '')
            runtime = round(r[5] / 60000, 2) if r[5] else ''
            max_speed = round(r[6], 2) if r[6] else r[6]
            temperature = 'N/A' if r[8] == -300 else r[8]
            max_elev = 'N/A' if r[12] == -32768 else r[12]
            min_elev = 'N/A' if r[13] == 32767 else r[13]
            humidity = 'N/A' if r[14] == -1 else r[14]
            start_t = _ms_to_utc(r[3])
            title = f'Adidas activity {r[0]}'
            subtitle = '  -  '.join(x for x in [
                start_t.strftime('%Y-%m-%d %H:%M UTC') if start_t else '',
                f'{runtime} min' if runtime != '' else ''] if x)

            route_map = ''
            png = render_gps_track_png(coords, title=title, subtitle=subtitle)
            if png:
                route_map = check_in_embedded_media(source_path, png, f'{r[0]}_route.png',
                                                    force_type='image/png', force_extension='png') or ''
            route_kml = ''
            kml = build_track_kml(coords, name=title)
            if kml:
                route_kml = check_in_embedded_media(source_path, kml, f'{r[0]}_route.kml',
                                                    force_type='application/vnd.google-earth.kml+xml',
                                                    force_extension='kml') or ''
            data_list.append((r[0], r[1], r[2], start_t, _ms_to_utc(r[4]), runtime, max_speed, r[7],
                              temperature, r[9], r[10], r[11], max_elev, min_elev, humidity,
                              start_lat, start_lon, end_lat, end_lon, route_map, route_kml))

    data_headers = ('Sample ID', 'User ID', 'Distance', ('Start Time', 'datetime'),
                    ('End Time', 'datetime'), 'Run Time (min)', 'Max Speed', 'Calories', 'Temperature',
                    'Note', 'Max Pulse', 'Avg Pulse', 'Max Elevation', 'Min Elevation', 'Humidity',
                    'Latitude', 'Longitude', 'End Latitude', 'End Longitude', ('Route Map', 'media'),
                    ('Route KML', 'media'))
    return data_headers, data_list, source_path
