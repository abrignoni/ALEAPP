__artifacts_v2__ = {
    "get_appSemloc": {
        "name": "Semantic Location Raw Signals - Positions",
        "description": "Position records in Google Play services' semantic location raw signal "
                       "LevelDB: time, latitude, longitude, accuracy, altitude, source and speed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2024/06/21",
        "last_update_date": "2026-11-18",
        "requirements": "",
        "category": "Semantic Location",
        "notes": "Read from Google Play services' semantic location raw signal LevelDB "
                 "(com.google.android.gms/app_semanticlocation_rawsignal_db) with the vendored "
                 "ccl_leveldb readers (thanks to Alex Caithness). Sources are the decompiled Google "
                 "Play services APK from dragna_pixel9a_a16 (com.google.android.gms 26.39.33, "
                 "versionCode 263933035, decompiled with jadx; the code is obfuscated). In that "
                 "version the class that opens the store names its folder, and Play services' location"
                 " history export reads every value in it as one raw signal message, which holds a "
                 "position, a Wi-Fi scan or an activity record. The export writes them to JSON under "
                 "rawSignals, and the field names here come from that export code. The same message is"
                 " also kept as type 5 rows of the transient semantic location store (see the Semantic"
                 " Location Transient artifacts). Values are decoded with the vendored "
                 "blackboxprotobuf and the field types of the app's own message classes. The code that"
                 " writes the store builds each key from the record's own time in milliseconds (8 "
                 "bytes, big-endian) and one byte for the kind: 0 position, 1 Wi-Fi scan, 2 activity "
                 "record. On every tested image with records, the key's time equals the record's time "
                 "field and its kind byte matches the payload, on every record. Field meaning was read"
                 " from one Play services version. The other images' versions were not decompiled; "
                 "their records decode with the same field numbers. Every version of a record that the"
                 " LevelDB files still hold is reported, with its sequence number, key and file, so "
                 "one key can appear on more than one row (on the tested images, at most 18 keys per "
                 "artifact did). No latest-version selection is done. Record Key Hex is the full key, "
                 "which in table files includes the 8-byte LevelDB trailer. Deletion records carry no "
                 "value and are not reported. Each table and log file is opened on its own, and a file"
                 " that cannot be opened is skipped and logged: on pixel7a_a14 one table file ended "
                 "without its footer and was skipped, and the rest of the store was read. A store seen"
                 " through several storage views of one Android user is read once. When rows come from"
                 " more than one store, a Source File column names the store folder. The export reads "
                 "only records newer than a number of days taken from a Play services configuration "
                 "value, which was not established. On the tested images the records of one store span"
                 " 26.8 to 37.7 days, and 51 days where a second user's store adds older records. "
                 "Field 2 of the raw signal message, a time value with several writers that the export"
                 " does not name, is not reported. Timestamp is the position's timestamp in "
                 "milliseconds. Latitude and Longitude are the LatLng the export writes, stored as "
                 "integers in units of 1e-7 degree. Accuracy (m) is the stored accuracy divided by "
                 "1000; the export uses integer division there and drops the fraction, which is kept "
                 "here. Altitude (m) is altitudeMeters and Speed (m/s) speedMetersPerSecond. Source "
                 "uses the names of Play services' own enum (UNKNOWN, GPS, CELL, WIFI, WIFI_ONLY); a "
                 "value outside it is shown as Unknown (N), where the export writes UNKNOWN. A "
                 "position is what Play services stored; the store does not show whether the device "
                 "was carried by its user. Position fields 8 to 10 are not written by the export and "
                 "are not reported; of them only field 8 was seen, on anne_a15. Record File Type held "
                 "one value on all rows of hc_pixel8pro_a16 and userb2_a13.",
        "paths": ('*/com.google.android.gms/app_semanticlocation_rawsignal_db/*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.gms 26.39.33 | 5265 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 5129 rows",
            "anne_a15": "Android 15 | com.google.android.gms | 6651 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 1497 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms | 5753 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 5033 rows",
            "russell_a14": "Android 14 | com.google.android.gms | 2114 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 662 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "sharon_a13": "Android 13 | com.google.android.gms | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "cookbook_a11": "Android 11 | com.google.android.gms | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gms | 0 rows",
            "falken_a326u_a13": "Android 13 | com.google.android.gms | 0 rows",
            "adams_ss135dl_a13": "Android 13 | com.google.android.gms | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.google.android.gms | 0 rows",
        },
    },
    "get_appSemlocActivityRecords": {
        "name": "Semantic Location Raw Signals - Activity Records",
        "description": "Activity records in Google Play services' semantic location raw signal "
                       "LevelDB: time and the probable activities with their confidence.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "",
        "category": "Semantic Location",
        "notes": "Read from Google Play services' semantic location raw signal LevelDB "
                 "(com.google.android.gms/app_semanticlocation_rawsignal_db) with the vendored "
                 "ccl_leveldb readers (thanks to Alex Caithness). Sources are the decompiled Google "
                 "Play services APK from dragna_pixel9a_a16 (com.google.android.gms 26.39.33, "
                 "versionCode 263933035, decompiled with jadx; the code is obfuscated). In that "
                 "version the class that opens the store names its folder, and Play services' location"
                 " history export reads every value in it as one raw signal message, which holds a "
                 "position, a Wi-Fi scan or an activity record. The export writes them to JSON under "
                 "rawSignals, and the field names here come from that export code. The same message is"
                 " also kept as type 5 rows of the transient semantic location store (see the Semantic"
                 " Location Transient artifacts). Values are decoded with the vendored "
                 "blackboxprotobuf and the field types of the app's own message classes. The code that"
                 " writes the store builds each key from the record's own time in milliseconds (8 "
                 "bytes, big-endian) and one byte for the kind: 0 position, 1 Wi-Fi scan, 2 activity "
                 "record. On every tested image with records, the key's time equals the record's time "
                 "field and its kind byte matches the payload, on every record. Field meaning was read"
                 " from one Play services version. The other images' versions were not decompiled; "
                 "their records decode with the same field numbers. Every version of a record that the"
                 " LevelDB files still hold is reported, with its sequence number, key and file, so "
                 "one key can appear on more than one row (on the tested images, at most 18 keys per "
                 "artifact did). No latest-version selection is done. Record Key Hex is the full key, "
                 "which in table files includes the 8-byte LevelDB trailer. Deletion records carry no "
                 "value and are not reported. Each table and log file is opened on its own, and a file"
                 " that cannot be opened is skipped and logged: on pixel7a_a14 one table file ended "
                 "without its footer and was skipped, and the rest of the store was read. A store seen"
                 " through several storage views of one Android user is read once. When rows come from"
                 " more than one store, a Source File column names the store folder. The export reads "
                 "only records newer than a number of days taken from a Play services configuration "
                 "value, which was not established. On the tested images the records of one store span"
                 " 26.8 to 37.7 days, and 51 days where a second user's store adds older records. "
                 "Field 2 of the raw signal message, a time value with several writers that the export"
                 " does not name, is not reported. Timestamp is the activity record's timestamp in "
                 "milliseconds. Probable Activities lists each probableActivities type and confidence "
                 "in stored order. Type names come from Play services' own enum (IN_VEHICLE, "
                 "ON_BICYCLE, ON_FOOT, STILL, UNKNOWN, TILTING, EXITING_VEHICLE, WALKING, RUNNING, "
                 "IN_ROAD_VEHICLE, IN_RAIL_VEHICLE, IN_TWO_WHEELER_VEHICLE); a value outside it is "
                 "shown as Unknown (N), where the export writes IN_VEHICLE. Top Activity and Top "
                 "Confidence are the pair with the highest confidence, chosen by this artifact, not by"
                 " Play services. A record whose type and confidence lists differ in length gets no "
                 "list, as in the export. An activity record is a stored classification; it is not a "
                 "record of what the user said they were doing. Field 5 is not written by the export "
                 "and is not reported; it was seen on one record of anne_a15. Record File Type held "
                 "one value on all rows of hc_pixel8pro_a16 and userb2_a13.",
        "paths": ('*/com.google.android.gms/app_semanticlocation_rawsignal_db/*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.gms 26.39.33 | 2074 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 13457 rows",
            "anne_a15": "Android 15 | com.google.android.gms | 4343 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 1971 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms | 2519 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 7644 rows",
            "russell_a14": "Android 14 | com.google.android.gms | 5798 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 188 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "sharon_a13": "Android 13 | com.google.android.gms | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "cookbook_a11": "Android 11 | com.google.android.gms | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gms | 0 rows",
            "falken_a326u_a13": "Android 13 | com.google.android.gms | 0 rows",
            "adams_ss135dl_a13": "Android 13 | com.google.android.gms | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.google.android.gms | 0 rows",
        },
    },
    "get_appSemlocWifiScans": {
        "name": "Semantic Location Raw Signals - Wi-Fi Scans",
        "description": "Wi-Fi scan records in Google Play services' semantic location raw signal "
                       "LevelDB: scan time and the access point MAC addresses with their signal "
                       "strength.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "",
        "category": "Semantic Location",
        "notes": "Read from Google Play services' semantic location raw signal LevelDB "
                 "(com.google.android.gms/app_semanticlocation_rawsignal_db) with the vendored "
                 "ccl_leveldb readers (thanks to Alex Caithness). Sources are the decompiled Google "
                 "Play services APK from dragna_pixel9a_a16 (com.google.android.gms 26.39.33, "
                 "versionCode 263933035, decompiled with jadx; the code is obfuscated). In that "
                 "version the class that opens the store names its folder, and Play services' location"
                 " history export reads every value in it as one raw signal message, which holds a "
                 "position, a Wi-Fi scan or an activity record. The export writes them to JSON under "
                 "rawSignals, and the field names here come from that export code. The same message is"
                 " also kept as type 5 rows of the transient semantic location store (see the Semantic"
                 " Location Transient artifacts). Values are decoded with the vendored "
                 "blackboxprotobuf and the field types of the app's own message classes. The code that"
                 " writes the store builds each key from the record's own time in milliseconds (8 "
                 "bytes, big-endian) and one byte for the kind: 0 position, 1 Wi-Fi scan, 2 activity "
                 "record. On every tested image with records, the key's time equals the record's time "
                 "field and its kind byte matches the payload, on every record. Field meaning was read"
                 " from one Play services version. The other images' versions were not decompiled; "
                 "their records decode with the same field numbers. Every version of a record that the"
                 " LevelDB files still hold is reported, with its sequence number, key and file, so "
                 "one key can appear on more than one row (on the tested images, at most 18 keys per "
                 "artifact did). No latest-version selection is done. Record Key Hex is the full key, "
                 "which in table files includes the 8-byte LevelDB trailer. Deletion records carry no "
                 "value and are not reported. Each table and log file is opened on its own, and a file"
                 " that cannot be opened is skipped and logged: on pixel7a_a14 one table file ended "
                 "without its footer and was skipped, and the rest of the store was read. A store seen"
                 " through several storage views of one Android user is read once. When rows come from"
                 " more than one store, a Source File column names the store folder. The export reads "
                 "only records newer than a number of days taken from a Play services configuration "
                 "value, which was not established. On the tested images the records of one store span"
                 " 26.8 to 37.7 days, and 51 days where a second user's store adds older records. "
                 "Field 2 of the raw signal message, a time value with several writers that the export"
                 " does not name, is not reported. Delivery Time is the scan's deliveryTime in "
                 "milliseconds. Access Points lists each MAC and RSSI pair in stored order, which the "
                 "export writes as mac and rawRssi; pairs past the shorter of the two lists are left "
                 "out, as in the export. In Play services' passive Wi-Fi scan receiver the MAC is the "
                 "access point's BSSID, parsed from hex into a 48-bit number; it is shown here the way"
                 " Play services' own formatter writes it (lowercase, separated by colons), and a "
                 "value outside 48 bits is shown as stored. RSSI is the scan result's level in dBm. "
                 "That receiver leaves out networks whose SSID contains _nomap or _optout, keeps one "
                 "entry per BSSID, and stops at a number of access points taken from a configuration "
                 "value; every tested scan held at most 9. SSIDs are not stored. Scans can also come "
                 "from a location fix that carries a Wi-Fi scan; that path was not traced field by "
                 "field. Some scans hold no access points (Access Point Count 0). A scan lists access "
                 "points the device detected; it does not show that the device connected to any of "
                 "them. Not reported: field 5, per access point details such as frequency and round "
                 "trip time measurements (none on any tested image), and field 6, a value without a "
                 "name in the decompiled code. Record File Type held one value on all rows of "
                 "anne_a15, hc_pixel8pro_a16, russell_a14 and userb2_a13.",
        "paths": ('*/com.google.android.gms/app_semanticlocation_rawsignal_db/*',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.google.android.gms 26.39.33 | 5445 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 1440 rows",
            "anne_a15": "Android 15 | com.google.android.gms | 2106 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 1703 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms | 6286 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 2862 rows",
            "russell_a14": "Android 14 | com.google.android.gms | 1820 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 109 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "sharon_a13": "Android 13 | com.google.android.gms | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "cookbook_a11": "Android 11 | com.google.android.gms | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gms | 0 rows",
            "falken_a326u_a13": "Android 13 | com.google.android.gms | 0 rows",
            "adams_ss135dl_a13": "Android 13 | com.google.android.gms | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | com.google.android.gms | 0 rows",
        },
    },
}

