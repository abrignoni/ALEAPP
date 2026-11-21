__artifacts_v2__ = {
    "googleMapsSyncPlaces": {
        "name": "Google Maps Sync - Places",
        "description": "Place records from the sync_item_data table of Google Maps' gmm_sync.db, "
                       "corpus 11 and 14: the row's timestamp and coordinates, and the name or label "
                       "text, address and stored id decoded from each record's item_proto.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Google Maps",
        "notes": "Reads the sync_item_data rows of corpus 11 and 14 from each gmm_sync.db, one row per "
                 "record. What the corpus numbers denote is not established; the artifact is named for "
                 "what their records were observed to hold. item_proto is decoded without a schema. "
                 "Timestamp is the row's timestamp column read as Unix milliseconds; what event it marks "
                 "is not established. It was 0, shown blank, on 7 of the 15 tested corpus 11 rows, and on "
                 "the 5 tested corpus 14 records that carry field 10 of the place message (seconds and "
                 "nanos) it equalled that value. Latitude and Longitude are latitude_e6 and longitude_e6 divided "
                 "by 1,000,000; on every tested record that also carries coordinates inside item_proto, "
                 "as 64-bit fields read as doubles at 5.4.3 and 5.4.4 (corpus 11) or 2.6.3 and 2.6.4 of the place message "
                 "(corpus 14), the two readings agreed. Corpus 11: Address is item_proto field 5.3 and "
                 "Label Code (as stored) is field 1.1, observed as 0, 1, 3, 4 and 5; what the codes mean "
                 "is not established. Label Text is field 3, present only on the 2 tested rows with code "
                 "3. Name and ID (as stored) are read only from corpus 14 records and are blank on "
                 "corpus 11 rows. Corpus 14: the place "
                 "message is item_proto field 1, or field 1.1 in the layout seen on hc_pixel8pro_a16 and "
                 "hc_pixel8pro_a17; Name is its field 3, Address its field 2.5 and ID (as stored) its field "
                 "2.8, a string beginning /g/ on the 4 tested rows that carry it; the 2 rows in the newer "
                 "layout carried none. Label Text is read only from corpus 11 records and is blank on "
                 "corpus 14 rows. Client ID is client_id "
                 "as stored. Android User is the user whose app data folder holds the database; the same "
                 "database under data/data and data/user/0 is read once. Not reported: corpus 13 records, "
                 "which hold list names: four list names appeared on all 16 tested images that hold "
                 "corpus 13 records, one more on 14 of them, one on 5, and two names on one image each, "
                 "and no field was found that tells a list a user "
                 "created from one present on every account; corpus 6 records, which hold integer fields "
                 "only; and the sync_corpus_metadata and sync_metadata tables, which hold sync tokens, a "
                 "provider number and last sync times. A constructed tree with the database under data/data, data/user/0 and "
                 "data/user/10 and a decoy copy under another package returned the user 0 rows once, the "
                 "user 10 rows separately, and nothing from the decoy. A text field the decoder does not "
                 "return as bytes is left blank and counted in the run log; none was on the tested images.",
        "paths": ('*/com.google.android.apps.maps/databases/gmm_sync.db*',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "anne_a15": "Android 15 | 1 row",
            "galaxys10_a10": "Android 10 | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
            "hickman_a13": "Android 13 | 3 rows",
            "pixel3_a11": "Android 11 | 3 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "sharon_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 2 rows",
            "cookbook_a11": "Android 11 | 0 rows (corpus 6 and 13 records only)",
            "pixel7a_a14": "Android 14 | 0 rows (no corpus 11 or 14 records)",
            "samsungs20_a13": "Android 13 | 0 rows (sync_item_data empty)",
        },
    },
    "googleMapsSyncPeople": {
        "name": "Google Maps Sync - People",
        "description": "Records of corpus 1 of the sync_item_data table of Google Maps' gmm_sync.db: "
                       "the row's timestamp, and the display name, photo URL and numeric id decoded "
                       "from each record's item_proto.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Google Maps",
        "notes": "Reads the sync_item_data rows of corpus 1 from each gmm_sync.db, one row per record. "
                 "What the corpus number denotes, and why these people are recorded, is not established. "
                 "item_proto is decoded without a schema. Timestamp is the row's timestamp column read "
                 "as Unix milliseconds; it equalled item_proto field 4.1 on all 14 tested records, and "
                 "what event it marks is not established. Display Name is field 2, Photo URL field 3 as "
                 "stored (beginning // with no scheme on the 8 tested rows that carry it) and ID field "
                 "1, an integer, as stored. Client ID is client_id as stored. Android User is the user "
                 "whose app data folder holds the database; on russell_a14 one record came from user 10.",
        "paths": ('*/com.google.android.apps.maps/databases/gmm_sync.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 3 rows",
            "russell_a14": "Android 14 | 8 rows",
            "russell_pixel6a_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 1 row",
            "hickman_a13": "Android 13 | 0 rows (no corpus 1 records)",
        },
    },
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, decode_protobuf, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import user_files

_PLACE_CORPORA = (11, 14)
_PEOPLE_CORPUS = 1


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    return datetime.datetime.fromtimestamp(value / 1000, datetime.timezone.utc)


def _get(message, *keys):
    for key in keys:
        if not isinstance(message, dict) or key not in message:
            return None
        message = message[key]
    return message


class _Text:
    """Decodes length delimited protobuf fields as UTF-8 and counts the ones that did not
    arrive as bytes, so a field the decoder guessed differently is logged, not dropped."""

    def __init__(self):
        self.misses = 0

    def __call__(self, value):
        if value is None:
            return ''
        if isinstance(value, (bytes, bytearray)):
            return bytes(value).decode('utf-8', errors='replace')
        self.misses += 1
        return ''


def _rows(path, corpora):
    db = open_sqlite_db_readonly(path)
    if db is None:
        return None
    try:
        marks = ','.join('?' * len(corpora))
        return db.execute(f'''
            SELECT corpus, client_id, timestamp, latitude_e6, longitude_e6, item_proto
            FROM sync_item_data WHERE corpus IN ({marks}) ORDER BY timestamp, corpus, client_id''',
                          corpora).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'gmm_sync.db: could not read {path}: {ex}')
        return None
    finally:
        db.close()


