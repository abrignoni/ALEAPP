# pylint: disable=W0718
__artifacts_v2__ = {
    "get_citymapperLocationHistory" : {
        "name": "Citymapper - Location History",
        "description": "Parses location history from the Citymapper App",
        "author": "Funeoz",
        "creation_date":"2025-12-12",
        "last_update_date": "2025-12-12",
        "requirements": "none",
        "category" : "Citymapper",
        "notes" : "Interactive online folium map removed; locations are exported to KML by the framework.",
        "paths" : ('*/data/com.citymapper.app.release/databases/citymapper.db'),
        "output_types": ['html', 'tsv', 'timeline', 'lava', 'kml'],
        "artifact_icon": "map-pin",
    },
    "get_citymapperSavedTrips" : {
        "name": "Citymapper - Saved Trips",
        "description": "Parses saved trips (home/work) from the Citymapper App",
        "author": "Funeoz",
        "creation_date":"2025-12-12",
        "last_update_date": "2025-12-12",
        "requirements": "none",
        "category" : "Citymapper",
        "notes" : "Interactive online folium map removed; home/work coordinates are shown in the table.",
        "paths" : ('*/data/com.citymapper.app.release/databases/citymapper.db'),
        "output_types": ['html', 'tsv', 'timeline', 'lava'],
        "artifact_icon": "map-pin",
    },
    "get_citymapperAppPreferences" : {
        "name": "Citymapper - App Preferences",
        "description": "Parses app preferences from the Citymapper App",
        "author": "Funeoz",
        "creation_date":"2025-12-12",
        "last_update_date": "2025-12-12",
        "requirements": "none",
        "category" : "Citymapper",
        "notes" : "Interactive online folium map removed; last known location is exported to KML by the framework.",
        "paths" : ('*/data/com.citymapper.app.release/shared_prefs/superProperties.xml*',
                   '*/data/com.citymapper.app.release/shared_prefs/preferences.xml*',
                   '*/data/com.citymapper.app.release/shared_prefs/Session.xml*',
                   '*/data/com.citymapper.app.release/shared_prefs/no_backup_preferences.xml*'
        ),
        "output_types": ['html', 'tsv', 'timeline', 'lava', 'kml'],
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

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, convert_unix_ts_to_utc

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
    files_found = context.get_files_found()

    location_data_list = []
    source = ''

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('citymapper.db'):
            source = file_found
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

    location_headers = ('ID', 'Address', 'Timestamp', 'Latitude', 'Longitude', 'Name', 'Role')

    return location_headers, location_data_list, source


@artifact_processor
def get_citymapperSavedTrips(context):
    files_found = context.get_files_found()

    saved_trip_data_list = []
    source = ''

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('citymapper.db'):
            source = file_found
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

    trip_headers = ('ID', 'Commute Type', 'Timestamp', 'Home Latitude', 'Home Longitude',
                    'Work Latitude', 'Work Longitude', 'Region Code')

    return trip_headers, saved_trip_data_list, source


@artifact_processor
def get_citymapperAppPreferences(context):
    files_found = context.get_files_found()

    data_list = []
    source = ''

    # Dictionary to store parsed data from all files
    user_data = {}

    for file_found in files_found:
        file_found = str(file_found)

        if not source:
            source = file_found

        try:
            root = _parse_xml(file_found)

            for child in root:
                name = child.attrib.get('name', '')

                # Handle different XML element types
                if child.tag == 'string':
                    user_data[name] = child.text if child.text else ''
                elif child.tag == 'long':
                    user_data[name] = child.attrib.get('value', '')
                elif child.tag == 'boolean':
                    user_data[name] = child.attrib.get('value', '')
                elif child.tag == 'set':
                    # Handle set elements (typically empty or with multiple values)
                    set_values = [item.text for item in child if item.text]
                    user_data[name] = ', '.join(set_values) if set_values else 'Empty'

        except Exception as e:
            logfunc(f"Error parsing XML from {file_found}: {e}")

    # Extract and format key data fields with proper timestamp conversion
    device_id = user_data.get('deviceID', '')
    device_ip = user_data.get('deviceIp', '')
    last_seen_version = user_data.get('lastSeenVersion', '')
    earliest_seen_version = user_data.get('earliestSeenVersion', '')

    # Split the "latitude,longitude" last-known location into separate columns so the
    # framework can export it to KML (no online map / network tiles).
    last_location = user_data.get('LAST_LOCATION', '')
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

    # Convert timestamps
    onboarding_date = user_data.get('onboarding_terms_accepted_date', '')
    if onboarding_date:
        onboarding_date = convert_unix_ts_to_utc(int(onboarding_date))

    last_used_date = user_data.get('LastUsedDate', '')
    if last_used_date:
        last_used_date = convert_unix_ts_to_utc(int(last_used_date))

    session_count = user_data.get('SessionCount', '')

    # App properties
    language = user_data.get('Language', '')
    app_installed = user_data.get('App Installed', '')
    cm_region = user_data.get('CM Region', '')
    connectivity_state = user_data.get('Connectivity State', '')
    os_api_level = user_data.get('OS API Level', '')
    build_flavor = user_data.get('Build Flavor', '')

    # Add main record with all important fields
    data_list.append((
        device_id,
        device_ip,
        last_seen_version,
        earliest_seen_version,
        latitude,
        longitude,
        onboarding_date,
        last_used_date,
        session_count,
        language,
        app_installed,
        cm_region,
        connectivity_state,
        os_api_level,
        build_flavor
    ))

    data_headers = (
        'Device ID',
        'Device IP',
        'Last Seen Version',
        'Earliest Seen Version',
        'Latitude',
        'Longitude',
        ('Onboarding Date', 'datetime'),
        ('Last Used Date', 'datetime'),
        'Session Count',
        'Language',
        'App Installed',
        'CityMapper Region',
        'Connectivity State',
        'OS API Level',
        'Build Flavor'
    )

    return data_headers, data_list, source
