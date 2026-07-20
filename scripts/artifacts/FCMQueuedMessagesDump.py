# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_fcm_dump": {
        "name": "FCM Dump",
        "description": "All records from the fcm_queued_messages.ldb leveldb (com.google.android.gms)",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-07-28",
        "last_update_date": "2022-07-28",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 5647 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 512 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 31046 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 38204 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 35523 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 5010 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 3914 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 36746 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 11408 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 2016 rows",
        },
    },
    "get_fcm_dump_verizon": {
        "name": "FCM Decoded - Verizon",
        "description": "Decoded Verizon Messages FCM queued message payloads",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-07-28",
        "last_update_date": "2022-07-28",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "get_fcm_dump_tiktok": {
        "name": "FCM Decoded - TikTok",
        "description": "Decoded TikTok (com.zhiliaoapp.musically) FCM queued message payloads",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-07-28",
        "last_update_date": "2022-07-28",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 225 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 32 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 475 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 433 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 102 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 40 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 391 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 86 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 142 rows",
        },
    },
    "get_fcm_dump_instagram": {
        "name": "FCM Decoded - Instagram",
        "description": "Decoded Instagram FCM queued message payloads",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-07-28",
        "last_update_date": "2022-07-28",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 33 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "get_fcm_dump_gqsb": {
        "name": "FCM Decoded - Geolocation",
        "description": "Geolocation recovered from Google Quick Search Box FCM queued messages",
        "author": "Alex Caithness (research [at] cclsolutionsgroup.com)",
        "creation_date": "2022-07-28",
        "last_update_date": "2022-07-28",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "",
        "paths": ('*/fcm_queued_messages.ldb/*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 29 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 53 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 54 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    }
}

import base64
import datetime
import gzip
import json
import pathlib

import blackboxprotobuf

from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.ilapfuncs import artifact_processor, logfunc

GQSB_TYPEDEF = {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'fixed64', 'name': ''}}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'fixed64', 'name': ''}}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {}, 'name': ''}, '6': {'type': 'int', 'name': ''}}, 'name': ''}, '5': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'bytes', 'name': ''}}, 'name': ''}, '6': {'type': 'message', 'message_typedef': {'3': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}, '4': {'type': 'int', 'name': ''}}, 'name': ''}, '7': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '7': {'type': 'int', 'name': ''}, '8': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '7': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'double', 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'bytes', 'name': ''}}, 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '8': {'type': 'bytes', 'name': ''}, '11': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}, '12': {'type': 'bytes', 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '16': {'type': 'int', 'name': ''}, '17': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '20': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '8': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'message', 'message_typedef': {'1': {'type': 'fixed64', 'name': ''}, '2': {'type': 'fixed64', 'name': ''}, '3': {'type': 'bytes', 'name': ''}}, 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '8': {'type': 'bytes', 'name': ''}, '11': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}, '3': {'type': 'int', 'name': ''}, '6': {'type': 'int', 'name': ''}, '10': {'type': 'message', 'message_typedef': {}, 'name': ''}, '11': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '14': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'bytes', 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '5': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '6': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '7': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '8': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '9': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '10': {'type': 'message', 'message_typedef': {'5': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'fixed32', 'name': ''}, '3': {'type': 'fixed32', 'name': ''}}, 'name': ''}}, 'name': ''}, '15': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '18': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}}

_CACHE = {}


def _to_utc(value):
    if not isinstance(value, datetime.datetime):
        return value if value else ''
    if value.tzinfo is None:
        return value.replace(tzinfo=datetime.timezone.utc)
    return value.astimezone(datetime.timezone.utc)


def _load_packages(files_found):
    cache_key = tuple(sorted(str(f) for f in files_found))
    if cache_key in _CACHE:
        return _CACHE[cache_key]
    in_dirs = set(pathlib.Path(str(x)).parent for x in files_found)
    package_tables = {}
    source = ''
    for in_db_dir in in_dirs:
        source = str(in_db_dir)
        try:
            with FcmIterator(in_db_dir) as iterator:
                for record in iterator:
                    for k, v in record.key_values.items():
                        package_tables.setdefault(record.package, []).append(
                            [record.timestamp, pathlib.Path(record.originating_file).name, record.key, k, v])
        except Exception as exc:
            logfunc(f'FCM: error reading {in_db_dir}: {exc}')
    _CACHE[cache_key] = (package_tables, source)
    return package_tables, source


