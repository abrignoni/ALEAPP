# Citymapper App (com.citymapper.app.release)
# Author : Funeoz
# Version : 0.0.1

# Tested with the following versions:
# 2025-12-12: Android 12.0, App: 11.43.2

# Requirements: Python 3.7 or higher, folium

__artifacts_v2__ = {
    "get_citymapperLocationHistory" : {
        "name": "Citymapper - Location History",
        "description": "Parses location history from the Citymapper App",
        "author": "Funeoz",
        "version": "0.0.1",
        "date":"2025-12-12",
        "requirements": "none",
        "category" : "Citymapper",
        "notes" : "",
        "paths" : ('*/data/data/com.citymapper.app.release/databases/citymapper.db'),
        "output_types": ['tsv', 'timeline', 'lava', 'kml']  # Exclude 'html' to use custom report     
    },
    "get_citymapperSavedTrips" : {
        "name": "Citymapper - Saved Trips",
        "description": "Parses saved trips (home/work) from the Citymapper App",
        "author": "Funeoz",
        "version": "0.0.1",
        "date":"2025-12-12",
        "requirements": "none",
        "category" : "Citymapper",
        "notes" : "",
        "paths" : ('*/data/data/com.citymapper.app.release/databases/citymapper.db'),
        "output_types": ['tsv', 'timeline', 'lava', 'kml']  # Exclude 'html' to use custom report     
    },
    "get_citymapperAppPreferences" : {
        "name": "Citymapper - App Preferences",
        "description": "Parses app preferences from the Citymapper App",
        "author": "Funeoz",
        "version": "0.0.1",
        "date":"2025-12-12",
        "requirements": "none",
        "category" : "Citymapper",
        "notes" : "",
        "paths" : ('*/data/data/com.citymapper.app.release/shared_prefs/superProperties.xml*', 
                   '*/data/data/com.citymapper.app.release/shared_prefs/preferences.xml*',
                   '*/data/data/com.citymapper.app.release/shared_prefs/Session.xml*',
                   '*/data/data/com.citymapper.app.release/shared_prefs/no_backup_preferences.xml*'
        ),
        "output_types": ['tsv', 'timeline', 'lava', 'kml']  # Exclude 'html' to use custom report
    }
}

import os
import folium
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, logfunc, kmlgen, open_sqlite_db_readonly, convert_unix_ts_to_utc

