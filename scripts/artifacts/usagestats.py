# pylint: disable=E0606,E1101,W0311,W0702,W1309
__artifacts_v2__ = {
    "get_usagestats": {
        "name": "Usage Stats",
        "description": "Android application, device-state, service, notification and user-interaction events from XML and protobuf UsageStats stores.",
        "author": "Alexis Brignoni",
        "creation_date": "2020-02-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Usage Stats",
        "notes": (
            "Daily, weekly, monthly and yearly files overlap; repeated rows across those "
            "intervals are not separate user actions. ACTIVITY_RESUMED records an Android "
            "activity lifecycle transition, not proof that a person intentionally opened or "
            "viewed the app. SCREEN_INTERACTIVE does not mean unlocked. Android source: "
            "https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/"
            "core/java/android/app/usage/UsageEvents.java"
        ),
        "paths": ('*/system/usagestats/*', '*/system_ce/*/usagestats*'),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "anne_a15": "Android 15 | 15346 rows",
            "galaxys10_a10": "Android 10 | 11333 rows",
            "hc_pixel8pro_a16": "Android 16 | 6843 rows",
            "kevin_pocox7_a15": "Android 15 | 14995 rows",
            "pixel7a_a14": "Android 14 | 35075 rows",
            "samsunga53_a14": "Android 14 | 4954 rows",
            "samsungs20_a13": "Android 13 | 15053 rows",
            "sharon_a14": "Android 14 | 13398 rows",
            "russell_pixel6a_a13": "Android 13 | 23654 rows",
            "userb2_a13": "Android 13 | 3115 rows",
        },
    }
}

import datetime
import glob
import json
import os
import scripts.artifacts.usagestats_pb.usagestatsservice_pb2 as usagestatsservice_pb2
import scripts.artifacts.usagestats_pb.usagestatsservice_v2_pb2 as usagestatsservice_v2_pb2
import sqlite3
import xml.etree.ElementTree as ET

from enum import IntEnum
from scripts.ilapfuncs import artifact_processor, logfunc, is_platform_windows


def _str_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S').replace(
            tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


# Event types referenced from core\java\android\app\usage\UsageEvents.java

class EventType(IntEnum):
    NONE = 0
    ACTIVITY_RESUMED = 1  # prev MOVE_TO_FOREGROUND
    ACTIVITY_PAUSED = 2   # prev MOVE_TO_BACKGROUND
    END_OF_DAY = 3
    CONTINUE_PREVIOUS_DAY = 4
    CONFIGURATION_CHANGE = 5
    SYSTEM_INTERACTION = 6
    USER_INTERACTION = 7
    SHORTCUT_INVOCATION = 8
    CHOOSER_ACTION = 9
    NOTIFICATION_SEEN = 10
    STANDBY_BUCKET_CHANGED = 11
    NOTIFICATION_INTERRUPTION = 12
    SLICE_PINNED_PRIV = 13
    SLICE_PINNED = 14
    SCREEN_INTERACTIVE = 15
    SCREEN_NON_INTERACTIVE = 16
    KEYGUARD_SHOWN = 17
    KEYGUARD_HIDDEN = 18
    FOREGROUND_SERVICE_START = 19
    FOREGROUND_SERVICE_STOP = 20
    CONTINUING_FOREGROUND_SERVICE = 21
    ROLLOVER_FOREGROUND_SERVICE = 22
    ACTIVITY_STOPPED = 23
    ACTIVITY_DESTROYED = 24
    FLUSH_TO_DISK = 25
    DEVICE_SHUTDOWN = 26
    DEVICE_STARTUP = 27
    USER_UNLOCKED = 28
    USER_STOPPED = 29
    LOCUS_ID_SET = 30
    APP_COMPONENT_USED = 31

    def __str__(self):
        return self.name # This returns 'KNOWN' instead of 'EventType.KNOWN'

class EventFlag(IntEnum):
    FLAG_IS_PACKAGE_INSTANT_APP = 1

    def __str__(self):
        return self.name


DATA_COLUMNS = (
    'usage_type', 'lastime', 'timeactive', 'last_time_service_used',
    'total_time_service_used', 'last_time_visible', 'total_time_visible',
    'last_time_component_used', 'app_launch_count', 'package', 'types', 'classs',
    'event_flags', 'shortcut_id', 'standby_bucket', 'standby_reason',
    'notification_channel', 'instance_id', 'task_root_package', 'task_root_class',
    'locus_id', 'interaction_category', 'interaction_action', 'source', 'fullatt'
)


