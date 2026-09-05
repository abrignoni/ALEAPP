__artifacts_v2__ = {
    "get_Life360_chat_messages": {
        "name": "Life360 - Chat Messages",
        "description": "Parses Life360 chat messages (messaging.db)",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2024-01-17",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Life360",
        "notes": "A message with a photo has a message_media row whose photo_key is the photo's URL. The app's "
                 "Picasso image cache (cache/picasso-cache) is an OkHttp DiskLruCache whose <hash>.0 file starts "
                 "with the URL requested and whose <hash>.1 file is the body, so the Photo column renders the "
                 "cached copy whose stored URL equals photo_key exactly, when the bytes are a JPEG, PNG, GIF or "
                 "WebP image; Photo URL is photo_key as stored. A photo message whose image was never cached, or "
                 "was evicted, has the URL and no picture. pixel7a_a14 was the only tested image with messages: "
                 "all 20 belong to one Thread ID, both of its photo messages resolved to a cached image, Location "
                 "Timestamp, Has Location, Latitude, Longitude, Location Name and Message Dismissed were blank on "
                 "all 20 messages, Message Sent and Message Read were Yes on all 20, and Message Deleted was Yes "
                 "on 1. Each Android user's messaging.db is read separately and its photos are resolved from that "
                 "user's own cache.",
        "paths": ('*/com.life360.android.safetymapd/databases/messaging.db*',
                  '*/com.life360.android.safetymapd/cache/picasso-cache/*'),
        "output_types": "all",
        "artifact_icon": "message-circle",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.life360.android.safetymapd vc 2897710 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.life360.android.safetymapd | 0 rows",
            "pixel7a_a14": "Android 14 | com.life360.android.safetymapd vc 294540 | 20 rows",
            "sharon_a14": "Android 14 | com.life360.android.safetymapd vc 296030 | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Message Sent",
                "directionSentValue": "Yes",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Name",
                "mediaColumn": "Photo"
            }
        },
    },
    "get_Life360_places": {
        "name": "Life360 - Places",
        "description": "Parses Life360 saved places (L360LocalStoreRoomDatabase)",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2024-01-17",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Life360",
        "notes": "Radius is reported as stored; the database does not record its unit.",
        "paths": ('*/com.life360.android.safetymapd/databases/L360LocalStoreRoomDatabase*',),
        "output_types": ['html', 'tsv', 'lava', 'kml'],
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.life360.android.safetymapd vc 2897710 | 6 rows",
            "pixel7a_a14": "Android 14 | com.life360.android.safetymapd vc 294540 | 0 rows",
        },
    },
    "get_Life360_locations": {
        "name": "Life360 - Locations",
        "description": "Parses Life360 device geolocation events (L360EventStore.db)",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2024-01-17",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Life360",
        "notes": "Speed and the two accuracy values are reported as stored; the JSON records no units "
                 "for them.",
        "paths": ('*/com.life360.android.safetymapd/databases/L360EventStore.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.life360.android.safetymapd vc 294540 | 15668 rows",
            "sharon_a14": "Android 14 | com.life360.android.safetymapd vc 296030 | 0 rows",
        },
    },
    "get_Life360_device_battery": {
        "name": "Life360 - Device Battery",
        "description": "Parses Life360 device battery events (L360EventStore.db)",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2024-01-17",
        "last_update_date": "2024-01-17",
        "requirements": "none",
        "category": "Life360",
        "notes": "",
        "paths": ('*/com.life360.android.safetymapd/databases/L360EventStore.db*',),
        "output_types": "standard",
        "artifact_icon": "battery",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.life360.android.safetymapd vc 294540 | 15668 rows",
            "sharon_a14": "Android 14 | com.life360.android.safetymapd vc 296030 | 0 rows",
        },
    }
}

import datetime
import json
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, check_in_media, open_sqlite_db_readonly
from scripts.context import Context
from scripts.artifacts.storagePathViews import canonical_path, unique_files


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


_PACKAGE = 'com.life360.android.safetymapd'


