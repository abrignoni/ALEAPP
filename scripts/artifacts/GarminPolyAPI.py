# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_poly_api": {
        "name": "Garmin - API Activities",
        "description": "GPS coordinates from the Garmin Connect API activity_details JSON",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "none",
        "category": "Garmin",
        "notes": "Requires data extracted from the Garmin Connect API. Interactive folium map and "
                 "online reverse-geocoding removed; route shown as an offline image (media) + a "
                 "downloadable route KML.",
        "paths": ('*/garmin.api/activity_details*',),
        "output_types": "all",
        "artifact_icon": "activity",
    }
}

import datetime
import json

from scripts.geo_utils import render_gps_track_png, build_track_kml
from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, logfunc


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_poly_api(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        try:
            with open(file_found, 'r', encoding='utf-8') as handle:
                data = json.load(handle)
        except (ValueError, OSError, UnicodeDecodeError) as exc:
            logfunc(f'Garmin API: could not read {file_found}: {exc}')
            continue
        if not isinstance(data, dict):
            continue

        activity_id = data.get('activityId')
        poly = (data.get('geoPolylineDTO') or {}).get('polyline') or []
        coords = [(p['lat'], p['lon']) for p in poly
                  if isinstance(p, dict) and 'lat' in p and 'lon' in p]
        if not coords:
            continue
        start_t = _ms_to_utc(poly[0].get('time')) if poly else ''
        end_t = _ms_to_utc(poly[-1].get('time')) if poly else ''
        start_lat, start_lon = coords[0]
        end_lat, end_lon = coords[-1]
        subtitle = start_t.strftime('%Y-%m-%d %H:%M UTC') if start_t else ''
        title = f'Garmin activity {activity_id}'

        route_map = ''
        png = render_gps_track_png(coords, title=title, subtitle=subtitle)
        if png:
            route_map = check_in_embedded_media(file_found, png, f'{activity_id}_route.png',
                                                force_type='image/png', force_extension='png') or ''
        route_kml = ''
        kml = build_track_kml(coords, name=title)
        if kml:
            route_kml = check_in_embedded_media(file_found, kml, f'{activity_id}_route.kml',
                                                force_type='application/vnd.google-earth.kml+xml',
                                                force_extension='kml') or ''
        data_list.append((activity_id, start_t, end_t, start_lat, start_lon, end_lat, end_lon,
                          route_map, route_kml))

    data_headers = ('Activity ID', ('Start Time', 'datetime'), ('End Time', 'datetime'), 'Latitude',
                    'Longitude', 'End Latitude', 'End Longitude', ('Route Map', 'media'),
                    ('Route KML', 'media'))
    return data_headers, data_list, source_path
