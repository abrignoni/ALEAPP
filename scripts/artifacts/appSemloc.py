# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_appSemloc": {
        "name": "App Semantic Locations",
        "description": "App Semantic Locations",
        "author": "Alexis 'Brigs' Brignoni",
        "creation_date": "2024/06/21",
        "last_update_date": "2024/06/21",
        "requirements": "",
        "category": "App Semantic Locations",
        "notes": "Thanks to Alex Caithness for the ccl_leveldb libraries",
        "paths": ('*/com.google.android.gms/app_semanticlocation_rawsignal_db/*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
    }
}

import datetime
import pathlib

import blackboxprotobuf

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
def get_appSemloc(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    in_dirs = set(pathlib.Path(str(x)).parent for x in files_found)
    for in_db_dir in in_dirs:
        source_path = str(in_db_dir)
        try:
            leveldb_records = ccl_leveldb.RawLevelDb(in_db_dir)
        except (ValueError, OSError):
            continue
        for record in leveldb_records.iterate_records_raw():
            try:
                value, _ = blackboxprotobuf.decode_message(record.value)
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
            data_list.append((timestamp, record.seq, latitude, longitude, accuracy, origin_pf))

    data_headers = (('Timestamp', 'datetime'), 'Rec. Sequence', 'Latitude', 'Longitude',
                    'Horizontal Acc.', 'Origin')
    return data_headers, data_list, source_path