def _insert_data(cursor, **values):
    placeholders = ','.join('?' for _ in DATA_COLUMNS)
    cursor.execute(
        f"INSERT INTO data ({','.join(DATA_COLUMNS)}) VALUES ({placeholders})",
        tuple(values.get(column, '') for column in DATA_COLUMNS)
    )


def _event_type_name(value):
    try:
        return EventType(int(value)).name
    except (ValueError, TypeError):
        return str(value) if value not in (None, '') else ''


def _event_flag_name(value):
    if value in (None, ''):
        return ''
    try:
        numeric = int(value)
    except (ValueError, TypeError):
        return str(value)
    if numeric == EventFlag.FLAG_IS_PACKAGE_INSTANT_APP:
        return EventFlag.FLAG_IS_PACKAGE_INSTANT_APP.name
    return str(numeric)


def _interval_time(value, interval_begin):
    """Convert a stored interval offset (or legacy negative absolute value) to epoch ms."""
    if value in (None, ''):
        return ''
    numeric = int(value)
    return abs(numeric) if numeric < 0 else interval_begin + numeric


def _duration(value):
    if value in (None, ''):
        return ''
    return abs(int(value))


def _field(message, name):
    return getattr(message, name) if message.HasField(name) else ''


def _pool_string(strings, index):
    """Resolve Android's one-based string-pool index without raising on bad evidence."""
    if not index:
        return ''
    offset = int(index) - 1
    return strings[offset] if 0 <= offset < len(strings) else ''


def _standby_parts(value):
    if value in (None, ''):
        return '', ''
    numeric = int(value)
    return (numeric & 0xFFFF0000) >> 16, numeric & 0x0000FFFF

def get_string_by_token(packages, token1, token2=0):
    strings = packages.get(token1, None)
    if not strings:
        # This happens with deleted processes.
        return ''
    # Optional event token fields are represented by an empty string in the
    # shared field helper. They are not package-name token 0.
    if token2 in (None, ''):
        return ''
    try:
        token2 = int(token2)
    except (TypeError, ValueError):
        return ''
    if token2 == 0:
        return strings[0]
    if len(strings) >= token2:
        return strings[token2 - 1]
    logfunc(f'index {token2 - 1} out of range')
    return ''

def ReadUsageStatsV2PbFile(input_path):
    '''Opens file, reads usagestats protobuf and returns IntervalStatsObfuscatedProto object'''
    stats_ob = usagestatsservice_v2_pb2.IntervalStatsObfuscatedProto()

    with open (input_path, 'rb') as f:
        stats_ob.ParseFromString(f.read())
        return stats_ob

