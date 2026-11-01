__artifacts_v2__ = {
    "chromiumWebsiteUsageEvents": {
        "name": "Chromium Website Usage Events",
        "description": "Start and stop browsing events Chromium on Android records per website in the profile's "
                       "shared_proto_db, including events it has since deleted whose key still names the site "
                       "and time.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the website events Chromium for Android keeps in a profile's shared_proto_db (any <package>/app_*/Default/shared_proto_db). Format and meanings come from Chromium at commit 77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784. The folder is the LevelDB database Chromium's proto clients share, each client's keys starting with its ProtoDbType number and an underscore (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/leveldb_proto/internal/shared_proto_database_client.cc#L178-L180). This artifact reads type 5, USAGE_STATS_WEBSITE_EVENT (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/leveldb_proto/public/shared_proto_database_client_list.h#L28). A key is 5_, the event time in Unix seconds written as 11 digits, an underscore and the site's host name (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/android/usage_stats/usage_stats_database.cc#L32-L35, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/android/usage_stats/usage_stats_database.cc#L98-L110), and the value is a WebsiteEvent holding the host, the time in seconds and nanoseconds, and a type (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/android/usage_stats/website_event.proto#L16-L34). Event is the type, 0 Unknown, 1 Start browsing and 2 Stop browsing (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/android/usage_stats/website_event.proto#L25-L27), and Event Type (as stored) is the number. Chromium writes Start browsing when the tab in view moves to a new http or https host and Stop browsing when it leaves that host (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/android/java/src/org/chromium/chrome/browser/usage_stats/PageViewObserver.java#L160-L178), so a row records that a page from that host was in view in that browser, not who was using it. Event Time is UTC: the value's time when its seconds equal the key's, otherwise the key's time to the second. The folder is read with the vendored ccl_leveldb, and State comes from the newest version of each key: LevelDB orders the versions of a key by sequence number (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). Live: the newest version is the event. Deleted, value kept: the newest version is a deletion and an earlier version of the event is still in the files; Event and Event Type come from it. Deleted, key only: the newest version is a deletion and no earlier version is left, so only the time and host in the key are known and Event and Event Type are blank. Chromium deletes events older than 7 days each time it opens the database (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/android/usage_stats/usage_stats_database.cc#L63, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/android/usage_stats/usage_stats_database.cc#L259-L262, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/android/usage_stats/usage_stats_database.h#L49) and has a path that deletes them when browsing history is deleted, by time range or all of it (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/android/usage_stats/usage_stats_bridge.cc#L297-L333). A deleted row does not record which of these removed it, and it is not by itself evidence of a user action. Records remain readable until LevelDB compacts its files, which drops versions hidden by a newer one and deletion markers no longer needed (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/db_impl.cc#L966-L981); how long that takes on a device was not measured. Known data (Chrome 124.0.6367.219 on an Android 15 emulator, no Google account, a local test page): opening the page wrote a Start browsing row; after the page was shared and Chrome sent to the background a Stop browsing row was present, and which of the two steps wrote it was not isolated. Digital Wellbeing's website tracking was never set up. After the device clock was moved 8 days forward and Chrome reopened, both earlier rows read Deleted, value kept. Clearing browsing history for the last hour left that hour's rows Live; why that clear did not reach them was not established. Clearing browsing history for all time turned every row written before the clear into Deleted, value kept; the Start browsing and Stop browsing rows written after it were Live. Other Chrome versions were not tested this way. The storage views one extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are read once; a second Android user's store is read as its own. When ccl_leveldb raises on a damaged record, the records read before it are kept and the run log names the folder; a key's state then reflects only the versions read before the stop. Samsung Internet and app WebView profiles are matched and read; no tested image had type 5 records in them. On the tested images: 2,052 rows on 18 of 20 images, Chrome 1,841, Brave 149 and Edge 62; 295 Live, 468 Deleted, value kept and 1,289 Deleted, key only. The value's host equalled the key's on every row with a value. Against the same profile's History urls (host match), 128 hosts on 13 images appeared only in deleted keys and had no History row. Event and Event Type (as stored) are blank on the 1,289 Deleted, key only rows. Browser and Store Folder held one value on every row of 10 of the 18 images with rows, which held one profile with events; the other 8 held two or three.",
        "paths": ('*/app_*/Default/shared_proto_db/*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | 148 rows",
            "cookbook_a11": "Android 11 | 70 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 9 rows",
            "galaxys10_a10": "Android 10 | 125 rows",
            "hc_pixel8pro_a16": "Android 16 | 40 rows",
            "hc_pixel8pro_a17": "Android 17 | 42 rows",
            "hickman_a13": "Android 13 | 68 rows",
            "kevin_pocox7_a15": "Android 15 | 274 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 83 rows",
            "pixel7a_a14": "Android 14 | 51 rows",
            "russell_a14": "Android 14 | 222 rows",
            "russell_pixel6a_a13": "Android 13 | 215 rows",
            "s20fe_a13": "Android 13 | 6 rows",
            "samsunga53_a14": "Android 14 | 14 rows",
            "samsungs20_a13": "Android 13 | 81 rows",
            "sharon_a13": "Android 13 | 200 rows",
            "sharon_a14": "Android 14 | 384 rows",
            "userb2_a13": "Android 13 | 20 rows",
        },
    },
    "chromiumShareHistory": {
        "name": "Chromium Share History",
        "description": "Per day, the apps a Chromium browser on Android shared to and how many times, from the "
                       "profile's shared_proto_db.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the share history Chromium for Android keeps in a profile's shared_proto_db (any <package>/app_*/Default/shared_proto_db). Format and meanings come from Chromium at commit 77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784. The folder is the LevelDB database Chromium's proto clients share, each client's keys starting with its ProtoDbType number and an underscore (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/leveldb_proto/internal/shared_proto_database_client.cc#L178-L180). This artifact reads type 35, SHARE_HISTORY_DATABASE (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/leveldb_proto/public/shared_proto_database_client_list.h#L60), key 35_share_history (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/share/share_history.cc#L38). The value is a ShareHistory: per day, counted in days since 1970-01-01 UTC, the share targets with a count (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/share/proto/share_history_message.proto#L12-L39). Chromium adds one to today's count for the chosen target when a share is made (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/share/share_history.cc#L100-L114, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/share/share_history.cc#L42-L43) and, each time it loads the record, drops the days older than 90 days (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/share/share_history.cc#L40, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/share/share_history.cc#L159-L173, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/share/share_history.cc#L207). Share Target (component) is the Android component of the app chosen, as stored; Share Day (UTC) is the day as a date. The folder is read with the vendored ccl_leveldb, and State comes from the newest version of each key: LevelDB orders the versions of a key by sequence number (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). Live: the day and target are in the newest version. Deleted, value kept: the newest version is a deletion and the row comes from the last version stored before it; no tested store had a deleted share history key, so this state is implemented but not exercised. Earlier version only: the day and target are in an earlier version still in the files and not in the newest one, with the count from the newest version that holds them; this is what a rewrite of the record without that day leaves. Known data (Chrome 124.0.6367.219 on an Android 15 emulator, no Google account, a local test page): sharing the page through Chrome's share sheet to a Copy to clipboard target wrote one row for that day with a count of 1. Moving the clock 8 days forward and clearing browsing history for the last hour left it Live. Clearing browsing history for all time rewrote the record as an empty value, and the earlier version kept the row, which then read Earlier version only; the code path that empties the record on that clear was not traced. Other Chrome versions were not tested this way. The storage views one extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are read once; a second Android user's store is read as its own. When ccl_leveldb raises on a damaged record, the records read before it are kept and the run log names the folder; a key's state then reflects only the versions read before the stop. On the tested images: 0 rows on every image. The record was present in a Chrome, Brave or Edge profile on 17 of 20 images and every stored version of it there was empty, so no share was recorded in any version left in the files.",
        "paths": ('*/app_*/Default/shared_proto_db/*',),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hickman_a13": "Android 13 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import datetime
import re
import struct

from scripts.artifacts.chrome import get_browser_name
from scripts.artifacts.storagePathViews import unique_files
from scripts.blackboxprotobuf import decode_message
from scripts.ccl import ccl_leveldb
from scripts.ilapfuncs import artifact_processor, logfunc

_STORE = 'shared_proto_db'
_READ_ERRORS = (OSError, ValueError, KeyError, IndexError, EOFError, struct.error)
# A client's keys carry the prefix "<ProtoDbType>_" (see the notes): 5 USAGE_STATS_WEBSITE_EVENT,
# 35 SHARE_HISTORY_DATABASE.
_EVENT_KEY = re.compile(rb'^5_(\d{11})_(.+)$', re.S)
_SHARE_KEY = b'35_share_history'
_EVENT_TYPES = {0: 'Unknown', 1: 'Start browsing', 2: 'Stop browsing'}
_EVENT_TYPEDEF = {'2': {'type': 'message', 'message_typedef': {'1': {'type': 'int'}, '2': {'type': 'int'}}},
                  '3': {'type': 'int'}}
_SHARE_TYPEDEF = {'1': {'type': 'message', 'message_typedef': {
    '1': {'type': 'int'},
    '2': {'type': 'message', 'message_typedef': {
        '1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes'}}},
        '2': {'type': 'int'}}}}}}
