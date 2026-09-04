__artifacts_v2__ = {
    "chrome_sync_sessions": {
        "name": "Chrome Sync - Synced Tabs",
        "description": "Pages held in the tabs Chrome synced for the signed-in account, with the "
                       "address, page title, visit time and the name of the device the tab "
                       "belongs to.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Chrome Sync",
        "notes": "Read from the Chrome sync LevelDB store app_chrome/<profile>/Sync Data/LevelDB "
                 "with the vendored ccl_leveldb, decoding each value with blackboxprotobuf. Only "
                 "keys beginning sessions-dt- are read; the sessions-md- keys hold sync "
                 "bookkeeping. The mirrored Android storage views of one store are collapsed "
                 "before it is opened so a record is not reported once per view.\n"
                 "Field numbers are Chromium's. SessionSpecifics: session_tag 1, header 2, tab 3, "
                 "tab_node_id 4. SessionHeader: window 2, client_name 3, device_type 4. "
                 "SessionTab: tab_id 1, window_id 2, current_navigation_index 4, pinned 5, "
                 "navigation 7. TabNavigation: virtual_url 2, referrer 3, title 4, "
                 "page_transition 6, unique_id 8, timestamp_msec 9, favicon_url 17, "
                 "http_status_code 20. References: Chromium, "
                 "components/sync/protocol/session_specifics.proto and "
                 "components/sync/protocol/tab_navigation.proto.\n"
                 "One row per navigation entry in a tab. Timestamp is timestamp_msec, Unix "
                 "milliseconds. Device Name is the client_name from the header record carrying "
                 "the same session tag, so a tab is attributed to the device that synced it and "
                 "is blank when no header for that tag is in the store. Browser is the package the store sits under, because the pattern carries no package name and every Chromium browser uses the same app_chrome layout. Navigation Index is the "
                 "entry's position in the tab's list and Current Navigation Index is the entry "
                 "the tab was on, so the two together show which page was showing. Page Transition is "
                 "an integer Chromium defines and is reported as stored. Favicon URL is carried by a "
                 "minority of entries, 35 of 2551 across the tested images, and is blank on the rest.\n"
                 "Sync carries tabs from the other devices signed into the same Chrome profile, "
                 "so a row is not necessarily a page opened on this device; read Device Name "
                 "before attributing it. LevelDB keeps superseded copies of a key, so Superseded "
                 "is True for every copy but the newest of that key and an earlier copy can hold "
                 "pages the newest one no longer lists. A navigation entry that repeats "
                 "unchanged across those copies is reported once, so the superseded rows that "
                 "remain are the ones that differ.",
        "paths": ('*/app_chrome/*/Sync Data/LevelDB/*',),
        "output_types": "standard",
        "artifact_icon": "cloud-computing",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 364 rows",
            "cookbook_a11": "Android 11 | 382 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 34 rows",
            "hc_pixel8pro_a17": "Android 17 | 37 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 406 rows",
            "pixel3_a11": "Android 11 | 35 rows",
            "pixel3_a12": "Android 12 | 300 rows",
            "pixel7a_a14": "Android 14 | 45 rows",
            "russell_a14": "Android 14 | 120 rows",
            "russell_pixel6a_a13": "Android 13 | 198 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 32 rows",
            "sharon_a13": "Android 13 | 162 rows",
            "sharon_a14": "Android 14 | 436 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 364 rows",
            "cookbook_a11": "Android 11 | 382 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 34 rows",
            "hc_pixel8pro_a17": "Android 17 | 37 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 406 rows",
            "pixel3_a11": "Android 11 | 35 rows",
            "pixel3_a12": "Android 12 | 300 rows",
            "pixel7a_a14": "Android 14 | 45 rows",
            "russell_a14": "Android 14 | 120 rows",
            "russell_pixel6a_a13": "Android 13 | 198 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 32 rows",
            "sharon_a13": "Android 13 | 162 rows",
            "sharon_a14": "Android 14 | 436 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
    "chrome_sync_devices": {
        "name": "Chrome Sync - Session Devices",
        "description": "The devices that synced browsing sessions to this Chrome profile, with "
                       "the device name each one reported and the tabs its window held.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Chrome Sync",
        "notes": "Read from the same Chrome sync LevelDB store, from the session records that "
                 "carry a header rather than a tab. One row per window in a header record.\n"
                 "Field numbers are Chromium's, from "
                 "components/sync/protocol/session_specifics.proto: SessionSpecifics.session_tag "
                 "1 and header 2; SessionHeader.window 2, client_name 3 and device_type 4; "
                 "SessionWindow.window_id 1, selected_tab_index 2, browser_type 3 and tab 4.\n"
                 "Device Name is the client_name the device reported, which is a model name on "
                 "the tested images. Session Tag is the identifier the sync store files that "
                 "device under, and it is the value that joins these rows to the synced tabs. Browser is "
                 "the package the store sits under. "
                 "Tabs In Window is the count of tab ids the window listed. Device Type and "
                 "Browser Type are integers reported as stored. The window record also carries a "
                 "selected tab index, which held no value or -1 on every tested record, so it is not "
                 "reported.\n"
                 "A device appears here because it synced a session to this account, not because "
                 "it was used at the device this extraction came from. The store keeps superseded copies "
                 "of each header, which are older snapshots of the same window, so only the newest "
                 "copy of each is reported here; the synced tabs artifact reports the older "
                 "copies that differ.",
        "paths": ('*/app_chrome/*/Sync Data/LevelDB/*',),
        "output_types": "standard",
        "artifact_icon": "devices",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 1 row",
            "cookbook_a11": "Android 11 | 1 row",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 2 rows",
            "pixel3_a11": "Android 11 | 4 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "pixel7a_a14": "Android 14 | 4 rows",
            "russell_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 2 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a13": "Android 13 | 6 rows",
            "sharon_a14": "Android 14 | 1 row",
            "userb2_a13": "Android 13 | 0 rows",
        },
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 1 row",
            "cookbook_a11": "Android 11 | 1 row",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 2 rows",
            "pixel3_a11": "Android 11 | 4 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "pixel7a_a14": "Android 14 | 4 rows",
            "russell_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 2 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a13": "Android 13 | 6 rows",
            "sharon_a14": "Android 14 | 1 row",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import datetime
import os
import pathlib
import re

from scripts.artifacts.storagePathViews import unique_files
from scripts.ccl import ccl_leveldb
from scripts import blackboxprotobuf
from scripts.ilapfuncs import artifact_processor, logfunc

# Chromium field numbers: components/sync/protocol/session_specifics.proto and tab_navigation.proto
_SESSION_TAG, _HEADER, _TAB = '1', '2', '3'
_HDR_WINDOW, _HDR_CLIENT_NAME, _HDR_DEVICE_TYPE = '2', '3', '4'
_WIN_ID, _WIN_SELECTED, _WIN_BROWSER_TYPE, _WIN_TABS = '1', '2', '3', '4'
_TAB_ID, _TAB_WINDOW, _TAB_CURRENT_INDEX, _TAB_PINNED, _TAB_NAV = '1', '2', '4', '5', '7'
_NAV_URL, _NAV_REFERRER, _NAV_TITLE = '2', '3', '4'
_NAV_TRANSITION, _NAV_UNIQUE_ID, _NAV_TIMESTAMP = '6', '8', '9'
_NAV_FAVICON, _NAV_HTTP_STATUS = '17', '20'

# blackboxprotobuf names a repeated field 7, then 7-1, 7-2 as its shapes differ.
_REPEAT = re.compile(r'^(\d+)(?:-\d+)?$')
# Every Chromium browser uses the app_chrome layout, so the package names the browser.
_PACKAGE = re.compile(r'/([^/]+)/app_chrome/', re.I)


def _text(value):
    """A stored string. An absent submessage decodes to an empty container, which must read as
    blank rather than as its Python repr."""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', 'replace')
    if value is None or isinstance(value, (dict, list, tuple)):
        return ''
    return value


def _ms(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(number / 1000, tz=datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _first(value):
    """blackboxprotobuf gives a repeated message as a dict or a list of dicts."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _repeated(message, number):
    """Every value of a repeated field, across the suffixed names the decoder gives it."""
    out = []
    for key, value in message.items():
        match = _REPEAT.match(key)
        if not match or match.group(1) != number:
            continue
        if isinstance(value, list):
            out.extend(v for v in value if isinstance(v, dict))
        elif isinstance(value, dict):
            out.append(value)
    return out


def _browser(path):
    """The package the store sits under, so one cross-browser pattern still attributes a row."""
    match = _PACKAGE.search(str(path).replace('\\', '/'))
    return match.group(1) if match else ''


def _stores(context):
    directories = set()
    for file_found in unique_files(context):
        file_found = str(file_found)
        if '/Sync Data/LevelDB/' not in file_found.replace('\\', '/'):
            continue
        directories.add(pathlib.Path(file_found).parent)
    return sorted(directories)


def _session_records(directory):
    """Live sessions-dt- records, newest first per key, each flagged as superseded or not."""
    try:
        database = ccl_leveldb.RawLevelDb(str(directory))
        records = [r for r in database.iterate_records_raw()
                   if r.state == ccl_leveldb.KeyState.Live and r.value
                   and r.user_key.startswith(b'sessions-dt-')]
    except Exception as error:  # pylint: disable=broad-except
        logfunc(f'Chrome Sync: could not read {os.path.basename(str(directory))}: {error}')
        return []
    records.sort(key=lambda r: r.seq, reverse=True)
    seen = set()
    out = []
    for record in records:
        try:
            message, _ = blackboxprotobuf.decode_message(record.value)
        except Exception:  # pylint: disable=broad-except
            continue
        if not isinstance(message, dict):
            continue
        key = bytes(record.user_key)
        out.append((message, key in seen))
        seen.add(key)
    return out


def _device_names(records):
    """session tag -> the client name of the header record carrying that tag."""
    names = {}
    for message, superseded in records:
        if superseded:
            continue
        header = _first(message.get(_HEADER))
        if not isinstance(header, dict):
            continue
        tag = _text(message.get(_SESSION_TAG))
        name = _text(header.get(_HDR_CLIENT_NAME))
        if tag and name:
            names.setdefault(tag, name)
    return names


@artifact_processor
def chrome_sync_sessions(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Device Name',
        'Browser',
        'URL',
        'Title',
        'Referrer',
        'HTTP Status',
        'Navigation Index',
        'Current Navigation Index',
        'Tab ID',
        'Window ID',
        'Session Tag',
        'Page Transition (as stored)',
        'Favicon URL',
        'Superseded',
        'Source File',
    )
    data_list = []
    sources = []

    for directory in _stores(context):
        records = _session_records(directory)
        names = _device_names(records)
        relative = context.get_relative_path(str(directory))
        browser = _browser(directory)
        reported = set()
        rows = 0
        for message, superseded in records:
            tab = _first(message.get(_TAB))
            if not isinstance(tab, dict):
                continue
            tag = _text(message.get(_SESSION_TAG))
            navigations = _repeated(tab, _TAB_NAV)
            for index, navigation in enumerate(navigations):
                url = _text(navigation.get(_NAV_URL))
                stamp = navigation.get(_NAV_TIMESTAMP)
                fingerprint = (tag, tab.get(_TAB_ID, ''), index, url, stamp)
                if fingerprint in reported:
                    continue
                reported.add(fingerprint)
                data_list.append((
                    _ms(stamp),
                    names.get(tag, ''),
                    browser,
                    url,
                    _text(navigation.get(_NAV_TITLE)),
                    _text(navigation.get(_NAV_REFERRER)),
                    navigation.get(_NAV_HTTP_STATUS, ''),
                    index,
                    tab.get(_TAB_CURRENT_INDEX, ''),
                    tab.get(_TAB_ID, ''),
                    tab.get(_TAB_WINDOW, ''),
                    tag,
                    navigation.get(_NAV_TRANSITION, ''),
                    _text(navigation.get(_NAV_FAVICON)),
                    superseded,
                    relative,
                ))
                rows += 1
        if rows:
            sources.append(str(directory))

    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chrome_sync_devices(context):
    data_headers = (
        'Device Name',
        'Browser',
        'Session Tag',
        'Window ID',
        'Tabs In Window',
        'Device Type (as stored)',
        'Browser Type (as stored)',
        'Source File',
    )
    data_list = []
    sources = []

    for directory in _stores(context):
        relative = context.get_relative_path(str(directory))
        browser = _browser(directory)
        rows = 0
        for message, superseded in _session_records(directory):
            if superseded:
                continue
            header = _first(message.get(_HEADER))
            if not isinstance(header, dict):
                continue
            tag = _text(message.get(_SESSION_TAG))
            name = _text(header.get(_HDR_CLIENT_NAME))
            device_type = header.get(_HDR_DEVICE_TYPE, '')
            windows = _repeated(header, _HDR_WINDOW) or [{}]
            for window in windows:
                tabs = window.get(_WIN_TABS)
                if isinstance(tabs, list):
                    tab_count = len(tabs)
                elif tabs in (None, ''):
                    tab_count = 0
                else:
                    tab_count = 1
                data_list.append((
                    name,
                    browser,
                    tag,
                    window.get(_WIN_ID, ''),
                    tab_count,
                    device_type,
                    window.get(_WIN_BROWSER_TYPE, ''),
                    relative,
                ))
                rows += 1
        if rows:
            sources.append(str(directory))

    return data_headers, data_list, '\n'.join(sources)
