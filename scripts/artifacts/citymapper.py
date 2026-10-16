# pylint: disable=W0718
__artifacts_v2__ = {
    "get_citymapperLocationHistory" : {
        "name": "Citymapper - Location History",
        "description": "Parses the locationhistoryentry table of the Citymapper app database (address, date, coordinates, name and role, as stored); what action adds an entry is not established",
        "author": "Funeoz, @AlexisBrignoni, Codex",
        "creation_date":"2025-12-12",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category" : "Citymapper",
        "notes" : "Interactive online folium map removed; locations are exported to KML by the framework. "
                  "The Date column holds the table's date value as stored, with no conversion: its "
                  "unit and epoch are not established, no source for them was found and no "
                  "registered test image holds this database. Where an extraction carries the same "
                  "database under more than one storage path (data/data, data/user/N, data_mirror), "
                  "one copy per Android user is read.",
        "paths" : ('*/data/com.citymapper.app.release/databases/citymapper.db*'),
        "output_types": ['html', 'tsv', 'lava', 'kml'],
        "artifact_icon": "map-pin",
    },
    "get_citymapperSavedTrips" : {
        "name": "Citymapper - Saved Trips",
        "description": "Parses the savedtripentry table of the Citymapper app database (commute type, created value, home and work coordinates and region code, as stored)",
        "author": "Funeoz, @AlexisBrignoni, Codex",
        "creation_date":"2025-12-12",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category" : "Citymapper",
        "notes" : "Interactive online folium map removed; home/work coordinates are shown in the table. "
                  "The Created column holds the table's created value as stored, with no conversion: "
                  "its unit and epoch are not established, no source for them was found and no "
                  "registered test image holds this database. Where an extraction carries the same "
                  "database under more than one storage path (data/data, data/user/N, data_mirror), "
                  "one copy per Android user is read.",
        "paths" : ('*/data/com.citymapper.app.release/databases/citymapper.db*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "map-pin",
    },
    "get_citymapperAppPreferences" : {
        "name": "Citymapper - App Preferences",
        "description": "Parses app preferences from the Citymapper App",
        "author": "Funeoz, @AlexisBrignoni, Codex",
        "creation_date":"2025-12-12",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category" : "Citymapper",
        "notes" : "Interactive online folium map removed. The LAST_LOCATION value is split into "
                  "Latitude and Longitude and exported to KML; what event sets it is not "
                  "established. One row is built per shared_prefs folder from the preference files "
                  "in it whose names end in .xml; where an extraction carries the same folder "
                  "under more than one storage path (data/data, data/user/N, data_mirror), one "
                  "copy per Android user is read. A folder in which none of the reported keys "
                  "was read gives no row. If two files of one folder hold the same key, the "
                  "value from the file read first is kept and the run log names the key and "
                  "the file whose value was not used. The onboarding_terms_accepted_date and "
                  "LastUsedDate columns hold those keys' values as stored, with no conversion: "
                  "their unit and epoch are not established, no source for them was found and "
                  "no registered test image holds these files.",
        "paths" : ('*/data/com.citymapper.app.release/shared_prefs/superProperties.xml*',
                   '*/data/com.citymapper.app.release/shared_prefs/preferences.xml*',
                   '*/data/com.citymapper.app.release/shared_prefs/Session.xml*',
                   '*/data/com.citymapper.app.release/shared_prefs/no_backup_preferences.xml*'
        ),
        "output_types": ['html', 'tsv', 'lava', 'kml'],
        "artifact_icon": "map-pin",
    }
}

# Citymapper App (com.citymapper.app.release)
# Author : Funeoz
# Version : 0.0.1

# Tested with the following versions:
# 2025-12-12: Android 12.0, App: 11.43.2

# Requirements: Python 3.7 or higher
import re
import xml.etree.ElementTree as ET

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_xml(file_found):
    """Parse XML, recovering from invalid tokens / unescaped ampersands; empty element if unparseable."""
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


@artifact_processor
def get_citymapperLocationHistory(context):
    # unique_files collapses the data/data, data/user/N and data_mirror views of one
    # database, so its rows are reported once per Android user.
    files_found = unique_files(context)

    location_data_list = []
    sources = []

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('citymapper.db'):
            sources.append(file_found)
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            # Fetch location history entries
            cursor.execute('''
            SELECT
                id,
                address,
                date,
                lat,
                lng,
                name,
                role
            FROM locationhistoryentry
            ''')

            for row in cursor.fetchall():
                location_data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

            db.close()

    # 'Date' is the stored column's own name: the value is reported as stored, and its
    # unit and epoch are not established.
    location_headers = ('ID', 'Address', 'Date', 'Latitude', 'Longitude', 'Name', 'Role')

    return location_headers, location_data_list, '\n'.join(sources)


@artifact_processor
def get_citymapperSavedTrips(context):
    # unique_files collapses the data/data, data/user/N and data_mirror views of one
    # database, so its rows are reported once per Android user.
    files_found = unique_files(context)

    saved_trip_data_list = []
    sources = []

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('citymapper.db'):
            sources.append(file_found)
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            # Fetch saved trip entries
            cursor.execute('''
            SELECT
                id,
                commuteType,
                created,
                homeLat,
                homeLng,
                workLat,
                workLng,
                tripData,
                regionCode
            FROM savedtripentry
            ''')

            for row in cursor.fetchall():
                saved_trip_data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[8]))

            db.close()

    # 'Created' is the stored column's own name: the value is reported as stored, and
    # its unit and epoch are not established.
    trip_headers = ('ID', 'Commute Type', 'Created', 'Home Latitude', 'Home Longitude',
                    'Work Latitude', 'Work Longitude', 'Region Code')

    return trip_headers, saved_trip_data_list, '\n'.join(sources)