@artifact_processor
def get_citymapperLocationHistory(files_found, report_folder, _seeker, _wrap_text):

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

            location_rows = cursor.fetchall()
            for row in location_rows:
                location_data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

            db.close()
    
    if not location_data_list:
        return ('No Data',), [], source
    
    location_headers = ('ID', 'Address', 'Timestamp', 'Latitude', 'Longitude', 'Name', 'Role')
    
    kmlgen(report_folder, 'Citymapper - Location History', location_data_list, location_headers)
    
    # Generate map for location history
    try:
        # Find center point (average of all coordinates)
        valid_coords = [(row[3], row[4]) for row in location_data_list if row[3] and row[4]]
        if valid_coords:
            center_lat = sum(coord[0] for coord in valid_coords) / len(valid_coords)
            center_lon = sum(coord[1] for coord in valid_coords) / len(valid_coords)
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=12, max_zoom=19)
            
            # Sort locations by date for chronological numbering
            sorted_locations = sorted(
                [row for row in location_data_list if row[3] and row[4]],
                key=lambda x: x[2] if x[2] else ''
            )
            
            # Add numbered markers for each location
            for idx, row in enumerate(sorted_locations, 1):
                popup_text = f"<b>#{idx}: {row[5] if row[5] else 'Location'}</b><br>"
                popup_text += f"Address: {row[1] if row[1] else 'N/A'}<br>"
                popup_text += f"Date: {row[2] if row[2] else 'N/A'}<br>"
                popup_text += f"Role: {row[6] if row[6] else 'N/A'}"
                
                # Different colors based on role
                color = 'blue'
                if row[6] == 'home':
                    color = 'green'
                elif row[6] == 'work':
                    color = 'red'
                
                folium.Marker(
                    [row[3], row[4]],
                    popup=popup_text,
                    icon=folium.DivIcon(html=f'''
                        <div style="
                            background-color: {color};
                            border: 2px solid white;
                            border-radius: 50%;
                            width: 30px;
                            height: 30px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: bold;
                            color: white;
                            font-size: 12px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
                        ">{idx}</div>
                    ''')
                ).add_to(m)
            
            # Save map
            map_filename = 'Citymapper_Location_History_Map.html'
            if os.name == 'nt':
                map_path = os.path.join(report_folder, map_filename)
            else:
                map_path = report_folder + '/' + map_filename
            
            m.save(map_path)
            
            # Create custom HTML report
            report = ArtifactHtmlReport('Citymapper - Location History')
            report.start_artifact_report(report_folder, 'Citymapper - Location History')
            report.add_script()
            
            # Source Path section
            report.add_section_heading('Source Path', 'h3')
            report.write_raw_html(f'''
                <dl class="row">
                    <dt class="col-sm-3">File Path</dt>
                    <dd class="col-sm-9">{source}</dd>
                </dl>
            ''')
            
            # Summary section
            report.add_section_heading('Location History Summary', 'h3')
            report.write_raw_html(f'''
                <dl class="row">
                    <dt class="col-sm-3">Total Locations</dt>
                    <dd class="col-sm-9">{len(location_data_list)}</dd>
                    <dt class="col-sm-3">Locations with Coordinates</dt>
                    <dd class="col-sm-9">{len(valid_coords)}</dd>
                </dl>
            ''')
            
            # Location Details Table
            report.add_section_heading('Location Details', 'h3')
            table_html = '<table class="table table-striped"><thead><tr>'
            for header in location_headers:
                table_html += f'<th>{header}</th>'
            table_html += '</tr></thead><tbody>'
            
            for row in location_data_list:
                table_html += '<tr>'
                for cell in row:
                    table_html += f'<td>{cell if cell is not None else ""}</td>'
                table_html += '</tr>'
            
            table_html += '</tbody></table>'
            report.write_raw_html(table_html)
            
            # Add map section
            report.add_section_heading('Location History Map')
            report.add_map(f'<iframe src="Citymapper/{map_filename}" width="100%" height="400" class="map"></iframe>')
            
            # End report
            report.end_artifact_report()

                
    except Exception as e:
        logfunc(f"Error generating location history map: {e}")
    
    return location_headers, location_data_list, source