_LIVE, _DELETED_VALUE, _DELETED_KEY = 'Live', 'Deleted, value kept', 'Deleted, key only'
_EARLIER = 'Earlier version only'


def _stores(context):
    """Distinct <profile>/shared_proto_db folders among the files found, storage views collapsed."""
    stores = []
    for found in unique_files(context):
        found = str(found)
        normal = found.replace('\\', '/')
        at = normal.find(f'/{_STORE}/')
        if at < 0:
            continue
        store = found[:at + len(_STORE) + 1]
        if store not in stores:
            stores.append(store)
    return stores


def _versions(folder, wanted, label, context):
    """{key: (state, [put values, newest first])} for the keys `wanted` accepts: the newest version's state, and
    every put still in the files, which a later deletion or overwrite leaves until the files are compacted."""
    newest, puts = {}, {}
    try:
        database = ccl_leveldb.RawLevelDb(folder)
    except _READ_ERRORS as ex:
        logfunc(f'{label}: could not open {context.get_relative_path(folder)}: {type(ex).__name__} {ex}')
        return None
    try:
        for record in database.iterate_records_raw():
            key = bytes(record.user_key)
            if not wanted(key):
                continue
            if key not in newest or record.seq > newest[key][0]:
                newest[key] = (record.seq, record.state)
            if record.state == ccl_leveldb.KeyState.Live:
                puts.setdefault(key, []).append((record.seq, bytes(record.value or b'')))
    except _READ_ERRORS as ex:
        # keep what was read before the damaged record rather than losing the whole store
        logfunc(f'{label}: stopped reading {context.get_relative_path(folder)} after {len(newest)} matching keys: '
                f'{type(ex).__name__} {ex}')
    finally:
        database.close()
    return {key: (state, [value for _seq, value in sorted(puts.get(key, []), reverse=True)])
            for key, (_seq, state) in newest.items()}


