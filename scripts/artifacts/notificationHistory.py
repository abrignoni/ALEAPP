# pylint: disable=E1101,W0613,W0718
__artifacts_v2__ = {
    "get_notificationHistory": {
        "name": "Android Notification History",
        "description": "A history of the notifications that landed on the device during the last 24h "
                       "(system_ce notification_history protobufs). Based on a research project.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-02",
        "last_update_date": "2024-07-02",
        "requirements": "",
        "category": "Android Notification History",
        "notes": "",
        "paths": ('**/system_ce/*/notification_history/history/*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "anne_a15": "Android 15 | 286 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 44 rows",
        },
    },
    "get_notificationHistory_status": {
        "name": "Android Notification History - Status",
        "description": 'Indicates whether the "Notification History" feature is enabled (settings_secure.xml).',
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-02",
        "last_update_date": "2024-07-02",
        "requirements": "",
        "category": "Android Notification History",
        "notes": "",
        "paths": ('**/system/users/*/settings_secure.xml',),
        "output_types": "standard",
        "artifact_icon": "toggle-right",
        "sample_data": {
            "anne_a15": "Android 15 | 1 row",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel7a_a14": "Android 14 | 1 row",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
        },
    },
    "get_notificationHistory_snoozed": {
        "name": "Android Notification History - Snoozed",
        "description": "Notifications the user chose to snooze for a specific time interval (notification_policy.xml).",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-02",
        "last_update_date": "2024-07-02",
        "requirements": "",
        "category": "Android Notification History",
        "notes": "",
        "paths": ('**/system/notification_policy.xml',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
        },
    }
}

import datetime
import os
import re
import xml.etree.ElementTree as ET

import scripts.artifacts.notification_history_pb.notificationhistory_pb2 as notificationhistory_pb2
from scripts.ilapfuncs import artifact_processor, logfunc, abxread, checkabx


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _parse_xml(file_found):
    '''Parse XML, recovering from invalid tokens (stray control chars / bare &).'''
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
        text = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)', '&amp;', text)
        try:
            return ET.fromstring(text)
        except ET.ParseError:
            return ET.Element('empty')


def _xml_root(file_found, multi_root):
    '''Return the XML root for either an ABX-encoded or plain-text XML file.'''
    if checkabx(file_found):
        return abxread(file_found, multi_root).getroot()
    return _parse_xml(file_found)


@artifact_processor
def get_notificationHistory_status(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found).endswith('settings_secure.xml'):
            continue
        source_path = file_found
        user = os.path.basename(os.path.dirname(file_found))
        root = _xml_root(file_found, True)
        for setting in root.findall(".//setting"):
            if setting.attrib.get('name') == 'notification_history_enabled':
                value = setting.attrib.get('value')
                value = "Enabled" if value == "1" else "Disabled" if value == "0" else "Unknown"
                data_list.append((value, user))

    data_headers = ('Status', 'User')
    return data_headers, data_list, source_path


@artifact_processor
def get_notificationHistory_snoozed(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found).endswith('notification_policy.xml'):
            continue
        source_path = file_found
        root = _xml_root(file_found, False)
        for elem in root:
            if elem.tag == 'snoozed-notifications':
                for notification in elem:
                    if notification.tag == 'notification':
                        data_list.append((_ms_to_utc(notification.attrib.get('time')),
                                          notification.attrib.get('key')))

    data_headers = (('Reminder Time', 'datetime'), 'Snoozed Notification')
    return data_headers, data_list, source_path


@artifact_processor
def get_notificationHistory(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    fields = ['uid', 'user_id', 'package_index', 'channel_name', 'channel_id',
              'channel_id_index', 'channel_name_index', 'conversation_id', 'conversation_id_index']
    icon_fields = ['image_type', 'image_bitmap_filename', 'image_resource_id', 'image_resource_id_package',
                   'image_data_length', 'image_data_offset', 'image_uri']

    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        source_path = os.path.dirname(file_found)
        try:
            notification_history = notificationhistory_pb2.NotificationHistoryProto()
            with open(file_found, 'rb') as f:
                try:
                    notification_history.ParseFromString(f.read())
                except Exception as e:
                    logfunc(f'Error in the ParseFromString() function. The error message was: {e}')
                    continue

            # One of the protobuf sections stores package names indexed from 1
            package_map = {i + 1: pkg for i, pkg in enumerate(notification_history.string_pool.strings)}
            major_version = notification_history.major_version if notification_history.HasField('major_version') else None
            file_creation = _ms_to_utc(file_name)

            for notification in notification_history.notification:
                package_name = notification.package if notification.package \
                    else package_map.get(notification.package_index, "")

                # Recover each field if present in the schema, else mark 'Error'
                values = {}
                for field in fields:
                    try:
                        values[field] = getattr(notification, field)
                    except AttributeError:
                        values[field] = 'Error'
                if notification.HasField('icon'):
                    for icon_field in icon_fields:
                        values[icon_field] = getattr(notification.icon, icon_field)
                else:
                    for icon_field in icon_fields:
                        values[icon_field] = None

                posted_time = _ms_to_utc(notification.posted_time_ms) if notification.HasField('posted_time_ms') else ''
                title = notification.title if notification.HasField('title') else None
                text = notification.text if notification.HasField('text') else None

                data_list.append((
                    posted_time, title, text, package_name, values['user_id'], values['uid'],
                    values['package_index'], values['channel_name'], values['channel_name_index'],
                    values['channel_id'], values['channel_id_index'], values['conversation_id'],
                    values['conversation_id_index'], major_version, values['image_type'],
                    values['image_bitmap_filename'], values['image_resource_id'],
                    values['image_resource_id_package'], values['image_data_length'],
                    values['image_data_offset'], values['image_uri'], file_name, file_creation))
        except Exception as e:
            logfunc(f'Error while opening notification pb files. The error message was: "{e}"')

    data_headers = (
        ('Posted Time', 'datetime'), 'Title', 'Text', 'Package Name', 'User ID', 'UID', 'Package Index',
        'Channel Name', 'Channel Name Index', 'Channel ID', 'Channel ID Index', 'Conversation ID',
        'Conversation ID Index', 'Major Version', 'Image Type', 'Image Bitmap Filename', 'Image Resource ID',
        'Image Resource ID Package', 'Image Data Length', 'Image Data Offset', 'Image URI',
        'Protobuf File Name', ('Protobuf File Creation Date', 'datetime'))
    return data_headers, data_list, source_path