@artifact_processor
def get_citymapperSavedTrips(files_found, report_folder, _seeker, _wrap_text):

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
            
            trip_rows = cursor.fetchall()
            for row in trip_rows:
                saved_trip_data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[8]))

            db.close()
    
    trip_headers = ('ID', 'Commute Type', 'Timestamp', 'Home Latitude', 'Home Longitude', 'Work Latitude', 'Work Longitude', 'Region Code')
    
    # Create KML
    kmlgen(report_folder, 'Citymapper - Saved Trips', saved_trip_data_list, trip_headers)
    
    # Generate map for saved trips
    try:
        # Collect home and work coordinates
        home_work_coords = []
        for row in saved_trip_data_list:
            if row[3] and row[4]:  # home lat, lng
                home_work_coords.append((row[3], row[4], 'Home', row[0]))
            if row[5] and row[6]:  # work lat, lng
                home_work_coords.append((row[5], row[6], 'Work', row[0]))
        
        if home_work_coords:
            # Find center point
            center_lat = sum(coord[0] for coord in home_work_coords) / len(home_work_coords)
            center_lon = sum(coord[1] for coord in home_work_coords) / len(home_work_coords)
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=11, max_zoom=19)
            
            # Add markers for home/work locations
            for coord in home_work_coords:
                lat, lon, place_type, trip_id = coord
                popup_text = f"<b>{place_type}</b><br>Trip ID: {trip_id}<br>Lat: {lat}, Lon: {lon}"
                
                color = 'green' if place_type == 'Home' else 'red'
                icon = 'home' if place_type == 'Home' else 'briefcase'
                
                folium.Marker(
                    [lat, lon],
                    popup=popup_text,
                    icon=folium.Icon(color=color, icon=icon, prefix='fa')
                ).add_to(m)
            
            # Draw lines between home and work for each trip
            for row in saved_trip_data_list:
                if row[3] and row[4] and row[5] and row[6]:
                    folium.PolyLine(
                        [[row[3], row[4]], [row[5], row[6]]],
                        color='blue',
                        weight=2,
                        opacity=0.6,
                        popup=f"Trip ID: {row[0]}"
                    ).add_to(m)
            
            # Save map
            map_filename = 'Citymapper_Saved_Trips_Map.html'
            if os.name == 'nt':
                map_path = os.path.join(report_folder, map_filename)
            else:
                map_path = report_folder + '/' + map_filename
            
            m.save(map_path)
            
            # Create custom HTML report
            report = ArtifactHtmlReport('Citymapper - Saved Trips')
            report.start_artifact_report(report_folder, 'Citymapper - Saved Trips')
            report.add_script()
            
            # Source Path section
            report.add_section_heading('Source Path', 'h3')
            report.write_raw_html(f'''
                <dl class="row">
                    <dt class="col-sm-3">File Path</dt>
                    <dd class="col-sm-9">{source}</dd>
                </dl>
            ''')
            
            # Summary section
            report.add_section_heading('Saved Trips Summary', 'h3')
            report.write_raw_html(f'''
                <dl class="row">
                    <dt class="col-sm-3">Total Saved Trips</dt>
                    <dd class="col-sm-9">{len(saved_trip_data_list)}</dd>
                </dl>
            ''')
            
            # Trip Details Table
            report.add_section_heading('Trip Details', 'h3')
            table_html = '<table class="table table-striped"><thead><tr>'
            for header in trip_headers:
                table_html += f'<th>{header}</th>'
            table_html += '</tr></thead><tbody>'
            
            for row in saved_trip_data_list:
                table_html += '<tr>'
                for cell in row:
                    table_html += f'<td>{cell if cell is not None else ""}</td>'
                table_html += '</tr>'
            
            table_html += '</tbody></table>'
            report.write_raw_html(table_html)
            
            # Add map section
            report.add_section_heading('Saved Trips Map')
            report.add_map(f'<iframe src="Citymapper/{map_filename}" width="100%" height="400" class="map"></iframe>')
            
            # End report
            report.end_artifact_report()

    except Exception as e:
        logfunc(f"Error generating saved trips map: {e}")

    return trip_headers, saved_trip_data_list, source


