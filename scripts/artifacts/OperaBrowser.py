__artifacts_v2__ = {
    "opera_tabs": {
        "name": "Opera Browser - Tabs",
        "description": "Browser tabs recorded in Opera's session_db tab-state store, "
                       "open or closed, with each tab's position in the tab bar and "
                       "the page it was showing. session_db is a separate store from the "
                       "Chromium History database.",
        "author": "@Gear-I, Claude", 
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Opera",
        "notes": "Opera's regular browsing history, search terms, bookmarks, "
                 "autofill, cookies and saved logins are already covered by this "
                 "project's Chromium artifacts (chrome.py and the chrome*.py family), "
                 "which already glob for 'app_opera' alongside Chrome, Samsung "
                 "Browser and WebView, since Opera stores that data in the same "
                 "Chromium schema. This module covers only what is unique to Opera "
                 "and not already collected there: its own session/tab-state store. "
                 "'Restored' is Yes when the recently_closed_tab.restored value for a closed tab "
                 "is set; what sets that value is not established here. No timestamp column was "
                 "found in session_db on the device this was validated against, and none was "
                 "found in the binary page_state or JSON user_data blobs. 'Current Page Last "
                 "Visit Time' is therefore not native to this store: it is recovered by matching "
                 "the current page's URL, exactly, against Opera's own History database's "
                 "urls.last_visit_time, and is left blank when no exact match exists (this "
                 "happens for Opera's internal 'operaui://startpage' and, on the device this was "
                 "validated against, for two address-bar searches whose visit did not leave a "
                 "matching literal URL in History either). Because it is the URL's *last* visit "
                 "and not necessarily the visit this specific tab made, a URL revisited after "
                 "this tab session would show a later time than when this tab actually had it "
                 "open. Two other Opera-only stores were inspected and left out of this release: "
                 "reading.db (the Reading List/'save for later' feature) had zero rows on the "
                 "device this was validated against, so its column mapping could not be "
                 "confirmed against real content; and searchengines.db held only a list of "
                 "built-in search engines on the device this was validated against. The "
                 "databases-off-the-record folder was empty on the device this was validated "
                 "against, "
                 "so no parser for it is included here. If an extraction contains more "
                 "than one Opera profile, only the first session_db/History pair found "
                 "is used; a device with multiple profiles is a known, untested edge "
                 "case rather than one confirmed to work.",
        "paths": ('*/app_opera/session_db*', '*/app_opera/History*'),
        "output_types": "standard",
        "artifact_icon": "layout",
        "sample_data": {
            "pixel7a_a14": "Android 14 |  3 rows",
        },
    },
    "opera_tab_navigation": {
        "name": "Opera Browser - Tab Navigation History",
        "description": "The back/forward navigation stack recorded inside each Opera "
                       "tab, from session_db's navigation_entry table: the pages the "
                       "tab moved to, in order, with the page currently on screen "
                       "flagged. Address-bar searches are decoded from the "
                       "'opera-internal://search' URL scheme into the search text the URL "
                       "carries.",
        "author": "@Gear-I, Claude", 
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Opera",
        "notes": "This is the tab's navigation stack as stored, not a full visit log; a page "
                 "absent here may still have been visited. The Chromium History artifact "
                 "(chrome.py) reads the History database separately, so the two should be read "
                 "together. Search Query is decoded from URLs carrying the "
                 "'opera-internal://search' scheme; for entries without that scheme the column "
                 "is left blank. No timestamp column was found in navigation_entry on the device "
                 "this was validated against, and none was found in the binary page_state or "
                 "JSON user_data "
                 "blobs. 'Last Visit Time' is recovered by matching this entry's URL, "
                 "exactly, against Opera's own History database's urls.last_visit_time, "
                 "and is left blank when no exact match exists, which happens for the "
                 "internal 'operaui://startpage' entry tab starts from and, on "
                 "the device this was validated against, for two address-bar searches "
                 "whose visit did not leave a matching literal URL in History either. "
                 "Because it is the URL's *last* visit rather than necessarily the "
                 "visit this entry represents, a URL revisited later than this "
                 "navigation would show that later time instead. If an extraction "
                 "contains more than one Opera profile, only the first "
                 "session_db/History pair found is used; a device with multiple "
                 "profiles is a known, untested edge case rather than one confirmed "
                 "to work.",
        "paths": ('*/app_opera/session_db*', '*/app_opera/History*'),
          "output_types": "standard",
        "artifact_icon": "compass",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 8 rows",
        },

    }

}

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc
from scripts.artifacts.storagePathViews import unique_files

_WEBKIT_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)