import datetime
import pathlib
import re

from scripts.artifacts.storagePathViews import unique_files
from scripts.blackboxprotobuf import decode_message
from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.vendor.ccl import ccl_leveldb

_INT = {'type': 'int', 'name': ''}
_FLOAT = {'type': 'float', 'name': ''}
# The raw signal message: field 1 holds one of a position (1), a Wi-Fi scan (2) or an
# activity record (3). Field types are those of the app's own message classes.
_RAW_SIGNAL = {'1': {'type': 'message', 'name': '', 'message_typedef': {
    '1': {'type': 'message', 'name': '', 'message_typedef': {
        '1': _INT, '2': _INT, '3': _INT, '4': _FLOAT, '5': _INT, '6': _INT, '7': _FLOAT}},
    '2': {'type': 'message', 'name': '', 'message_typedef': {
        '1': _INT, '3': {'type': 'packed_int', 'name': ''},
        '4': {'type': 'packed_sint', 'name': ''}}},
    '3': {'type': 'message', 'name': '', 'message_typedef': {
        '2': _INT, '3': {'type': 'packed_int', 'name': ''},
        '4': {'type': 'packed_float', 'name': ''}}},
}}}
_POSITION_SOURCES = {0: 'UNKNOWN', 1: 'GPS', 2: 'CELL', 3: 'WIFI', 4: 'WIFI_ONLY'}
_ACTIVITY_TYPES = {0: 'IN_VEHICLE', 1: 'ON_BICYCLE', 2: 'ON_FOOT', 3: 'STILL', 4: 'UNKNOWN',
                   5: 'TILTING', 6: 'EXITING_VEHICLE', 7: 'WALKING', 8: 'RUNNING',
                   9: 'IN_ROAD_VEHICLE', 10: 'IN_RAIL_VEHICLE', 11: 'IN_TWO_WHEELER_VEHICLE'}
