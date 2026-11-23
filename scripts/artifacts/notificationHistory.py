# pylint: disable=E1101,W0718
__artifacts_v2__ = {
    "get_notificationHistory": {
        "name": "Android Notification History",
        "description": "Notifications recorded in the system_ce notification_history protobufs.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-02",
        "last_update_date": "2026-11-22",
        "requirements": "",
        "category": "Android Notification History",
        "notes": "Coverage is limited to the protobuf files still present under "
                 "notification_history/history at the time of extraction, which is not the "
                 "device's full notification history. In AOSP at the android-14.0.0_r1 tag, "
                 "NotificationHistoryDatabase.prune() deletes history files whose file name "
                 "time is at or before a boundary HISTORY_RETENTION_DAYS (1) day back "
                 "(https://android.googlesource.com/platform/frameworks/base/+/"
                 "299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/services/core/java/com/android/server/"
                 "notification/NotificationHistoryDatabase.java#56 "
                 "and lines 229 to 256 of the same file). Other Android releases and vendor builds were not checked. The four Index columns are blank when the record holds no string pool index: the AOSP writer stores an index only for a string in the pool, as its position plus one (https://android.googlesource.com/platform/frameworks/base/+/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/services/core/java/com/android/server/notification/NotificationHistoryProtoHelper.java#257). On anne_a15 and sharon_a14 (330 rows) no record holds an index, so a filled Index column is not exercised on real data. Where a record holds no string of its own for Package Name, Channel Name, Channel ID or Conversation ID, the value is looked up in the file's string pool by the record's index. An index with no entry in the pool leaves the value blank and the Index column filled. That path was run only on a constructed file. Image Data Length and Image Data Offset are blank unless the icon is a data icon (Image Type 3) or the record holds the field, and Image Resource ID is blank unless the icon is a resource icon (Image Type 2) or the record holds the field. The AOSP writer stores them only for those types (writeIcon, line 227 of the same file; type numbers at https://android.googlesource.com/platform/frameworks/base/+/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/graphics/java/android/graphics/drawable/Icon.java#85). Every tested row is Image Type 2, so the other types are not exercised. UID, User ID and Image Type are shown as read. The AOSP writer's ProtoOutputStream does not write a zero (https://android.googlesource.com/platform/frameworks/base/+/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/util/proto/ProtoOutputStream.java#1061) and that writer passes UID and User ID on each record, so with that writer a 0 in UID or User ID is the value 0 with nothing written to the file. User ID is 0 and absent from the file on all 330 tested rows. Image Type is blank when the record holds no icon.",
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
        "description": 'Reports the notification_history_enabled value found in each user\'s '
                       'settings_secure.xml.',
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-02",
        "last_update_date": "2024-07-02",
        "requirements": "",
        "category": "Android Notification History",
        "notes": "A stored 1 is shown as Enabled, 0 as Disabled and any other "
                 "value as Unknown. No row is produced when the "
                 "notification_history_enabled key is absent, which is not by "
                 "itself evidence the feature was off.",
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
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "userb2_a13": "Android 13 | 1 row",
        },
    },
    "get_notificationHistory_snoozed": {
        "name": "Android Notification History - Snoozed",
        "description": "The child elements of snoozed-notifications in "
                       "notification_policy.xml, with the stored key and time.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-02",
        "last_update_date": "2026-10-09",
        "requirements": "",
        "category": "Android Notification History",
        "notes": "Reminder Time is the element's time attribute read as Unix "
                 "milliseconds and Snoozed Notification is its key attribute. "
                 "In AOSP at the android-14.0.0_r1 tag, SnoozeHelper.writeXml "
                 "writes the time attribute only when the value is not before "
                 "the time of writing, and also writes context elements "
                 "there "
                 "(https://android.googlesource.com/platform/frameworks/base/+/"
                 "299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/services/core/java/com/android/server/"
                 "notification/SnoozeHelper.java#464). "
                 "Other Android releases and vendor builds were not checked. "
                 "One row is reported per child element, whatever its tag. Element "
                 "is the tag as stored, Reminder Time is blank where the element has "
                 "no time attribute, and Other Attributes lists every remaining "
                 "attribute as name=value as stored; the meaning of the attributes "
                 "of a context element is not established here. No recorded sample "
                 "held a child element, so the context rows are not exercised on "
                 "real data.",
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
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
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
def get_notificationHistory_status(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found).endswith('settings_secure.xml'):
            continue
        source_paths.append(file_found)
        user = os.path.basename(os.path.dirname(file_found))
        root = _xml_root(file_found, True)
        for setting in root.findall(".//setting"):
            if setting.attrib.get('name') == 'notification_history_enabled':
                value = setting.attrib.get('value')
                value = "Enabled" if value == "1" else "Disabled" if value == "0" else "Unknown"
                data_list.append((value, user))

    data_headers = ('Status', 'User')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_notificationHistory_snoozed(context):
    files_found = context.get_files_found()
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
                for child in elem:
                    other = '; '.join(f'{name}={value}' for name, value in child.attrib.items()
                                      if name not in ('time', 'key'))
                    data_list.append((_ms_to_utc(child.attrib.get('time')),
                                      child.attrib.get('key'), child.tag, other))

    data_headers = (('Reminder Time', 'datetime'), 'Snoozed Notification', 'Element',
                    'Other Attributes')
    return data_headers, data_list, source_path


ICON_TYPE_RESOURCE = 2
ICON_TYPE_DATA = 3


@artifact_processor
def get_notificationHistory(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    fields = ['uid', 'user_id', 'package_index', 'channel_name', 'channel_id',
              'channel_id_index', 'channel_name_index', 'conversation_id', 'conversation_id_index']
    icon_fields = ['image_type', 'image_bitmap_filename', 'image_resource_id', 'image_resource_id_package',
                   'image_data_length', 'image_data_offset', 'image_uri']

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            # The glob also returns the enclosing history directory on some
            # extractions; only the per-notification files are protobufs.
            continue
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

            # The string pool holds package, channel and conversation strings, indexed from 1. The AOSP reader
            # also appends each inline string to its pool as it reads. The AOSP writer's indexes all point into
            # the written pool, so that step is not needed for its files and is not repeated here.
            string_pool = {i + 1: text for i, text in enumerate(notification_history.string_pool.strings)}
            major_version = notification_history.major_version if notification_history.HasField('major_version') else None
            file_creation = _ms_to_utc(file_name)

            for notification in notification_history.notification:
                package_name = notification.package if notification.package \
                    else string_pool.get(notification.package_index, "")

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

                for text, index in (('channel_name', 'channel_name_index'), ('channel_id', 'channel_id_index'),
                                    ('conversation_id', 'conversation_id_index')):
                    if not values[text]:
                        values[text] = string_pool.get(values[index], '')

                # The writer stores an index only for a pooled string, and these icon fields only for their
                # own icon type. An unset field there reads as 0, which is not a stored value. A value the
                # record does hold is always shown, and a 0 on the field's own icon type is kept.
                for field in ('package_index', 'channel_name_index', 'channel_id_index', 'conversation_id_index'):
                    if not notification.HasField(field):
                        values[field] = None
                if notification.HasField('icon'):
                    for field, icon_type in (('image_data_length', ICON_TYPE_DATA), ('image_data_offset', ICON_TYPE_DATA),
                                             ('image_resource_id', ICON_TYPE_RESOURCE)):
                        if values['image_type'] != icon_type and not notification.icon.HasField(field):
                            values[field] = None

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
        'Protobuf File Name', ('Timestamp From Protobuf File Name', 'datetime'))
    return data_headers, data_list, source_path
