# pylint: disable=W0613
__artifacts_v2__ = {
    "get_hikvision": {
        "name": "Hikvision - CCTV Channels",
        "description": "Available CCTV record channels from the Hik-Connect app",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2023-03-23",
        "last_update_date": "2023-03-23",
        "requirements": "none",
        "category": "Hikvision",
        "notes": "",
        "paths": ('*/com.connect.enduser/databases/database.hik*',),
        "output_types": "standard",
        "artifact_icon": "video",
    },
    "get_hikvision_info": {
        "name": "Hikvision - CCTV Info",
        "description": "Information about the connected CCTV system from the Hik-Connect app",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2023-03-23",
        "last_update_date": "2023-03-23",
        "requirements": "none",
        "category": "Hikvision",
        "notes": "",
        "paths": ('*/com.connect.enduser/databases/database.hik*',),
        "output_types": "standard",
        "artifact_icon": "video",
    },
    "get_hikvision_activity": {
        "name": "Hikvision - CCTV Activity",
        "description": "User interaction with the Hik-Connect app (may indicate remote live view / playback)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2023-03-23",
        "last_update_date": "2023-03-23",
        "requirements": "none",
        "category": "Hikvision",
        "notes": "",
        "paths": ('*/com.connect.enduser/databases/ezvizlog.db',),
        "output_types": "standard",
        "artifact_icon": "video",
    },
    "get_hikvision_media": {
        "name": "Hikvision - User Created Media",
        "description": "Media files the user created while viewing CCTV footage in the Hik-Connect app",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2023-03-23",
        "last_update_date": "2023-03-23",
        "requirements": "none",
        "category": "Hikvision",
        "notes": "",
        "paths": ('*/com.connect.enduser/databases/image.db*', '*/0/Pictures/Hik-Connect Album/*'),
        "output_types": "standard",
        "artifact_icon": "video",
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _db(files_found, db_name):
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == db_name:
            return file_found
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


@artifact_processor
def get_hikvision(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found, 'database.hik')
    rows = _run(source_path, '''
        SELECT nDeviceID, nChannelNo, chChannelName,
        CASE nEnable WHEN '0' THEN 'Disabled' WHEN '1' THEN 'Enabled' END
        FROM channelinfo
    ''')
    data_headers = ('Device ID', 'Channel No.', 'Channel Name', 'Status')
    return data_headers, [tuple(r) for r in rows], source_path


@artifact_processor
def get_hikvision_info(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found, 'database.hik')
    rows = _run(source_path, '''
        SELECT nDeviceID, chDeviceName, chDeviceSerialNo, nDevicePort, nChannelNum, nStartChan,
        nIPChannelNum, nStartIPChan, chDDNSAddress, nDDNSPort
        FROM deviceinfo
    ''')
    data_headers = ('ID', 'Name/IP', 'Serial Number', 'Port', 'Channels', '1st Channel',
                    'IP Channels', '1st IP Channel', 'DDNS Address', 'DDNS Port')
    return data_headers, [tuple(r) for r in rows], source_path


@artifact_processor
def get_hikvision_activity(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found, 'ezvizlog.db')
    rows = _run(source_path, 'SELECT time, systemName, content FROM event')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Record Type', 'Activity')
    return data_headers, data_list, source_path


@artifact_processor
def get_hikvision_media(files_found, report_folder, seeker, wrap_text):
    files_by_name = {os.path.basename(str(f)): str(f) for f in files_found}
    source_path = _db(files_found, 'image.db')
    rows = _run(source_path, '''
        SELECT createdTime, cameraID, deviceID,
        CASE type WHEN '0' THEN 'Image' WHEN '1' THEN 'Video' END,
        filePath, thumbPath, user, folderName, videoStartTime, videoStopTime
        FROM images
    ''')
    data_list = []
    for r in rows:
        media = check_in_media(files_by_name.get(os.path.basename(r[4])), os.path.basename(r[4])) if r[4] else ''
        thumb = check_in_media(files_by_name.get(os.path.basename(r[5])), os.path.basename(r[5])) if r[5] else ''
        data_list.append((_ms_to_utc(r[0]), r[1], r[2], r[3], media, thumb, r[6], r[7], r[8], r[9]))

    data_headers = (
        ('Creation Timestamp', 'datetime'), 'Camera ID', 'Device ID', 'Type', ('File', 'media'),
        ('Thumbnail', 'media'), 'User', 'Folder Name', 'Video Start Time', 'Video End Time')
    return data_headers, data_list, source_path