def _state(state, value):
    if state == ccl_leveldb.KeyState.Live:
        return _LIVE
    return _DELETED_VALUE if value is not None else _DELETED_KEY


def _decode(value, typedef, what, folder, label, context):
    try:
        message, _typedef = decode_message(value, typedef)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logfunc(f'{label}: {what} in {context.get_relative_path(folder)} did not decode: {ex}')
        return None
    return message


def _unix(seconds, nanos=0):
    try:
        return (datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
                + datetime.timedelta(seconds=int(seconds), microseconds=int(nanos or 0) // 1000))
    except (OverflowError, ValueError, TypeError):
        return ''


def _text(value):
    return value.decode('utf-8', 'replace') if isinstance(value, (bytes, bytearray)) else str(value or '')


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _share_pairs(message):
    """{(UTC date, target component): count} from one ShareHistory message."""
    pairs = {}
    for day_history in _as_list(message.get('1')):
        try:
            date = (datetime.date(1970, 1, 1) + datetime.timedelta(days=int(day_history.get('1')))).isoformat()
        except (OverflowError, ValueError, TypeError):
            date = ''
        for target in _as_list(day_history.get('2')):
            pairs[(date, _text((target.get('1') or {}).get('1')))] = target.get('2', '')
    return pairs


@artifact_processor
def chromiumWebsiteUsageEvents(context):
    label = 'Chromium Website Usage Events'
    data_list = []
    sources = []
    for store in _stores(context):
        records = _versions(store, _EVENT_KEY.match, label, context)
        if not records:
            continue
        sources.append(store)
        browser = get_browser_name(store + '/x')
        relative = context.get_relative_path(store)
        for key in sorted(records):
            state, values = records[key]
            value = values[0] if values else None
            match = _EVENT_KEY.match(key)
            key_seconds, key_site = int(match.group(1)), _text(match.group(2))
            event_time, event, stored_type = _unix(key_seconds), '', ''
            if value is not None:
                message = _decode(value, _EVENT_TYPEDEF, f'event {key_seconds}', store, label, context)
                if message is not None:
                    stamp = message.get('2') or {}
                    if stamp.get('1') == key_seconds:
                        event_time = _unix(key_seconds, stamp.get('2'))
                    if '3' in message:
                        stored_type = message['3']
                        event = _EVENT_TYPES.get(stored_type, '')
            data_list.append((event_time, key_site, event, stored_type, _state(state, value), browser, relative))
    data_headers = (('Event Time', 'datetime'), 'Site', 'Event', 'Event Type (as stored)', 'State', 'Browser',
                    'Store Folder')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chromiumShareHistory(context):
    label = 'Chromium Share History'
    data_list = []
    sources = []
    for store in _stores(context):
        records = _versions(store, lambda key: key == _SHARE_KEY, label, context)
        if not records:
            continue
        sources.append(store)
        state, values = records[_SHARE_KEY]
        browser = get_browser_name(store + '/x')
        relative = context.get_relative_path(store)
        current, earlier = {}, {}
        for index, value in enumerate(values):
            message = _decode(value, _SHARE_TYPEDEF, 'share history', store, label, context) if value else {}
            if message is None:
                continue
            pairs = _share_pairs(message)
            if index == 0:  # the newest put: the record itself, or the last one before a deletion
                current = pairs
            else:
                for pair, count in pairs.items():
                    earlier.setdefault(pair, count)  # values run newest first: keep the newest count
        newest_state = _LIVE if state == ccl_leveldb.KeyState.Live else _DELETED_VALUE
        for (date, target), count in sorted(current.items(), key=lambda item: (str(item[0][0]), item[0][1])):
            data_list.append((date, target, count, newest_state, browser, relative))
        for (date, target), count in sorted(earlier.items(), key=lambda item: (str(item[0][0]), item[0][1])):
            if (date, target) not in current:
                data_list.append((date, target, count, _EARLIER, browser, relative))
    data_headers = (('Share Day (UTC)', 'date'), 'Share Target (component)', 'Share Count', 'State', 'Browser',
                    'Store Folder')
    return data_headers, data_list, '\n'.join(sources)
