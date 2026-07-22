# pylint: disable=W0718
__artifacts_v2__ = {
    "get_sharedProto": {
        "name": "Shared Proto Data",
        "description": "Shared Proto data from Samsung Browser",
        "author": "@AlexisBrignoni",
        "creation_date": "2024-07-23",
        "last_update_date": "2024-07-23",
        "requirements": "none",
        "category": "Samsung Browser",
        "notes": "",
        "paths": ('*/data/com.sec.android.app.sbrowser/app_sbrowser/Default/shared_proto_db/*',),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.sbrowser vc 1280509502 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.sec.android.app.sbrowser vc 1300067502 | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.sbrowser vc 1260103502 | 261 rows",
        },
    }
}

import datetime
import pathlib

from scripts.ilapfuncs import decode_protobuf

from scripts.ccl import ccl_leveldb
from scripts.ilapfuncs import artifact_processor, logfunc


def _win_to_utc(value):
    '''Field 16 is milliseconds since the 1601 (Windows FILETIME) epoch.'''
    try:
        return (datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
                + datetime.timedelta(seconds=int(value) / 1000))
    except (ValueError, TypeError, OverflowError, OSError):
        return ''


def _txt(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')
    return value if value is not None else ''


@artifact_processor
def get_sharedProto(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    in_dirs = set(pathlib.Path(str(x)).parent for x in files_found)
    for in_db_dir in in_dirs:
        source_path = str(in_db_dir)
        try:
            leveldb_records = ccl_leveldb.RawLevelDb(in_db_dir)
        except Exception as exc:
            logfunc(f'Shared Proto: could not open leveldb {in_db_dir}: {exc}')
            continue

        for record in leveldb_records.iterate_records_raw():
            origin = str(record.origin_file)
            pf = f'{pathlib.Path(origin).parent.name}/{pathlib.Path(origin).name}'
            try:
                record_key = record.user_key.decode('utf-8', 'replace')
                protostuff, _ = decode_protobuf(record.value)
            except Exception:
                continue
            outer = protostuff.get('1')
            if not isinstance(outer, dict) or not isinstance(outer.get('4'), dict):
                continue
            four = outer['4']
            try:
                urlone = four['1']
                if isinstance(urlone, list):
                    agg = '\n'.join(_txt(u) for u in urlone)
                else:
                    agg = _txt(urlone)
                timestamp_b = _txt(four.get('9', ''))
                timestamp = _win_to_utc(four['16']) if four.get('16') else ''
                data_list.append((timestamp, timestamp_b, record_key, record.seq, agg,
                                  _txt(four.get('4')), _txt(four.get('2')), _txt(four.get('13')), pf))
            except (KeyError, ValueError, TypeError, AttributeError):
                continue

    data_headers = (('Timestamp', 'datetime'), 'Timestamp B', 'Record Key', 'Record Sequence',
                    'URL One', 'URL Two', 'Domain', 'Data', 'Origin')
    return data_headers, data_list, source_path
