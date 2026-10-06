# pylint: disable=W0718
__artifacts_v2__ = {
    "get_appSemloc": {
        "name": "App Semantic Locations",
        "description": "Decoded nested protobuf fields and record provenance from Google Play services' semantic-location LevelDB.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2024/06/21",
        "last_update_date": "2026-10-06",
        "requirements": "",
        "category": "App Semantic Locations",
        "notes": "Thanks to Alex Caithness for the ccl_leveldb libraries. Raw Nested Field values "
                 "come from field 1 within field 1 of each decoded record value; raw means decoded "
                 "protobuf values, not wire bytes or independently established signedness. Field "
                 "meanings and units are undocumented here. The prior parser read field 6 as Unix "
                 "milliseconds, fields 1 and 2 divided by 10000000 as coordinates and field 3 divided "
                 "by 1000 as horizontal accuracy. These derivations are retained with neutral labels, "
                 "without asserting their meaning or producing coordinate exports. All versions that "
                 "decode under the existing field checks are retained. Record Operation State is the "
                 "ccl record flag: Live does not establish that a version is current. No latest-key "
                 "selection is performed. Record Key Hex preserves the full key, including the internal "
                 "LDB trailer when present. Undecodable values and tombstones without the required "
                 "nested fields are not output. Source File appears only when returned rows combine "
                 "database directories. Recorded sample counts do not verify field semantics.",
        "paths": ('*/com.google.android.gms/app_semanticlocation_rawsignal_db/*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 6651 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 1497 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 5033 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 1324 rows",
        },
    }
}

import datetime
import pathlib

from scripts.ilapfuncs import decode_protobuf

from scripts.ccl import ccl_leveldb
from scripts.ilapfuncs import artifact_processor


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_appSemloc(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []
    in_dirs = dict.fromkeys(pathlib.Path(str(x)).parent for x in files_found)
    for in_db_dir in in_dirs:
        try:
            leveldb_records = ccl_leveldb.RawLevelDb(in_db_dir)
        except (ValueError, OSError):
            continue
        with leveldb_records:
            for record in leveldb_records.iterate_records_raw():
                try:
                    value, _ = decode_protobuf(record.value)
                except Exception:
                    continue
                outer = value.get('1') if isinstance(value, dict) else None
                latlongrecord = outer.get('1') if isinstance(outer, dict) else None
                if not isinstance(latlongrecord, dict):
                    continue
                try:
                    timestamp = _ms_to_utc(latlongrecord['6'])
                    latitude = latlongrecord['1'] / 1e7
                    longitude = latlongrecord['2'] / 1e7
                    accuracy = latlongrecord['3'] / 1000
                except (KeyError, TypeError):
                    continue
                origin = str(record.origin_file)
                origin_pf = f'{pathlib.Path(origin).parent.name}/{pathlib.Path(origin).name}'
                data_list.append((timestamp, latlongrecord['6'], record.seq, record.key.hex(),
                                  record.state.name, record.file_type.name, latlongrecord['1'],
                                  latlongrecord['2'], latlongrecord['3'], latitude, longitude,
                                  accuracy, origin_pf, context.get_relative_path(origin)))
                if str(in_db_dir) not in sources:
                    sources.append(str(in_db_dir))

    data_headers = (('Field 6 as Unix Milliseconds (Unverified)', 'datetime'),
                    'Raw Nested Field 6', 'Rec. Sequence', 'Record Key Hex',
                    'Record Operation State', 'Record File Type', 'Raw Nested Field 1',
                    'Raw Nested Field 2', 'Raw Nested Field 3', 'Field 1 / 10000000',
                    'Field 2 / 10000000', 'Field 3 / 1000', 'Origin')
    if len(sources) > 1:
        data_headers += ('Source File',)
    else:
        data_list = [row[:-1] for row in data_list]
    return data_headers, data_list, '\n'.join(sources)
