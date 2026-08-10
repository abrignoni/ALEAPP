# pylint: disable=W0718
__artifacts_v2__ = {
    "get_gps": {
        "name": "Strava - Activities",
        "description": "GPS activities decoded from Strava FIT files (com.strava/files/activities)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-03-24",
        "last_update_date": "2023-03-24",
        "requirements": "fitdecode",
        "category": "Strava",
        "notes": "Interactive folium map and online reverse-geocoding removed; the route is rendered "
                 "as an offline image (media) and the activity start point is emitted as KML.",
        "paths": ('*/com.strava/files*',),
        "output_types": "all",
        "artifact_icon": "activity",
    }
}

import datetime

import fitdecode

from scripts.geo_utils import render_gps_track_png, build_track_kml
from scripts.ilapfuncs import artifact_processor, logfunc, check_in_embedded_media

_SEMI_TO_DEG = 180.0 / 2 ** 31


def _to_utc(value):
    if not isinstance(value, datetime.datetime):
        return ''
    if value.tzinfo is None:
        return value.replace(tzinfo=datetime.timezone.utc)
    return value.astimezone(datetime.timezone.utc)


@artifact_processor
def get_gps(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('fit'):
            continue
        source_path = file_found
        coordinates = []
        sport = ''
        start_time = ''
        end_time = ''
        total_minutes = ''
        total_distance_km = ''
        try:
            with fitdecode.FitReader(file_found) as fit:
                for frame in fit:
                    if frame.frame_type != fitdecode.FIT_FRAME_DATAMESG:
                        continue
                    if (frame.name == 'record' and frame.has_field('position_lat')
                            and frame.has_field('position_long')):
                        lat = frame.get_value('position_lat') * _SEMI_TO_DEG
                        lon = frame.get_value('position_long') * _SEMI_TO_DEG
                        coordinates.append([round(lat, 5), round(lon, 5)])
                    elif frame.name == 'session':
                        elapsed = (frame.get_value('total_elapsed_time')
                                   if frame.has_field('total_elapsed_time') else None)
                        if elapsed is not None:
                            total_minutes = int(elapsed / 60)
                        if frame.has_field('start_time'):
                            st = frame.get_value('start_time')
                            start_time = _to_utc(st)
                            if elapsed is not None and isinstance(st, datetime.datetime):
                                end_time = _to_utc(st + datetime.timedelta(seconds=elapsed))
                        if frame.has_field('sport'):
                            sport = frame.get_value('sport')
                        if frame.has_field('total_distance'):
                            total_distance_km = round(frame.get_value('total_distance') / 1000, 2)
        except Exception as exc:
            logfunc(f'Strava: could not read {file_found}: {exc}')
            continue

        start_lat = coordinates[0][0] if coordinates else ''
        start_lon = coordinates[0][1] if coordinates else ''
        name = sport or 'activity'
        caption_bits = []
        if start_time:
            caption_bits.append(start_time.strftime('%Y-%m-%d %H:%M UTC'))
        if total_distance_km != '':
            caption_bits.append(f'{total_distance_km} km')
        if total_minutes != '':
            caption_bits.append(f'{total_minutes} min')

        route_map = ''
        png = render_gps_track_png(coordinates, title=str(sport).title() if sport else 'Activity',
                                   subtitle='  -  '.join(caption_bits))
        if png:
            route_map = check_in_embedded_media(file_found, png, f'{name}_route.png',
                                                force_type='image/png', force_extension='png') or ''
        route_kml = ''
        kml = build_track_kml(coordinates, name=f'{name} {start_time}')
        if kml:
            route_kml = check_in_embedded_media(file_found, kml, f'{name}_route.kml',
                                                force_type='application/vnd.google-earth.kml+xml',
                                                force_extension='kml') or ''
        data_list.append((sport, start_time, end_time, total_minutes, total_distance_km,
                          start_lat, start_lon, route_map, route_kml))

    data_headers = ('Activity Type', ('Start Time', 'datetime'), ('End Time', 'datetime'),
                    'Total Time (minutes)', 'Total Distance (km)', 'Latitude', 'Longitude',
                    ('Route Map', 'media'), ('Route KML', 'media'))
    return data_headers, data_list, source_path