def AddV2EntriesToDb(sourced, file_name_int, stats_ob, db, packages):
    cursor = db.cursor()
    # packages
    for usagestat_ob in stats_ob.packages:
        pkg = get_string_by_token(packages, usagestat_ob.package_token)
        _insert_data(
            cursor,
            usage_type='packages',
            lastime=_interval_time(_field(usagestat_ob, 'last_time_active_ms'), file_name_int),
            timeactive=_duration(_field(usagestat_ob, 'total_time_active_ms')),
            last_time_service_used=_interval_time(
                _field(usagestat_ob, 'last_time_service_used_ms'), file_name_int),
            total_time_service_used=_duration(
                _field(usagestat_ob, 'total_time_service_used_ms')),
            last_time_visible=_interval_time(
                _field(usagestat_ob, 'last_time_visible_ms'), file_name_int),
            total_time_visible=_duration(_field(usagestat_ob, 'total_time_visible_ms')),
            last_time_component_used=_interval_time(
                _field(usagestat_ob, 'last_time_component_used_ms'), file_name_int),
            app_launch_count=_duration(_field(usagestat_ob, 'app_launch_count')),
            package=pkg,
            source=sourced,
        )
    #configurations
    for conf in stats_ob.configurations:
        usagetype = 'configurations'
        finalt = ''
        if conf.HasField('last_time_active_ms'):
            finalt = conf.last_time_active_ms
            if finalt < 0:
                finalt = abs(finalt)
            else:
                finalt += file_name_int
        tac = ''
        if conf.HasField('total_time_active_ms'):
            tac = abs(conf.total_time_active_ms)
        fullatti_str = str(conf.config)
        _insert_data(cursor, usage_type=usagetype, lastime=finalt, timeactive=tac,
                     source=sourced, fullatt=fullatti_str)
    #event-log
    usagetype = 'event-log'
    for event in stats_ob.event_log:
        pkg = ''
        classy = ''
        tipes = ''
        finalt = ''
        if event.HasField('time_ms'):
            finalt = event.time_ms
            if finalt < 0:
                finalt = abs(finalt)
            else:
                finalt += file_name_int
        if event.HasField('package_token'):
            pkg = get_string_by_token(packages, event.package_token)
        if event.HasField('class_token'):
            classy = get_string_by_token(packages, event.package_token, event.class_token)
        if event.HasField('type'):
            tipes = _event_type_name(event.type)
        event_package_token = _field(event, 'package_token')
        task_root_package_token = _field(event, 'task_root_package_token')
        standby_bucket, standby_reason = _standby_parts(_field(event, 'standby_bucket'))
        interaction_category = ''
        interaction_action = ''
        if event.HasField('interaction_extras'):
            interaction_category = get_string_by_token(
                packages, event_package_token,
                _field(event.interaction_extras, 'category_token'))
            interaction_action = get_string_by_token(
                packages, event_package_token,
                _field(event.interaction_extras, 'action_token'))
        _insert_data(
            cursor,
            usage_type=usagetype,
            lastime=finalt,
            package=pkg,
            types=tipes,
            classs=classy,
            event_flags=_event_flag_name(_field(event, 'flags')),
            shortcut_id=get_string_by_token(
                packages, event_package_token, _field(event, 'shortcut_id_token')),
            standby_bucket=standby_bucket,
            standby_reason=standby_reason,
            notification_channel=get_string_by_token(
                packages, event_package_token, _field(event, 'notification_channel_id_token')),
            instance_id=_field(event, 'instance_id'),
            task_root_package=get_string_by_token(packages, task_root_package_token),
            task_root_class=get_string_by_token(
                packages, task_root_package_token, _field(event, 'task_root_class_token')),
            locus_id=get_string_by_token(
                packages, event_package_token, _field(event, 'locus_id_token')),
            interaction_category=interaction_category,
            interaction_action=interaction_action,
            source=sourced,
        )

    db.commit()

def ReadUsageStatsPbFile(input_path):
    '''Opens file, reads usagestats protobuf and returns IntervalStatsProto object'''
    stats = usagestatsservice_pb2.IntervalStatsProto()

    with open (input_path, 'rb') as f:
        stats.ParseFromString(f.read())
        return stats

def AddEntriesToDb(sourced, file_name_int, stats, db):
    cursor = db.cursor()
    # packages
    for usagestat in stats.packages:
        pkg = (_pool_string(stats.stringpool.strings, usagestat.package_index)
               if usagestat.HasField('package_index') else _field(usagestat, 'package'))
        _insert_data(
            cursor,
            usage_type='packages',
            lastime=_interval_time(_field(usagestat, 'last_time_active_ms'), file_name_int),
            timeactive=_duration(_field(usagestat, 'total_time_active_ms')),
            last_time_service_used=_interval_time(
                _field(usagestat, 'last_time_service_used_ms'), file_name_int),
            total_time_service_used=_duration(
                _field(usagestat, 'total_time_service_used_ms')),
            last_time_visible=_interval_time(
                _field(usagestat, 'last_time_visible_ms'), file_name_int),
            total_time_visible=_duration(_field(usagestat, 'total_time_visible_ms')),
            last_time_component_used=_interval_time(
                _field(usagestat, 'last_time_component_used_ms'), file_name_int),
            app_launch_count=_duration(_field(usagestat, 'app_launch_count')),
            package=pkg,
            source=sourced,
        )
    #configurations
    for conf in stats.configurations:
        usagetype = 'configurations'
        finalt = ''
        if conf.HasField('last_time_active_ms'):
            finalt = conf.last_time_active_ms
            if finalt < 0:
                finalt = abs(finalt)
            else:
                finalt += file_name_int
        tac = ''
        if conf.HasField('total_time_active_ms'):
            tac = abs(conf.total_time_active_ms)
        fullatti_str = str(conf.config)
        _insert_data(cursor, usage_type=usagetype, lastime=finalt, timeactive=tac,
                     source=sourced, fullatt=fullatti_str)
    #event-log
    usagetype = 'event-log'
    for event in stats.event_log:
        pkg = ''
        classy = ''
        tipes = ''
        finalt = ''
        if event.HasField('time_ms'):
            finalt = event.time_ms
            if finalt < 0:
                finalt = abs(finalt)
            else:
                finalt += file_name_int
        if event.HasField('package_index'):
            pkg = _pool_string(stats.stringpool.strings, event.package_index)
        elif event.HasField('package'):
            pkg = event.package
        if event.HasField('class_index'):
            classy = _pool_string(stats.stringpool.strings, event.class_index)
        elif event.HasField('class'):
            classy = getattr(event, 'class')
        if event.HasField('type'):
            tipes = _event_type_name(event.type)
        standby_bucket, standby_reason = _standby_parts(_field(event, 'standby_bucket'))
        notification_channel = _field(event, 'notification_channel')
        if not notification_channel and event.HasField('notification_channel_index'):
            notification_channel = _pool_string(
                stats.stringpool.strings, event.notification_channel_index)
        _insert_data(
            cursor,
            usage_type=usagetype,
            lastime=finalt,
            package=pkg,
            types=tipes,
            classs=classy,
            event_flags=_event_flag_name(_field(event, 'flags')),
            shortcut_id=_field(event, 'shortcut_id'),
            standby_bucket=standby_bucket,
            standby_reason=standby_reason,
            notification_channel=notification_channel,
            instance_id=_field(event, 'instance_id'),
            task_root_package=_pool_string(
                stats.stringpool.strings, _field(event, 'task_root_package_index')),
            task_root_class=_pool_string(
                stats.stringpool.strings, _field(event, 'task_root_class_index')),
            locus_id=_pool_string(stats.stringpool.strings, _field(event, 'locus_id_index')),
            source=sourced,
        )

    db.commit()

