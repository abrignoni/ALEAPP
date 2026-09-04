__artifacts_v2__ = {
    "nearby_fast_pair": {
        "name": "Nearby - Fast Pair Devices",
        "description": "Bluetooth accessories the device holds a Fast Pair record for, with the "
                       "accessory's address, its model name, the name shown for it and the times "
                       "it was first and last observed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Nearby",
        "notes": "Read from the Play services LevelDB store "
                 "files/nearby-fast-pair/nearby_fast_pair_item_cache.db with the vendored "
                 "ccl_leveldb, decoding each record's value with blackboxprotobuf. The store is a "
                 "directory, so the path pattern matches the files inside it and the directory is "
                 "opened once, after the mirrored Android storage views of one store are "
                 "collapsed so a record is not reported once per view.\n"
                 "Each record wraps a discovery item whose field numbers are Chromium's "
                 "StoredDiscoveryItem: mac_address 4, device_name 6, title 7, description 8, "
                 "last_observation_timestamp_millis 10, first_observation_timestamp_millis 11, "
                 "state 17. Reference: Chromium, ash/quick_pair/proto/fastpair_data.proto. The "
                 "two timestamps are Unix milliseconds and, where both are present, the last "
                 "observation is the later of the two. Their presence varies by image: on four of "
                 "the seven tested images every record carried both, while on the other three "
                 "they were on 1 of 7, 1 of 11 and 0 of 15 records, so the table leads with the "
                 "address rather than a time and Last Observed and First Observed can be blank.\n"
                 "Device Name is the model name the record carries and was blank on three of the "
                 "seven tested images; Title is the name shown for the accessory, which on the "
                 "tested images was mostly a personalised name of the form <name>'s <model>, with "
                 "the bare model on some superseded copies, so the two are reported separately. "
                 "State is reported as stored. The record also holds the accessory's image, which "
                 "is reported only as a byte count, and a short binary account key that is not "
                 "reported. On an image whose records are all for one accessory, MAC Address, "
                 "Manufacturer, Model ID and Image Bytes each hold a single value; they are kept "
                 "as columns because an image with several accessories separates them.\n"
                 "LevelDB keeps superseded copies of a key, so the same address can appear more "
                 "than once; Superseded is True for every copy but the newest for that address, "
                 "and an earlier copy can carry an earlier name. A row records that the device "
                 "held a Fast Pair entry for that accessory, which is not the same as the "
                 "accessory having been paired.",
        "paths": ('*/nearby-fast-pair/nearby_fast_pair_item_cache.db/*',),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 2 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 5 rows",
            "pixel7a_a14": "Android 14 | 6 rows",
            "russell_a14": "Android 14 | 7 rows",
            "russell_pixel6a_a13": "Android 13 | 11 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 15 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 3 rows",
        },
    },
    "nearby_discovery": {
        "name": "Nearby - Discovered Items",
        "description": "Items the Nearby discovery cache recorded, with the address seen, the "
                       "signal strength and the times the item was first and last observed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Nearby",
        "notes": "Read from the Play services LevelDB store "
                 "files/nearby-discovery/nearby_discovery_item_cache.db with the vendored "
                 "ccl_leveldb, decoding each record's value with blackboxprotobuf. The store is a "
                 "directory, so the path pattern matches the files inside it and the directory is "
                 "opened once, after the mirrored Android storage views of one store are collapsed so a "
                 "record is not reported once per view.\n"
                 "Field numbers are Chromium's StoredDiscoveryItem: id 1, type 2, mac_address 4, "
                 "device_name 6, title 7, description 8, last_observation_timestamp_millis 10, "
                 "first_observation_timestamp_millis 11, state 17, rssi 22. Reference: Chromium, "
                 "ash/quick_pair/proto/fastpair_data.proto. The timestamps are Unix milliseconds "
                 "and RSSI is a signal strength in decibel-milliwatts as stored, which is a "
                 "coarse indication of nearness at that moment and not a distance.\n"
                 "The discovery records carry no device name or title field, so those columns are not "
                 "reported for this store. Item ID is the identifier the cache filed the entry under and often names the "
                 "app the item relates to. Status Text is a message the store carries describing "
                 "how recently the item was seen, and it is reported as stored. Type and State "
                 "are integers reported as stored.\n"
                 "LevelDB keeps superseded copies of a key, so Superseded is True for every copy "
                 "but the newest for that identifier. A row records that the device's Nearby "
                 "cache held an entry for that item; it does not establish that the user "
                 "interacted with it.",
        "paths": ('*/nearby-discovery/nearby_discovery_item_cache.db/*',),
        "output_types": "standard",
        "artifact_icon": "broadcast",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 3 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 26 rows",
            "pixel7a_a14": "Android 14 | 3 rows",
            "russell_a14": "Android 14 | 39 rows",
            "russell_pixel6a_a13": "Android 13 | 40 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 3 rows",
        },
    },
}

import datetime
import os
import pathlib