@artifact_processor
def get_citymapperAppPreferences(files_found, report_folder, _seeker, _wrap_text):

    data_list = []
    source = ''
    
    # Dictionary to store parsed data from all files
    user_data = {}

    for file_found in files_found:
        file_found = str(file_found)
        
        if not source:
            source = file_found

        try:
            tree = ET.parse(file_found)
            root = tree.getroot()
            
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
    last_location = user_data.get('LAST_LOCATION', '')
    
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
        last_location,
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
        'Last Location (Lat,Lon)',
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
    
    # Generate and add folium map if location exists
    if last_location and len(data_list) > 0:
        try:
            # Parse coordinates (format: "latitude,longitude")
            coords = last_location.split(',')
            if len(coords) == 2:
                lat = float(coords[0])
                lon = float(coords[1])
                
                # Create folium map
                m = folium.Map(location=[lat, lon], zoom_start=13, max_zoom=19)
                
                # Add marker for last location
                folium.Marker(
                    [lat, lon],
                    popup=f'Last Location<br>Lat: {lat}, Lon: {lon}',
                    icon=folium.Icon(color='red', icon='map-pin', prefix='fa')
                ).add_to(m)
                
                # Save map to HTML file
                map_filename = 'Citymapper_Last_Location_Map.html'
                if os.name == 'nt':
                    map_path = os.path.join(report_folder, map_filename)
                else:
                    map_path = report_folder + '/' + map_filename
                    
                m.save(map_path)
                
                # Create report and add map section
                report = ArtifactHtmlReport('Citymapper - App Preferences')
                report.start_artifact_report(report_folder, 'Citymapper - App Preferences')
                report.add_script()
                
                # Source Path section
                report.add_section_heading('Source Paths', 'h3')
                for file_found in files_found:
                    report.write_raw_html(f'''
                        <dl class="row">
                            <dt class="col-sm-3">File Path</dt>
                            <dd class="col-sm-9">{file_found}</dd>
                        </dl>
                    ''')
                
                # Device Information
                report.add_section_heading('Device Information', 'h3')
                report.write_raw_html(f'''
                    <dl class="row">
                        <dt class="col-sm-3">Device ID</dt>
                        <dd class="col-sm-9">{device_id}</dd>
                        <dt class="col-sm-3">Device IP</dt>
                        <dd class="col-sm-9">{device_ip}</dd>
                    </dl>
                ''')
                
                # App Version Information
                report.add_section_heading('App Version Information', 'h3')
                report.write_raw_html(f'''
                    <dl class="row">
                        <dt class="col-sm-3">Last Seen Version</dt>
                        <dd class="col-sm-9">{last_seen_version}</dd>
                        <dt class="col-sm-3">Earliest Seen Version</dt>
                        <dd class="col-sm-9">{earliest_seen_version}</dd>
                        <dt class="col-sm-3">App Installed</dt>
                        <dd class="col-sm-9">{app_installed}</dd>
                    </dl>
                ''')
                
                # Location Information
                report.add_section_heading('Location Information', 'h3')
                report.write_raw_html(f'''
                    <dl class="row">
                        <dt class="col-sm-3">Last Location (Latitude, Longitude)</dt>
                        <dd class="col-sm-9">{last_location}</dd>
                        <dt class="col-sm-3">CityMapper Region</dt>
                        <dd class="col-sm-9">{cm_region}</dd>
                    </dl>
                ''')
                
                # Session Information
                report.add_section_heading('Session Information', 'h3')
                report.write_raw_html(f'''
                    <dl class="row">
                        <dt class="col-sm-3">Onboarding Date</dt>
                        <dd class="col-sm-9">{onboarding_date}</dd>
                        <dt class="col-sm-3">Last Used Date</dt>
                        <dd class="col-sm-9">{last_used_date}</dd>
                        <dt class="col-sm-3">Session Count</dt>
                        <dd class="col-sm-9">{session_count}</dd>
                    </dl>
                ''')
                
                # System & App Settings
                report.add_section_heading('System & App Settings', 'h3')
                report.write_raw_html(f'''
                    <dl class="row">
                        <dt class="col-sm-3">Language</dt>
                        <dd class="col-sm-9">{language}</dd>
                        <dt class="col-sm-3">Connectivity State</dt>
                        <dd class="col-sm-9">{connectivity_state}</dd>
                        <dt class="col-sm-3">OS API Level</dt>
                        <dd class="col-sm-9">{os_api_level}</dd>
                        <dt class="col-sm-3">Build Flavor</dt>
                        <dd class="col-sm-9">{build_flavor}</dd>
                    </dl>
                ''')
                
                # Add map section
                report.add_section_heading('Last Location Map')
                report.add_map(f'<iframe src="Citymapper/{map_filename}" width="100%" height="400" class="map"></iframe>')
                
                # End report
                report.end_artifact_report()
                
        except Exception as e:
            logfunc(f"Error generating map for last location: {e}")
    
    return data_headers, data_list, source