# Keys of the preference files that the App Preferences row reports.
_PREFERENCE_KEYS = (
    'deviceID', 'deviceIp', 'lastSeenVersion', 'earliestSeenVersion', 'LAST_LOCATION',
    'onboarding_terms_accepted_date', 'LastUsedDate', 'SessionCount', 'Language',
    'App Installed', 'CM Region', 'Connectivity State', 'OS API Level', 'Build Flavor',
)


@artifact_processor
def get_citymapperAppPreferences(context):
    # unique_files collapses the data/data, data/user/N and data_mirror views of one
    # preference file, so each is read once per Android user.
    files_found = unique_files(context)

    data_list = []
    sources = []

    # One dictionary of parsed values per shared_prefs folder, so two Android users'
    # (or two unrelated folders') values are never merged into one row.
    folders = {}

    for file_found in files_found:
        file_found = str(file_found)

        # The patterns end in a wildcard; only the preference files themselves are read.
        if not file_found.endswith('.xml'):
            continue

        relative_path = str(context.get_relative_path(file_found)).replace('\\', '/')
        folder = relative_path.rsplit('/', 1)[0] if '/' in relative_path else ''
        user_data = folders.setdefault(folder, {})

        try:
            root = _parse_xml(file_found)

            for child in root:
                name = child.attrib.get('name', '')

                # Handle different XML element types
                if child.tag == 'string':
                    value = child.text if child.text else ''
                elif child.tag in ('long', 'boolean'):
                    value = child.attrib.get('value', '')
                elif child.tag == 'set':
                    # Handle set elements (typically empty or with multiple values)
                    set_values = [item.text for item in child if item.text]
                    value = ', '.join(set_values) if set_values else 'Empty'
                else:
                    continue

                if name in user_data:
                    # The value read first is kept; say so rather than replace it silently.
                    if name in _PREFERENCE_KEYS and user_data[name][0] != value:
                        logfunc(f'Citymapper preference key {name} is also in {relative_path} '
                                'with a different value; the value read first is reported')
                    continue
                user_data[name] = (value, file_found)

        except Exception as e:
            logfunc(f"Error parsing XML from {file_found}: {e}")

    for user_data in folders.values():
        values = {key: user_data[key][0] for key in _PREFERENCE_KEYS if key in user_data}
        if not values:
            continue
        for key in _PREFERENCE_KEYS:
            if key in user_data and user_data[key][1] not in sources:
                sources.append(user_data[key][1])

        # Split the "latitude,longitude" LAST_LOCATION value into separate columns so the
        # framework can export it to KML (no online map / network tiles).
        last_location = values.get('LAST_LOCATION', '')
        latitude = ''
        longitude = ''
        if last_location:
            parts = last_location.split(',')
            if len(parts) == 2:
                try:
                    latitude = float(parts[0])
                    longitude = float(parts[1])
                except ValueError:
                    latitude = ''
                    longitude = ''

        data_list.append((
            values.get('deviceID', ''),
            values.get('deviceIp', ''),
            values.get('lastSeenVersion', ''),
            values.get('earliestSeenVersion', ''),
            latitude,
            longitude,
            # Reported as stored: the unit and epoch of these two values are not established.
            values.get('onboarding_terms_accepted_date', ''),
            values.get('LastUsedDate', ''),
            values.get('SessionCount', ''),
            values.get('Language', ''),
            values.get('App Installed', ''),
            values.get('CM Region', ''),
            values.get('Connectivity State', ''),
            values.get('OS API Level', ''),
            values.get('Build Flavor', '')
        ))

    data_headers = (
        'Device ID',
        'Device IP',
        'Last Seen Version',
        'Earliest Seen Version',
        'Latitude',
        'Longitude',
        'onboarding_terms_accepted_date',
        'LastUsedDate',
        'Session Count',
        'Language',
        'App Installed',
        'CityMapper Region',
        'Connectivity State',
        'OS API Level',
        'Build Flavor'
    )

    return data_headers, data_list, '\n'.join(sources)
