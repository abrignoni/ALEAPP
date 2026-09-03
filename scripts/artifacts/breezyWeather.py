__artifacts_v2__ = {
    "breezyweather_locations": {
        "name": "Breezy Weather - Locations",
        "description": "Parses saved weather locations from the Breezy Weather Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Breezy Weather",
        "notes": "One row per entry in the locations table of databases/breezyweather.db, joined to "
                 "the weathers table for the times the app last fetched for that place. Breezy "
                 "Weather is an open source weather app, and a row here is a place someone added "
                 "to it. Each row carries the Latitude and Longitude, the Timezone the app "
                 "resolved for the place, and the geographic hierarchy the source returned: City, "
                 "District, Country and Country Code, plus the Admin 1 and Admin 2 divisions. "
                 "Custom Name is a name a person typed to rename the entry and is empty unless "
                 "they did. "
                 "Current Position is the distinction that matters: Yes marks the entry the app "
                 "maintains for the device's own detected location, while No marks a place "
                 "someone searched for and chose to keep. A searched place is a deliberate act "
                 "and is not evidence the device was ever there; the tested device held one such "
                 "entry, Reykjavik, Iceland, added by search while the device's own position was "
                 "set elsewhere. "
                 "Last Refresh and Main Update are Unix milliseconds reported as UTC and come "
                 "from the weathers row for that location, so they date the last time the app "
                 "fetched for it rather than anything the person did. Weather Text and Weather "
                 "Code are the conditions recorded at that fetch. List Order is the position the "
                 "place occupies in the app's own list. Weather Source names the provider the "
                 "data came from. KML output is produced from the coordinates. "
                 "The dailys, hourlys and minutelys tables hold the forecast payload the app "
                 "downloaded (16, 408 and 8 rows respectively on the tested device for a single "
                 "location); that is provider data rather than device activity, it would bury the "
                 "rows above, and it is not parsed. The normals and location_parameters tables "
                 "were present and empty.",
        "paths": ('*/org.breezyweather/databases/breezyweather.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
    },
    "breezyweather_alerts": {
        "name": "Breezy Weather - Weather Alerts",
        "description": "Parses stored weather alerts from the Breezy Weather Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Breezy Weather",
        "notes": "One row per entry in the alerts table of databases/breezyweather.db, joined to "
                 "the location the alert was issued for. An alert is a warning the weather "
                 "provider published for that place and the app stored, with a Headline, a "
                 "Description, an Instruction, a Severity and the Start and End times of the "
                 "period it covers, reported as UTC from Unix milliseconds. Source names the "
                 "provider that issued it. "
                 "An alert is provider content rather than something a person wrote, so a row "
                 "records what the device received for a place it was tracking, not an action "
                 "anyone took. It is reported because the time span and the place together can "
                 "corroborate where a device's interest lay on a given date. "
                 "The alerts table was present and empty on the tested device, where the one "
                 "saved location had no active warnings, so this is a checked absence there and "
                 "the columns are described from the schema.",
        "paths": ('*/org.breezyweather/databases/breezyweather.db*',),
        "output_types": "standard",
        "artifact_icon": "alert-triangle",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/breezyweather.db'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _yesno(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0'):
        return 'No'
    return ''


@artifact_processor
def breezyweather_locations(context):
    query = '''SELECT l.latitude, l.longitude, l.city, l.district, l.country, l.country_code,
                      l.admin1, l.admin2, l.timezone, l.custom_name, l.current_position,
                      l.list_order, l.weather_source, w.refresh_time, w.main_update_time,
                      w.weather_text, w.weather_code, l.formatted_id
               FROM locations l
               LEFT JOIN weathers w ON w.location_formatted_id = l.formatted_id
               ORDER BY l.list_order'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[13]), _ms(r[14]), r[2] or '', r[3] or '', r[4] or '', r[5] or '',
                r[6] or '', r[7] or '', r[0], r[1], r[8] or '', r[9] or '',
                _yesno(r[10]), r[11], r[12] or '', r[15] or '', r[16] or '', r[17] or '',
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Last Refresh', 'datetime'), ('Main Update', 'datetime'), 'City', 'District',
        'Country', 'Country Code', 'Admin 1', 'Admin 2', 'Latitude', 'Longitude',
        'Timezone', 'Custom Name', 'Current Position', 'List Order', 'Weather Source',
        'Weather Text', 'Weather Code', 'Location ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def breezyweather_alerts(context):
    query = '''SELECT a.start_date, a.end_date, a.headline, a.description, a.instruction,
                      a.severity, a.source, l.city, l.country, a.alert_id,
                      a.location_formatted_id
               FROM alerts a
               LEFT JOIN locations l ON l.formatted_id = a.location_formatted_id
               ORDER BY a.start_date DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), _ms(r[1]), r[2] or '', r[3] or '', r[4] or '', r[5],
                r[6] or '', r[7] or '', r[8] or '', r[9] or '', r[10] or '',
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Start', 'datetime'), ('End', 'datetime'), 'Headline', 'Description',
        'Instruction', 'Severity (as stored)', 'Source', 'City', 'Country',
        'Alert ID', 'Location ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
