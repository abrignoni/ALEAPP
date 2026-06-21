# pylint: disable=W0613
__artifacts_v2__ = {
    "get_dmss": {
        "name": "Dahua CCTV - Channels",
        "description": "Available CCTV record channels from the Dahua DMSS app",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2023-04-13",
        "last_update_date": "2023-04-13",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/com.mm.android.DMSS/databases/devicechannel.db*',),
        "output_types": "standard",
        "artifact_icon": "video",
    },
    "get_dmss_info": {
        "name": "Dahua CCTV - Info",
        "description": "Information about the connected CCTV system from the Dahua DMSS app",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2023-04-13",
        "last_update_date": "2023-04-13",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/com.mm.android.DMSS/databases/devicechannel.db*',),
        "output_types": "standard",
        "artifact_icon": "video",
    },
    "get_dmss_sensors": {
        "name": "Dahua IoT - Registered Sensors",
        "description": "IoT registered sensors connected with the Dahua DMSS app (per account)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2023-04-13",
        "last_update_date": "2023-04-13",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/com.mm.android.DMSS/databases/*',),
        "output_types": "standard",
        "artifact_icon": "shield",
    },
    "get_dmss_cloud": {
        "name": "Dahua IoT - Registered Cloud Devices",
        "description": "IoT registered cloud devices connected with the Dahua DMSS app (per account)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2023-04-13",
        "last_update_date": "2023-04-13",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/com.mm.android.DMSS/databases/*',),
        "output_types": "standard",
        "artifact_icon": "cloud",
    },
    "get_dmss_notifications": {
        "name": "Dahua IoT - Notifications",
        "description": "Cached IoT smart-home notifications from the Dahua DMSS app (per account)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2023-04-13",
        "last_update_date": "2023-04-13",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/com.mm.android.DMSS/databases/*',),
        "output_types": "standard",
        "artifact_icon": "bell",
    },
    "get_dmss_media": {
        "name": "Dahua CCTV - User Created Media",
        "description": "Media files the user created while viewing CCTV footage in the Dahua DMSS app",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2023-04-13",
        "last_update_date": "2023-04-13",
        "requirements": "none",
        "category": "Dahua Technology (DMSS)",
        "notes": "",
        "paths": ('*/Android/data/com.mm.android.DMSS/files/Download/snapshot/*',),
        "output_types": "standard",
        "artifact_icon": "video",
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media

SENSORS_SQL = '''
    SELECT name, model, sn, type,
    CASE alarmState WHEN '0' THEN 'Off' WHEN '1' THEN 'On' END,
    batteryPercent, deviceSn, disableDelay, enableDelay,
    CASE fullDayAlarm WHEN '0' THEN 'Off' WHEN '1' THEN 'On' END,
    CASE sensitivity WHEN '1' THEN 'Low' WHEN '2' THEN 'Medium' WHEN '3' THEN 'High' END,
    sensorCaps, tamper, version
    FROM AlarmPartEntity
'''

CLOUD_SQL = '''
    SELECT devicename, deviceModel, channelcount, isOnline,
    CASE shareEnable WHEN '0' THEN 'Off' WHEN '1' THEN 'On' END,
    receiveShare, sendShare, username, ability, deviceCaps, port, rtspPort, appVersion
    FROM CloudDevices
'''

NOTIF_SQL = '''
    SELECT alarmTime, alarmTimeStr, areaName, nickName, sensorName, alarmDeviceId, alarmMessageId,
    CASE
        WHEN alarmTypeStr = 'gwMsg_ATSFault_Start' THEN 'ATS fault. Check network connection'
        WHEN alarmTypeStr = 'gwMsg_ATSFault_Stop' THEN 'ATS restored'
        WHEN alarmTypeStr = 'gwMsg_AreaAlarm_AddArea' THEN '"area name", added by "nickname"'
        WHEN alarmTypeStr = 'gwMsg_AreaAlarm_AreaDelete' THEN '"area name", removed by "nickname"'
        WHEN alarmTypeStr = 'gwMsg_AreaArmModeChange_Remote_DisArm' THEN '"area name", disarmed by "nickname"'
        WHEN alarmTypeStr = 'gwMsg_AreaArmModeChange_Remote_Arm_p1' THEN '"area name", Home mode activated by "nickname"'
        WHEN alarmTypeStr = 'gwMsg_ArmingFailure' THEN 'Unsuccessful arming "area name" attempt by "nickname"'
        WHEN alarmTypeStr = 'gwMsg_AlarmLocal_PassiveInfrared' THEN 'Motion detected, "device name" in "area name"'
        WHEN alarmTypeStr = 'gwMsg_AlarmLocal_DoorMagnetism_Start' THEN 'Opening detected, "device name" in "area name"'
        WHEN alarmTypeStr = 'gwMsg_AlarmLocal_DoorMagnetism_Stop' THEN 'Closing detected, "device name" in "area name"'
        ELSE alarmTypeStr
    END,
    CASE checked WHEN '1' THEN 'Yes' WHEN '0' THEN 'No' END
    FROM GeneralAlarmMessage
'''


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _run(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _find_db(files_found, db_name):
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == db_name:
            return file_found
    return ''


def _iot_dbs(files_found):
    """Yield (db_path, account_label) for the no-account .db and each per-account DB."""
    for file_found in files_found:
        file_found = str(file_found)
        name = os.path.basename(file_found)
        if name == '.db':
            yield file_found, 'Without Account'
        elif (name.startswith('ez') or len(name) > 25) and name.endswith('.db'):
            yield file_found, name[:-3]


@artifact_processor
def get_dmss(files_found, report_folder, seeker, wrap_text):
    source_path = _find_db(files_found, 'devicechannel.db')
    rows = _run(source_path, '''
        SELECT devices.devicename, num, name,
        CASE WHEN isfavorite = '1' THEN 'Yes' ELSE 'No' END
        FROM channels LEFT JOIN devices ON did = devices.id
    ''')
    data_headers = ('Device Name', 'Channel No.', 'Channel Name', 'Favorite')
    return data_headers, [tuple(r) for r in rows], source_path


@artifact_processor
def get_dmss_info(files_found, report_folder, seeker, wrap_text):
    source_path = _find_db(files_found, 'devicechannel.db')
    rows = _run(source_path, '''
        SELECT devicename, channelcount, uid, ip, port, username, password FROM devices
    ''')
    data_headers = ('Name/IP', 'Channels', 'UID', 'IP (Enc.)', 'Port (Enc.)',
                    'Username (Enc.)', 'Password (Enc.)')
    return data_headers, [tuple(r) for r in rows], source_path


@artifact_processor
def get_dmss_sensors(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for db_path, account in _iot_dbs(files_found):
        for r in _run(db_path, SENSORS_SQL):
            source_path = db_path
            data_list.append((account,) + tuple(r))
    data_headers = ('Account', 'Device Name', 'Device Model', 'Device SN', 'Device Type', 'Alarm State',
                    'Battery Percent', 'Associated Hub SN', 'Disable Delay', 'Enable Delay', 'Full Day Alarm',
                    'Sensitivity', 'Capabilities', 'Tamper Status', 'Version')
    return data_headers, data_list, source_path


@artifact_processor
def get_dmss_cloud(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for db_path, account in _iot_dbs(files_found):
        for r in _run(db_path, CLOUD_SQL):
            source_path = db_path
            data_list.append((account,) + tuple(r))
    data_headers = ('Account', 'Device Name', 'Device Model', 'Channels', 'Online', 'Shared Enabled',
                    'Receive Share From', 'Send Share To', 'Username', 'Abilities', 'Capabilities', 'Port',
                    'RTSP Port', 'App Version')
    return data_headers, data_list, source_path


@artifact_processor
def get_dmss_notifications(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for db_path, account in _iot_dbs(files_found):
        for r in _run(db_path, NOTIF_SQL):
            source_path = db_path
            data_list.append((account, _ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]))
    data_headers = ('Account', ('Timestamp', 'datetime'), 'Device Reported Time', 'Area Name', 'Nickname',
                    'Device Name', 'Alarm Device ID', 'Alarm Message ID', 'Alarm Notification', 'Checked')
    return data_headers, data_list, source_path


@artifact_processor
def get_dmss_media(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        if not file_name.endswith(('.jpg', '.mp4', '.dav')):
            continue
        if '.thumb' in file_found:
            continue
        # Intentionally skip jpg thumbnails of videos to reduce duplicate media
        if file_name.endswith('.jpg') and 'video' in file_found:
            continue
        source_path = os.path.dirname(file_found)
        media = check_in_media(file_found, file_name)
        data_list.append((file_found, file_name, media))

    data_headers = ('File Path', 'File Name', ('File Content', 'media'))
    return data_headers, data_list, source_path
