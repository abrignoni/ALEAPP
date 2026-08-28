# https://untappd.com/api/docs
__artifacts_v2__ = {
    "untappd_notifications": {
        "name": "Untappd - Push Notifications",
        "description": "Parses Untappd FCM push notifications and venue menu updates from SharedPreferences",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Social",
        "notes": "",
        "paths": (
            '*/com.untappdllc.app/shared_prefs/io.invertase.firebase.xml'
        ), 
        "output_types": "standard",
        "artifact_icon": "bell-ringing",
    },
    "untappd_profile": {
        "name": "Untappd - User Profile",
        "description": "Parses the Untappd user profile",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Social",
        "notes": "",
        "paths": (
            '*/com.untappdllc.app/databases/clevertap*',
        ),
        "output_types": ["html","tsv","lava"],
        "artifact_icon": "user",
    },
    "untappd_dev_events": {
        "name": "Untappd - Device Analytics",
        "description": "Logs information about the device running the Untappd app"
                       "such as model, OS version, radio type, approximate IP location, and more",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Social",
        "notes": "",
        "paths": (
            '*/com.untappdllc.app/databases/superwall_database*',
        ),
        "output_types": "standard",
        "artifact_icon": "activity",
    },
    "untappd_app_events": {
        "name": "Untappd - App Events",
        "description": "Logs information about the app status"
                       "such as launch, open, close, install.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Social",
        "notes": "",
        "paths": (
            '*/com.untappdllc.app/databases/superwall_database*',
        ),
        "output_types": "standard",
        "artifact_icon": "activity",
    },
    "untappd_cached_checkins": {
        "name": "Untappd - Cached Checkins",
        "description": "Parses checkin events including user and beer info"
                       "as well as potentially location/venue information",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Social",
        "notes": "",
        "paths": (
            '*/com.untappdllc.app/cache/http-cache/*.1',
        ),
        "output_types": "standard",
        "artifact_icon": "beer",
    },
    "untappd_discover_locations": {
        "name": "Untappd - Discover Locations",
        "description": "When the Discover page loads, it fetches current locations for"
                       "feeding local events, badges, beers, etc.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Social",
        "notes": "",
        "paths": (
            '*/com.untappdllc.app/cache/http-cache/*.*',
        ),
        "output_types": "standard",
        "artifact_icon": "location-pin",
    },
    "untappd_recent_locations": {
        "name": "Untappd - Checkin Location Suggestions",
        "description": "When checking in a new beer it gives suggestions on locations"
                       "such as recent past checkin locations and nearby locations fed by Foursquare",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Social",
        "notes": "",
        "paths": (
            '*/com.untappdllc.app/cache/http-cache/*.*',
        ),
        "output_types": "standard",
        "artifact_icon": "location-search",
    }
}

import datetime
import gzip
import json
import os
import xml.etree.ElementTree as ET
from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    null_absent_columns
)

def process_gzip(gzip_file):
    try:
        # 1. Open the GZIP compressed binary file
        with gzip.open(gzip_file, 'rb') as f:
            uncompressed_binary = f.read()
            
        # 2. Decode the raw bytes into a UTF-8 string
        json_string = uncompressed_binary.decode('utf-8')
        
        # 3. Parse and print the JSON payload cleanly
        parsed_json = json.loads(json_string)
        
        # 4. Get response data
        response_data = parsed_json.get('response', {})
        
        return response_data
    except Exception:
        pass
        