from scripts.artifacts.storagePathViews import unique_files
from scripts.ccl import ccl_leveldb
from scripts import blackboxprotobuf
from scripts.ilapfuncs import artifact_processor, logfunc

# Field numbers from Chromium's StoredDiscoveryItem, ash/quick_pair/proto/fastpair_data.proto.
_ID = '1'
_TYPE = '2'
_MAC = '4'
_DEVICE_NAME = '6'
_TITLE = '7'
_DESCRIPTION = '8'
_LAST_SEEN = '10'
_FIRST_SEEN = '11'
_STATE = '17'
_RSSI = '22'
_DEBUG_MESSAGE = '37'
# The Fast Pair record wraps that item in this field, and repeats the address at the top level.
_WRAPPED_ITEM = '12'
_IMAGE = '36'
_MANUFACTURER_GROUP = '46'
_MANUFACTURER = '6'


def _text(value):
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', 'replace')
    if value is None:
        return ''
    return value


def _ms(value):
    """Unix milliseconds as an aware UTC datetime; 0 and empty are reported as blank."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(number / 1000, tz=datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _stores(context, marker):
    """Each LevelDB store directory once, for the files the seeker handed us."""
    directories = set()
    for file_found in unique_files(context):
        file_found = str(file_found)
        if marker not in file_found.replace('\\', '/'):
            continue
        directories.add(pathlib.Path(file_found).parent)
    return sorted(directories)


def _records(directory):
    """Live records, newest first per key, each tagged with whether it is superseded."""
    try:
        database = ccl_leveldb.RawLevelDb(str(directory))
        records = [r for r in database.iterate_records_raw()
                   if r.state == ccl_leveldb.KeyState.Live and r.value]
    except Exception as error:  # pylint: disable=broad-except
        logfunc(f'Nearby: could not read {os.path.basename(str(directory))}: {error}')
        return []
    records.sort(key=lambda r: r.seq, reverse=True)
    seen = set()
    out = []
    for record in records:
        key = bytes(record.user_key)
        out.append((record, key in seen))
        seen.add(key)
    return out


def _decode(record):
    try:
        message, _ = blackboxprotobuf.decode_message(record.value)
        return message if isinstance(message, dict) else None
    except Exception:  # pylint: disable=broad-except
        return None


@artifact_processor
def nearby_fast_pair(context):
    data_headers = (
        'MAC Address',
        'Device Name',
        'Title',
        'Manufacturer',
        'Model ID',
        ('Last Observed', 'datetime'),
        ('First Observed', 'datetime'),
        'Description',
        'State (as stored)',
        'Image Bytes',
        'Superseded',
        'Source File',
    )
    data_list = []
    sources = []

    for directory in _stores(context, '/nearby-fast-pair/'):
        rows = 0
        for record, superseded in _records(directory):
            message = _decode(record)
            if not message:
                continue
            item = message.get(_WRAPPED_ITEM)
            if isinstance(item, list):
                item = item[0] if item else None
            if not isinstance(item, dict):
                item = {}
            manufacturer_group = item.get(_MANUFACTURER_GROUP)
            if isinstance(manufacturer_group, list):
                manufacturer_group = manufacturer_group[0] if manufacturer_group else {}
            manufacturer = ''
            if isinstance(manufacturer_group, dict):
                manufacturer = _text(manufacturer_group.get(_MANUFACTURER))
            image = item.get(_IMAGE)
            data_list.append((
                _text(item.get(_MAC)) or _text(message.get(_ID)),
                _text(item.get(_DEVICE_NAME)),
                _text(item.get(_TITLE)),
                manufacturer,
                _text(item.get(_ID)),
                _ms(item.get(_LAST_SEEN)),
                _ms(item.get(_FIRST_SEEN)),
                _text(item.get(_DESCRIPTION)),
                item.get(_STATE, ''),
                len(image) if isinstance(image, (bytes, bytearray)) else 0,
                superseded,
                context.get_relative_path(str(directory)),
            ))
            rows += 1
        if rows:
            sources.append(str(directory))

    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def nearby_discovery(context):
    data_headers = (
        ('Last Observed', 'datetime'),
        ('First Observed', 'datetime'),
        'Item ID',
        'MAC Address',
        'RSSI',
        'Status Text',
        'Type (as stored)',
        'State (as stored)',
        'Superseded',
        'Source File',
    )
    data_list = []
    sources = []

    for directory in _stores(context, '/nearby-discovery/'):
        rows = 0
        for record, superseded in _records(directory):
            message = _decode(record)
            if not message:
                continue
            data_list.append((
                _ms(message.get(_LAST_SEEN)),
                _ms(message.get(_FIRST_SEEN)),
                _text(message.get(_ID)),
                _text(message.get(_MAC)),
                message.get(_RSSI, ''),
                _text(message.get(_DEBUG_MESSAGE)),
                message.get(_TYPE, ''),
                message.get(_STATE, ''),
                superseded,
                context.get_relative_path(str(directory)),
            ))
            rows += 1
        if rows:
            sources.append(str(directory))

    return data_headers, data_list, '\n'.join(sources)
