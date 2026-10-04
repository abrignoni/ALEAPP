__artifacts_v2__ = {
    "osmand_search_history": {
        "name": "OsmAnd - Search History",
        "description": "Parses the search and navigation history recorded by the OsmAnd Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "OsmAnd",
        "notes": "One row per entry in the history_recents table of databases/search_history. OsmAnd is an "
                 "offline maps and navigation app, and this table records the entries the app kept "
                 "in its history. Place entries carry a Latitude and Longitude the app held, which "
                 "are not positions the device was measured at. The app also stores POI type and "
                 "POI filter entries with 0 and 0 as coordinates (SearchHistoryHelper.java lines "
                 "103 to 108 at the commit cited below), so a 0, 0 row is not a location. Time is "
                 "Unix milliseconds, is set again each time the app adds an entry that already "
                 "exists (SearchHistoryHelper.java addNewItemToHistory at the commit cited below), "
                 "and "
                 "was UTC on the tested device (18:20 UTC matched the device's 2:20 PM local clock), so "
                 "it is reported as UTC. The stored name is serialised by the app as type#name, as "
                 "type.subtype#name where a subtype is present, and with a further #iconName "
                 "appended where an icon name is set (serializeToString in PointDescription.java "
                 "at osmandapp/OsmAnd b0dadd38e37023cd58a62ff031f9ac3ff1942ae9). It is split here "
                 "at the first # into a Point Type column and a Name column, with the type "
                 "reported as stored, so an icon name stays in the Name column. Types the app "
                 "defines include favorite, poi, address, marker, destination, "
                 "gpx, wpt, route, location, my_location and world_region; the tested row was a "
                 "favorite. Source is the HistorySource value as stored, either SEARCH or NAVIGATION "
                 "(HistorySource.java in the same tree). The freq_intervals and freq_values "
                 "columns are not reported. This "
                 "artifact covers the search history only; the app's favourites are kept as GPX files "
                 "under its files/favorites folder and are not parsed here. The database uses a rollback "
                 "journal rather than WAL, and the -journal sidecar is in the paths.",
        "paths": ('*/net.osmand*/databases/search_history*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "emu_a15_oss_v2": "Android 15 | net.osmand.plus vc 531003 | 1 rows",
        },
    },
    "osmand_app_events": {
        "name": "OsmAnd - App Events",
        "description": "Parses the in-app event log recorded by the OsmAnd Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "OsmAnd",
        "notes": "One row per entry in the app_events table of databases/analytics. Each row is an "
                 "event name and a time as stored. What causes the app to write a row was not "
                 "sourced here. Date is Unix milliseconds and is reported as UTC. Event is the "
                 "app's own event "
                 "name as stored; the values seen on the tested device were search_open and "
                 "open_context_menu, and the set is not enumerated in this artifact, so any other value "
                 "is carried through unchanged. Event Type is the accompanying integer as stored, which "
                 "was 1 on every tested row. The table does not record what was searched for or which "
                 "place a menu was opened on, so it carries event names and times and no content; "
                 "the Search History artifact covers the places. The database uses a "
                 "rollback journal rather than WAL, and the -journal sidecar is in the paths.",
        "paths": ('*/net.osmand*/databases/analytics*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "emu_a15_oss_v2": "Android 15 | net.osmand.plus vc 531003 | 4 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

HISTORY_SUFFIX = 'databases/search_history'
ANALYTICS_SUFFIX = 'databases/analytics'


def _db_files(context, suffix):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(suffix)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _split_name(serialized):
    # serializeToString in PointDescription.java writes "<type>[.<subtype>]#<name>".
    if not serialized:
        return '', ''
    if '#' in serialized:
        point_type, _, name = serialized.partition('#')
        return point_type, name
    return '', serialized


@artifact_processor
def osmand_search_history(context):
    query = '''SELECT time, name, latitude, longitude, source
               FROM history_recents ORDER BY time DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context, HISTORY_SUFFIX):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            point_type, name = _split_name(r[1])
            data_list.append((
                _ms(r[0]), name, point_type, r[2], r[3], r[4] or '',
                context.get_relative_path(db_path),
            ))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Time', 'datetime'), 'Name', 'Point Type', 'Latitude', 'Longitude',
        'Source', 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def osmand_app_events(context):
    query = 'SELECT date, event, event_type FROM app_events ORDER BY date DESC'
    data_list = []
    sources = []
    for db_path in _db_files(context, ANALYTICS_SUFFIX):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', r[2],
                              context.get_relative_path(db_path)))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (('Date', 'datetime'), 'Event', 'Event Type', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
