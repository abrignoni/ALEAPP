__artifacts_v2__ = {
    "Life360": {
        "name": "Life360",
        "description": "Parses the Life360 app locations, device battery, and more",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2024-01-17",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/com.life360.android.safetymapd/databases/messaging.db*','*/com.life360.android.safetymapd/databases/L360LocalStoreRoomDatabase*','*/com.life360.android.safetymapd/databases/L360EventStore.db*'),
        "function": "get_Life360"
    }
}

from datetime import *
import json
import os
import shutil
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, get_next_unused_name, convert_ts_human_to_utc, convert_utc_human_to_timezone, kmlgen

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/'

def get_Life360(files_found, report_folder, seeker, wrap_text):
    
    data_list_messaging = []
    data_list_places = []
    data_list_places_kml = []
    data_list_geo = []
    data_list_battery = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        # Chat Messages
        if file_found.endswith('messaging.db'):
            messaging_db = file_found            
            db = open_sqlite_db_readonly(messaging_db)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(message.created_at,'unixepoch'),
            message.thread_id,
            message.sender_id,
            thread_participant.participant_name as 'Sender',
            message.content,
            case message.sent
                when 0 then ''
                when 1 then 'Yes'
            end as 'Message Sent',
            case message.read
                when 0 then ''
                when 1 then 'Yes'
            end as 'Message Read',
            case message.dismissed
                when 0 then ''
                when 1 then 'Yes'
            end as 'Message Dismissed',
            case message.deleted
                when 0 then ''
                when 1 then 'Yes'
            end as 'Message Deleted',
            case message.has_location 
                when 0 then ''
                when 1 then 'Yes'
            end as 'Has Location',
            message.location_latitude,
            message.location_longitude,
            message.location_name,
            datetime(message.location_timestamp,'unixepoch')
            from message
            left join thread_participant on message.sender_id = thread_participant.participant_id
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    time_create = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[0]),'UTC')
                    loc_time = ''
                    if not row[13] is None:
                        loc_time = convert_utc_human_to_timezone(convert_ts_human_to_utc(row[13]),'UTC')
                    data_list_messaging.append((time_create,row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],loc_time,messaging_db))
            db.close()
        
        # Places        
        if file_found.endswith('L360LocalStoreRoomDatabase'):
            places_db = file_found            
            db = open_sqlite_db_readonly(places_db)
            cursor = db.cursor()
            cursor.execute('''
            select
            name,
            latitude,
            longitude,
            radius,
            source,
            source_id,
            owner_id
            from places
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    data_list_places.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],places_db))
                    data_list_places_kml.append(('',row[1],row[2],row[0]))
            db.close()
            
        # Geolocation & Device Battery
        if file_found.endswith('L360EventStore.db'):
            geo_db = file_found            
            db = open_sqlite_db_readonly(geo_db)
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(timestamp/1000,'unixepoch'),
            data,
            id,
            json_extract(data, '$.tag') as 'Tag'
            from event
            where eventVersion = 5 and Tag = 'BLE'
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    json_load = json.loads(row[1])
                
                    json_timestamp = str(datetime.fromtimestamp(json_load['locationData'].get('time','')/1000,tz=timezone.utc))[:-6]
                    time_create = convert_utc_human_to_timezone(convert_ts_human_to_utc(json_timestamp),'UTC')
                    
                    json_lat = json_load['locationData'].get('latitude','')
                    json_long = json_load['locationData'].get('longitude','')
                    json_speed = json_load['locationData'].get('speed','')
                    json_alt = json_load['locationData'].get('altitude','')
                    json_course = json_load['locationData'].get('course','')
                    json_bearing = json_load['locationData'].get('bearing','')
                    json_vert = json_load['locationData'].get('verticalAccuracy','')
                    json_hor = json_load['locationData'].get('horizontalAccuracy','')
                    
                    
                    json_battery = json_load['metaData'].get('battery','')
                    json_charging = json_load['metaData'].get('chargingState','')
                    json_lmode = json_load['metaData'].get('lmode','')
                    
                    json_bssid = ''
                    json_ssid = ''
                    if not (json_load['metaData']['wifiData'].get('connectedAccessPoint') is None):
                        json_bssid = json_load['metaData']['wifiData']['connectedAccessPoint'].get('bssid','')
                        json_ssid = json_load['metaData']['wifiData']['connectedAccessPoint'].get('ssid','').replace('\"','')
                    
                    data_list_geo.append((time_create,json_lat,json_long,json_alt,json_speed,json_course,json_bearing,json_vert,json_hor,json_lmode,json_bssid,json_ssid,row[2],geo_db))
                    data_list_battery.append((time_create,json_battery,json_charging,geo_db))
            db.close()
        
        else:
            continue # skip -journal and other files

        if report_folder[-1] == slash: 
            folder_name = os.path.basename(report_folder[:-1])
        else:
            folder_name = os.path.basename(report_folder)

    # Chat Messages Report
    if len(data_list_messaging) > 0:
        report = ArtifactHtmlReport(f'Life360 - Chat Messages')
        report.start_artifact_report(report_folder, f'Life360 - Chat Messages')
        report.add_script()
        data_headers = ('Timestamp','Thread ID','Sender ID','Sender Name','Message','Message Sent','Message Read','Message Dismissed','Message Deleted','Has Location','Latitude','Longitude','Location Name','Location Timestamp','Source File')

        report.write_artifact_data_table(data_headers, data_list_messaging, messaging_db, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Life360 - Chat Messages'
        tsv(report_folder, data_headers, data_list_messaging, tsvname)
        
        tlactivity = f'Life360 - Chat Messages'
        timeline(report_folder, tlactivity, data_list_messaging, data_headers)
    else:
        logfunc('No Life360 - Chat Messages data available')
    
    # Places Report
    if len(data_list_places) > 0:
        report = ArtifactHtmlReport(f'Life360 - Places')
        report.start_artifact_report(report_folder, f'Life360 - Places')
        report.add_script()
        data_headers = ('Place Name','Latitude','Longitude','Radius (m)','Places Source','Source ID','Owner ID','Source File')
        data_headers_kml = ('Timestamp','Latitude','Longitude','Place Name')

        report.write_artifact_data_table(data_headers, data_list_places, places_db, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Life360 - Places'
        tsv(report_folder, data_headers, data_list_places, tsvname)
        
        kmlactivity = 'Life360 - Places'
        kmlgen(report_folder, kmlactivity, data_list_places_kml, data_headers_kml)
        
    else:
        logfunc('No Life360 - Places data available')
        
    # Geolocation Report
    if len(data_list_geo) > 0:
        report = ArtifactHtmlReport(f'Life360 - Locations')
        report.start_artifact_report(report_folder, f'Life360 - Locations')
        report.add_script()
        data_headers = ('Timestamp','Latitude','Longitude','Altitude','Speed (mps)','Course','Bearing','Vertical Accuracy (+/- m)','Horizontal Accuracy (+/- m)','Location Mode','Connected Access Point BSSID','Connected Access Point SSID','ID','Source File')

        report.write_artifact_data_table(data_headers, data_list_geo, geo_db, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Life360 - Locations'
        tsv(report_folder, data_headers, data_list_geo, tsvname)
        
        tlactivity = f'Life360 - Locations'
        timeline(report_folder, tlactivity, data_list_geo, data_headers)
        
        kmlactivity = 'Life360 - Locations'
        kmlgen(report_folder, kmlactivity, data_list_geo, data_headers)
        
    else:
        logfunc('No Life360 - Locations data available')
        
    # Battery Report
    if len(data_list_battery) > 0:
        report = ArtifactHtmlReport(f'Life360 - Device Battery')
        report.start_artifact_report(report_folder, f'Life360 - Device Battery')
        report.add_script()
        data_headers = ('Timestamp','Device Battery (%)','Charging','Source File')

        report.write_artifact_data_table(data_headers, data_list_battery, geo_db, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Life360 - Device Battery'
        tsv(report_folder, data_headers, data_list_battery, tsvname)
        
        tlactivity = f'Life360 - Device Battery'
        timeline(report_folder, tlactivity, data_list_battery, data_headers)
        
    else:
        logfunc('No Life360 - Device Battery data available')