__artifacts_v2__ = {
    "here_wego_recent_searches": {
        "name": "HERE WeGo Recent Searches",
        "description": "Recent searches HERE WeGo kept, with the time of each",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "HERE WeGo",
        "sample_data": {
            "emu_a15_oss_v14": "HERE WeGo 4.21.100 | 2 rows",
        },
        "notes": "One row per entry of the recentSearchResults value in "
                 "com.here.app.maps/shared_prefs/FlutterSharedPreferences.xml. The app is built "
                 "with Flutter, so that file holds its settings and the value is a Flutter string "
                 "list: a base64 marker, an exclamation mark, then a JSON array whose members are "
                 "themselves JSON objects. The field names below are the ones the app itself "
                 "writes into that JSON. "
                 "Searched is the entry's own timestamp field. It carries no zone and is not "
                 "reported as UTC, because it is not UTC: on the tested device the two stored "
                 "values matched the device's local clock at the moment each search was made, and "
                 "the device was four hours behind UTC. Read it against the device's own time "
                 "zone setting. "
                 "Search Term is the title field, which for a typed search is the text submitted. "
                 "Type read freeText on both rows of the tested device, where both searches were "
                 "typed rather than chosen from a suggestion. Place ID, Address, Category, "
                 "Latitude, Longitude, Place Category ID and Href were null on every row for the "
                 "same reason: they are the fields the app fills when an entry names a resolved "
                 "place rather than a free text query, and they are reported because that is the "
                 "case worth having on a device where it occurs. "
                 "The list is a recent-searches list, so the app orders it and may drop older "
                 "entries. Whether it is capped, and at what, was not established: the tested "
                 "device held two entries, which cannot reach a cap. Either way an absent term "
                 "is not evidence it was never searched for.",
        "paths": ('*/com.here.app.maps/shared_prefs/FlutterSharedPreferences.xml',),
        "output_types": "standard",
        "artifact_icon": "search",
    },
    "here_wego_saved_places": {
        "name": "HERE WeGo Saved Places",
        "description": "Place entries in HERE WeGo collections, with their coordinates",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "HERE WeGo",
        "sample_data": {
            "emu_a15_oss_v14": "HERE WeGo 4.21.100 | 2 rows",
        },
        "notes": "One row per entry in com.here.app.maps/app_flutter/collection.place.box.hive, "
                 "a Hive box, which is the store the app's Flutter code uses for saved places. "
                 "The box is a sequence of frames, each ending in its own CRC32 over the rest of "
                 "the frame; every frame read here is checked against that CRC and a frame that "
                 "fails it stops the read, so a row is only produced from a frame the format's "
                 "own checksum accepts. "
                 "Saved is the entry's timestamp field, Unix milliseconds, reported as UTC. "
                 "Latitude and Longitude come from the entry's own coordinate object, so a saved "
                 "place is a coordinate an examiner can map, and KML output is produced. "
                 "Collection is resolved through collection.box.hive beside it. A collection there "
                 "carries its places as a list, and each place in that list repeats the entry id "
                 "the place box files the full record under, so the list is the join and it is "
                 "one the store itself records. Collection is blank when no collection lists that "
                 "entry id. A collection holding no places produces no row here, because this "
                 "artifact reports places. "
                 "The field names are not in the file. Hive writes a registered class as numbered "
                 "fields, and the names live in the app's compiled Dart, so each column here is "
                 "named from what the value was on data created for this purpose: a place saved "
                 "under a collection named for the test, whose title, address, coordinate, "
                 "category and category id were all known before the file was read. Fields that "
                 "held no value on the tested device are not reported. "
                 "A Hive box is append only, so an entry that was written more than once keeps "
                 "its earlier frames in the file. The current state is the last frame for a key, "
                 "which is what is reported, and Earlier Writes counts the superseded frames that "
                 "remain in the file for that key. "
                 "Entry Key is the key the box stores the entry under. Rows are box entries, not "
                 "distinct places: on the tested device one saved place was present under two "
                 "different entry keys with identical content, so a place can be counted twice.",
        "paths": ('*/com.here.app.maps/app_flutter/collection.place.box.hive',
                  '*/com.here.app.maps/app_flutter/collection.box.hive'),
        "output_types": "all",
        "artifact_icon": "star",
    },
    "here_wego_map_positions": {
        "name": "HERE WeGo Map Positions",
        "description": "The last device location and last map view HERE WeGo recorded",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "HERE WeGo",
        "sample_data": {
            "emu_a15_oss_v14": "HERE WeGo 4.21.100 | 2 rows",
        },
        "notes": "Up to two rows, read from the last_location and last_map_view_center values in "
                 "com.here.app.maps/shared_prefs/FlutterSharedPreferences.xml. "
                 "Last Location is a bare latitude and longitude pair the app stores for the "
                 "device's own last known position. Last Map View Center is a JSON object holding "
                 "the centre of the map the last time it was displayed, together with a distance "
                 "and a zoom level, which are reported as stored. "
                 "These are two different things and the notes are worth reading before either is "
                 "used. The first is where the app last placed the device. The second is where "
                 "the map was last looking, which a person can pan anywhere without going there. "
                 "On the tested device they differed, the map centre sitting about 2.7 kilometres "
                 "from the recorded device position. "
                 "Neither value carries a timestamp, so neither can be placed in time from this "
                 "file. KML output is produced for both.",
        "paths": ('*/com.here.app.maps/shared_prefs/FlutterSharedPreferences.xml',),
        "output_types": "all",
        "artifact_icon": "map-pin",
    },
    "here_wego_settings": {
        "name": "HERE WeGo Settings",
        "description": "HERE WeGo preferences, including whether the terms were accepted",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "HERE WeGo",
        "sample_data": {
            "emu_a15_oss_v14": "HERE WeGo 4.21.100 | 28 rows",
        },
        "notes": "One row per key in "
                 "com.here.app.maps/shared_prefs/FlutterSharedPreferences.xml, with the flutter. "
                 "prefix the Flutter plugin adds stripped from the reported name. Type is the XML "
                 "element the value was stored as. "
                 "Setting names are the app's own. is_terms_and_privacy_accepted records whether "
                 "the service terms were accepted, is_ftu_complete whether first time use "
                 "finished, and first_session_monthly_date carries a timestamp for the first "
                 "session that does end in Z and so is UTC, unlike the search timestamps in the "
                 "Recent Searches artifact. prefs_app_version carries the app version the "
                 "preferences were last written by. "
                 "recentSearchResults, last_location and last_map_view_center are reported by the "
                 "other three artifacts in this module and are skipped here, so that a long "
                 "encoded value does not sit in this table. Every other key is reported as "
                 "stored, including keys this module does not interpret, because the set of keys "
                 "changes between releases and an unrecognised one is still evidence of a "
                 "setting.",
        "paths": ('*/com.here.app.maps/shared_prefs/FlutterSharedPreferences.xml',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
}

import json
import os
import struct
import xml.etree.ElementTree as ET
import zlib

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc
from scripts.artifacts.storagePathViews import unique_files

PREFS_SUFFIX = 'shared_prefs/FlutterSharedPreferences.xml'
PLACE_BOX = 'app_flutter/collection.place.box.hive'
COLLECTION_BOX = 'app_flutter/collection.box.hive'

# Flutter's shared_preferences plugin prefixes a string list with this marker.
LIST_MARKER = 'VGhpcyBpcyB0aGUgcHJlZml4IGZvciBhIGxpc3Qu!'

# Reported by the other artifacts in this module rather than in the settings table.
SETTINGS_SKIP = ('recentSearchResults', 'last_location', 'last_map_view_center')

# Hive value type ids, from the format's own writer.
_NULL, _INT, _DOUBLE, _BOOL, _STRING, _BYTELIST = 0, 1, 2, 3, 4, 5
_INTLIST, _DOUBLELIST, _BOOLLIST, _STRINGLIST, _LIST, _MAP = 6, 7, 8, 9, 10, 11
_HIVELIST, _DATETIME = 12, 13

# Field numbers of a saved place, named from data created for the purpose. Hive stores a
# registered class as numbered fields and keeps the names in the app's compiled Dart.
PLACE_TIME, PLACE_ENTRY_ID, PLACE_TITLE = 1, 3, 4
PLACE_ADDRESS, PLACE_COORD, PLACE_ID, PLACE_AREA = 5, 6, 7, 8
PLACE_CATEGORY, PLACE_CATEGORY_ID = 9, 10
COORD_LAT, COORD_LON = 0, 1
COLLECTION_NAME, COLLECTION_ID, COLLECTION_PLACES = 3, 4, 5


def _prefs_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(PREFS_SUFFIX)]


def _box_files(context, suffix):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(suffix)]