def _webkit_to_utc(value):
    """Chromium/WebKit timestamp: microseconds since 1601-01-01 UTC."""
    if value is None:
        return None
    try:
        return _WEBKIT_EPOCH + timedelta(microseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return None


def _history_last_visit_times(history_db_path):
    """Map url -> last_visit_time (datetime) from Opera's own History database.

    session_db carries no timestamp of any kind, so this is the only way to put
    a real date on a tab or navigation entry: an exact URL match against a
    second, independent file. Callers must treat a hit as that URL's *last*
    visit, not necessarily the specific visit being dated.
    """
    times = {}
    if not history_db_path:
        return times
    try:
        rows = get_sqlite_db_records(
            history_db_path, "SELECT url, last_visit_time FROM urls")
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logfunc(f"Opera: could not read History for timestamp correlation: {ex}")
        return times
    for url, last_visit_time in rows:
        converted = _webkit_to_utc(last_visit_time)
        if converted is not None:
            times[url] = converted
    return times


def _decode_title(value):
    if isinstance(value, bytes):
        try:
            return value.decode("utf-16-le").rstrip("\x00")
        except UnicodeDecodeError:
            return value.decode("utf-8", "replace")
    if value is None:
        return ""
    return str(value)


def _search_query(virtual_url):
    if not virtual_url or not virtual_url.startswith("opera-internal://search"):
        return ""
    query = parse_qs(urlparse(virtual_url).query)
    values = query.get("display_string")
    return values[0] if values else ""


def _stores_by_container(files_found):
    """[(session_db path, History path or None)] per app container, sorted.

    An extraction can carry a container per Android user, each with its own
    tabs and history. The History join must stay inside one container: a
    tab's URL is dated against the same user's History, never another's.
    Both files sit directly under app_opera/, so the shared parent directory
    is the container key. The exact-suffix test never matches a sidecar.
    """
    normalized = [str(f).replace('\\', '/') for f in files_found]
    history_by_root = {f[:-len('History')]: f for f in normalized
                       if f.endswith('History')}
    return [(f, history_by_root.get(f[:-len('session_db')]))
            for f in sorted(normalized) if f.endswith('session_db')]


@artifact_processor
def opera_tabs(context):
    data_headers = (
        "Status", "Tab Position", "Current Page Title", "Current Page URL",
        ("Current Page Last Visit Time (History Match)", "datetime"),
        "Navigation Entry Count", "Restored", "Internal Tab ID",
    )

    stores = _stores_by_container(unique_files(context))
    if not stores:
        return data_headers, [], ""

    data_list = []
    for db_path, history_db_path in stores:
        history_times = _history_last_visit_times(history_db_path)

        tab_order = {}
        for tab_id, ix in get_sqlite_db_records(db_path, "SELECT tab, ix FROM tab_order"):
            tab_order[tab_id] = ix

        closed = {}
        for tab_id, restored in get_sqlite_db_records(
                db_path, "SELECT tab, restored FROM recently_closed_tab"):
            closed[tab_id] = bool(restored)

        entry_counts = {}
        current_page = {}
        for tab_id, ix, url, title in get_sqlite_db_records(
                db_path, "SELECT tab, ix, url, title FROM navigation_entry"):
            entry_counts[tab_id] = entry_counts.get(tab_id, 0) + 1
            current_page[(tab_id, ix)] = (url, _decode_title(title))

        for tab_id, current_entry in get_sqlite_db_records(
                db_path, "SELECT tab, current_entry FROM tab"):
            is_closed = tab_id in closed
            url, title = current_page.get((tab_id, current_entry), ("", ""))
            data_list.append((
                "Closed" if is_closed else "Open",
                tab_order.get(tab_id, ""),
                title,
                url,
                history_times.get(url),
                entry_counts.get(tab_id, 0),
                "Yes" if closed.get(tab_id) else ("" if is_closed else "N/A"),
                tab_id,
            ))

    data_list.sort(key=lambda row: (row[0] != "Open", row[1] if row[1] != "" else 999))
    logfunc(f"Opera Browser Tabs: {len(data_list)} tab(s) recovered from session_db.")
    return data_headers, data_list, '\n'.join(db for db, _ in stores)


@artifact_processor
def opera_tab_navigation(context):
    data_headers = (
        "Internal Tab ID", "Entry Index", "Is Current Page", "Title", "URL",
        "Search Query", ("Last Visit Time (History Match)", "datetime"),
    )

    stores = _stores_by_container(unique_files(context))
    if not stores:
        return data_headers, [], ""

    data_list = []
    for db_path, history_db_path in stores:
        history_times = _history_last_visit_times(history_db_path)

        current_entry_by_tab = {}
        for tab_id, current_entry in get_sqlite_db_records(
                db_path, "SELECT tab, current_entry FROM tab"):
            current_entry_by_tab[tab_id] = current_entry

        for tab_id, ix, url, virtual_url, title in get_sqlite_db_records(
                db_path,
                "SELECT tab, ix, url, virtual_url, title FROM navigation_entry "
                "ORDER BY tab, ix"):
            data_list.append((
                tab_id,
                ix,
                "Yes" if current_entry_by_tab.get(tab_id) == ix else "",
                _decode_title(title),
                url,
                _search_query(virtual_url),
                history_times.get(url),
            ))

    logfunc(f"Opera Browser Tab Navigation History: {len(data_list)} navigation "
            f"entr{'y' if len(data_list) == 1 else 'ies'} recovered.")
    return data_headers, data_list, '\n'.join(db for db, _ in stores)