@artifact_processor
def get_usagestats(context):
    files_found = context.get_files_found()

    logfunc('Android Usagestats XML & Protobuf Parser')

    slash = '\\' if is_platform_windows() else '/'

    uids_processed = set()
    data_list = []
    source = ''

    for file_found in files_found:
        file_found = str(file_found)
        parts = file_found.split(slash)
        if os.path.isdir(file_found): # filter for directory only.
            # Target = .../system/usagestats/0  <-- Android <= 10
            # Target = .../system_ce/0/usagestats  <-- Android = 11
            if len(parts) > 2 and parts[-2] == 'usagestats' and parts[-3] == 'system':
                uid = parts[-1]
                try:
                    int(uid)
                except ValueError:
                    continue # uid was not a number
                # Skip /sbin/.magisk/mirror/data/system/usagestats/0/ , it should be duplicate data??
                if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
                    continue
                source = source or file_found
                data_list.extend(process_usagestats(file_found, uid, 1))
            elif len(parts) > 3 and parts[-1] == 'usagestats' and parts[-3] == 'system_ce':
                uid = parts[-2]
                try:
                    uid_int = int(uid)
                except ValueError:
                    continue # uid was not a number
                if uid_int in uids_processed:
                    continue
                uids_processed.add(uid_int)
                # Skip /sbin/.magisk/mirror/data/system/usagestats/0/ , it should be duplicate data??
                if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
                    continue
                source = source or file_found
                data_list.extend(process_usagestats(file_found, uid, 2))

    data_headers = (
        'User (UID)', ('Timestamp / Last Time Active', 'datetime'), 'Usage Type',
        'Time Active (ms)', 'Time Active (sec)',
        ('Last Time Service Used', 'datetime'), 'Total Time Service Used (ms)',
        ('Last Time Visible', 'datetime'), 'Total Time Visible (ms)',
        ('Last Time Component Used', 'datetime'), 'App Launch Count', 'Package',
        'Event Type', 'Class', 'Event Flags', 'Shortcut ID', 'Standby Bucket',
        'Standby Reason', 'Notification Channel', 'Instance ID', 'Task Root Package',
        'Task Root Class', 'Locus ID', 'Interaction Category', 'Interaction Action',
        'Interval'
    )
    return data_headers, data_list, source

