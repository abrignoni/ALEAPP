__artifacts_v2__ = {
    "chromiumWebNotifications": {
        "name": "Chromium Web Notifications",
        "description": "Notifications websites asked a Chromium browser or WebView on Android to show, from the "
                       "profile's Platform Notifications database, with title, body, clicks and close, including "
                       "notifications Chromium has since deleted whose record is still readable, and the icon and "
                       "image from the browser's HTTP cache when it holds them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the Platform Notifications database of a Chromium profile on Android (any <package>/app_*/Default/Platform Notifications), where Chromium keeps the notifications websites show through their service worker. Format and meanings come from Chromium at commit 77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784. Each notification is a key DATA:, the site's origin identifier, a zero byte and the notification id (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database.cc#L33, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database.cc#L45, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database.cc#L81-L87), holding a NotificationDatabaseDataProto (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database_data.proto#L27-L36, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database_data.proto#L66-L80). Site is the origin; Title, Body, Tag, Icon URL and Image URL are the notification's own fields as stored, and Action Buttons the stored titles of its buttons. Created is when the notification was first requested to be shown (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/public/browser/notification_database_data.h#L81-L82), stored as microseconds since 1601-01-01 UTC although the field is named creation_time_millis (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database_conversions.cc#L62-L63). Site Timestamp is the notification's timestamp field, which a site may set, in the same unit (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database_conversions.cc#L131-L132). In the known data the site set none and Site Timestamp equalled Created to within 40 milliseconds. Clicks and Action Button Clicks are the stored counts. First Click, Last Click and Closed are Created plus the stored delays, which Chromium keeps in milliseconds measured from Created when the click or close is recorded (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database.cc#L142-L145, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database.cc#L247-L251, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/public/browser/notification_database_data.h#L84-L93, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database_conversions.cc#L65-L67). Closed Reason (as stored) is User, Developer or Unknown (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database_data.proto#L16-L20, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_database_data.proto#L36), and is Unknown until a close is recorded (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/public/browser/notification_database_data.h#L95-L96). The folder is read with the vendored ccl_leveldb, and State comes from the newest version of each key: LevelDB orders the versions of a key by sequence number (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). Live: the newest version is the notification. Deleted, value kept: the newest version is a deletion and an earlier version is still in the files; the columns come from the last version stored before it. Deleted, key only: no earlier version is left and every column but State is blank (not seen on any tested image or in the known data). Records remain readable until LevelDB compacts its files, which drops versions hidden by a newer one and deletion markers no longer needed (https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/db_impl.cc#L966-L981); how long that takes on a device was not measured. Chromium deletes a notification's record when the page's close event has run (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/notification_event_dispatcher_impl.cc#L286-L300), at browser start, when it is older than 7 days, or when the platform reports which notifications are on screen and it is not among them (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/platform_notification_context_impl.cc#L46, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/platform_notification_context_impl.cc#L248-L268), and when its site no longer holds the notification permission (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/content/browser/notifications/platform_notification_context_impl.cc#L389-L409). Other paths also delete records, such as a later notification with the same tag. A deleted row does not record what removed it. The notification's own copies of its pictures, kept in RESOURCES keys, are not read: in the known data and on the tested images only deletion markers for RESOURCES keys were found, never a stored value. Icon and Image show the picture at Icon URL and Image URL when the HTTP cache of the same app and Android user holds a Simple Cache entry keyed by that URL (<package>/cache/Cache/Cache_Data, or <package>/cache/Cache on older Chrome), read with the entry reader of Chromium Browsers - HTTP Cache Entries. The cached body is the entry's stream 1 (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/net/http/http_cache.h#L461-L462, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/net/disk_cache/simple/simple_entry_format.h#L20-L27) and is shown only when its first bytes are a PNG, JPEG, GIF or WebP signature; when the URL has several entries, one whose isolation key names the notification's site is used first. A cached picture is the copy the cache held for that URL at extraction, which need not be the one shown with this notification if the site changed it. App WebView caches (cache/WebView) are not searched. Known data (Chrome 124.0.6367.219 on an Android 15 emulator, no Google account, a local test page whose service worker closes a notification when it is clicked): a notification still on screen was Live with Closed blank and Closed Reason Unknown. A notification clicked in the shade read Deleted, value kept, with Clicks 1 and First Click and Last Click 18 seconds after Created, matching the click; its Closed was blank and Closed Reason Unknown. A notification swiped away in the shade read Deleted, value kept, with Closed set 12 seconds after the last screenshot that still showed it, consistent with the swipe, and Closed Reason User. In a fresh session of the same emulator, a notification with an icon and an image left both pictures in Chrome's HTTP cache under their URLs, and Icon and Image showed files identical to the test page's own. Other Chrome versions were not tested this way. The storage views one extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are read once; a second Android user's store is read as its own (no tested image had one), and Android User is the user whose app data directory holds the store, read from the store's path (data/data, data/user/0 and userdata/data are user 0, data/user/<n> and userdata/user/<n> user n). The store folders that held a notification record are listed in the report's source paths. When ccl_leveldb raises on a damaged record, the records read before it are kept and the run log names the folder; no tested image exercised this. On the tested images: 25 rows on 4 of 20 images (galaxys10_a10 17, sharon_a14 6, hickman_a13 1, pixel3_a12 1), 17 Live and 8 Deleted, value kept, all Chrome and all Android User 0; no other browser or app profile on those images held a notification record. On sharon_a14, Android's notification history (read with ALEAPP's notification history parser) held 44 entries, none from Chrome, and none of the 21 titles in the stored versions of its 6 notification records was among them. Closed was blank and Closed Reason Unknown on all 25 rows, Action Button Clicks held 0 and Action Buttons was blank on all 25, Clicks was 1 on 2 rows, First Click and Last Click were set on those 2, Body on 22, Tag on 8 and Image URL on 1. Icon showed a picture on 8 of the 25 rows (sharon_a14 6, hickman_a13 1, pixel3_a12 1) and Image on 1 (sharon_a14); Icon and Image were empty on all 17 rows of galaxys10_a10, whose 17 icon URLs had no entry in its cache. Site held one value on every row of galaxys10_a10 (17 rows), hickman_a13 and pixel3_a12, and two values on sharon_a14. State held 15 Live and 2 Deleted, value kept on galaxys10_a10, Deleted, value kept on all 6 rows of sharon_a14, and Live on the one row of hickman_a13 and of pixel3_a12. Browser held Chrome and Android User held 0 on every row of every image. First Click and Last Click were identical on every row: equal on the 2 clicked rows, each clicked once, and blank on the rest.",
        "paths": ('*/app_*/Default/Platform Notifications/*', '*/cache/[Cc]ache/*_0'),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 17 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hickman_a13": "Android 13 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 1 row",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 6 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import datetime
import os
import re
import struct

from scripts.artifacts.chrome import get_browser_name
from scripts.artifacts.chromiumHttpCache import _HEADER, _read_entry, _split_key
from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.blackboxprotobuf import decode_message
from scripts.ccl import ccl_leveldb
from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, logfunc

_STORE = 'Platform Notifications'
_READ_ERRORS = (OSError, ValueError, KeyError, IndexError, EOFError, struct.error)
# "DATA:" <origin identifier> '\0' <notification id> (see the notes)
_DATA_KEY = re.compile(rb'^DATA:([^\x00]*)\x00(.*)$', re.S)
_CLOSED = {0: 'User', 1: 'Developer', 2: 'Unknown'}
_TYPEDEF = {
    '2': {'type': 'bytes'}, '5': {'type': 'bytes'}, '7': {'type': 'int'}, '8': {'type': 'int'},
    '9': {'type': 'int'}, '10': {'type': 'int'}, '11': {'type': 'int'}, '12': {'type': 'int'},
    '13': {'type': 'int'},
    '4': {'type': 'message', 'message_typedef': {
        '1': {'type': 'bytes'}, '4': {'type': 'bytes'}, '5': {'type': 'bytes'}, '6': {'type': 'bytes'},
        '12': {'type': 'int'}, '15': {'type': 'bytes'},
        '10': {'type': 'message', 'message_typedef': {'2': {'type': 'bytes'}}}}},
}
_LIVE, _DELETED_VALUE, _DELETED_KEY = 'Live', 'Deleted, value kept', 'Deleted, key only'


def _stores(context):
    """Distinct <profile>/Platform Notifications folders among the files found, storage views collapsed."""
    stores = []
    for found in unique_files(context):
        found = str(found)
        at = found.replace('\\', '/').find(f'/{_STORE}/')
        if at < 0:
            continue
        store = found[:at + len(_STORE) + 1]
        if store not in stores:
            stores.append(store)
    return stores


def _versions(folder, label, context):
    """{key: (state, newest put value or None)} for the DATA keys: the newest version's state, and the newest put,
    which a later deletion leaves in the files until they are compacted."""
    newest, put = {}, {}
    try:
        database = ccl_leveldb.RawLevelDb(folder)
    except _READ_ERRORS as ex:
        logfunc(f'{label}: could not open {context.get_relative_path(folder)}: {type(ex).__name__} {ex}')
        return None
    try:
        for record in database.iterate_records_raw():
            key = bytes(record.user_key)
            if not _DATA_KEY.match(key):
                continue
            if key not in newest or record.seq > newest[key][0]:
                newest[key] = (record.seq, record.state)
            if record.state == ccl_leveldb.KeyState.Live and record.value and (
                    key not in put or record.seq > put[key][0]):
                put[key] = (record.seq, bytes(record.value))
    except _READ_ERRORS as ex:
        # keep what was read before the damaged record rather than losing the whole store
        logfunc(f'{label}: stopped reading {context.get_relative_path(folder)} after {len(newest)} notification '
                f'keys: {type(ex).__name__} {ex}')
    finally:
        database.close()
    return {key: (state, put.get(key, (0, None))[1]) for key, (_seq, state) in newest.items()}


def _text(value):
    return value.decode('utf-8', 'replace') if isinstance(value, (bytes, bytearray)) else str(value or '')


def _chromium_time(microseconds):
    """base::Time stored as microseconds since 1601-01-01 UTC."""
    if not isinstance(microseconds, int) or microseconds <= 0:
        return ''
    try:
        return datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(
            microseconds=microseconds)
    except OverflowError:
        return ''


def _after(created, milliseconds):
    """Created plus a stored delay in milliseconds, blank when either is missing."""
    if not created or not isinstance(milliseconds, int):
        return ''
    try:
        return created + datetime.timedelta(milliseconds=milliseconds)
    except OverflowError:
        return ''


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


_ENTRY = re.compile(r'^[0-9a-f]{16}_0$')
# leading bytes of the image formats a notification icon or image can be served in
_IMAGE_TYPES = ((b'\x89PNG\r\n\x1a\n', 'image/png', '.png'), (b'\xff\xd8\xff', 'image/jpeg', '.jpg'),
                (b'GIF87a', 'image/gif', '.gif'), (b'GIF89a', 'image/gif', '.gif'))


def _cache_entries(store, cache):
    """{url: [(isolation key, entry path)]} from the HTTP cache of the app that holds the store: the Simple Cache
    entries under <package>/cache/Cache[/Cache_Data], read once per package folder and storage view."""
    root = store[:store.replace('\\', '/').rfind('/app_')]
    if root in cache:
        return cache[root]
    found = {}
    for name in ('Cache', 'cache'):
        for folder in (os.path.join(root, 'cache', name, 'Cache_Data'), os.path.join(root, 'cache', name)):
            if not os.path.isdir(folder):
                continue
            for entry_name in sorted(os.listdir(folder)):
                if not _ENTRY.match(entry_name):
                    continue
                path = os.path.join(folder, entry_name)
                try:
                    with open(path, 'rb') as handle:
                        head = handle.read(_HEADER.size)
                        if len(head) < _HEADER.size:
                            continue
                        key = handle.read(_HEADER.unpack(head)[2]).decode('utf-8', 'replace')
                except (OSError, struct.error):
                    continue
                url, isolation = _split_key(key)
                found.setdefault(url, []).append((isolation, path))
    cache[root] = found
    return found


def _cached_image(url, site, entries):
    """(bytes, MIME type, extension, entry path) of the cached body for url when it is an image, else None.
    An entry whose isolation key names the notification's site is preferred."""
    candidates = entries.get(url) or []
    candidates = sorted(candidates, key=lambda item: (site not in item[0], item[1]))
    for _isolation, path in candidates:
        entry, _reason = _read_entry(path)
        if entry is None:
            continue
        try:
            with open(path, 'rb') as handle:
                handle.seek(_HEADER.size + len(entry['key'].encode('utf-8')))
                body = handle.read(entry['stream1_size'])
        except OSError:
            continue
        for magic, mime, extension in _IMAGE_TYPES:
            if body.startswith(magic):
                return body, mime, extension, path
        if body[:4] == b'RIFF' and body[8:12] == b'WEBP':
            return body, 'image/webp', '.webp', path
    return None


def _media(url, site, entries):
    if not url:
        return ''
    found = _cached_image(url, site, entries)
    if found is None:
        return ''
    body, mime, extension, path = found
    return check_in_embedded_media(path, body, os.path.basename(path) + extension, force_type=mime) or ''


def _row(state, value, store, label, context, entries):
    """One notification's columns, from its newest stored version when one is readable."""
    if value is None:
        return ('',) * 17 + (_DELETED_KEY,)
    stored_state = _LIVE if state == ccl_leveldb.KeyState.Live else _DELETED_VALUE
    try:
        message, _typedef = decode_message(value, _TYPEDEF)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logfunc(f'{label}: a notification in {context.get_relative_path(store)} did not decode: {ex}')
        return ('',) * 17 + (stored_state,)
    payload = message.get('4') or {}
    created = _chromium_time(message.get('9'))
    closed = message.get('13')
    actions = '; '.join(_text(action.get('2')) for action in _as_list(payload.get('10')) if action.get('2'))
    return (created, _after(created, message.get('10')), _after(created, message.get('11')),
            _after(created, message.get('12')), _chromium_time(payload.get('12')),
            _text(message.get('2')), _text(payload.get('1')), _text(payload.get('4')),
            _media(_text(payload.get('6')), _text(message.get('2')), entries),
            _media(_text(payload.get('15')), _text(message.get('2')), entries),
            message.get('7', ''), message.get('8', ''), _CLOSED.get(closed, closed if closed is not None else ''),
            _text(payload.get('5')), _text(payload.get('6')), _text(payload.get('15')), actions, stored_state)


@artifact_processor
def chromiumWebNotifications(context):
    label = 'Chromium Web Notifications'
    data_list = []
    sources = []
    cache = {}
    for store in _stores(context):
        records = _versions(store, label, context)
        if not records:
            continue
        sources.append(store)
        browser = get_browser_name(store + '/x')
        user = android_user(context.get_relative_path(store))
        for key in sorted(records):
            state, value = records[key]
            data_list.append(_row(state, value, store, label, context, _cache_entries(store, cache))
                             + (browser, user))
    data_headers = (('Created', 'datetime'), ('First Click', 'datetime'), ('Last Click', 'datetime'),
                    ('Closed', 'datetime'), ('Site Timestamp', 'datetime'), 'Site', 'Title', 'Body', ('Icon', 'media'),
                    ('Image', 'media'), 'Clicks',
                    'Action Button Clicks', 'Closed Reason (as stored)', 'Tag', 'Icon URL', 'Image URL',
                    'Action Buttons', 'State', 'Browser', 'Android User')
    return data_headers, data_list, '\n'.join(sources)
