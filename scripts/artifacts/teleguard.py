__artifacts_v2__ = {
    "get_teleguard": {
        "name": "Teleguard - Messages",
        "description": "Teleguard messenger messages",
        "author": "",
        "creation_date": "2024-01-09",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "",
        "paths": ('*/data/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',
                  '*/data/ch.swisscows.messenger.teleguardapp/cache/**'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 2 rows",
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 42 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat ID",
                "textColumn": "Content",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender",
                "mediaColumn": "Media"
            }
        },
    },
    "get_teleguard_posts": {
        "name": "Teleguard - Posts",
        "description": "Teleguard channel posts",
        "author": "",
        "creation_date": "2024-01-09",
        "last_update_date": "2024-01-09",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "",
        "paths": ('*/data/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows",
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 0 rows",
        },
    },
    "get_teleguard_contacts": {
        "name": "Teleguard - Contacts",
        "description": "Teleguard contacts with avatars",
        "author": "",
        "creation_date": "2024-01-09",
        "last_update_date": "2024-01-09",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "",
        "paths": ('*/data/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 2 rows",
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 5 rows",
        },
    },
    "get_teleguard_channels": {
        "name": "Teleguard - Channels",
        "description": "Teleguard channels",
        "author": "",
        "creation_date": "2024-01-09",
        "last_update_date": "2024-01-09",
        "requirements": "none",
        "category": "Teleguard",
        "notes": "",
        "paths": ('*/data/ch.swisscows.messenger.teleguardapp/app_flutter/teleguard_database.db*',),
        "output_types": "standard",
        "artifact_icon": "radio",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | ch.swisscows.messenger.teleguardapp vc 176 | 0 rows",
            "pixel7a_a14": "Android 14 | ch.swisscows.messenger.teleguardapp vc 162 | 0 rows",
        },
    }
}

import datetime
import json
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media, check_in_embedded_media


def _str_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('teleguard_database.db'):
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
def get_teleguard(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    rows = _run(source_path, '''
        SELECT datetime(createDate/1000,'unixepoch'), datetime(userTime/1000,'unixepoch'),
        type, sender, receiver, content, metadata, status, isEdited, chatId
        FROM messages
    ''')
    # local account id lives in the service table ('user' row) of the same db
    owner_id = ''
    for (svc_data,) in _run(source_path, "SELECT data FROM service WHERE id = 'user'"):
        try:
            owner_id = (json.loads(svc_data) or {}).get('serverId', '')
        except (ValueError, TypeError):
            owner_id = ''
    data_list = []
    for row in rows:
        media_refs = []
        if row[2] == 'MEDIA' and row[6]:
            try:
                files = json.loads(row[6]).get('files', {})
            except (ValueError, TypeError):
                files = {}
            for key in files:
                # The metadata key is a path fragment: TeleGuard stores each item
                # under cache/<key>/<file>, so match by substring. Require an actual
                # file so the cache/<key> directory itself is never matched -- a
                # directory makes check_in_media return None, and a None -> null in
                # the serialized media list makes the LAVA viewer show a broken-media
                # marker and crash on hover (the HTML report silently skips it).
                match = next((str(f) for f in files_found
                              if os.path.isfile(str(f)) and key in str(f)), None)
                if match:
                    ref = check_in_media(match, os.path.basename(match))
                    if ref:
                        media_refs.append(ref)
        if len(media_refs) == 1:
            media_cell = media_refs[0]
        elif media_refs:
            media_cell = media_refs
        else:
            media_cell = ''
        if owner_id and row[3]:
            direction = 'Outgoing' if row[3] == owner_id else 'Incoming'
        else:
            direction = ''
        data_list.append((_str_to_utc(row[0]), _str_to_utc(row[1]), row[2], row[3], row[4], row[5],
                          media_cell, row[6], row[7], row[8], direction, row[9]))

    data_headers = (('Timestamp', 'datetime'), ('User Time', 'datetime'), 'Type', 'Sender', 'Receiver',
                    'Content', ('Media', 'media'), 'Metadata', 'Status', 'Is Edited?', 'Direction',
                    'Chat ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_teleguard_posts(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    rows = _run(source_path, '''
        SELECT datetime(createDate/1000,'unixepoch'), channelId, header, content, type, localStatus,
        viewsCount, likesCount, dislikesCount, metadata, media
        FROM posts
    ''')
    data_list = [(_str_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Channel ID', 'Header', 'Content', 'Type', 'Local Status',
                    'Views Count', 'Likes Count', 'Dislikes Count', 'Metadata', 'Media')
    return data_headers, data_list, source_path


@artifact_processor
def get_teleguard_contacts(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    rows = _run(source_path, '''
        SELECT datetime(lastActivityTime/1000,'unixepoch'), serverId, alias, type, color, avatar, options,
        info, datetime(lastVisitTime/1000,'unixepoch'), personalId
        FROM contacts
    ''')
    data_list = []
    for r in rows:
        avatar = ''
        if r[5] is not None:
            avatar = check_in_embedded_media(source_path, r[5], f'{r[1]}_avatar.jpg',
                                             force_type='image/jpeg', force_extension='jpg')
        data_list.append((_str_to_utc(r[0]), r[1], r[2], r[3], r[4], avatar, r[6], r[7], _str_to_utc(r[8]), r[9]))

    data_headers = (('Last Activity Timestamp', 'datetime'), 'Server ID', 'Alias', 'Type', 'Color',
                    ('Avatar', 'media'), 'Options', 'Info', ('Last Visit Time', 'datetime'), 'Personal ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_teleguard_channels(context):
    files_found = context.get_files_found()
    source_path = _db(files_found)
    rows = _run(source_path, 'SELECT * FROM channels')
    data_headers = ('ID', 'Alias', 'Description', 'Category', 'Color', 'Avatar ID', 'Subscribers Count',
                    'Admin', 'Posts Count', 'Is Deleted', 'Language', 'Type')
    return data_headers, [tuple(r)[:12] for r in rows], source_path
