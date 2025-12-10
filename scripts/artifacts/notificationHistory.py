__artifacts_v2__ = {
    "Android Notification History": {
        "name": "Android Notification History",
        "description": "Get Android notifications' history, policy and settings.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "version": "0.0.1",
        "date": "2024-07-02",
        "requirements": "",
        "category": "Android Notification History",
        "paths": (
            '**/system_ce/*/notification_history/history/*',
            '**/system/users/*/settings_secure.xml',
            '**/system/notification_policy.xml',
        ),
        "function": "get_notificationHistory"
    }
}

import xml.etree.ElementTree as ET
import os
from scripts.artifacts.notification_history_pb import notificationhistory_pb2
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, abxread, checkabx, convert_ts_int_to_utc, convert_utc_human_to_timezone

def get_notificationHistory(files_found, report_folder, _seeker, _wrap_text):
    data_pb_list = []
    file_directory = None
    
    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        
        # Simpan direktori file terakhir yang diproses untuk digunakan di report
        current_file_directory = os.path.dirname(file_found)

        # parsing settings_secure.xml
        if file_name.endswith('settings_secure.xml'):
            data_list = []
            user = os.path.basename(os.path.dirname(file_found))
            if checkabx(file_found):
                multi_root = True
                tree = abxread(file_found, multi_root)
            else:
                tree = ET.parse(file_found)
            
            root = tree.getroot()
            for setting in root.findall(".//setting"):
                if setting.attrib.get('name') == 'notification_history_enabled':
                    value = setting.attrib.get('value')
                    value = "Enabled" if value == "1" else "Disabled" if value == "0" else "Unknown"
                    data_list.append((value, user))

            if data_list:
                description = 'Indicates whether "Notification History" feature is enabled.'
                report = ArtifactHtmlReport('Android Notification History - Status')
                report.start_artifact_report(report_folder, 'Status', description)
                report.add_script()
                data_headers = ('Status', 'User')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Android Notification History - Status'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc('No Android Notification History - Status data available')
        
        elif file_name.endswith('notification_policy.xml'):
            data_list = []
            if checkabx(file_found):
                multi_root = False
                tree = abxread(file_found, multi_root)
            else:
                tree = ET.parse(file_found)
            
            root = tree.getroot()
            for elem in root:
                if elem.tag == 'snoozed-notifications':
                    if list(elem):
                        for notification in elem:
                            if notification.tag == 'notification':
                                notification_ts = int(notification.attrib.get('time'))
                                snooze_time = convert_utc_human_to_timezone(convert_ts_int_to_utc(int(notification_ts/1000.0)), 'UTC')
                                notification_key = notification.attrib.get('key')
                                data_list.append((f'{snooze_time}', notification_key))
            
            if data_list:
                description = 'Notifications the user chose to snooze for a specific time interval'
                report = ArtifactHtmlReport('Android Notification History - Snoozed notifications')
                report.start_artifact_report(report_folder, 'Snoozed notifications', description)
                report.add_script()
                data_headers = ('Reminder Time', 'Snoozed Notification')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = 'Android Notification History - Snoozed notifications'
                tsv(report_folder, data_headers, data_list, tsvname)
            else:
                logfunc('No Android Notification History - Snoozed notifications data available')

        else:
            if file_name.endswith('.xml'):
                continue

            # iterate through the notification pbs
            try:
                notification_history = notificationhistory_pb2.NotificationHistoryProto()
                with open(file_found, 'rb') as f:
                    try:
                        content = f.read()
                        if not content: # Skip if file is empty
                            continue
                        notification_history.ParseFromString(content) 
                    except (ValueError, TypeError) as e:
                        logfunc(f'Error in the ParseFromString() function for {file_name}. The error message was: {e}')
                        continue

                    # FIX: Gunakan getattr untuk menghindari error no-member pada string_pool
                    string_pool = getattr(notification_history, 'string_pool', None)
                    if string_pool:
                        package_map = {i + 1: pkg for i, pkg in enumerate(string_pool.strings)} 
                    else:
                        package_map = {}

                    # FIX: Gunakan getattr untuk major_version
                    major_version = getattr(notification_history, 'major_version', None) if notification_history.HasField('major_version') else None
                    
                    # FIX: Gunakan getattr untuk notification list
                    notifications = getattr(notification_history, 'notification', [])

                    for notification in notifications:
                        package_name = notification.package if notification.package else package_map.get(notification.package_index, "")
                        
                        fields = ['uid', 'user_id', 'package_index', 'channel_name', 'channel_id','channel_id_index', 'channel_name_index', 'conversation_id', 'conversation_id_index']
                        # HAPUS: defaults = {field: 'Error' for field in fields} (Unused variable removed)
                        
                        values = {}
                        for field in fields:
                            try:
                                values[field] = getattr(notification, field)
                            except AttributeError:
                                values[field] = 'Error'
                        
                        if notification.HasField('icon'):
                            icon_fields = ['image_type', 'image_bitmap_filename', 'image_resource_id', 'image_resource_id_package','image_data_length', 'image_data_offset', 'image_uri']
                            for icon_field in icon_fields:
                                values[icon_field] = getattr(notification.icon, icon_field)
                        else:
                            icon_fields = [
                                'image_type', 'image_bitmap_filename', 'image_resource_id', 'image_resource_id_package',
                                'image_data_length', 'image_data_offset', 'image_uri'
                            ]
                            for icon_field in icon_fields:
                                values[icon_field] = None
                        
                        uid = values['uid']
                        user_id = values['user_id']
                        package_index = values['package_index']
                        channel_name = values['channel_name']
                        channel_id = values['channel_id']
                        channel_id_index = values['channel_id_index']
                        channel_name_index = values['channel_name_index']
                        conversation_id = values['conversation_id']
                        conversation_id_index = values['conversation_id_index']
                        posted_time = convert_utc_human_to_timezone(convert_ts_int_to_utc(int(notification.posted_time_ms/1000.0)),'UTC') if notification.HasField('posted_time_ms') else None
                        title = notification.title if notification.HasField('title') else None
                        text = notification.text if notification.HasField('text') else None
                        image_type = values['image_type']
                        image_bitmap_filename = values['image_bitmap_filename']
                        image_resource_id = values['image_resource_id']
                        image_resource_id_package = values['image_resource_id_package']
                        image_data_length = values['image_data_length']
                        image_data_offset = values['image_data_offset']
                        image_uri = values['image_uri']
                        
                        try:
                            file_creation = convert_utc_human_to_timezone(convert_ts_int_to_utc(int(file_name)/1000.0),'UTC')
                        except ValueError:
                            file_creation = ''
                            
                        data_pb_list.append((f'{posted_time}',title,text,package_name,user_id,uid,package_index,channel_name,channel_name_index,channel_id,channel_id_index,conversation_id,conversation_id_index,major_version,image_type,image_bitmap_filename,image_resource_id,image_resource_id_package,image_data_length,image_data_offset,image_uri,file_name,f'{file_creation}'))
                        
                        # Set file_directory jika berhasil mendapatkan data dari setidaknya satu file
                        file_directory = current_file_directory

            except (IOError, OSError) as e:
                logfunc(f'Error reading file {file_found}: {e}')
    
    if len(data_pb_list) > 0:
        description = 'A history of the notifications that landed on the device during the last 24h'
        report = ArtifactHtmlReport('Android Notification History - Notifications')
        report.start_artifact_report(report_folder, 'Notifications', description)
        report.add_script()
        data_headers = ('Posted Time','Title', 'Text','Package Name','User ID','UID','Package Index','Channel Name','Channel Name Index','Channel ID','Channel ID Index','Conversation ID','Conversation ID Index','Major Version','Image Type','Image Bitmap Filename','Image Resource ID','Image Resource ID Package','Image Data Length','Image Data Offset','Image URI','Protobuf File Name','Protobuf File Creation Date')
        
        # Pastikan file_directory memiliki nilai sebelum digunakan
        if file_directory:
            report.write_artifact_data_table(data_headers, data_pb_list, file_directory, html_escape=False)
        else:
            # Fallback jika file_directory entah kenapa masih None tapi data ada (kasus edge case)
            report.write_artifact_data_table(data_headers, data_pb_list, "", html_escape=False)
            
        report.end_artifact_report()
        
        tsvname = 'Android Notification History - Notifications'
        tsv(report_folder, data_headers, data_pb_list, tsvname)
        
        tlactivity = 'Android Notification History - Notifications'
        timeline(report_folder, tlactivity, data_pb_list, data_headers)
    else:
        logfunc('No Android Notification History - Notifications available')