def add_xml_or_v1_usagestats_to_db(folder, db):
    '''Process usagestats xml files or version 1 of protobuf files'''
    err=0
    ferr = 0
    stats = None

    for filename in glob.iglob(os.path.join(folder, '**'), recursive=True):
        if os.path.isfile(filename): # filter dirs
            file_name = os.path.basename(filename)
            #Test if xml is well formed
            if file_name == 'version':
                continue
            else:
                if 'daily' in filename:
                    sourced = 'daily'
                elif 'weekly' in filename:
                    sourced = 'weekly'
                elif 'monthly' in filename:
                    sourced = 'monthly'
                elif 'yearly' in filename:
                    sourced = 'yearly'

                try:
                    file_name_int = int(file_name)
                except:
                    logfunc('Invalid filename: ')
                    logfunc(filename)
                    logfunc('')
                    err = 1
                    ferr = 1

                try:
                    ET.parse(filename)
                except ET.ParseError:
                    # Perhaps an Android Q protobuf file
                    try:
                        stats = ReadUsageStatsPbFile(filename)
                        err = 0
                    except:
                        logfunc('Parse error - Non XML and Non Protobuf file? at: ')
                        logfunc(filename)
                        logfunc('')
                        err = 1
                    if stats:
                        if ferr == 1:
                          ferr = 0
                          continue
                        else:
                          AddEntriesToDb(sourced, file_name_int, stats, db)
                          continue

                if err == 1:
                    err = 0
                    continue
                else:
                    tree = ET.parse(filename)
                    root = tree.getroot()
                    for elem in root:
                        usagetype = elem.tag
                        if usagetype == 'packages':
                            for subelem in elem:
                                fullatti_str = json.dumps(subelem.attrib)
                                time1 = subelem.attrib['lastTimeActive']
                                time1 = int(time1)
                                if time1 < 0:
                                    finalt = abs(time1)
                                else:
                                    finalt = file_name_int + time1
                                pkg = (subelem.attrib['package'])
                                tac = subelem.attrib['timeActive']
                                cursor = db.cursor()
                                _insert_data(
                                    cursor,
                                    usage_type=usagetype,
                                    lastime=finalt,
                                    timeactive=tac,
                                    last_time_service_used=_interval_time(
                                        subelem.attrib.get('lastTimeServiceUsed', ''), file_name_int),
                                    total_time_service_used=_duration(
                                        subelem.attrib.get('totalTimeServiceUsed', '')),
                                    last_time_visible=_interval_time(
                                        subelem.attrib.get('lastTimeVisible', ''), file_name_int),
                                    total_time_visible=_duration(
                                        subelem.attrib.get('totalTimeVisible', '')),
                                    last_time_component_used=_interval_time(
                                        subelem.attrib.get('lastTimeComponentUsed', ''), file_name_int),
                                    app_launch_count=subelem.attrib.get('appLaunchCount', ''),
                                    package=pkg,
                                    source=sourced,
                                    fullatt=fullatti_str,
                                )
                                db.commit()

                        elif usagetype == 'configurations':
                            for subelem in elem:
                                fullatti_str = json.dumps(subelem.attrib)
                                time1 = subelem.attrib['lastTimeActive']
                                time1 = int(time1)
                                if time1 < 0:
                                    finalt = abs(time1)
                                else:
                                    finalt = file_name_int + time1
                                tac = (subelem.attrib['timeActive'])
                                #insert in database
                                cursor = db.cursor()
                                _insert_data(cursor, usage_type=usagetype, lastime=finalt,
                                             timeactive=tac, source=sourced, fullatt=fullatti_str)
                                db.commit()

                        elif usagetype == 'event-log':
                            for subelem in elem:
                                time1 = subelem.attrib['time']
                                time1 = int(time1)
                                if time1 < 0:
                                    finalt = abs(time1)
                                else:
                                    finalt = file_name_int + time1
                                pkg = (subelem.attrib['package'])
                                tipes = _event_type_name(subelem.attrib['type'])
                                fullatti_str = json.dumps(subelem.attrib)
                                standby_bucket, standby_reason = _standby_parts(
                                    subelem.attrib.get('standbyBucket', ''))
                                cursor = db.cursor()
                                _insert_data(
                                    cursor,
                                    usage_type=usagetype,
                                    lastime=finalt,
                                    package=pkg,
                                    types=tipes,
                                    classs=subelem.attrib.get('class', ''),
                                    event_flags=_event_flag_name(subelem.attrib.get('flags', '')),
                                    shortcut_id=subelem.attrib.get('shortcutId', ''),
                                    standby_bucket=standby_bucket,
                                    standby_reason=standby_reason,
                                    notification_channel=subelem.attrib.get(
                                        'notificationChannel', ''),
                                    instance_id=subelem.attrib.get('instanceId', ''),
                                    task_root_package=subelem.attrib.get('taskRootPackage', ''),
                                    task_root_class=subelem.attrib.get('taskRootClass', ''),
                                    locus_id=subelem.attrib.get('locusId', ''),
                                    interaction_category=subelem.attrib.get(
                                        'interactionCategory', subelem.attrib.get('category', '')),
                                    interaction_action=subelem.attrib.get(
                                        'interactionAction', subelem.attrib.get('action', '')),
                                    source=sourced,
                                    fullatt=fullatti_str,
                                )
                                db.commit()