def get_cache_date(file_found_1):
    """
    Finds the companion .0 file by swapping the extension of the .1 file, 
    then extracts the HTTP Date header.
    """
    # Swap the trailing .1 for .0 on the absolute file path
    meta_file = str(file_found_1).rpartition('.')[0] + '.0'
    
    # Check if the file physically exists on the disk
    if not os.path.exists(meta_file):
        return ''
        
    try:
        with open(meta_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line_clean = line.strip()
                if line_clean.lower().startswith('date:'):
                    # Extract: 'Mon, 02 Jun 2025 17:08:15 GMT'
                    date_str = line_clean.split(':', 1)[1].strip()
                    try:
                        dt_obj = datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
                        return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        return date_str
    except Exception:
        pass

    return ''

@artifact_processor
def untappd_notifications(context):
    source_path = get_file_path(context.get_files_found(), "io.invertase.firebase.xml")
    data_list = []

    tree = ET.parse(source_path)
    root = tree.getroot()

    for item in root.findall('string'):
        name = item.attrib.get('name')
        
        # Skip the comma-separated list of all IDs
        if name == 'all_notification_ids':
            continue

        json_data = item.text
        if not json_data:
            continue

        # Extract the timestamp from the XML key
        # Example key: 0:1744128023360436%2d6851052d685105
        timestamp = ''
        try:
            if ':' in name and '%' in name:
                time_str = name.split(':')[1].split('%')[0]
                time_sec = int(time_str) / 1000000.0
                
                # Convert to UTC and format it, truncating to milliseconds
                dt_obj = datetime.datetime.fromtimestamp(time_sec, datetime.timezone.utc)
                timestamp = dt_obj.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        except Exception:
            # Fallback if the key doesn't match the expected format
            timestamp = ''

        try:
            parsed_json = json.loads(json_data)
            notification = parsed_json.get('notification', {})
            app_data = parsed_json.get('data', {})

            title = notification.get('title', '')
            body = notification.get('body', '')
            push_type = app_data.get('pushType', '')
            action_id = app_data.get('action_id', '')
            message_id = parsed_json.get('messageId', '')

            data_list.append((timestamp, message_id, title, body, push_type, action_id))
        except json.JSONDecodeError:
            pass

    if data_list:
        data_headers = (
            ('Timestamp','datetime'),
            'Message ID',
            'Title',
            'Body',
            'Push Type',
            'Action ID'
        )
        data_list.sort()
        return data_headers, data_list, source_path
    else:
        return None

@artifact_processor
def untappd_profile(context):
    source_path = get_file_path(context.get_files_found(), "clevertap")
    data_list = []

    query = '''
    select
    json_extract(data, '$.Email'),
    json_extract(data, '$.Name'),
    json_extract(data, '$.Username'),
    json_extract(data, '$.Gender'),
    datetime(json_extract(data, '$.dob'),'unixepoch'),
    json_extract(data, '$.last_checkin_beer'),
    json_extract(data, '$.last_checkin_category'),
    json_extract(data, '$.CountryID'),
    json_extract(data, '$.Identity')
    from userProfiles
    '''

    db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

    for record in db_records:
        data_list.append((
            record[0],
            record[1],
            record[2],
            record[3],
            record[4],
            record[5],
            record[6],
            record[7],
            record[8],
        ))

    data_headers = (
        'Email Address',
        'Name',
        'Username',
        'Gender',
        'Date of Birth',
        'Last Checkin Beer',
        'Last Checkin Category',
        'Country ID',
        'Identity',
    )
    data_list.sort()
    return data_headers, data_list, source_path
    
@artifact_processor
def untappd_dev_events(context):
    source_path = get_file_path(context.get_files_found(), "superwall_database")
    data_list = []

    query = '''
    select 
    datetime(createdAt/1000,'unixepoch') as "Timestamp",
    json_extract(parameters, '$.$appVersion'),
    json_extract(parameters, '$.$ipCity'),
    json_extract(parameters, '$.$ipRegion'),
    json_extract(parameters, '$.$ipCountry'),
    json_extract(parameters, '$.$ipContinent'),
    json_extract(parameters, '$.$ipTimezone'),
    json_extract(parameters, '$.$deviceModel'),
    json_extract(parameters, '$.$platform'),
    json_extract(parameters, '$.$osVersion'),
    json_extract(parameters, '$.$radioType'),
    json_extract(parameters, '$.$daysSinceInstall'),
    json_extract(parameters, '$.$app_session_id') as "Session ID"
    from ManagedEventData
    where name IS "device_attributes"
    group by "Session ID"
    order by "Timestamp" ASC
    '''

    db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

    for record in db_records:
        data_list.append((
            record[0],
            record[1],
            record[2],
            record[3],
            record[4],
            record[5],
            record[6],
            record[7],
            record[8],
            record[9],
            record[10],
            record[11],
            record[12],
        ))

    data_headers = (
        ('Timestamp','datetime'),
        'App Version',
        'IP City',
        'IP Region',
        'IP Country',
        'IP Continent',
        'IP Timezone',
        'Device Model',
        'OS',
        'OS Version',
        'Radio Type',
        'Days Since Install',
        'Session ID',
    )

    data_list.sort()
    return data_headers, data_list, source_path
    
@artifact_processor
def untappd_app_events(context):
    source_path = get_file_path(context.get_files_found(), "superwall_database")
    data_list = []

    query = '''
    select 
    datetime(ManagedEventData.createdAt/1000,'unixepoch') as "Timestamp",
    case ManagedEventData.name
        when 'app_close' then 'App Close'
        when 'app_install' then 'App Install'
        when 'app_launch' then 'App Launch'
        when 'app_open' then 'App Open'
        when 'session_start' then 'Session Start'
    end as "Event",
    json_extract(ManagedEventData.parameters, '$.$app_session_id') as "Session ID"
    from ManagedEventData
    where ManagedEventData.name IN ('app_close','app_open','app_launch','app_install','session_start')
    order by "Timestamp" ASC, name ASC
    '''

    db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

    for record in db_records:
        data_list.append((
            record[0],
            record[1],
            record[2]
        ))

    data_headers = (
        ('Timestamp','datetime'),
        'App Event',
        'Session ID'
    )

    data_list.sort()
    return data_headers, data_list, source_path
    
@artifact_processor
def untappd_cached_checkins(context):
    data_list = []
    source_paths = set()
    
    for file_found in context.get_files_found():
        source_name = str(context.get_relative_path(file_found))
        
        response_data = process_gzip(file_found)
        if response_data:
            source_paths.add(file_found)
            checkin_data = response_data.get('checkin', {})
            if not checkin_data:
                continue
                
            # Top-Level Checkin Details
            checkin_id = checkin_data.get('checkin_id', '')
            created_at = checkin_data.get('created_at', '')
            if created_at:
                try:
                    dt_obj = datetime.datetime.strptime(created_at, "%a, %d %b %Y %H:%M:%S %z")
                    created_at = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
            
            rating = checkin_data.get('rating_score', '')
            comment = checkin_data.get('checkin_comment', '')
            
            # User Information
            user = checkin_data.get('user', {})
            uid = user.get('uid', '')
            username = user.get('user_name', '')
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            
            # Beer & Brewery Information
            beer = checkin_data.get('beer', {})
            beer_name = beer.get('beer_name', '')
            beer_abv = beer.get('beer_abv', '')
            
            brewery = checkin_data.get('brewery', {})
            brewery_name = brewery.get('brewery_name', '')
            
            # Venue & Geolocation Information
            venue = checkin_data.get('venue', {})
            venue_name = ''
            lat, lng = '', ''
            
            # Some checkins don't have venues, so venue might be empty or a list
            if isinstance(venue, dict) and venue:
                venue_name = venue.get('venue_name', '')
                location = venue.get('location', {})
                lat = location.get('lat', '')
                lng = location.get('lng', '')
                
            # Application Source
            source = checkin_data.get('source', {})
            app_name = source.get('app_name', '')
            
            # Attached Media (Photos)
            media = checkin_data.get('media', {})
            media_items = media.get('items', [])
            photo_url = ''
            if media_items:
                # Grabbing the high-res image URL if available
                photo_url = media_items[0].get('photo', {}).get('photo_img_lg', '')
            
            # Serving Types
            serving_types = checkin_data.get('serving_types',{})
            container_name = ''
            
            if isinstance(serving_types, dict):
                container_name = serving_types.get('container_name','')

            data_list.append((
                created_at, checkin_id, uid, username, full_name, 
                beer_name, beer_abv, brewery_name, rating, comment, 
                venue_name, lat, lng, app_name, photo_url, container_name, source_name))
    
    data_headers = (('Checkin Date','datetime'),'Checkin ID','UID','Username','Full Name','Beer Name','Beer ABV %','Brewery Name','Rating','Comment','Venue Name','Venue Latitude','Venue Longitude','App Name','Photo URL','Serving Style','Source File')
    
    data_list.sort()
    return data_headers, data_list, '\n'.join(sorted(source_paths))
    
@artifact_processor
def untappd_discover_locations(context):
    data_list = []
    source_paths = set()
    
    for file_found in context.get_files_found():
        source_name = str(context.get_relative_path(file_found))
        
        # Pass context and the current .1 file to search for the meta file
        cache_date = get_cache_date(file_found)
        response_data = process_gzip(file_found)
        
        if response_data:
            source_paths.add(file_found)
            discover_items = response_data.get('discover_items', {}).get('items', [])

            for item in discover_items:
                content = item.get('content', {})
                
                # Extract lat and lng, defaulting to None if they don't exist
                lat = content.get('lat')
                lng = content.get('lng')
                item_type = item.get('item_type')

                data_list.append((cache_date,item_type, lat, lng, source_name))
    
    data_headers = (('Cache Timestamp','datetime'),'Item Type', 'Latitude', 'Longitude', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))

