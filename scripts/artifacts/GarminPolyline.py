# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_garmin_polyline": {
        "name": "Garmin - Polyline Activities",
        "description": "GPS activities decoded from the Garmin Connect cache (activity_polyline)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "polyline",
        "category": "Garmin",
        "notes": "Interactive folium map and online reverse-geocoding removed; route shown as an "
                 "offline image (media) + a downloadable route KML; start point exported via KML.",
        "paths": ('*/com.garmin.android.apps.connectmobile/databases/cache-database*',),
        "output_types": "all",
        "artifact_icon": "activity",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 0 rows",
        },
    }
}

import datetime
import sqlite3

import polyline

from scripts.geo_utils import render_gps_track_png, build_track_kml
from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly, check_in_embedded_media)


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
        if 'cache-database' in file_found and not file_found.endswith(('wal', 'shm', '-journal')):
            return file_found
    return ''


@artifact_processor
def get_garmin_polyline(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found)
    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT activity_details.activityId, lastUpdated, activityName, startTimeGMT,
                       activityTypeKey, round(distance, 0), round(duration / 60, 0), steps,
                       encodedSamples
                FROM activity_details
                LEFT JOIN activity_polyline ap ON activity_details.activityId = ap.activityId
                WHERE activity_details.activityId = ap.activityId
            ''')
            rows = cursor.fetchall()
        except sqlite3.Error:
            rows = []
        db.close()

        for r in rows:
            try:
                coords = polyline.decode(r[8]) if r[8] else []
            except Exception:
                coords = []
            start_lat, start_lon = coords[0] if coords else ('', '')
            end_lat, end_lon = coords[-1] if coords else ('', '')
            title = r[2] or r[4] or 'Activity'
            subtitle = '  -  '.join(x for x in [r[3], f'{r[6]} min' if r[6] not in (None, '') else '']
                                    if x)

            route_map = ''
            png = render_gps_track_png(coords, title=str(title), subtitle=subtitle)
            if png:
                route_map = check_in_embedded_media(source_path, png, f'{r[0]}_route.png',
                                                    force_type='image/png', force_extension='png') or ''
            route_kml = ''
            kml = build_track_kml(coords, name=f'{title} {r[0]}')
            if kml:
                route_kml = check_in_embedded_media(source_path, kml, f'{r[0]}_route.kml',
                                                    force_type='application/vnd.google-earth.kml+xml',
                                                    force_extension='kml') or ''
            data_list.append((r[0], r[3], _ms_to_utc(r[1]), r[2], r[4], r[5], r[6], r[7],
                              start_lat, start_lon, end_lat, end_lon, route_map, route_kml))

    data_headers = ('Activity ID', 'Start Time GMT', ('Last Updated', 'datetime'), 'Activity Name',
                    'Activity Type', 'Distance', 'Duration (min)', 'Steps', 'Latitude', 'Longitude',
                    'End Latitude', 'End Longitude', ('Route Map', 'media'), ('Route KML', 'media'))
    return data_headers, data_list, source_path
