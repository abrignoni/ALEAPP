__artifacts_v2__ = {
    "gmsOdlhSemanticSegments": {
        "name": "ODLH Semantic Segments",
        "description": "Time-bounded segments stored by Google's On Device Location "
                       "History (odlh-storage.db, semantic_segment_table). For segments "
                       "whose semantic_segment protobuf embeds a coordinate pair the "
                       "latitude and longitude are decoded; for activity segments the start "
                       "and end coordinates, the activity type and three undocumented values "
                       "read as a distance and two probabilities (see notes) are decoded, "
                       "and for path segments the number of path points is given "
                       "(the points are in ODLH Path Points). The segment type is stored "
                       "as a raw integer and is reported as-is.",
        "author": "@abrignoni, Heather Charpentier, Claude",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-10-16",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "Coordinates are read as E7 fixed-point integers inside the protobuf. "
                 "The pair is read from protobuf path 3.1.4.5, fields 1 and 2, and a "
                 "value above 2**31 is wrapped to a negative number. What the pair "
                 "represents is not established here; it is reported as decoded. "
                 "Activity columns are read only where the protobuf has path 3.2: start "
                 "coordinates from 3.2.1 and end coordinates from 3.2.2 (E7, fields 1 "
                 "and 2), distance from 3.2.3, activity probability from 3.2.4, activity "
                 "type from 3.2.6.1 and its probability from 3.2.6.2. Distance and the "
                 "probabilities are fixed32 values read as 32-bit floats. No "
                 "documentation for these fields was found, so \"distance\" and "
                 "\"probability\" are working labels taken from the value ranges, not "
                 "from a source. The activity type is Google's number, reported "
                 "as stored; its meaning is not established here. On the six tested "
                 "images holding ODLH data (anne_a15, hc_pixel8pro_a16, kevin_pocox7_a15, "
                 "pixel7a_a14, russell_pixel6a_a13, userb2_a13; 1,035 activities), the "
                 "start pair was within 600 m of the preceding visit for 941 of the 1,033 "
                 "activities that had one, and the end pair within 600 m of the following "
                 "visit for 933 of 1,035. With the mean Earth radius (6,371,008.8 m) no "
                 "distance was below the straight-line distance in meters between the "
                 "start and end pairs, and 148 of 1,035 were within 0.1 percent of it, so "
                 "the comparison depends on the radius used; the 3 activities whose pairs "
                 "were identical stored 0. This is consistent with meters, but the unit "
                 "is not established, so the column is labelled as stored. Both "
                 "probability values ranged from 0.0 to 0.9998 on those images. Path Point Count is the number of coordinate pairs stored at "
                 "3.3.4 and 3.3.5; the points are reported in ODLH Path Points. Activity "
                 "and path fields are read from the protobuf wire format, because the "
                 "type-guessing decoder used for visits read the packed path fields of "
                 "403 of the 4,757 path segments on those images as nested messages. On "
                 "the same images segment types 1, 2 and 3 were the only ones holding "
                 "paths 3.1, 3.2 and 3.3 respectively, Shown In Timeline and Is "
                 "Finalized held no value (NULL) on every row, and Obfuscated GAIA ID "
                 "held one value per image. "
                 "Reference: Cellebrite, 'Location Booklet 2025'; no URL or page is "
                 "recorded here for it.",
        "paths": ('*/com.google.android.gms/databases/odlh-storage.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 545 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 605 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 3251 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 2102 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 393 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 127 rows",
        },
    },
    "gmsOdlhEditedSegments": {
        "name": "ODLH Edited Segments",
        "description": "Entries in the edited_segment_table of Google's On Device Location "
                       "History (odlh-storage.db): segment time ranges with the block range "
                       "they belong to and the is_edit_uploaded value as stored.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "",
        "paths": ('*/com.google.android.gms/databases/odlh-storage.db*',),
        "output_types": "standard",
        "artifact_icon": "edit",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 112 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 61 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 184 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "gmsOdlhPathPoints": {
        "name": "ODLH Path Points",
        "description": "Coordinate points of the path segments stored by Google's On Device "
                       "Location History (odlh-storage.db, semantic_segment_table), one row "
                       "per point, with a time derived from the segment start and the "
                       "point's stored offset, read as minutes (see notes).",
        "author": "Heather Charpentier, Claude",
        "creation_date": "2026-10-14",
        "last_update_date": "2026-10-16",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "Read from segments whose semantic_segment protobuf has path 3.3. Field "
                 "3.3.4 holds packed little-endian 32-bit latitudes and 3.3.5 the matching "
                 "longitudes, both E7 fixed-point; field 3.3.6 holds packed varint "
                 "offsets, reported in Minute Offset (as stored). Point Time is not "
                 "stored: it is the segment's start_timestamp_seconds plus the offset "
                 "times 60, so it has whole-minute resolution from the segment start. "
                 "Where a point has no offset, Point Time is empty (not seen on the "
                 "tested images). No documentation of the offset unit was found. On the six tested images holding ODLH data (4,757 path "
                 "segments, 42,285 points) every segment stored one offset per point, the "
                 "offsets never decreased within a segment, none placed a point after the "
                 "segment end, and the median last offset fell between 0.62 and 0.96 of "
                 "the segment duration per image, which fits minutes and not seconds. "
                 "The protobuf's own start second (field 1.1) equalled "
                 "start_timestamp_seconds on every path segment. Obfuscated GAIA ID held one value per image. The points "
                 "are what the segment stores; whether they are every fix Google "
                 "recorded or a reduced route is not established here.",
        "paths": ('*/com.google.android.gms/databases/odlh-storage.db*',),
        "output_types": "all",
        "artifact_icon": "route",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 3919 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 8056 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 15036 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 14207 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 904 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 163 rows",
        },
    },
}