_DECODE_ERRORS = (ValueError, KeyError, TypeError, IndexError, EOFError)
_DATA_FILE = re.compile(r'[0-9]{6}\.(ldb|log|sst)')
_PROVENANCE = ('Rec. Sequence', 'Record Key Hex', 'Record File Type', 'Origin')


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _as_dict(value):
    if isinstance(value, list):
        value = value[0] if value else {}
    return value if isinstance(value, dict) else {}


def _name(names, value):
    if not isinstance(value, int):
        return ''
    return names.get(value, f'Unknown ({value})')


def _num(value):
    return value if isinstance(value, (int, float)) else ''


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(value / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return ''


def _mac(value):
    # The same formatting Play services applies to the 48-bit value it parsed from the BSSID.
    if not isinstance(value, int) or not 0 <= value <= 0xFFFFFFFFFFFF:
        return f'{value} (as stored)'
    return ':'.join(f'{(value >> shift) & 0xFF:02x}' for shift in range(40, -8, -8))


def _stores(context):
    """Staged database folders, one per store after storage views are removed, with files."""
    stores = {}
    for found in unique_files(context):
        found = pathlib.Path(str(found))
        if _DATA_FILE.fullmatch(found.name):
            stores.setdefault(found.parent, []).append(found)
    return stores


def _open_files(paths):
    """Open each table and log file on its own, so one unreadable file does not hide the rest."""
    opened = []
    for path in paths:
        try:
            if path.suffix.lower() == '.log':
                opened.append(ccl_leveldb.LogFile(path))
            else:
                opened.append(ccl_leveldb.LdbFile(path))
        except (ValueError, OSError) as error:
            logfunc(f'Semantic Location Raw Signals: skipped {path.name}, which could not be '
                    f'opened ({type(error).__name__})')
    return sorted(opened, key=lambda item: item.file_no)


def _records(context, kind):
    """Yield (record, payload, origin, relative source) for every record holding this kind."""
    stores = _stores(context)
    sources = []
    rows = []
    for folder, paths in stores.items():
        failed = 0
        files = _open_files(paths)
        try:
            for file in files:
                for record in file:
                    if not record.value:
                        continue
                    try:
                        message, _ = decode_message(record.value, _RAW_SIGNAL)
                    except _DECODE_ERRORS:
                        failed += 1
                        continue
                    signal = _as_dict(_as_dict(message).get('1'))
                    if signal.get(kind) is None:
                        continue
                    origin = pathlib.Path(str(record.origin_file))
                    rows.append((record, _as_dict(signal.get(kind)),
                                 f'{origin.parent.name}/{origin.name}',
                                 context.get_relative_path(str(origin))))
        finally:
            for file in files:
                file.close()
        if failed:
            logfunc(f'Semantic Location Raw Signals: {failed} values in {folder.name} '
                    f'did not decode')
        sources.append(str(folder))
    return rows, sources


def _provenance(record, origin):
    return (record.seq, record.key.hex(), record.file_type.name, origin)


def _finish(headers, data_list, sources):
    """Add Source File only when this artifact's rows come from more than one store."""
    if len({row[-1] for row in data_list}) > 1:
        headers = headers + ('Source File',)
    else:
        data_list = [row[:-1] for row in data_list]
    return headers, data_list, '\n'.join(sources)


def _store_of(relative):
    return str(pathlib.PurePath(relative).parent)


@artifact_processor
def get_appSemloc(context):
    headers = (('Timestamp', 'datetime'), ('Latitude', 'latitude'), ('Longitude', 'longitude'),
               'Accuracy (m)', 'Altitude (m)', 'Source', 'Speed (m/s)') + _PROVENANCE
    rows, sources = _records(context, '1')
    data_list = []
    for record, position, origin, relative in rows:
        lat, lng = position.get('1'), position.get('2')
        if isinstance(lat, int) and isinstance(lng, int):
            lat, lng = lat / 1e7, lng / 1e7
        else:
            lat, lng = '', ''
        accuracy = position.get('3')
        data_list.append((
            _ms_to_utc(position.get('6')), lat, lng,
            accuracy / 1000 if isinstance(accuracy, int) else '', _num(position.get('4')),
            _name(_POSITION_SOURCES, position.get('5')), _num(position.get('7')),
            *_provenance(record, origin), _store_of(relative)))
    return _finish(headers, data_list, sources)


@artifact_processor
def get_appSemlocActivityRecords(context):
    headers = (('Timestamp', 'datetime'), 'Top Activity', 'Top Confidence',
               'Probable Activities') + _PROVENANCE
    rows, sources = _records(context, '3')
    data_list = []
    for record, activity, origin, relative in rows:
        types = _as_list(activity.get('3'))
        confidences = _as_list(activity.get('4'))
        pairs = []
        if len(types) == len(confidences):
            pairs = [(_name(_ACTIVITY_TYPES, kind), conf)
                     for kind, conf in zip(types, confidences)
                     if isinstance(kind, int) and isinstance(conf, float)]
        top_name, top_conf = max(pairs, key=lambda pair: pair[1]) if pairs else ('', '')
        listing = ', '.join(f'{name} {conf:.3g}' for name, conf in pairs)
        data_list.append((_ms_to_utc(activity.get('2')), top_name, top_conf, listing,
                          *_provenance(record, origin), _store_of(relative)))
    return _finish(headers, data_list, sources)


@artifact_processor
def get_appSemlocWifiScans(context):
    headers = (('Delivery Time', 'datetime'), 'Access Point Count',
               'Access Points (MAC RSSI dBm)') + _PROVENANCE
    rows, sources = _records(context, '2')
    data_list = []
    for record, scan, origin, relative in rows:
        macs = _as_list(scan.get('3'))
        levels = _as_list(scan.get('4'))
        pairs = list(zip(macs, levels))
        listing = ', '.join(f'{_mac(mac)} {level}' for mac, level in pairs)
        data_list.append((_ms_to_utc(scan.get('1')), len(pairs), listing,
                          *_provenance(record, origin), _store_of(relative)))
    return _finish(headers, data_list, sources)
