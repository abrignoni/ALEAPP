__artifacts_v2__ = {
    "breezyweather_locations": {
        "name": "Breezy Weather - Locations",
        "description": "Parses saved weather locations from the Breezy Weather Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Breezy Weather",
        "sample_data": {
            "emu_a15_oss_v7": "Breezy Weather 6.2.2 | 1 rows",
        },
        "notes": "One row per entry in the locations table of databases/breezyweather.db, joined to "
                 "the weathers table for the times the app last fetched for that place. Breezy "
                 "Weather is an open source weather app, and a row here is an entry in its "
                 "locations table. Each row carries the Latitude and Longitude, the Timezone the "
                 "app resolved for the place, and the geographic hierarchy the source returned: "
                 "City, District, Country and Country Code, plus the Admin 1 and Admin 2 "
                 "divisions. Custom Name is reported as stored and was empty on the tested "
                 "device. Current Position is the app's flag as stored. On the tested device the "
                 "one entry with Current Position No was Reykjavik, Iceland, added by search "
                 "while the device's own position was set elsewhere, so a No entry is not "
                 "evidence the device was ever at that place; no source for how the app sets the "
                 "flag is cited here. Last Refresh and Main Update are Unix milliseconds "
                 "reported as UTC and come from the weathers row for that location; they are not "
                 "times of anything a person did. Weather Text and Weather Code are the "
                 "conditions recorded at that fetch. List Order is the position the place "
                 "occupies in the app's own list. Weather Source names the provider the data "
                 "came from. KML output is produced from the coordinates. The dailys, hourlys "
                 "and minutelys tables held 16, 408 and 8 rows respectively on the tested device "
                 "for a single location; they hold forecast values rather than device activity "
                 "and are not parsed. The normals and location_parameters tables "
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
        "sample_data": {
            "emu_a15_oss_v7": "Breezy Weather 6.2.2 | 0 rows, checked: the alerts table is present and empty",
        },
        "notes": "One row per entry in the alerts table of databases/breezyweather.db, joined to "
                 "the location the alert was issued for. A row carries a Headline, a "
                 "Description, an Instruction, a Severity, Start and End times reported as UTC "
                 "from Unix milliseconds, and a Source. These are described from the schema, "
                 "since the table held no rows on the tested device, and a row is not an action "
                 "anyone took. "
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