import re
import struct

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc, decode_protobuf


def _unique_db_files(context, name_suffix):
    '''Database files matching the suffix, without -journal/-wal/-shm sidecars and
    without the duplicates extractions carry for the same file (data_mirror, and
    /data/data next to /data/user/0).

    The dedupe key is the evidence-relative path, not the extracted path: the report's own
    data folder ends in /data, so a raw-path replace can rewrite the harness boundary
    instead of the evidence path on archives whose members start with data/.'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(name_suffix):
            continue
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if 'data_mirror' in relative:
            continue
        normalized = re.sub(r'(^|/)data/data/', r'\1data/user/0/', relative)
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(file_found)
    return result


def _pb_get(node, *path):
    '''Defensively walk a blackboxprotobuf dict.'''
    cur = node
    for key in path:
        if isinstance(cur, list):
            cur = cur[0] if cur else None
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _e7_to_deg(value, limit):
    '''E7 fixed-point coordinate stored as an unsigned varint; negative values wrap.'''
    if not isinstance(value, int):
        return ''
    if value > 2**31:
        value -= 2**32
    degrees = value / 1e7
    if abs(degrees) > limit:
        return ''
    return degrees


def _lat_lon(point):
    '''(latitude, longitude) of an E7 pair message, or ('', '').'''
    if not isinstance(point, dict):
        return '', ''
    latitude = _e7_to_deg(point.get('1'), 90)
    longitude = _e7_to_deg(point.get('2'), 180)
    if latitude == '' or longitude == '':
        return '', ''
    return latitude, longitude


def _packed_e7(data, limit):
    '''Packed little-endian 32-bit E7 values; an out-of-range value becomes ''.'''
    if not isinstance(data, bytes):
        return []
    values = []
    for (value,) in struct.iter_unpack('<i', data[:len(data) // 4 * 4]):
        degrees = value / 1e7
        values.append(degrees if abs(degrees) <= limit else '')
    return values


def _packed_varints(data):
    '''Packed unsigned varints.'''
    if not isinstance(data, bytes):
        return []
    values, value, shift = [], 0, 0
    for byte in data:
        value |= (byte & 0x7F) << shift
        shift += 7
        if byte < 0x80:
            values.append(value)
            value, shift = 0, 0
    return values


def _segment_coordinates(blob):
    '''Lat/long of the place coordinate a semantic_segment protobuf embeds, if any.'''
    try:
        info, _ = decode_protobuf(blob)
    except Exception:  # pylint: disable=broad-exception-caught
        return '', ''
    return _lat_lon(_pb_get(info, '3', '1', '4', '5'))


def _wire_fields(data):
    '''{field number: [value, ...]} of one protobuf message read from the wire format:
    varints as int, length-delimited fields as bytes, fixed64 / fixed32 as raw bytes.
    Unlike a type-guessing decoder, a length-delimited field is never reinterpreted as a
    nested message. Raises ValueError on a malformed message.'''
    fields, i = {}, 0

    def varint():
        nonlocal i
        value = shift = 0
        while True:
            if i >= len(data):
                raise ValueError('truncated varint')
            byte = data[i]
            i += 1
            value |= (byte & 0x7F) << shift
            shift += 7
            if byte < 0x80:
                return value

    while i < len(data):
        key = varint()
        number, wire_type = key >> 3, key & 7
        if wire_type == 0:
            value = varint()
        elif wire_type in (1, 2, 5):
            size = 8 if wire_type == 1 else 4 if wire_type == 5 else varint()
            if i + size > len(data):
                raise ValueError('truncated field')
            value = data[i:i + size]
            i += size
        else:
            raise ValueError(f'unsupported wire type {wire_type}')
        fields.setdefault(number, []).append(value)
    return fields


def _wire_message(fields, number):
    '''The first length-delimited field with that number, read as a message, or {}.'''
    value = (fields.get(number) or [None])[0]
    if not isinstance(value, bytes):
        return {}
    try:
        return _wire_fields(value)
    except ValueError:
        return {}


def _wire_float(fields, number):
    '''A fixed32 field read as a 32-bit float, or ''.'''
    value = (fields.get(number) or [None])[0]
    return struct.unpack('<f', value)[0] if isinstance(value, bytes) and len(value) == 4 else ''


def _wire_lat_lon(point):
    '''(latitude, longitude) of an E7 pair message with fixed32 fields 1 and 2, or ('', '').'''
    values = []
    for number, limit in ((1, 90), (2, 180)):
        value = (point.get(number) or [None])[0]
        if not isinstance(value, bytes) or len(value) != 4:
            return '', ''
        degrees = struct.unpack('<i', value)[0] / 1e7
        if abs(degrees) > limit:
            return '', ''
        values.append(degrees)
    return tuple(values)


def _segment_body(blob, kind):
    '''The message at path 3.<kind> of a semantic_segment protobuf, read from the wire
    format, or {}.'''
    if not isinstance(blob, bytes):
        return {}
    try:
        top = _wire_fields(blob)
    except ValueError:
        return {}
    return _wire_message(_wire_message(top, 3), kind)


def _activity_columns(blob):
    '''Start lat/long, end lat/long, distance, activity type, type probability and
    activity probability of an activity segment (path 3.2); empty strings otherwise.'''
    activity = _segment_body(blob, 2)
    if not activity:
        return ('',) * 8
    kind = _wire_message(activity, 6)
    kind_type = (kind.get(1) or [None])[0]
    return (*_wire_lat_lon(_wire_message(activity, 1)), *_wire_lat_lon(_wire_message(activity, 2)),
            _wire_float(activity, 3),
            kind_type if isinstance(kind_type, int) else '',
            _wire_float(kind, 2),
            _wire_float(activity, 4))


def _path_points(blob):
    '''[(latitude, longitude, minute offset or None), ...] of a path segment (path 3.3),
    read from the wire format so packed fields are never mistaken for messages.'''
    path = _segment_body(blob, 3)
    if not path:
        return []

    def first(number):
        return (path.get(number) or [None])[0]

    latitudes = _packed_e7(first(4), 90)
    longitudes = _packed_e7(first(5), 180)
    offsets = _packed_varints(first(6))
    return [(lat, lon, offsets[i] if i < len(offsets) else None)
            for i, (lat, lon) in enumerate(zip(latitudes, longitudes))]


@artifact_processor
def gmsOdlhSemanticSegments(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'odlh-storage.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT start_timestamp_seconds, end_timestamp_seconds, segment_type,
                   semantic_segment, shown_in_timeline, is_finalized, hierarchy_level,
                   segment_id, obfuscated_gaia_id
            FROM semantic_segment_table
            ORDER BY start_timestamp_seconds DESC, semantic_segment_table.rowid
        ''')

        for row in db_records:
            source_path = file_found
            latitude, longitude = _segment_coordinates(row[3])
            points = _path_points(row[3])
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                convert_unix_ts_to_utc(row[1]),
                row[2],
                latitude,
                longitude,
                *_activity_columns(row[3]),
                len(points) if points else '',
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
            ))

    data_headers = (
        ('Start Time', 'datetime'),
        ('End Time', 'datetime'),
        'Segment Type',
        'Latitude',
        'Longitude',
        'Activity Start Latitude',
        'Activity Start Longitude',
        'Activity End Latitude',
        'Activity End Longitude',
        'Activity Distance (as stored)',
        'Activity Type (as stored)',
        'Activity Type Probability (as stored)',
        'Activity Probability (as stored)',
        'Path Point Count',
        'Shown In Timeline',
        'Is Finalized',
        'Hierarchy Level',
        'Segment ID',
        'Obfuscated GAIA ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def gmsOdlhPathPoints(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'odlh-storage.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT start_timestamp_seconds, end_timestamp_seconds, semantic_segment,
                   segment_id, obfuscated_gaia_id
            FROM semantic_segment_table
            ORDER BY start_timestamp_seconds DESC, semantic_segment_table.rowid
        ''')

        for row in db_records:
            source_path = file_found
            points = _path_points(row[2])
            try:
                start = int(row[0])
            except (TypeError, ValueError):
                start = None
            for number, (latitude, longitude, offset) in enumerate(points, 1):
                point_time = convert_unix_ts_to_utc(start + offset * 60) \
                    if start is not None and offset is not None else ''
                data_list.append((
                    point_time,
                    convert_unix_ts_to_utc(row[0]),
                    convert_unix_ts_to_utc(row[1]),
                    latitude,
                    longitude,
                    offset if offset is not None else '',
                    number,
                    len(points),
                    row[3],
                    row[4],
                ))

    data_headers = (
        ('Point Time', 'datetime'),
        ('Segment Start Time', 'datetime'),
        ('Segment End Time', 'datetime'),
        'Latitude',
        'Longitude',
        'Minute Offset (as stored)',
        'Point Number',
        'Points In Segment',
        'Segment ID',
        'Obfuscated GAIA ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def gmsOdlhEditedSegments(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'odlh-storage.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT start_timestamp_seconds, end_timestamp_seconds,
                   block_start_timestamp_seconds, block_end_timestamp_seconds,
                   segment_type, is_edit_uploaded, segment_id, obfuscated_gaia_id
            FROM edited_segment_table
            ORDER BY start_timestamp_seconds DESC
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                convert_unix_ts_to_utc(row[1]),
                convert_unix_ts_to_utc(row[2]),
                convert_unix_ts_to_utc(row[3]),
                row[4],
                row[5],
                row[6],
                row[7],
            ))

    data_headers = (
        ('Start Time', 'datetime'),
        ('End Time', 'datetime'),
        ('Block Start Time', 'datetime'),
        ('Block End Time', 'datetime'),
        'Segment Type',
        'Is Edit Uploaded',
        'Segment ID',
        'Obfuscated GAIA ID',
    )
    return data_headers, data_list, source_path
