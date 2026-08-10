__artifacts_v2__ = {
    "what3words_saved_places": {
        "name": "what3words - Saved Places",
        "description": "Places saved in what3words, with the three word address, the label given to "
                       "it, the nearest place and the coordinates",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "what3words",
        "notes": "Read from the class_LocationRealm table of the app's Realm store "
                 "(files/default.realm) using the vendored realm_parser. Each three word address "
                 "maps to a fixed 3m square; the latitude and longitude are the square's "
                 "coordinates as the app stored them.",
        "paths": ('*/com.what3words.android/files/default.realm',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.what3words.android | 2 rows",
        },
    },
    "what3words_lists": {
        "name": "what3words - Location Lists",
        "description": "Lists that group saved what3words locations, with the list label, the number "
                       "of locations in it, who created it and when",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "what3words",
        "notes": "Read from the class_LocationsListsRealm table of the app's Realm store.",
        "paths": ('*/com.what3words.android/files/default.realm',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.what3words.android | 1 row",
        },
    },
}

from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc
from scripts.realm_parser import parse_realm_file, realm_rows


def _realm_ts(value):
    """The vendored realm_parser renders Realm date columns as 'YYYY-MM-DD HH:MM:SS UTC';
    turn that into a timezone-aware datetime so it sorts and timelines correctly."""
    if not value or not isinstance(value, str):
        return value
    try:
        return datetime.strptime(value.replace(' UTC', ''), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return value


def _is_what3words_realm(path):
    """Guard: the default.realm name is used by several apps, so confirm this Realm
    actually carries what3words classes before reporting rows."""
    tables = parse_realm_file(path).get("active", {})
    return 'class_LocationRealm' in tables or 'class_LocationsListsRealm' in tables


def _realm_path(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('default.realm') and _is_what3words_realm(file_found):
            return file_found
    return ''


@artifact_processor
def what3words_saved_places(context):
    source_path = _realm_path(context.get_files_found())
    data_list = []

    for row in realm_rows(source_path, 'class_LocationRealm'):
        data_list.append((
            _realm_ts(row.get('modificationTime')),
            row.get('threeWordAddress'),
            row.get('label'),
            row.get('nearestPlace'),
            row.get('lat'),
            row.get('lng'),
            row.get('countryCode'),
            row.get('language'),
            row.get('locationType'),
            row.get('order'),
        ))

    data_headers = (
        ('Modification Time', 'datetime'),
        'Three Word Address',
        'Label',
        'Nearest Place',
        'Latitude',
        'Longitude',
        'Country Code',
        'Language',
        'Location Type Value',
        'Order',
    )
    return data_headers, data_list, source_path


@artifact_processor
def what3words_lists(context):
    source_path = _realm_path(context.get_files_found())
    data_list = []

    for row in realm_rows(source_path, 'class_LocationsListsRealm'):
        created_when = row.get('createdWhen')
        updated_at = row.get('updatedAt')
        data_list.append((
            convert_unix_ts_to_utc(created_when) if created_when else '',
            convert_unix_ts_to_utc(updated_at) if updated_at else '',
            row.get('label'),
            row.get('count'),
            row.get('createdBy'),
            row.get('color'),
            'Yes' if row.get('isSharedList') else 'No',
            row.get('shareType'),
            row.get('sharedListId'),
            row.get('id'),
        ))

    data_headers = (
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        'Label',
        'Location Count',
        'Created By',
        'Colour',
        'Shared List',
        'Share Type',
        'Shared List ID',
        'List ID',
    )
    return data_headers, data_list, source_path
