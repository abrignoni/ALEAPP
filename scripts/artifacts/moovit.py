__artifacts_v2__ = {
    "moovit_trip_plan_history": {
        "name": "Moovit Trip Plan History",
        "description": "Journeys planned in Moovit, with both endpoints and their coordinates",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Moovit",
        "sample_data": {
            "emu_a15_oss_v14": "Moovit 5.199.1.1804 | 2 rows",
        },
        "notes": "One row per entry of "
                 "com.tranzmate/app_moovit/data_trip_plan/history_trip_plan.ds, the file the app "
                 "keeps its planned journeys in. It is not SQLite and not JSON. It is Moovit's "
                 "own serialisation: a string is a four byte big endian character count followed "
                 "by that many UTF-16 big endian characters, a time is eight big endian bytes of "
                 "Unix milliseconds, and a place is a signed four byte latitude and a signed four "
                 "byte longitude, both big endian and both in millionths of a degree, written "
                 "immediately before the string that names it. "
                 "That reading of the coordinates was checked against places whose position was "
                 "known before the file was read, not inferred from the layout: on the tested "
                 "device the three endpoints decoded to 4, 14 and 116 metres from the published "
                 "positions of the building at the origin address and of the two destinations, "
                 "which a wrong scale or byte order would not do. "
                 "Planned is the entry's own time and is reported as UTC. Origin and Destination "
                 "are the addresses the app stored for the two ends of the journey; the origin "
                 "was the device's own position on the tested device, which the app resolves to a "
                 "street address, so an origin is not necessarily somewhere a person typed. "
                 "Latitude and Longitude are the destination's, and KML output plots the "
                 "destination only. The origin's coordinates are in their own two columns and are "
                 "not plotted, because a row holds two places and the KML writer takes one pair. "
                 "Itinerary ID is the entry's own identifier and is also the file name of the "
                 "saved itinerary under app_moovit/data_trip_plan/itinerary_entities and "
                 "raw_itinerary_entities beside this file, which is the link the store itself "
                 "records. Those itinerary files hold the full route, leg by leg, and are not "
                 "parsed here. "
                 "Metro Area ID is the app's own identifier for the transit region the journey "
                 "was planned in. It is reported as stored, and the name that goes with it is in "
                 "the metro_info table of databases/moovit_v1.db beside this file. "
                 "A row records that a journey was planned, not that it was travelled. Nothing "
                 "in this file says the route was followed.",
        "paths": ('*/com.tranzmate/app_moovit/data_trip_plan/history_trip_plan.ds',),
        "output_types": "all",
        "artifact_icon": "map",
    },
}

import os
import struct

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc
from scripts.artifacts.storagePathViews import unique_files

HISTORY_SUFFIX = 'app_moovit/data_trip_plan/history_trip_plan.ds'

# A Moovit string is a four byte big endian character count then UTF-16BE characters.
MAX_STRING = 4096
# Millionths of a degree, so a real place is inside these bounds.
MAX_LAT, MAX_LON = 90_000_000, 180_000_000
# Unix milliseconds, wide enough to hold any plausible entry.
MIN_MS, MAX_MS = 1_000_000_000_000, 4_000_000_000_000
# A UUID written as a string is this long.
UUID_LENGTH = 36


def _history_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(HISTORY_SUFFIX)]


def _string_at(buf, index):
    """The Moovit string starting at `index`, or None when one does not start there."""
    if index + 4 > len(buf):
        return None
    count = struct.unpack('>I', buf[index:index + 4])[0]
    if count == 0 or count > MAX_STRING or index + 4 + 2 * count > len(buf):
        return None
    try:
        text = buf[index + 4:index + 4 + 2 * count].decode('utf-16-be')
    except UnicodeDecodeError:
        return None
    if any(ord(character) < 32 for character in text):
        return None
    return text, index + 4 + 2 * count


def _place_at(buf, index):
    """(latitude, longitude, name, next index) when a place starts at `index`."""
    if index + 8 > len(buf):
        return None
    latitude, longitude = struct.unpack('>ii', buf[index:index + 8])
    if abs(latitude) > MAX_LAT or abs(longitude) > MAX_LON:
        return None
    if latitude == 0 and longitude == 0:
        return None
    found = _string_at(buf, index + 8)
    if not found:
        return None
    name, after = found
    return latitude / 1_000_000, longitude / 1_000_000, name, after


def _is_uuid(text):
    return len(text) == UUID_LENGTH and text.count('-') == 4


def _entries(buf):
    """Yield one journey per identifier in the file.

    The entries are laid out in a fixed order, so the walk follows it rather than
    scanning for whatever looks like a place: an identifier starts a journey, the next
    eight byte value in the millisecond range is its time, the next string is the metro
    area, and the next two places are the two ends of the journey. Everything after those
    is the app's own catalogue of route options, which is skipped by looking only for the
    next identifier.
    """
    index = 0
    current = None
    while index < len(buf) - 8:
        found = _string_at(buf, index)
        if found and _is_uuid(found[0]):
            if current:
                yield current
            current = {'id': found[0], 'time': None, 'metro': '', 'places': []}
            index = found[1]
            continue
        if current is None or len(current['places']) >= 2:
            index += 1
            continue
        if current['time'] is None:
            value = struct.unpack('>Q', buf[index:index + 8])[0]
            if MIN_MS < value < MAX_MS:
                current['time'] = value
                index += 8
                continue
            index += 1
            continue
        if not current['metro']:
            if found:
                current['metro'] = found[0]
                index = found[1]
            else:
                index += 1
            continue
        place = _place_at(buf, index)
        if place:
            current['places'].append(place[:3])
            index = place[3]
            continue
        index += 1
    if current:
        yield current


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


@artifact_processor
def moovit_trip_plan_history(context):
    data_list = []
    sources = []
    for path in _history_files(context):
        try:
            with open(path, 'rb') as handle:
                buf = handle.read()
        except OSError as ex:
            logfunc(f'Moovit: could not read {os.path.basename(path)}: {ex}')
            continue
        found = False
        for entry in _entries(buf):
            places = entry['places']
            if len(places) < 2:
                logfunc(f'Moovit: journey {entry["id"]} carried '
                        f'{len(places)} endpoints, so it is not reported')
                continue
            (origin_lat, origin_lon, origin), (dest_lat, dest_lon, dest) = places[0], places[1]
            data_list.append((
                _ms(entry['time']), origin.rstrip(', '), dest.rstrip(', '),
                dest_lat, dest_lon, origin_lat, origin_lon,
                entry['metro'], entry['id'], context.get_relative_path(path)))
            found = True
        if found and path not in sources:
            sources.append(path)

    data_headers = (('Planned', 'datetime'), 'Origin', 'Destination',
                    'Latitude', 'Longitude', 'Origin Latitude', 'Origin Longitude',
                    'Metro Area ID', 'Itinerary ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