def add_v2_usagestats_to_db(folder, db):
    '''Process usagestats version 2 protobuf files'''
    mappings_path = os.path.join(folder, 'mappings')
    mappings = usagestatsservice_v2_pb2.ObfuscatedPackagesProto()
    packages = {} # { token: (string, string, ..), .. }

    with open (mappings_path, 'rb') as f:
        mappings.ParseFromString(f.read())
        for package in mappings.packages_map:
            if package.HasField('package_token'):
                packages[package.package_token] = package.strings
            else:
                logfunc('No package_token, mapping may be problematic!')

    for filepath in glob.iglob(os.path.join(folder, '**'), recursive=True):
        if os.path.isfile(filepath): # filter dirs
            file_name = os.path.basename(filepath)
            if file_name in ('version', 'migrated', 'mappings'):
                continue

            if 'daily' in filepath:
                sourced = 'daily'
            elif 'weekly' in filepath:
                sourced = 'weekly'
            elif 'monthly' in filepath:
                sourced = 'monthly'
            elif 'yearly' in filepath:
                sourced = 'yearly'

            try:
                file_name_int = int(file_name)
            except:
                logfunc('Invalid filename at {filename}')
                continue

            # An Android R protobuf file
            try:
                stats_ob = ReadUsageStatsV2PbFile(filepath)
                AddV2EntriesToDb(sourced, file_name_int, stats_ob, db, packages)
            except:
                logfunc(f'Parse error - Error parsing Protobuf file: {filepath}')

def process_usagestats(folder, uid, version):

    # In-memory working database; the parsed rows are returned to the framework
    # for rendering as one consolidated table across all users.
    db = sqlite3.connect(':memory:')
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE data(usage_type TEXT, lastime INTEGER, timeactive INTEGER,
                          last_time_service_used INTEGER, total_time_service_used INTEGER,
                          last_time_visible INTEGER, total_time_visible INTEGER,
                          last_time_component_used INTEGER, app_launch_count INTEGER,
                          package TEXT, types TEXT, classs TEXT, event_flags TEXT,
                          shortcut_id TEXT, standby_bucket INTEGER, standby_reason INTEGER,
                          notification_channel TEXT, instance_id INTEGER,
                          task_root_package TEXT, task_root_class TEXT, locus_id TEXT,
                          interaction_category TEXT, interaction_action TEXT,
                          source TEXT, fullatt TEXT)
    ''')

    db.commit()

    if version == 1:
        add_xml_or_v1_usagestats_to_db(folder, db)
    else:
        add_v2_usagestats_to_db(folder, db)

    #query for reporting
    # Types mentioned here: UsageEvents.Event in platform_frameworks_base\api\current.txt
    cursor.execute('''
    select
    case lastime WHEN '' THEN ''
     ELSE datetime(lastime/1000, 'UNIXEPOCH')
    end as lasttimeactive,
    usage_type,
    timeactive as time_Active_in_msecs,
    timeactive/1000 as timeactive_in_secs,
    case last_time_service_used  WHEN '' THEN ''
     ELSE datetime(last_time_service_used/1000, 'UNIXEPOCH')
    end last_time_service_used,
    total_time_service_used,
    case last_time_visible  WHEN '' THEN ''
     ELSE datetime(last_time_visible/1000, 'UNIXEPOCH')
    end last_time_visible,
    total_time_visible,
    case last_time_component_used WHEN '' THEN ''
     ELSE datetime(last_time_component_used/1000, 'UNIXEPOCH')
    end last_time_component_used,
    app_launch_count,
    package,
    types,
    classs,
    event_flags,
    shortcut_id,
    standby_bucket,
    standby_reason,
    notification_channel,
    instance_id,
    task_root_package,
    task_root_class,
    locus_id,
    interaction_category,
    interaction_action,
    source,
    fullatt
    from data
    order by lasttimeactive DESC
    ''')
    all_rows = cursor.fetchall()

    data_list = []
    for row in all_rows:
        data_list.append((
            uid, _str_to_utc(row[0]), row[1], row[2], row[3], _str_to_utc(row[4]),
            row[5], _str_to_utc(row[6]), row[7], _str_to_utc(row[8]), row[9], row[10],
            row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18],
            row[19], row[20], row[21], row[22], row[23], row[24]
        ))

    logfunc(f'Records processed for user {uid}: {len(data_list)}')
    db.close()
    return data_list