def _sources(context, suffix):
    """Every distinct copy of the store named by suffix, one per app container.

    The duplicate storage views of one file (data/data, data/user/0, data_mirror) collapse to
    one; a second Android user's copy is its own source.
    """
    return [f for f in unique_files(context)
            if str(f).endswith(suffix) and not str(f).endswith(('-wal', '-shm', '-journal'))
            and not os.path.isdir(f)]


def _container_key(context, file_found):
    """A key shared by every file of one app container, across its storage-view spellings."""
    parts = context.get_relative_path(file_found).replace('\\', '/').split('/')
    if _PACKAGE in parts:
        parts = parts[:parts.index(_PACKAGE) + 1]
    return canonical_path('/'.join(parts))[0]


_IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'image/png', 'png'),
    (b'GIF87a', 'image/gif', 'gif'),
    (b'GIF89a', 'image/gif', 'gif'),
)


def _image_type(head):
    for magic, mime, extension in _IMAGE_MAGIC:
        if head.startswith(magic):
            return mime, extension
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'image/webp', 'webp'
    return '', ''


def _picasso_bodies(context, container):
    """{stored URL: path of the <hash>.1 body} for the OkHttp entries of one container's Picasso cache."""
    bodies = {}
    urls = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        if '/picasso-cache/' not in file_found.replace('\\', '/') or os.path.isdir(file_found):
            continue
        if _container_key(context, file_found) != container:
            continue
        stem, ext = os.path.splitext(os.path.basename(file_found))
        if ext == '.0':
            try:
                with open(file_found, 'rb') as handle:
                    first = handle.readline().decode('utf-8', 'replace').rstrip('\n')
            except OSError:
                continue
            if first.startswith(('http://', 'https://')):
                urls[stem] = first
        elif ext == '.1':
            bodies[stem] = file_found
    return {url: bodies[stem] for stem, url in urls.items() if stem in bodies}


def _cached_photo(bodies, photo_key):
    """Media reference for the cached image whose stored URL equals photo_key, else ''."""
    path = bodies.get(photo_key or '')
    if not path:
        return ''
    try:
        with open(path, 'rb') as handle:
            head = handle.read(16)
    except OSError:
        return ''
    mime, extension = _image_type(head)
    if not mime:
        return ''
    return check_in_media(path, os.path.basename(path), force_type=mime, force_extension=extension) or ''


def _q(cursor, sql):
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error:
        return []


def _ble_events(file_found):
    """Parse the BLE geolocation/battery events from L360EventStore.db into dicts."""
    rows = []
    db = open_sqlite_db_readonly(file_found)
    if db is None:
        return rows
    cursor = db.cursor()
    # Filter to BLE events in Python (json_extract in SQL errors on any malformed-JSON row).
    for data, ev_id in _q(cursor, 'SELECT data, id FROM event WHERE eventVersion = 5'):
        try:
            j = json.loads(data)
        except (ValueError, TypeError):
            continue
        if j.get('tag') != 'BLE':
            continue
        loc = j.get('locationData') or {}
        meta = j.get('metaData') or {}
        wifi = (meta.get('wifiData') or {}).get('connectedAccessPoint') or {}
        rows.append({
            'time': _ms_to_utc(loc.get('time')),
            'lat': loc.get('latitude', ''), 'lon': loc.get('longitude', ''),
            'alt': loc.get('altitude', ''), 'speed': loc.get('speed', ''),
            'course': loc.get('course', ''), 'bearing': loc.get('bearing', ''),
            'vert': loc.get('verticalAccuracy', ''), 'hor': loc.get('horizontalAccuracy', ''),
            'lmode': meta.get('lmode', ''), 'battery': meta.get('battery', ''),
            'charging': meta.get('chargingState', ''),
            'bssid': wifi.get('bssid', ''),
            'ssid': (wifi.get('ssid', '') or '').replace('"', ''),
            'id': ev_id,
        })
    db.close()
    return rows


