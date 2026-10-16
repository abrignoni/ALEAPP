__artifacts_v2__ = {
    "chrome_session_tabs": {
        "name": "Chromium Session Tabs - Navigation Entries",
        "description": "Pages held in the tab restore file of a Chromium browser, with the "
                       "address, page title, stored timestamp and HTTP status the browser "
                       "stored for "
                       "each entry, and the tab it belongs to.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Chromium Sessions",
        "notes": "Read from the Sessions/Tabs_<number> files a Chromium browser writes under its "
                 "app_chrome folder, with the vendored snss_parser. The path pattern carries no "
                 "package name and matches any package that keeps an "
                 "app_chrome/<profile>/Sessions folder, so the Browser column reports the package "
                 "the file was found under and the same glob covers Chrome, Brave and Edge.\nOne "
                 "row per navigation entry in each matched file, taken from the command Chromium "
                 "calls kCommandUpdateTabNavigation. Mirrored storage views with the same canonical "
                 "identity and exactly equal complete bytes are reported once, using the preferred "
                 "storage spelling. Different byte states remain separate; Source File names the "
                 "selected path. Original parser contribution: @AlexisBrignoni, Claude. Timestamp is the "
                 "entry's stored time, microseconds since 1601, and Tab ID and Index identify the "
                 "tab and the position of the entry in that tab's back and forward list, so "
                 "several rows with one Tab ID are one tab's history. Transition Type and "
                 "Referrer Policy are integers Chromium defines and are reported as stored. "
                 "Reference: Chromium at commit 5babd82a3403ae4c580afc34df4c677d70779b52: "
                 "https://github.com/chromium/chromium/blob/5babd82a3403ae4c580afc34df4c677d70779b52/components/sessions/core/serialized_navigation_entry.cc#L116 "
                 "(WriteToPickle, which sets the field order) and "
                 "https://github.com/chromium/chromium/blob/5babd82a3403ae4c580afc34df4c677d70779b52/components/sessions/core/tab_restore_service_impl.cc#L116-L119 "
                 "(the two command ids).\nHas Post Data, Overriding User Agent and HTTP Status "
                 "hold one value across every row of an image whose entries are all ordinary page "
                 "loads; they are reported as stored and what sets them is not established here. "
                 "Each entry also carries a page state blob holding form and scroll state; it is "
                 "not decoded and only its size is reported. Every entry decoded on the tested "
                 "images consumed its record exactly, which is what shows the field order is "
                 "right.\nChromium's components/sessions/core/tab_restore_service.h describes the "
                 "service whose command ids are used here as maintaining the most recently closed "
                 "tabs and windows "
                 "(https://github.com/chromium/chromium/blob/5babd82a3403ae4c580afc34df4c677d70779b52/components/sessions/core/tab_restore_service.h#L37). "
                 "A row is a navigation entry stored in that file. It does not show that the page "
                 "was open at acquisition, and the file is not a full browsing history. Which "
                 "tabs reach the file on Android was not measured. A page here "
                 "need not appear in the browser's History database.",
        "paths": ('*/app_chrome/*/Sessions/Tabs_*',),
        "output_types": "standard",
        "artifact_icon": "browser",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 4 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 14 rows",
            "galaxys10_a10": "Android 10 | 10 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 6 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 39 rows",
            "pixel7a_a14": "Android 14 | 11 rows",
            "russell_a14": "Android 14 | 4 rows",
            "russell_pixel6a_a13": "Android 13 | 21 rows",
            "s20fe_a13": "Android 13 | 7 rows",
            "samsunga53_a14": "Android 14 | 6 rows",
            "samsungs20_a13": "Android 13 | 3 rows",
            "sharon_a13": "Android 13 | 9 rows",
            "sharon_a14": "Android 14 | 3 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
    "chrome_session_tab_state": {
        "name": "Chromium Session Tabs - Tab State",
        "description": "The entry each tab was sitting on in the tab restore file, with the "
                       "timestamp the browser stored against it.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-09-04",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Chromium Sessions",
        "notes": "Read from the same Tabs_<number> files, from the command Chromium calls "
                 "kCommandSelectedNavigationInTab. Unlike the navigation entries this record is "
                 "not a pickle but a fixed structure of a tab id, the selected navigation index "
                 "and a timestamp, microseconds since 1601. The event at which Chromium records "
                 "that timestamp was not sourced here, so it is reported as stored. One row per "
                 "record in each selected file. Mirrored storage views with the same canonical identity "
                 "and exactly equal complete bytes are reported once using the preferred spelling; "
                 "different byte states remain separate. Original parser contribution: "
                 "@AlexisBrignoni, Claude.\n"
                 "Selected Index refers to the Index column of the navigation entries artifact "
                 "for the same Tab ID, so the two join on Tab ID to show which page the tab was "
                 "on. Browser reports the package the file was found under.",
        "paths": ('*/app_chrome/*/Sessions/Tabs_*',),
        "output_types": "standard",
        "artifact_icon": "browser-check",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 2 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 2 rows",
            "galaxys10_a10": "Android 10 | 7 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 4 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 12 rows",
            "pixel7a_a14": "Android 14 | 4 rows",
            "russell_a14": "Android 14 | 4 rows",
            "russell_pixel6a_a13": "Android 13 | 8 rows",
            "s20fe_a13": "Android 13 | 1 row",
            "samsunga53_a14": "Android 14 | 3 rows",
            "samsungs20_a13": "Android 13 | 1 row",
            "sharon_a13": "Android 13 | 7 rows",
            "sharon_a14": "Android 14 | 3 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import datetime
import hashlib
import os
import re

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.snss_parser import SNSSError, read_navigation_entries, read_selected_navigations
from scripts.artifacts.storagePathViews import canonical_path

_CHROMIUM_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
_PACKAGE = re.compile(r'/([^/]+)/app_chrome/', re.I)


def _chromium_time(value):
    """Microseconds since 1601 as an aware UTC datetime; 0 and empty are reported as blank."""
    if value in (None, '', 0):
        return ''
    try:
        return _CHROMIUM_EPOCH + datetime.timedelta(microseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _browser(path):
    """The package the file sits under, so one cross-browser glob still attributes each row."""
    match = _PACKAGE.search(path.replace('\\', '/'))
    return match.group(1) if match else ''


def _file_fingerprint(path):
    """Index possible aliases without holding file contents in memory."""
    digest = hashlib.sha256()
    size = 0
    with open(path, 'rb') as handle:
        while chunk := handle.read(65536):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.digest()


def _same_file_bytes(left, right):
    """A digest match is only a candidate; compare every byte before collapsing."""
    with open(left, 'rb') as left_file, open(right, 'rb') as right_file:
        while True:
            left_chunk = left_file.read(65536)
            right_chunk = right_file.read(65536)
            if left_chunk != right_chunk:
                return False
            if not left_chunk:
                return True


def _tab_files(context):
    states = {}
    independent = []
    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if not os.path.basename(file_found).startswith('Tabs_'):
            continue
        key, rank = canonical_path(context.get_relative_path(file_found))
        try:
            size, digest = _file_fingerprint(file_found)
            candidates = states.setdefault((key, size, digest), [])
            for index, (prior_rank, prior_path) in enumerate(candidates):
                if _same_file_bytes(file_found, prior_path):
                    if (rank, file_found) < (prior_rank, prior_path):
                        candidates[index] = (rank, file_found)
                    break
            else:
                candidates.append((rank, file_found))
        except OSError:
            # Let the unchanged decoder and wrapper log/handle this path.
            independent.append(file_found)
    retained = independent + [path for candidates in states.values() for _, path in candidates]
    yield from sorted(retained)


@artifact_processor
def chrome_session_tabs(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Browser',
        'Tab ID',
        'Index',
        'URL',
        'Title',
        'HTTP Status',
        'Transition Type (as stored)',
        'Referrer URL',
        'Original Request URL',
        'Has Post Data',
        'Overriding User Agent',
        'Referrer Policy (as stored)',
        'Page State Bytes',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in _tab_files(context):
        try:
            entries = read_navigation_entries(file_found)
        except (SNSSError, OSError) as error:
            logfunc(f'Chromium Session Tabs: could not read {os.path.basename(file_found)}: {error}')
            continue
        browser = _browser(file_found)
        relative = context.get_relative_path(file_found)
        for entry in entries:
            data_list.append((
                _chromium_time(entry['timestamp']),
                browser,
                entry['tab_id'],
                entry['index'],
                entry['url'],
                entry['title'],
                entry['http_status_code'] if entry['http_status_code'] is not None else '',
                entry['transition_type'] if entry['transition_type'] is not None else '',
                entry['referrer_url'],
                entry['original_request_url'],
                entry['has_post_data'] if entry['has_post_data'] is not None else '',
                entry['is_overriding_user_agent'] if entry['is_overriding_user_agent'] is not None else '',
                entry['referrer_policy'] if entry['referrer_policy'] is not None else '',
                entry['page_state_length'],
                relative,
            ))
        if entries:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chrome_session_tab_state(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Browser',
        'Tab ID',
        'Selected Index',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in _tab_files(context):
        try:
            records = read_selected_navigations(file_found)
        except (SNSSError, OSError) as error:
            logfunc(f'Chromium Session Tabs: could not read {os.path.basename(file_found)}: {error}')
            continue
        browser = _browser(file_found)
        relative = context.get_relative_path(file_found)
        for record in records:
            data_list.append((
                _chromium_time(record['timestamp']),
                browser,
                record['tab_id'],
                record['index'],
                relative,
            ))
        if records:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
