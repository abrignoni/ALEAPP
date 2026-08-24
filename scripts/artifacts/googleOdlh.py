__artifacts_v2__ = {
    "gmsOdlhSemanticSegments": {
        "name": "ODLH Semantic Segments",
        "description": "Time-bounded segments stored by Google's On Device Location "
                       "History (odlh-storage.db, semantic_segment_table). For segments "
                       "whose semantic_segment protobuf embeds a coordinate pair the "
                       "latitude and longitude are decoded; the segment type is stored "
                       "as a raw integer and is reported as-is.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "Coordinates are stored as E7 fixed-point integers inside the protobuf "
                 "and were validated against multiple test images. Reference: Cellebrite "
                 "Location Booklet 2025.",
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
                       "they belong to and whether the edit was uploaded.",
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
}

import re

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


def _segment_coordinates(blob):
    '''Lat/long of the place coordinate a semantic_segment protobuf embeds, if any.'''
    try:
        info, _ = decode_protobuf(blob)
    except Exception:  # pylint: disable=broad-exception-caught
        return '', ''
    point = _pb_get(info, '3', '1', '4', '5')
    if not isinstance(point, dict):
        return '', ''
    latitude = _e7_to_deg(point.get('1'), 90)
    longitude = _e7_to_deg(point.get('2'), 180)
    if latitude == '' or longitude == '':
        return '', ''
    return latitude, longitude


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
            ORDER BY start_timestamp_seconds DESC
        ''')

        for row in db_records:
            source_path = file_found
            latitude, longitude = _segment_coordinates(row[3])
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                convert_unix_ts_to_utc(row[1]),
                row[2],
                latitude,
                longitude,
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
        'Shown In Timeline',
        'Is Finalized',
        'Hierarchy Level',
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