def _decode(blob, path):
    if not blob:
        return {}
    try:
        message, _ = decode_protobuf(blob)
        return message
    except Exception as ex:  # pylint: disable=broad-exception-caught
        # blackboxprotobuf raises several unrelated types on a malformed blob.
        logfunc(f'gmm_sync.db: item_proto not decoded in {path}: {type(ex).__name__}')
        return {}


def _place(message):
    """The place submessage: field 1 on the older layout, field 1.1 on the newer one."""
    outer = _get(message, '1')
    if isinstance(_get(outer, '1'), dict) and isinstance(_get(outer, '1', '2'), dict):
        return outer['1']
    return outer


@artifact_processor
def googleMapsSyncPlaces(context):
    data_list = []
    sources = []
    text = _Text()
    for path, user in user_files(context, 'gmm_sync.db'):
        rows = _rows(path, _PLACE_CORPORA)
        if rows is None:
            continue
        sources.append(path)
        for corpus, client_id, timestamp, lat_e6, lon_e6, blob in rows:
            message = _decode(blob, context.get_relative_path(path))
            code = name = label = address = place_id = ''
            if corpus == 11:
                code = _get(message, '1', '1')
                label = text(_get(message, '3'))
                address = text(_get(message, '5', '3'))
            else:
                place = _place(message)
                name = text(_get(place, '3'))
                address = text(_get(place, '2', '5'))
                place_id = text(_get(place, '2', '8'))
            latitude = lat_e6 / 1e6 if isinstance(lat_e6, int) and lat_e6 else ''
            longitude = lon_e6 / 1e6 if isinstance(lon_e6, int) and lon_e6 else ''
            data_list.append((_ms_to_utc(timestamp), name, label, address, latitude, longitude,
                              place_id, corpus, code if code is not None else '', client_id, user))
    if text.misses:
        logfunc(f'Google Maps Sync - Places: {text.misses} text fields were not bytes and were left blank')
    data_headers = (('Timestamp', 'datetime'), 'Name', 'Label Text', 'Address', 'Latitude',
                    'Longitude', 'ID (as stored)', 'Corpus', 'Label Code (as stored)', 'Client ID',
                    'Android User')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def googleMapsSyncPeople(context):
    data_list = []
    sources = []
    text = _Text()
    for path, user in user_files(context, 'gmm_sync.db'):
        rows = _rows(path, (_PEOPLE_CORPUS,))
        if rows is None:
            continue
        sources.append(path)
        for _corpus, client_id, timestamp, _lat, _lon, blob in rows:
            message = _decode(blob, context.get_relative_path(path))
            person_id = _get(message, '1')
            data_list.append((_ms_to_utc(timestamp), text(_get(message, '2')),
                              text(_get(message, '3')),
                              person_id if isinstance(person_id, int) else '', client_id, user))
    if text.misses:
        logfunc(f'Google Maps Sync - People: {text.misses} text fields were not bytes and were left blank')
    data_headers = (('Timestamp', 'datetime'), 'Display Name', 'Photo URL', 'ID', 'Client ID',
                    'Android User')
    return data_headers, data_list, '\n'.join(sources)
