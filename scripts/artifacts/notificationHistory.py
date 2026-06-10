__artifacts_v2__ = {
    "Android Notification History": {
        "name": "Android Notification History",
        "description": "Get Android notifications' history, policy and settings. This parser is based on a research project",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "version": "0.0.2",
        "date": "2024-07-02",
        "requirements": "blackboxprotobuf",
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
from datetime import *
import os
import scripts.artifacts.notification_history_pb.notificationhistory_pb2 as notificationhistory_pb2

try:
    import blackboxprotobuf
    HAS_BLACKBOXPROTOBUF = True
except ImportError:
    HAS_BLACKBOXPROTOBUF = False

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, abxread, checkabx,convert_ts_int_to_utc,convert_utc_human_to_timezone


def parse_notification_with_blackbox(pb_data, file_name):
    """
    Fallback parser using blackboxprotobuf for when the compiled schema fails.
    Returns a list of notification tuples or empty list if parsing fails.
    """
    data_list = []
    try:
        message, typedef = blackboxprotobuf.decode_message(pb_data)
        
        # Try to extract notifications from the decoded message
        # The structure may vary, so we try common field numbers
        notifications = []
        
        # Field 3 is typically the notification list based on the proto schema
        if '3' in message:
            notif_data = message['3']
            if isinstance(notif_data, list):
                notifications = notif_data
            else:
                notifications = [notif_data]
        
        # Try to get string pool from field 1
        string_pool = []
        if '1' in message and isinstance(message['1'], dict):
            pool_data = message['1']
            if '2' in pool_data:
                pool_strings = pool_data['2']
                if isinstance(pool_strings, list):
                    string_pool = [s.decode('utf-8') if isinstance(s, bytes) else str(s) for s in pool_strings]
                else:
                    string_pool = [pool_strings.decode('utf-8') if isinstance(pool_strings, bytes) else str(pool_strings)]
        
        package_map = {i + 1: pkg for i, pkg in enumerate(string_pool)}
        
        # Get major version from field 2
        major_version = message.get('2', None)
        
        for notif in notifications:
            if not isinstance(notif, dict):
                continue
                
            # Extract fields based on proto field numbers
            package = notif.get('1', b'')
            if isinstance(package, bytes):
                package = package.decode('utf-8', errors='ignore')
            package_index = notif.get('2', 0)
            
            # If package is empty, try to get from string pool
            if not package and package_index:
                package = package_map.get(package_index, '')
            
            channel_name = notif.get('3', b'')
            if isinstance(channel_name, bytes):
                channel_name = channel_name.decode('utf-8', errors='ignore')
            channel_name_index = notif.get('4', 0)
            
            channel_id = notif.get('5', b'')
            if isinstance(channel_id, bytes):
                channel_id = channel_id.decode('utf-8', errors='ignore')
            channel_id_index = notif.get('6', 0)
            
            uid = notif.get('7', 0)
            user_id = notif.get('8', 0)
            posted_time_ms = notif.get('9', 0)
            
            title = notif.get('10', b'')
            if isinstance(title, bytes):
                title = title.decode('utf-8', errors='ignore')
            
            text = notif.get('11', b'')
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            
            conversation_id = notif.get('13', b'')
            if isinstance(conversation_id, bytes):
                conversation_id = conversation_id.decode('utf-8', errors='ignore')
            conversation_id_index = notif.get('14', 0)
            
            # Handle icon (field 12)
            icon_data = notif.get('12', {})
            image_type = icon_data.get('1', None) if isinstance(icon_data, dict) else None
            image_bitmap_filename = icon_data.get('2', None) if isinstance(icon_data, dict) else None
            if isinstance(image_bitmap_filename, bytes):
                image_bitmap_filename = image_bitmap_filename.decode('utf-8', errors='ignore')
            image_resource_id = icon_data.get('3', None) if isinstance(icon_data, dict) else None
            image_resource_id_package = icon_data.get('4', None) if isinstance(icon_data, dict) else None
            if isinstance(image_resource_id_package, bytes):
                image_resource_id_package = image_resource_id_package.decode('utf-8', errors='ignore')
            image_data_length = icon_data.get('6', None) if isinstance(icon_data, dict) else None
            image_data_offset = icon_data.get('7', None) if isinstance(icon_data, dict) else None
            image_uri = icon_data.get('8', None) if isinstance(icon_data, dict) else None
            if isinstance(image_uri, bytes):
                image_uri = image_uri.decode('utf-8', errors='ignore')
            
            # Convert timestamp
            posted_time = None
            if posted_time_ms:
                try:
                    posted_time = convert_utc_human_to_timezone(convert_ts_int_to_utc(int(posted_time_ms/1000.0)),'UTC')
                except:
                    pass
            
            # Convert file creation time
            file_creation = None
            try:
                file_creation = convert_utc_human_to_timezone(convert_ts_int_to_utc(int(file_name)/1000.0),'UTC')
            except:
                pass
            
            data_list.append((
                f'{posted_time}', title, text, package, user_id, uid, package_index,
                channel_name, channel_name_index, channel_id, channel_id_index,
                conversation_id, conversation_id_index, major_version,
                image_type, image_bitmap_filename, image_resource_id,
                image_resource_id_package, image_data_length, image_data_offset,
                image_uri, file_name, f'{file_creation}'
            ))
    except Exception as e:
        pass  # Silently fail for blackbox parsing
    
    return data_list




def get_notificationHistory(files_found, report_folder, seeker, wrap_text):
    data_pb_list = []
    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        #parsing settings_secure.xml
        if file_name.endswith('settings_secure.xml'):
            data_list = []
            user = os.path.basename(os.path.dirname(file_found))
            if (checkabx(file_found)):
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
                else:
                    pass # setting not available

            if data_list:
                description = f'Indicates whether "Notification History" feature is enabled.'
                report = ArtifactHtmlReport('Android Notification History - Status')
                report.start_artifact_report(report_folder, 'Status',description)
                report.add_script()
                data_headers = ('Status', 'User')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Android Notification History - Status'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc('No Android Notification History - Status data available')
        
        #parsing notification_policy.xml
        if file_name.endswith('notification_policy.xml'):
            data_list = []
            if (checkabx(file_found)):
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
                                snooze_time = convert_utc_human_to_timezone(convert_ts_int_to_utc(int(notification_ts/1000.0)),'UTC')
                                notification_key = notification.attrib.get('key')
                                data_list.append((f'{snooze_time}', notification_key))
                    else:
                        pass #no snoozed notifications found    
            if data_list:
                description = f'Notifications the user chose to snooze for a specific time interval'
                report = ArtifactHtmlReport('Android Notification History - Snoozed notifications')
                report.start_artifact_report(report_folder, 'Snoozed notifications', description) #'Android Notification History - Snoozed notifications')
                report.add_script()
                data_headers = ('Reminder Time', 'Snoozed Notification')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Android Notification History - Snoozed notifications'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc('No Android Notification History - Snoozed notifications data available')

        else:
            #iterate through the notification pbs
            try:
                pb_data = None
                with open(file_found, 'rb') as f:
                    pb_data = f.read()
                
                parsed_with_schema = False
                notification_history = notificationhistory_pb2.NotificationHistoryProto()
                
                try:
                    notification_history.ParseFromString(pb_data)
                    # Check if we actually got any notifications
                    if notification_history.notification:
                        parsed_with_schema = True
                except Exception as e:
                    # Schema parsing failed, will try blackboxprotobuf
                    parsed_with_schema = False
                
                if parsed_with_schema:
                    # Use the compiled schema parser
                    package_map = {i + 1: pkg for i, pkg in enumerate(notification_history.string_pool.strings)}
                    major_version = notification_history.major_version if notification_history.HasField('major_version') else None
                    
                    for notification in notification_history.notification:
                        package_name = notification.package if notification.package else package_map.get(notification.package_index, "")
                        
                        fields = ['uid', 'user_id', 'package_index', 'channel_name', 'channel_id','channel_id_index', 'channel_name_index', 'conversation_id', 'conversation_id_index']
                        defaults = {field: 'Error' for field in fields}
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
                        file_creation = convert_utc_human_to_timezone(convert_ts_int_to_utc(int(file_name)/1000.0),'UTC')
                        data_pb_list.append((f'{posted_time}',title,text,package_name,user_id,uid,package_index,channel_name,channel_name_index,channel_id,channel_id_index,conversation_id,conversation_id_index,major_version,image_type,image_bitmap_filename,image_resource_id,image_resource_id_package,image_data_length,image_data_offset,image_uri,file_name,f'{file_creation}'))
                
                elif HAS_BLACKBOXPROTOBUF and pb_data:
                    # Fallback to blackboxprotobuf parser
                    fallback_results = parse_notification_with_blackbox(pb_data, file_name)
                    if fallback_results:
                        data_pb_list.extend(fallback_results)
                    # No log message if blackbox parsing also returns empty - just means no data
                        
            except Exception as e:
                # Only log if there's a real file error, not parsing errors
                logfunc(f'Error reading notification pb file {file_name}: {e}')

    if len(data_pb_list) > 0:
        description = f'A history of the notifications that landed on the device during the last 24h'
        report = ArtifactHtmlReport('Android Notification History - Notifications')
        report.start_artifact_report(report_folder, f'Notifications', description)
        report.add_script()
        data_headers = ('Posted Time','Title', 'Text','Package Name','User ID','UID','Package Index','Channel Name','Channel Name Index','Channel ID','Channel ID Index','Conversation ID','Conversation ID Index','Major Version','Image Type','Image Bitmap Filename','Image Resource ID','Image Resource ID Package','Image Data Length','Image Data Offset','Image URI','Protobuf File Name','Protobuf File Creation Date')#,'','','','','','','','','','','','','','')
        file_directory = os.path.dirname(file_found)  
        report.write_artifact_data_table(data_headers, data_pb_list, file_directory, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Android Notification History - Notifications'
        tsv(report_folder, data_headers, data_pb_list, tsvname)
        
        tlactivity = f'Android Notification History - Notifications'
        timeline(report_folder, tlactivity, data_pb_list, data_headers)
    else:
        logfunc(f'No Android Notification History - Notifications available')