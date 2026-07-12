# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_nike_polyline": {
        "name": "Nike - Activity Route",
        "description": "GPS activity routes decoded from the Nike Run app (activity_polyline)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "polyline",
        "category": "Nike-Run",
        "notes": "Interactive folium map and online reverse-geocoding removed; route shown as an "
                 "offline image (media) + a downloadable route KML.",
        "paths": ('*/com.nike.plusgps/databases/com.nike.nrc.room*',),
        "output_types": "all",
        "artifact_icon": "activity",
        "sample_data": {
            "samsunga53_a14": "Android 14 | com.nike.plusgps vc 1717605525 | 0 rows",
            "userb2_a13": "Android 13 | com.nike.plusgps vc 1717303105 | 0 rows",
        },
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
        if 'com.nike.nrc.room' in file_found and not file_found.endswith(('wal', 'shm', '-journal')):
            return file_found
    return ''


@artifact_processor
def get_nike_polyline(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT activity.as2_sa_id, activity.as2_sa_start_utc_ms, activity.as2_sa_end_utc_ms,
                       activity.as2_sa_active_duration_ms, ap.as2_p_encoded_polyline
                FROM activity
                LEFT JOIN activity_polyline ap ON activity.as2_sa_id = ap.as2_p_activity_id
                WHERE ap.as2_p_encoded_polyline IS NOT NULL
            ''')
            rows = cursor.fetchall()
        except sqlite3.Error:
            rows = []
        db.close()

        for r in rows:
            try:
                coords = polyline.decode(r[4]) if r[4] else []
            except Exception:
                coords = []
            start_lat, start_lon = coords[0] if coords else ('', '')
            end_lat, end_lon = coords[-1] if coords else ('', '')
            duration = round(r[3] / 60000, 2) if r[3] else ''
            start_t = _ms_to_utc(r[1])
            title = f'Nike activity {r[0]}'
            subtitle = '  -  '.join(x for x in [
                start_t.strftime('%Y-%m-%d %H:%M UTC') if start_t else '',
                f'{duration} min' if duration != '' else ''] if x)

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
            data_list.append((r[0], start_t, _ms_to_utc(r[2]), duration, start_lat, start_lon,
                              end_lat, end_lon, route_map, route_kml))

    data_headers = ('Activity ID', ('Start Time UTC', 'datetime'), ('End Time UTC', 'datetime'),
                    'Duration (min)', 'Latitude', 'Longitude', 'End Latitude', 'End Longitude',
                    ('Route Map', 'media'), ('Route KML', 'media'))
    return data_headers, data_list, source_path
