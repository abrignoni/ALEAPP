# pylint: disable=E0606,E1101,W0311,W0613,W0702,W1309
__artifacts_v2__ = {
    "get_usagestats": {
        "name": "usagestats",
        "description": "Event types referenced from core/java/android/app/usage/UsageEvents.java",
        "author": "",
        "creation_date": "2020-02-25",
        "last_update_date": "2020-02-25",
        "requirements": "none",
        "category": "Usage Stats",
        "notes": "",
        "paths": ('*/system/usagestats/*', '*/system_ce/*/usagestats*'),
        "output_types": "standard",
        "artifact_icon": "battery",
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

    def __str__(self):
        return self.name # This returns 'KNOWN' instead of 'EventType.KNOWN'

class EventFlag(IntEnum):
    FLAG_IS_PACKAGE_INSTANT_APP = 1

    def __str__(self):
        return self.name

def get_string_by_token(packages, token1, token2=0):
    strings = packages.get(token1, None)
    if strings:
        if token2 == 0:
            return strings[0]
        if len(strings) >= token2:
            return strings[token2 - 1]
        else:
            logfunc(f'index {token2 - 1} out of range')
    else:
        pass
        # logfunc('No strings!') # This happens with deleted processes
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
        finalt = ''
        if usagestat_ob.HasField('last_time_active_ms'):
            finalt = usagestat_ob.last_time_active_ms
            if finalt < 0:
                finalt = abs(finalt)
            else:
                finalt += file_name_int
        tac = ''
        if usagestat_ob.HasField('total_time_active_ms'):
            tac = abs(usagestat_ob.total_time_active_ms)
        pkg = get_string_by_token(packages, usagestat_ob.package_token)
        alc = ''
        if usagestat_ob.HasField('app_launch_count'):
            alc = abs(usagestat_ob.app_launch_count)

        datainsert = ('packages', finalt, tac, '', '', '', alc, pkg, '' , '' , sourced, '')
        cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
                        'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
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
        datainsert = (usagetype, finalt, tac, '', '', '', '', '', '', '', sourced, fullatti_str)
        cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
                        'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
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
            tipes = str(EventType(event.type)) if event.type <= 30 else str(event.type)
        datainsert = (usagetype, finalt, '' , '' , '' , '' ,'' , pkg , tipes , classy , sourced, '')
        cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
                    'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)

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
        finalt = ''
        if usagestat.HasField('last_time_active_ms'):
            finalt = usagestat.last_time_active_ms
            if finalt < 0:
                finalt = abs(finalt)
            else:
                finalt += file_name_int
        tac = ''
        if usagestat.HasField('total_time_active_ms'):
            tac = abs(usagestat.total_time_active_ms)
        pkg = stats.stringpool.strings[usagestat.package_index - 1]
        alc = ''
        if usagestat.HasField('app_launch_count'):
            alc = abs(usagestat.app_launch_count)

        datainsert = ('packages', finalt, tac, '', '', '', alc, pkg, '' , '' , sourced, '')
        cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
                        'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
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
        datainsert = (usagetype, finalt, tac, '', '', '', '', '', '', '', sourced, fullatti_str)
        cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
                        'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
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
            pkg = stats.stringpool.strings[event.package_index - 1]
        if event.HasField('class_index'):
            classy = stats.stringpool.strings[event.class_index - 1]
        if event.HasField('type'):
            tipes = str(EventType(event.type)) if event.type <= 30 else str(event.type)
        datainsert = (usagetype, finalt, '' , '' , '' , '' ,'' , pkg , tipes , classy , sourced, '')
        cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
                    'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)

    db.commit()

@artifact_processor
def get_usagestats(files_found, report_folder, seeker, wrap_text):

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
                data_list.extend(process_usagestats(file_found, uid, report_folder, 1))
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
                data_list.extend(process_usagestats(file_found, uid, report_folder, 2))

    data_headers = ('User (UID)', ('Last Time Active', 'datetime'), 'Usage Type',
                    'Time Active in Msecs', 'Time Active in Secs',
                    ('Last Time Service Used', 'datetime'), ('Last Time Visible', 'datetime'),
                    'Total Time Visible', 'App Launch Count', 'Package', 'Types', 'Class', 'Source')
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
                                tac = (subelem.attrib['timeActive'])
                                alc = (subelem.attrib.get('appLaunchCount', ''))
                                #insert in database
                                cursor = db.cursor()
                                datainsert = (usagetype, finalt, tac, '', '', '', alc, pkg, '', '', sourced, fullatti_str,)
                                cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
                                               'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
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
                                datainsert = (usagetype, finalt, tac, '', '', '', '', '', '', '', sourced, fullatti_str,)
                                cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
                                               'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
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
                                tipes = (subelem.attrib['type'])
                                fullatti_str = json.dumps(subelem.attrib)
                                if 'class' in subelem.attrib:
                                    classy = subelem.attrib['class']
                                    cursor = db.cursor()
                                    datainsert = (usagetype, finalt, '' , '' , '' , '' ,'' , pkg , tipes , classy , sourced, fullatti_str,)
                                    cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
                                               'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
                                    db.commit()
                                else:
                                #insert in database
                                    datainsert = (usagetype, finalt, '' , '' , '', '', '', pkg , tipes , '' , sourced, fullatti_str,)
                                    cursor = db.cursor()
                                    cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
                                               'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
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

def process_usagestats(folder, uid, report_folder, version):

    # In-memory working database; the parsed rows are returned to the framework
    # for rendering as one consolidated table across all users.
    db = sqlite3.connect(':memory:')
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE data(usage_type TEXT, lastime INTEGER, timeactive INTEGER,
                          last_time_service_used INTEGER, last_time_visible INTEGER, total_time_visible INTEGER,
                          app_launch_count INTEGER,
                          package TEXT, types TEXT, classs TEXT,
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
    case last_time_visible  WHEN '' THEN ''
     ELSE datetime(last_time_visible/1000, 'UNIXEPOCH')
    end last_time_visible,
    total_time_visible,
    app_launch_count,
    package,
    CASE types
         WHEN '0' THEN 'NONE'
         WHEN '1' THEN 'ACTIVITY_RESUMED'
         WHEN '2' THEN 'ACTIVITY_PAUSED'
         WHEN '5' THEN 'CONFIGURATION_CHANGE'
         WHEN '7' THEN 'USER_INTERACTION'
         WHEN '8' THEN 'SHORTCUT_INVOCATION'
         WHEN '11' THEN 'STANDBY_BUCKET_CHANGED'
         WHEN '15' THEN 'SCREEN_INTERACTIVE'
         WHEN '16' THEN 'SCREEN_NON_INTERACTIVE'
         WHEN '17' THEN 'KEYGUARD_SHOWN'
         WHEN '18' THEN 'KEYGUARD_HIDDEN'
         WHEN '19' THEN 'FOREGROUND_SERVICE_START'
         WHEN '20' THEN 'FOREGROUND_SERVICE_STOP'
         WHEN '23' THEN 'ACTIVITY_STOPPED'
         WHEN '26' THEN 'DEVICE_SHUTDOWN'
         WHEN '27' THEN 'DEVICE_STARTUP'
         ELSE types
    END types,
    classs,
    source,
    fullatt
    from data
    order by lasttimeactive DESC
    ''')
    all_rows = cursor.fetchall()

    data_list = []
    for row in all_rows:
        data_list.append((uid, _str_to_utc(row[0]), row[1], row[2], row[3], _str_to_utc(row[4]),
                          _str_to_utc(row[5]), row[6], row[7], row[8], row[9], row[10], row[11]))

    logfunc(f'Records processed for user {uid}: {len(data_list)}')
    db.close()
    return data_list
