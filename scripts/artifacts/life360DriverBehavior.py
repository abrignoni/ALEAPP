__artifacts_v2__ = {
    "Life360DriverBehavior": {
        "name": "Life360 Driver Behavior Trip Events and Waypoints",
        "description": "Parses Events and Waypoints from Life360 DriverBehavior/trips JSON files",
        "author": "Heather Charpentier",
        "category": "Life360DriverBehavior",
        "notes": "Processes event data and waypoints from trip JSON files",
        "paths": ('*/trips/*.json',),  
        "function": "get_TripEvents"
    }
}

import json
import os
from datetime import datetime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import tsv

def get_TripEvents(files_found, report_folder, seeker, wrap_text):
    data_list_events = []  
    data_list_waypoints = []  
    trips_dict = {}  

    
    target_directory = 'data/com.life360.android.safetymapd/files/DriverBehavior/trips'

    
    for file_found in files_found:
        file_found = str(file_found)

        #Normalize the file path by removing the \\?\ prefix, if present
        if file_found.startswith('\\\\?\\'):
            file_found = file_found[4:]

        #Ensure that we are processing files from the correct directory
        if file_found.endswith('.json') and target_directory in file_found.replace('\\', '/'):
            with open(file_found, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue

            if 'events' not in data:
                continue

            for event in data.get('events', []):
                timestamp = datetime.fromtimestamp(event.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')
                event_type = event.get('eventType', '')
                lat = event.get('location', {}).get('lat', '')
                lon = event.get('location', {}).get('lon', '')
                speed = event.get('speed', '')  #Speed in meters per second
                top_speed = event.get('topSpeed', '')
                avg_speed = event.get('averageSpeed', '')
                distance = event.get('distance', '')
                trip_id = event.get('tripId', '')  

                #Convert speeds from meters per second to miles per hour
                speed_mph = ''
                if speed != '':
                    speed_mph = round(float(speed) * 2.23694, 2)  #Converts speed and rounds

                top_speed_mph = ''
                if top_speed != '':
                    top_speed_mph = round(float(top_speed) * 2.23694, 2)  

                avg_speed_mph = ''
                if avg_speed != '':
                    avg_speed_mph = round(float(avg_speed) * 2.23694, 2)  

                
                data_list_events.append((timestamp, event_type, lat, lon, speed, speed_mph, top_speed, top_speed_mph, avg_speed, avg_speed_mph, distance, trip_id))

                
                if trip_id not in trips_dict:
                    trips_dict[trip_id] = []

                #Combine trips and waypoints in the tsv
                trips_dict[trip_id].append({
                    'timestamp': timestamp,
                    'type': 'event',
                    'event_type': event_type,
                    'lat': lat,
                    'lon': lon,
                    'speed': speed,
                    'speed_mph': speed_mph,
                    'top_speed': top_speed,
                    'top_speed_mph': top_speed_mph,
                    'avg_speed': avg_speed,
                    'avg_speed_mph': avg_speed_mph,
                    'distance': distance,
                    'accuracy': '',  
                    'trip_id': trip_id
                })

                
                waypoints = event.get('waypoints', [])
                for waypoint in waypoints:
                    wp_lat = waypoint.get('lat', '')
                    wp_lon = waypoint.get('lon', '')
                    wp_accuracy = waypoint.get('accuracy', '')

                    #Add waypoint data to the combined data list for HTML report (Waypoints)
                    data_list_waypoints.append((wp_lat, wp_lon, wp_accuracy, trip_id))

                    #Add waypoint data linked to the trip for TSV
                    trips_dict[trip_id].append({
                        'type': 'waypoint',
                        'event_type': 'Waypoint',
                        'timestamp': '',
                        'lat': wp_lat,  
                        'lon': wp_lon,  
                        'speed': '',
                        'speed_mph': '',
                        'top_speed': '',
                        'top_speed_mph': '',
                        'avg_speed': '',
                        'avg_speed_mph': '',
                        'distance': '',  
                        'accuracy': wp_accuracy,  
                        'trip_id': trip_id
                    })
    
   
    if data_list_events:
        description = 'Life360 Trip Event Report'
        report = ArtifactHtmlReport('Trip Events')
        report.start_artifact_report(report_folder, 'Trip Events', description)
        report.add_script()
        event_headers = ('Timestamp', 'Event Type', 'Latitude', 'Longitude', 'Speed (m/s)', 'Speed (mph)', 'Top Speed (m/s)', 'Top Speed (mph)', 'Average Speed (m/s)', 'Average Speed (mph)', 'Distance (m)', 'Trip ID')
        report.write_artifact_data_table(event_headers, data_list_events, file_found, html_escape=False)
        report.end_artifact_report()

    
    if data_list_waypoints:
        description = 'Life360 Waypoints'
        report = ArtifactHtmlReport('Trip Waypoints')
        report.start_artifact_report(report_folder, 'Trip Waypoints', description)
        report.add_script()
        waypoint_headers = ('Latitude', 'Longitude', 'Accuracy (m)', 'Trip ID')
        report.write_artifact_data_table(waypoint_headers, data_list_waypoints, file_found, html_escape=False)
        report.end_artifact_report()

    
    for trip_id, trip_data in trips_dict.items():
        if trip_data:
            combined_data = []
            for entry in trip_data:
                combined_data.append((
                    entry['timestamp'],
                    entry['event_type'],
                    entry['lat'],  
                    entry['lon'],  
                    entry['speed'],
                    entry['speed_mph'],
                    entry['top_speed'],
                    entry['top_speed_mph'],
                    entry['avg_speed'],
                    entry['avg_speed_mph'],
                    entry['distance'],  
                    entry['accuracy'],  
                    entry['trip_id']
                ))

            #Headers for both events and waypoints
            combined_headers = ('Timestamp', 'Event Type', 'Latitude', 'Longitude', 'Speed (m/s)', 'Speed (mph)', 'Top Speed (m/s)', 'Top Speed (mph)', 'Average Speed (m/s)', 'Average Speed (mph)', 'Distance (m)', 'Accuracy (m)', 'Trip ID')
            tsvname = f'Trip_{trip_id}_Combined'
            tsv(report_folder, combined_headers, combined_data, tsvname)










    



