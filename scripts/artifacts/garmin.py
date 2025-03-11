# Module Description: Parses the Garmin app for activities, connections and notifications
# Author: @KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)
# Date: 2023-01-18
# Artifact version: 0.0.1

import calendar
import os
import sqlite3
import time

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, kmlgen, is_platform_windows, open_sqlite_db_readonly

def get_garmin(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith(('-wal','-shm','-journal')):
            continue
            
        if file_found.endswith('gcm_cache.db'):
            db = open_sqlite_db_readonly(file_found)
            
            #Get Garmin GCM cache activities
            cursor = db.cursor()
            cursor.execute('''
            select
            replace(trim(json_extract(cached_val, '$.summaryDTO.startTimeGMT'),'.0'),'T',' ') as "Start Timestamp (UTC)",
            replace(trim(json_extract(cached_val, '$.summaryDTO.startTimeLocal'),'.0'),'T',' ') as "Start Timestamp (Local)",
            json_extract(cached_val, '$.summaryDTO.duration') as "Duration (Seconds)",
            json_extract(cached_val, '$.activityTypeDTO.typeKey') as "Activity Type",
            json_extract(cached_val, '$.metadataDTO.userInfoDto.fullname') as "User Full Name",
            json_extract(cached_val, '$.metadataDTO.userInfoDto.displayname') as "User ID",
            round(json_extract(cached_val, '$.summaryDTO.distance')/1609,3) as "Distance (Miles)",
            round(json_extract(cached_val, '$.summaryDTO.distance')/1000,3) as "Distance (KM)",
            json_extract(cached_val, '$.summaryDTO.startLatitude') as "Start Latitude",
            json_extract(cached_val, '$.summaryDTO.startLongitude') as "Start Longitude",
            json_extract(cached_val, '$.summaryDTO.endLatitude') as "End Latitude",
            json_extract(cached_val, '$.summaryDTO.endLongitude') as "End Longitude",
            json_extract(cached_val, '$.summaryDTO.averageHR') as "Average Heart Rate",
            json_extract(cached_val, '$.summaryDTO.calories') as "Calories Burned",
            json_extract(cached_val, '$.activityName') as "Activity Name",
            json_extract(cached_val, '$.activityId') as "Activity ID",
            json_extract(cached_val, '$.locationName') as "Location Name",
            concept_id
            from json_activities
            where data_type = "ACTIVITY_DETAILS"
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                data_list_kml = []
                for row in all_rows:
                    
                    start_ts_seconds = calendar.timegm(time.strptime(row[0], '%Y-%m-%d %H:%M:%S'))
                    end_ts_seconds = start_ts_seconds + row[2]
                    
                    end_ts_convert = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end_ts_seconds))
                
                    duration = time.strftime('%H:%M:%S', time.gmtime(row[2]))
                                    
                    data_list.append((row[0],row[1],end_ts_convert,duration,row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))
                    
                    data_list_kml.append((row[0],row[8],row[9]))
                    data_list_kml.append((end_ts_convert,row[10],row[11]))
                    
                    data_headers_kml = ('Timestamp','Latitude','Longitude')
                    
                    kmlactivity = 'Garmin - GCM Cache Activities - ' + str(row[0].replace(':','_'))
                    kmlgen(report_folder, kmlactivity, data_list_kml, data_headers_kml)
                    data_list_kml = []

                description = 'Garmin GCM cache activities'
                report = ArtifactHtmlReport('Garmin - GCM Cache Activities')
                report.start_artifact_report(report_folder, 'Garmin - GCM Cache Activities', description)
                report.add_script()
                data_headers = ('Start Timestamp (UTC)', 'Start Timestamp (Local)','End Timestamp (UTC)','Duration','Activity Type','User Full Name','User ID','Distance (Miles)','Distance (KM)','Start Latitude','Start Longitude','End Latitude','End Longitude','Average Heart Rate','Calories Burned','Activity Name','Activity ID','Location Name')
                report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
                report.end_artifact_report()
                
                tsvname = 'Garmin - GCM Cache Activities'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Garmin - GCM Cache Activities'
                timeline(report_folder, tlactivity, data_list, data_headers)
            
            else:
                logfunc('No Garmin - GCM Cache Activities data available')
                
            #Get Garmin devices
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(last_connected_timestamp/1000,'unixepoch') as "Last Connection Timetamp",
            product_display_name,
            bt_friendly_name,
            mac_address,
            connection_type,
            software_version,
            unit_id,
            image_url
            from devices
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                for row in all_rows:
                                    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))

                description = 'Garmin devices'
                report = ArtifactHtmlReport('Garmin - Devices')
                report.start_artifact_report(report_folder, 'Garmin - Devices', description)
                report.add_script()
                data_headers = ('Last Connection Timestamp','Product Display Name','Bluetooth Friendly Name','Mac Address','Connection Type','Software Version','Unit ID','Product Image URL')
                report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
                report.end_artifact_report()
                
                tsvname = 'Garmin - Devices'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Garmin - Devices'
                timeline(report_folder, tlactivity, data_list, data_headers)
            
            else:
                logfunc('No Garmin - Devices data available')
            
            #Get Garmin weather
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(saved_timestamp/1000,'unixepoch') as "Saved Timestamp",
            replace(json_extract(cached_val, '$.issueDate'),'T',' ') as "Issue Date",
            json_extract(cached_val, '$.latitude') as "Latitude",
            json_extract(cached_val, '$.longitude') as "Longitude",
            json_extract(cached_val, '$.weatherStationDTO.id') as "Weather Station ID",
            json_extract(cached_val, '$.weatherStationDTO.name') as "Weather Station Name",
            json_extract(cached_val, '$.temp') as "Temperature",
            json_extract(cached_val, '$.apparentTemp') as "Apparent Temperature",
            json_extract(cached_val, '$.dewPoint') as "Dew Point",
            json_extract(cached_val, '$.relativeHumidity') as "Relative Humidity",
            json_extract(cached_val, '$.weatherTypeDTO.desc') as "Weather Type",
            json_extract(cached_val, '$.windDirection') as "Wind Direction (Degrees)",
            json_extract(cached_val, '$.windDirectionCompassPoint') as "Wind Direction (Compass Point)",
            json_extract(cached_val, '$.windSpeed') as "Wind Speed",
            concept_id
            from json_activities
            where data_type = "ACTIVITY_WEATHER"
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                data_list_kml = []
                for row in all_rows:
                                    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))

                description = 'Garmin weather'
                report = ArtifactHtmlReport('Garmin - Weather')
                report.start_artifact_report(report_folder, 'Garmin - Weather', description)
                report.add_script()
                data_headers = ('Saved Timestamp','Issue Date','Latitude','Longitude','Weather Station ID','Weather Station Name','Temperature','Apparent Temperature','Dew Point','Relative Humidity','Weather Type','Wind Direction (Degrees)','Wind Direction (Compass Point)','Wind Speed','Concept ID')
                report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
                report.end_artifact_report()
                
                tsvname = 'Garmin - Weather'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Garmin - Weather'
                timeline(report_folder, tlactivity, data_list, data_headers)
            
            else:
                logfunc('No Garmin - Weather data available')
            
            db.close()
        
        elif file_found.endswith('notification-database'):
            db = open_sqlite_db_readonly(file_found)
            
            #Get Garmin notifications
            cursor = db.cursor()
            cursor.execute('''
            select
            case 
                when statusTimestamp = 0 then ''
                else datetime(statusTimestamp/1000,'unixepoch')
            end,
            status,
            title,
            subTitle,
            message,
            packageName,
            positiveAction,
            negativeAction,
            phoneNumber,            
            type,
            datetime(postTime/1000,'unixepoch'),
            datetime("when"/1000,'unixepoch')
            from notification_info
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                for row in all_rows:
                                    
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

                description = 'Garmin notifications'
                report = ArtifactHtmlReport('Garmin - Notifications')
                report.start_artifact_report(report_folder, 'Garmin - Notifications', description)
                report.add_script()
                data_headers = ('Status Timestamp','Notification Status','Title','Subtitle','Message','Package Name','Positive Action','Negative Action','Phone Number','Type','Post Timestamp','When Timestamp')
                report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
                report.end_artifact_report()
                
                tsvname = 'Garmin - Notifications'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Garmin - Notifications'
                timeline(report_folder, tlactivity, data_list, data_headers)
            
            else:
                logfunc('No Garmin - Notifications data available')
                
            db.close()
            
        elif file_found.endswith('cache-database'):
            db = open_sqlite_db_readonly(file_found)
            
            #Get Garmin cache db activities
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(json_extract(json, '$.beginTimestamp')/1000,'unixepoch') as "Start Timestamp (UTC)",
            datetime((json_extract(json, '$.beginTimestamp')/1000)+json_extract(json, '$.duration'),'unixepoch') as "End Timestamp (UTC)",
            json_extract(json, '$.startTimeLocal') as "Start Time (Local)",
            json_extract(json, '$.duration') as "Duration",
            json_extract(json, '$.activityType.typeKey') as "Activity Type",
            json_extract(json, '$.ownerFullName') as "Owner Full Name",
            displayName,
            round(json_extract(json, '$.distance')/1609,3) as "Distance (Miles)",
            round(json_extract(json, '$.distance')/1000,3) as "Distance (KM)",
            json_extract(json, '$.startLatitude') as "Start Latitude",
            json_extract(json, '$.startLongitude') as "Start Longitude",
            json_extract(json, '$.endLatitude') as "End Latitude",
            json_extract(json, '$.endLongitude') as "End Longitude",
            json_extract(json, '$.averageHR') as "Average Heart Rate",
            json_extract(json, '$.calories') as "Calories Burned",
            json_extract(json, '$.steps') as "Steps",
            json_extract(json, '$.manufacturer') as "Device Manufacturer",
            json_extract(json, '$.deviceId') as "Device ID",
            json_extract(json, '$.locationName') as "Location Name",
            json_extract(json, '$.activityName') as "Activity Name",
            activityId,
            datetime(lastUpdate/1000,'unixepoch')
            from activity_summaries
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                data_list_kml = []
                for row in all_rows:
                
                    start_ts_seconds = calendar.timegm(time.strptime(row[2], '%Y-%m-%d %H:%M:%S'))
                    end_ts_seconds = start_ts_seconds + row[3]
                    
                    end_ts_convert = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end_ts_seconds))
                
                    duration = time.strftime('%H:%M:%S', time.gmtime(row[3]))
                                    
                    data_list.append((row[0],row[1],row[2],end_ts_convert,duration,row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21]))
                    
                    data_list_kml.append((row[0],row[9],row[10]))
                    data_list_kml.append((end_ts_convert,row[11],row[12]))
                    
                    data_headers_kml = ('Timestamp','Latitude','Longitude')
                    
                    kmlactivity = 'Garmin - Cache DB Activities - ' + str(row[0].replace(':','_'))
                    kmlgen(report_folder, kmlactivity, data_list_kml, data_headers_kml)
                    data_list_kml = []

                description = 'Garmin cache DB activities'
                report = ArtifactHtmlReport('Garmin - Cache DB Activities')
                report.start_artifact_report(report_folder, 'Garmin - Cache DB Activities', description)
                report.add_script()
                data_headers = ('Start Timestamp (UTC)','End Timestamp (UTC)','Start Timestamp (Local)','End Timestamp (Local)','Duration','Activity Type','Owner Full Name','Owner ID','Distance (Miles)','Distance (KM)','Start Latitude','Start Longitude','End Latitude','End Longitude','Average Heart Rate','Calories Burned','Steps','Device Manufacturer','Device ID','Location Name','Activity Name','Activity ID','Last Update Timestamp')
                report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
                report.end_artifact_report()
                
                tsvname = 'Garmin - Cache DB Activities'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Garmin - Cache DB Activities'
                timeline(report_folder, tlactivity, data_list, data_headers)
            
            else:
                logfunc('No Garmin - Cache DB Activities data available')
                
            #Get Garmin sleep details
            cursor = db.cursor()
            cursor.execute('''
            select
            datetime(sleepStartTimeGMT/1000,'unixepoch') as "Sleep Start Timestamp (UTC)",
            datetime(sleepEndTimeGMT/1000,'unixepoch') as "Sleep End Timestamp (UTC)",
            datetime(autoSleepStartTimeGMT/1000,'unixepoch') as "Auto Sleep Start Timestamp (UTC)",
            datetime(autoSleepEndTimeGMT/1000,'unixepoch') as "Auto Sleep End Timestamp (UTC)",
            sleepTimeInSeconds,
            deepSleepSeconds,
            lightSleepSeconds,
            remSleepSeconds,
            awakeSleepSeconds,
            averageSpO2Value,
            lowestSpO2Value,
            averageRespirationValue,
            lowestRespirationValue,
            highestRespirationValue,
            datetime(lastUpdated/1000,'unixepoch') as "Last Updated"
            from sleep_detail
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                for row in all_rows:
                
                    sleep_time = time.strftime('%H:%M:%S', time.gmtime(row[4]))
                    deep_sleep_time = time.strftime('%H:%M:%S', time.gmtime(row[5]))
                    light_sleep_time = time.strftime('%H:%M:%S', time.gmtime(row[6]))
                    rem_sleep_time = time.strftime('%H:%M:%S', time.gmtime(row[7]))
                    awake_sleep_time = time.strftime('%H:%M:%S', time.gmtime(row[8]))
                                    
                    data_list.append((row[0],row[1],row[2],row[3],sleep_time,deep_sleep_time,light_sleep_time,rem_sleep_time,awake_sleep_time,row[9],row[10],row[11],row[12],row[13],row[14]))

                description = 'Garmin sleep activities'
                report = ArtifactHtmlReport('Garmin - Sleep Activities')
                report.start_artifact_report(report_folder, 'Garmin - Sleep Activities', description)
                report.add_script()
                data_headers = ('Sleep Start Timestamp (UTC)','Sleep End Timestamp (UTC)','Auto Sleep Start Timestamp (UTC)','Auto Sleep End Timestamp (UTC)','Total Sleep Time','Deep Sleep','Light Sleep','REM Sleep','Awake Sleep','Average Sp02','Lowest Sp02','Average Breaths/min','Lowest Breaths/min','Highest Breaths/min','Last Updated Timestamp')
                report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
                report.end_artifact_report()
                
                tsvname = 'Garmin - Sleep Activities'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = 'Garmin - Sleep Activities'
                timeline(report_folder, tlactivity, data_list, data_headers)
            
            else:
                logfunc('No Garmin - Sleep Activities data available')
                
            db.close()
            
        else:
            break
    
__artifacts__ = {
        "Garmin": (
                "Garmin",
                ('*/data/com.garmin.android.apps.connectmobile/databases/gcm_cache.db*','*/data/com.garmin.android.apps.connectmobile/databases/notification-database*','*/data/com.garmin.android.apps.connectmobile/databases/cache-database*'),
                get_garmin)
}