@artifact_processor
def get_Life360_chat_messages(context):
    sources = _sources(context, 'messaging.db')
    data_list = []
    for source in sources:
        bodies = _picasso_bodies(context, _container_key(context, source))
        db = open_sqlite_db_readonly(source)
        if db is None:
            continue
        cursor = db.cursor()
        has_media = bool(_q(cursor, "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'message_media'"))
        photo_select = 'message_media.photo_key' if has_media else 'NULL AS photo_key'
        photo_join = 'LEFT JOIN message_media ON message_media._id = message._id' if has_media else ''
        rows = _q(cursor, f'''
        SELECT
            message.created_at,
            message.thread_id,
            message.sender_id,
            thread_participant.participant_name,
            message.content,
            CASE message.sent WHEN 1 THEN 'Yes' ELSE '' END,
            CASE message.read WHEN 1 THEN 'Yes' ELSE '' END,
            CASE message.dismissed WHEN 1 THEN 'Yes' ELSE '' END,
            CASE message.deleted WHEN 1 THEN 'Yes' ELSE '' END,
            CASE message.has_location WHEN 1 THEN 'Yes' ELSE '' END,
            message.location_latitude,
            message.location_longitude,
            message.location_name,
            message.location_timestamp,
            {photo_select}
        FROM message
        LEFT JOIN thread_participant ON message.sender_id = thread_participant.participant_id
        {photo_join}
        ''')
        for row in rows:
            data_list.append((
                _sec_to_utc(row[0]),
                _sec_to_utc(row[13]),
                row[5],
                row[3],
                row[4],
                _cached_photo(bodies, row[14]),
                row[14] or '',
                row[1],
                row[2],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[11],
                row[12],
                Context.get_relative_path(source),
            ))
        db.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        ('Location Timestamp', 'datetime'),
        'Message Sent',
        'Sender Name',
        'Message',
        ('Photo', 'media'),
        'Photo URL',
        'Thread ID',
        'Sender ID',
        'Message Read',
        'Message Dismissed',
        'Message Deleted',
        'Has Location',
        'Latitude',
        'Longitude',
        'Location Name',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(Context.get_relative_path(s) for s in sources)


@artifact_processor
def get_Life360_places(context):
    sources = _sources(context, 'L360LocalStoreRoomDatabase')
    data_list = []
    for source in sources:
        db = open_sqlite_db_readonly(source)
        if db is None:
            continue
        cursor = db.cursor()
        for row in _q(cursor, '''SELECT name, latitude, longitude, radius, source, source_id, owner_id
                FROM places'''):
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], Context.get_relative_path(source)))
        db.close()

    data_headers = ('Place Name', 'Latitude', 'Longitude', 'Radius (as stored)', 'Places Source', 'Source ID',
                    'Owner ID', 'Source File')
    return data_headers, data_list, '\n'.join(Context.get_relative_path(s) for s in sources)


@artifact_processor
def get_Life360_locations(context):
    sources = _sources(context, 'L360EventStore.db')
    data_list = []
    for source in sources:
        for e in _ble_events(source):
            data_list.append((e['time'], e['lat'], e['lon'], e['alt'], e['speed'], e['course'],
                              e['bearing'], e['vert'], e['hor'], e['lmode'], e['bssid'], e['ssid'],
                              e['id'], Context.get_relative_path(source)))

    data_headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Altitude', 'Speed (as stored)',
                    'Course', 'Bearing', 'Vertical Accuracy (as stored)', 'Horizontal Accuracy (as stored)',
                    'Location Mode', 'Connected Access Point BSSID', 'Connected Access Point SSID',
                    'ID', 'Source File')
    return data_headers, data_list, '\n'.join(Context.get_relative_path(s) for s in sources)


@artifact_processor
def get_Life360_device_battery(context):
    sources = _sources(context, 'L360EventStore.db')
    data_list = []
    for source in sources:
        for e in _ble_events(source):
            data_list.append((e['time'], e['battery'], e['charging'], Context.get_relative_path(source)))

    data_headers = (('Timestamp', 'datetime'), 'Device Battery (%)', 'Charging', 'Source File')
    return data_headers, data_list, '\n'.join(Context.get_relative_path(s) for s in sources)