@artifact_processor
def get_fcm_dump(files_found, report_folder, seeker, wrap_text):
    package_tables, source = _load_packages(files_found)
    data_list = []
    for package, rows in package_tables.items():
        for row in rows:
            data_list.append((package, _to_utc(row[0]), row[1], row[2], row[3], row[4]))
    data_headers = ('Package', ('Timestamp', 'datetime'), 'Originating File', 'Record ID', 'Key', 'Value')
    return data_headers, data_list, source


@artifact_processor
def get_fcm_dump_verizon(files_found, report_folder, seeker, wrap_text):
    package_tables, source = _load_packages(files_found)
    data_list = []
    for data in package_tables.get('com.verizon.messaging.vzmsgs', []):
        fecha, origfile, llave, datos = data[0], data[1], data[3], data[4]
        if llave == 'message':
            try:
                datos = base64.b64decode(str(datos).encode('ascii')).decode('ascii')
            except Exception:
                datos = data[4]
        data_list.append((_to_utc(fecha), origfile, llave, datos))
    data_headers = (('Timestamp', 'datetime'), 'Originating File', 'Key', 'Value')
    return data_headers, data_list, source


@artifact_processor
def get_fcm_dump_tiktok(files_found, report_folder, seeker, wrap_text):
    package_tables, source = _load_packages(files_found)
    data_list = []
    for data in package_tables.get('com.zhiliaoapp.musically', []):
        fecha, origfile, llave, datos = data[0], data[1], data[3], data[4]
        if llave == 'payload':
            try:
                datos = json.loads(datos)
            except Exception:
                logfunc('FCM TikTok: error reading json data')
            if isinstance(datos, dict):
                data_list.append((_to_utc(fecha), origfile, datos.get('text'), datos.get('title')))
    data_headers = (('Timestamp', 'datetime'), 'Originating File', 'Data', 'Title')
    return data_headers, data_list, source


@artifact_processor
def get_fcm_dump_instagram(files_found, report_folder, seeker, wrap_text):
    package_tables, source = _load_packages(files_found)
    data_list = []
    for data in package_tables.get('com.instagram.android', []):
        fecha, origfile, fcm_key, datos = data[0], data[1], data[2], data[4]
        try:
            datos = json.loads(datos)
        except Exception:
            pass
        if isinstance(datos, dict):
            if 'collapse_key' in datos:
                ntype = datos['collapse_key']
            elif 'c' in datos:
                ntype = datos['c']
            else:
                continue
            data_list.append((_to_utc(fecha), origfile, ntype, datos.get('m'), datos.get('s'),
                              datos.get('u'), fcm_key, datos.get('PushNotifID'), datos.get('ig')))
    data_headers = (('Timestamp', 'datetime'), 'Originating File', 'Data', 'M', 'S', 'U',
                    'FCM Key', 'Push Notification ID', 'IG Endpoint')
    return data_headers, data_list, source


@artifact_processor
def get_fcm_dump_gqsb(files_found, report_folder, seeker, wrap_text):
    package_tables, source = _load_packages(files_found)
    data_list = []
    for data in package_tables.get('com.google.android.googlequicksearchbox', []):
        fecha, origfile, llave, datos = data[0], data[1], data[3], data[4]
        if llave != 'casp':
            continue
        try:
            datos = base64.b64decode(datos)
            values, _ = blackboxprotobuf.decode_message(datos)
            values = values['3']
            try:
                smartspacecheck = values['3'].decode()
            except Exception:
                smartspacecheck = values['3']
            if 'Smartspace' in smartspacecheck:
                values = values['14']['2']['13']['2']
                values = gzip.decompress(values)
                values, _ = blackboxprotobuf.decode_message(values)
                url = values['2']['14'].decode()
                lat = url.split('?')[1].split('lat=')[1].split('&')[0]
                lon = url.split('?')[1].split('lat=')[1].split('&')[1].split('lon=')[1]
                data_list.append((_to_utc(fecha), lat, lon, url, origfile))

            tomorrow = values.get('12', None)
            if tomorrow is not None:
                tomorrow = values['12']['1']
                if isinstance(tomorrow, bytes):
                    tomorrow = tomorrow.decode()
                    if 'Tomorrow' in tomorrow:
                        try:
                            values = values['14']['2']['20']
                            values = gzip.decompress(values)
                            values, _ = blackboxprotobuf.decode_message(values, GQSB_TYPEDEF)
                            lat = values['1']['7']['1']['8']['7']['2']['1']
                            lon = values['1']['7']['1']['8']['7']['2']['2']
                            city = values['1']['7']['1']['8']['7']['2']['3'].decode()
                            data_list.append((_to_utc(fecha), lat, lon, city, origfile))
                        except Exception:
                            pass
        except Exception:
            pass

    data_headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'URL or Location', 'Originating File')
    return data_headers, data_list, source