def _prefs(path):
    """{name without the flutter. prefix: (element tag, value)} from one preferences file."""
    out = {}
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'HERE WeGo: could not read {os.path.basename(path)}: {ex}')
        return out
    for entry in root:
        name = entry.get('name')
        if not name:
            continue
        value = entry.get('value')
        if value is None:
            value = (entry.text or '').strip()
        out[name[8:] if name.startswith('flutter.') else name] = (entry.tag, value)
    return out


def _ms(value):
    if not value:
        return ''
    try:
        value = int(value)
        if value <= 0:
            return ''
        return convert_unix_ts_to_utc(value // 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _read_value(buf, index):
    """One Hive value at `index`, returning it and the index after it."""
    kind = buf[index]
    index += 1
    if kind == _NULL:
        return None, index
    if kind in (_INT, _DOUBLE, _DATETIME):
        number, = struct.unpack('<d', buf[index:index + 8])
        return (number if kind == _DOUBLE else int(number)), index + 8
    if kind == _BOOL:
        return bool(buf[index]), index + 1
    if kind in (_STRING, _BYTELIST):
        length, = struct.unpack('<I', buf[index:index + 4])
        index += 4
        chunk = buf[index:index + length]
        return (chunk.decode('utf-8', 'replace') if kind == _STRING else chunk), index + length
    if kind in (_INTLIST, _DOUBLELIST, _BOOLLIST, _STRINGLIST, _LIST, _MAP, _HIVELIST):
        count, = struct.unpack('<I', buf[index:index + 4])
        index += 4
        items = []
        for _ in range(count):
            if kind in (_INTLIST, _DOUBLELIST):
                number, = struct.unpack('<d', buf[index:index + 8])
                items.append(int(number) if kind == _INTLIST else number)
                index += 8
            elif kind == _BOOLLIST:
                items.append(bool(buf[index]))
                index += 1
            elif kind == _STRINGLIST:
                length, = struct.unpack('<I', buf[index:index + 4])
                index += 4
                items.append(buf[index:index + length].decode('utf-8', 'replace'))
                index += length
            else:
                item, index = _read_value(buf, index)
                items.append(item)
        return items, index
    # A registered class: a field count, then that many (field number, value) pairs.
    count = buf[index]
    index += 1
    obj = {}
    for _ in range(count):
        field = buf[index]
        index += 1
        obj[field], index = _read_value(buf, index)
    return obj, index


def _hive_entries(path):
    """The live entries of a Hive box, plus how many superseded frames each key has.

    Every frame carries a CRC32 of itself, so a frame that does not match is not read and
    the walk stops there rather than guessing at the rest of the file.
    """
    try:
        with open(path, 'rb') as handle:
            buf = handle.read()
    except OSError as ex:
        logfunc(f'HERE WeGo: could not read {os.path.basename(path)}: {ex}')
        return {}, {}
    live = {}
    earlier = {}
    offset = 0
    try:
        while offset + 4 <= len(buf):
            length, = struct.unpack('<I', buf[offset:offset + 4])
            if length < 8 or offset + length > len(buf):
                break
            frame = buf[offset:offset + length]
            stored, = struct.unpack('<I', frame[-4:])
            if (zlib.crc32(frame[:-4]) & 0xffffffff) != stored:
                logfunc(f'HERE WeGo: frame at offset {offset} of '
                        f'{os.path.basename(path)} failed its own CRC, stopping there')
                break
            index = 4
            key_kind = frame[index]
            index += 1
            if key_kind == 0:
                key, = struct.unpack('<I', frame[index:index + 4])
                index += 4
            else:
                key_length = frame[index]
                index += 1
                key = frame[index:index + key_length].decode('utf-8', 'replace')
                index += key_length
            value = None
            if index < length - 4:
                value, index = _read_value(frame, index)
            if key in live:
                earlier[key] = earlier.get(key, 0) + 1
            live[key] = value
            offset += length
    except (IndexError, struct.error, ValueError) as ex:
        logfunc(f'HERE WeGo: stopped reading {os.path.basename(path)} at offset {offset}: {ex}')
    return live, earlier


def _collection_names(context):
    """{place entry id: collection name}, the link the store itself records.

    A collection carries its places as a list of place objects, and each of those repeats
    the entry id the place box stores the full record under, so the list is the join.
    """
    names = {}
    for path in _box_files(context, COLLECTION_BOX):
        live, _ = _hive_entries(path)
        for value in live.values():
            if not isinstance(value, dict):
                continue
            name = value.get(COLLECTION_NAME) or ''
            for place in (value.get(COLLECTION_PLACES) or []):
                if isinstance(place, dict) and place.get(PLACE_ENTRY_ID):
                    names[place[PLACE_ENTRY_ID]] = name
    return names


@artifact_processor
def here_wego_recent_searches(context):
    data_list = []
    sources = []
    for path in _prefs_files(context):
        raw = _prefs(path).get('recentSearchResults', ('', ''))[1]
        if not raw or LIST_MARKER not in raw:
            continue
        try:
            entries = json.loads(raw.split('!', 1)[1])
        except (ValueError, IndexError) as ex:
            logfunc(f'HERE WeGo: could not read the recent search list: {ex}')
            continue
        found = False
        for entry in entries:
            try:
                item = json.loads(entry) if isinstance(entry, str) else entry
            except ValueError:
                continue
            if not isinstance(item, dict):
                continue
            data_list.append((
                item.get('timestamp') or '', item.get('title') or '',
                item.get('type') or '', item.get('placeId') or '',
                item.get('address') or '', item.get('category') or '',
                item.get('lat') if item.get('lat') is not None else '',
                item.get('lon') if item.get('lon') is not None else '',
                item.get('placeCategoryId') or '', item.get('href') or '',
                context.get_relative_path(path)))
            found = True
        if found and path not in sources:
            sources.append(path)

    data_headers = ('Searched (device local time)', 'Search Term', 'Type', 'Place ID',
                    'Address', 'Category', 'Latitude', 'Longitude',
                    'Place Category ID', 'Href', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def here_wego_saved_places(context):
    collections = _collection_names(context)
    data_list = []
    sources = []
    for path in _box_files(context, PLACE_BOX):
        live, earlier = _hive_entries(path)
        found = False
        for key, value in live.items():
            if not isinstance(value, dict):
                continue
            coord = value.get(PLACE_COORD)
            latitude = coord.get(COORD_LAT, '') if isinstance(coord, dict) else ''
            longitude = coord.get(COORD_LON, '') if isinstance(coord, dict) else ''
            area = value.get(PLACE_AREA)
            area_text = ''
            if isinstance(area, dict):
                area_text = ', '.join(str(area[k]) for k in sorted(area) if area[k])
            entry_id = value.get(PLACE_ENTRY_ID) or ''
            data_list.append((
                _ms(value.get(PLACE_TIME)), value.get(PLACE_TITLE) or '',
                value.get(PLACE_ADDRESS) or '', latitude, longitude,
                value.get(PLACE_CATEGORY) or '', value.get(PLACE_CATEGORY_ID) or '',
                collections.get(entry_id, ''), entry_id,
                area_text, value.get(PLACE_ID) or '',
                earlier.get(key, 0), key,
                context.get_relative_path(path)))
            found = True
        if found and path not in sources:
            sources.append(path)

    data_headers = (('Saved', 'datetime'), 'Title', 'Address',
                    'Latitude', 'Longitude',
                    'Category', 'Category ID', 'Collection', 'Place Entry ID',
                    'Area', 'Place ID', 'Earlier Writes', 'Entry Key', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def here_wego_map_positions(context):
    data_list = []
    sources = []
    for path in _prefs_files(context):
        values = _prefs(path)
        relative = context.get_relative_path(path)
        found = False
        raw = values.get('last_location', ('', ''))[1]
        if raw and ',' in raw:
            latitude, _, longitude = raw.partition(',')
            data_list.append(('Last Location', latitude.strip(), longitude.strip(),
                              '', '', relative))
            found = True
        raw = values.get('last_map_view_center', ('', ''))[1]
        if raw:
            try:
                centre = json.loads(raw)
            except ValueError:
                centre = {}
            position = str(centre.get('pos', ''))
            latitude, _, longitude = position.partition(',')
            data_list.append(('Last Map View Center', latitude.strip(), longitude.strip(),
                              centre.get('distance', ''), centre.get('zoomLevel', ''),
                              relative))
            found = True
        if found and path not in sources:
            sources.append(path)

    data_headers = ('Position', 'Latitude', 'Longitude',
                    'Distance (as stored)', 'Zoom Level (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def here_wego_settings(context):
    data_list = []
    sources = []
    for path in _prefs_files(context):
        values = _prefs(path)
        found = False
        for name in sorted(values):
            if name in SETTINGS_SKIP:
                continue
            tag, value = values[name]
            data_list.append((name, value, tag, context.get_relative_path(path)))
            found = True
        if found and path not in sources:
            sources.append(path)

    data_headers = ('Setting', 'Value', 'Type', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