@artifact_processor
def untappd_recent_locations(context):
    data_list = []
    source_paths = set()
    
    for file_found in context.get_files_found():
        source_name = str(context.get_relative_path(file_found))
        
        cache_date = get_cache_date(file_found)
    
        # Assuming process_gzip returns the dict containing 'location', 'recent', and 'foursquare'
        response_data = process_gzip(file_found)
        
        if response_data:
            source_paths.add(file_found)
            # 1. Extract Current Location
            current_location = response_data.get('location')
            if not current_location:
                continue
            
            current_lat = current_location.get('lat')
            current_lng = current_location.get('lng')
            
            # 2. Extract Recent Entries
            recent_items = response_data.get('recent', {}).get('items', [])
            
            for item in recent_items:
                entry_type = "Recent"
                recent_date = item.get('recent_date', '')
                venue_name = item.get('venue_name', '')
                distance = item.get('distance', '')
                
                venue_loc = item.get('location', {})
                venue_lat = venue_loc.get('lat')
                venue_lng = venue_loc.get('lng')
                
                # Clean up the date string for better sorting
                if recent_date:
                    try:
                        dt_obj = datetime.datetime.strptime(recent_date, "%a, %d %b %Y %H:%M:%S %z")
                        recent_date = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
                
                data_list.append((
                    cache_date,
                    recent_date, 
                    entry_type,
                    venue_name, 
                    distance, 
                    venue_lat, 
                    venue_lng, 
                    current_lat, 
                    current_lng, 
                    source_name
                ))

            # 3. Extract Foursquare Suggestions
            foursquare_items = response_data.get('foursquare', {}).get('items', [])
            
            for item in foursquare_items:
                entry_type = "Foursquare"
                recent_date = ""  # Foursquare suggestions lack a timestamp
                venue_name = item.get('venue_name', '')
                distance = item.get('distance', '')
                
                venue_loc = item.get('location', {})
                venue_lat = venue_loc.get('lat')
                venue_lng = venue_loc.get('lng')
                
                data_list.append((
                    cache_date,
                    recent_date,
                    entry_type,
                    venue_name,
                    distance,
                    venue_lat,
                    venue_lng,
                    current_lat,
                    current_lng,
                    source_name
                ))

    data_headers = (
        ('Cached Query Timestamp','datetime'),
        ('Recent Checkin Timestamp','datetime'),
        'Entry Type',
        'Venue Name',
        'Distance (Miles)',
        'Venue Latitude',
        'Venue Longitude',
        'Current Latitude',
        'Current Longitude',
        'Source File'
    )
    
    data_list.sort()
    return data_headers, data_list, '\n'.join(sorted(source_paths))