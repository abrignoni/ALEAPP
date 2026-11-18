__artifacts_v2__ = {
    "samsung_internet_bookmarks": {
        "name": "Samsung Internet - Bookmarks",
        "description": "Bookmarks from the Samsung Internet BOOKMARKS table in SBrowser.db, with the folder each "
                       "sits in.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            'One row per BOOKMARKS row in com.sec.android.app.sbrowser/databases/SBrowser.db that is not a '
            'folder (FOLDER 1); Folder is the TITLE of the row PARENT names, or PARENT as stored when no '
            'folder row has that id. Created and Modified are CREATED and MODIFIED read as Unix milliseconds. '
            'A stored 0, a NULL, a negative or a non-integer time is shown blank. On '
            'samsung_a166u_a16_known_20261116 the two bookmarks added in the session (15:37:29 and 15:40:42 '
            'UTC in the mint log) had Created 15:37:28 and 15:40:41 UTC and bookmark_type 2, and the four '
            'rows not added in the session had CREATED 0 and bookmark_type 1. What bookmark_type means is not '
            'established. Modified held 17:37:39 UTC on 3 of the 6 rows and a stored 0 on the other 3. On the '
            'known-data image BOOKMARKS MODIFIED (3 rows), READINGLIST modified, and TABS DATE_CREATED and '
            'DATE_MODIFIED held times of 17:37:39 to 17:37:59 UTC, while most of the items were made between '
            '15:19 and 15:41 UTC (mint log); those four columns do not by themselves record when the item was '
            'made. Folder held Samsung account, Deleted (as stored) held 0 and Tags (as stored) had no value '
            'on all 6 rows of the known-data image; a NULL TAGS is shown blank. Rows with DELETED other than '
            '0 are kept and shown; no image checked had such a row. Only the columns shown are read; the '
            'FAVICON and TOUCH_ICON blobs and the sync, account, device, position and guid columns are among '
            'those not reported. app_sbrowser/Default/Bookmarks, which the Bookmarks artifact '
            '(chromeBookmarks.py) reads, was not present on the known-data image. Created leads the table '
            'because on the two known-data bookmarks it matched the time the bookmark was added; Created is '
            'blank on 4 of 6 rows there.'
        ),
        "paths": ('*/com.sec.android.app.sbrowser/databases/SBrowser.db*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.sbrowser 28.0.4.71 | 6 rows",
            "adams_ss135dl_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "anne_a15": "Android 15 | com.sec.android.app.sbrowser | 2 rows",
            "cookbook_a11": "Android 11 | com.sec.android.app.sbrowser | 1 row",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.sbrowser | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | com.sec.android.app.sbrowser | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.sec.android.app.sbrowser | 0 rows",
            "s20fe_a13": "Android 13 | com.sec.android.app.sbrowser | 1 row",
            "samsunga53_a14": "Android 14 | com.sec.android.app.sbrowser | 0 rows",
            "sharon_a13": "Android 13 | com.sec.android.app.sbrowser | 4 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.sbrowser | 4 rows",
        },
    },
    "samsung_internet_saved_pages": {
        "name": "Samsung Internet - Saved Pages",
        "description": "Pages saved in Samsung Internet (READINGLIST table in SBrowser.db), with the saved "
                       "page file the row records.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            'One row per READINGLIST row in SBrowser.db, the list Samsung Internet showed as Saved pages in '
            "the known-data session. Saved Page links the file the row's dir_path records, matched on that "
            'recorded path inside the same app container under files/readinglist/; the copy is given an '
            '.mhtml extension when its own headers say MIME multipart/related. Created and Modified are '
            'created and modified read as Unix milliseconds. A stored 0, a NULL, a negative or a non-integer '
            'time is shown blank. On samsung_a166u_a16_known_20261116 the one page saved at 15:41:09 UTC '
            "(mint log) had created 15:41:06 UTC, and the saved file's own Date header gives the same time. "
            'Modified held 17:37:39 UTC. On the known-data image BOOKMARKS MODIFIED (3 rows), READINGLIST '
            'modified, and TABS DATE_CREATED and DATE_MODIFIED held times of 17:37:39 to 17:37:59 UTC, while '
            'most of the items were made between 15:19 and 15:41 UTC (mint log); those four columns do not by '
            'themselves record when the item was made. is_deleted (as stored) and isReadingItem (as stored) '
            'held 0; their meaning is not established. Only the columns shown are read; the path, '
            'description, favicon, device, sync and account columns are among those not reported. The Offline '
            'Pages artifact (chromeOfflinePages.py) lists app_sbrowser/Default/Offline Pages in its paths; '
            'that folder was not present on the known-data image. No other image checked had a READINGLIST '
            'row.'
        ),
        "paths": ('*/com.sec.android.app.sbrowser/databases/SBrowser.db*',
                  '*/com.sec.android.app.sbrowser/files/readinglist/*'),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.sbrowser 28.0.4.71 | 1 row",
            "adams_ss135dl_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "anne_a15": "Android 15 | com.sec.android.app.sbrowser | 0 rows",
            "cookbook_a11": "Android 11 | com.sec.android.app.sbrowser | 0 rows",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.sec.android.app.sbrowser | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.sec.android.app.sbrowser | 0 rows",
            "s20fe_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.sbrowser | 0 rows",
            "sharon_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.sbrowser | 0 rows",
        },
    },
    "samsung_internet_tabs": {
        "name": "Samsung Internet - Tabs",
        "description": "Tabs listed in the Samsung Internet TABS table in SBrowser.db, with the tab's cached "
                       "page thumbnail where one is in the extraction.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            'One row per TABS row in SBrowser.db. Thumbnail renders cache/Bitmap/Thumbnail/<w>/<n>.0 in the '
            'same app container for the tab whose TAB_ID is <w>_<n>. That link is by name: on '
            'samsung_a166u_a16_known_20261116 each of the four thumbnails (tabs 1_1, 1_3, 1_5 and 1_6) showed '
            'the page its tab row names, and tabs 1_2 and 1_7 had none. On sharon_a13 5 of 5 and on '
            'sharon_a14 3 of 4 tabs had a thumbnail by that name, not checked against the pages. On the '
            'known-data image the LiteThumbnail and FullScreen folders beside it hold files keyed the same '
            'way; they are not reported. Date Created and Date Modified are DATE_CREATED and DATE_MODIFIED '
            'read as Unix milliseconds. A stored 0, a NULL, a negative or a non-integer time is shown blank. '
            'Date Modified leads the table; what event either column records is not established. The mint log '
            'records four tabs left open at 15:41:55 UTC and two pages opened at 17:37:37 and 17:37:50 UTC, '
            'and TABS held six rows, one per page. No row has TAB_ID 1_4; the Tab Records artifact holds a '
            'closed record for tab 4 (closing time 15:41:54 UTC) and the mint log records one tab closed at '
            '15:41:55 UTC. Five tabs whose pages the mint log places between 15:19 (intents sent before first '
            'run) and 17:37:37 UTC all had Date Created 17:37:39 UTC, and the tab opened at 17:37:50 UTC had '
            'Date Created 17:37:50 UTC. On the known-data image BOOKMARKS MODIFIED (3 rows), READINGLIST '
            'modified, and TABS DATE_CREATED and DATE_MODIFIED held times of 17:37:39 to 17:37:59 UTC, while '
            'most of the items were made between 15:19 and 15:41 UTC (mint log); those four columns do not by '
            'themselves record when the item was made. TAB_ACTIVATE (as stored) held true on one row (TAB_ID '
            '1_6) on the known-data image. IS_DELETED (as stored) and IS_INCOGNITO (as stored) held 0 and '
            'Group Name had no value on every row of the images checked. The per-tab files files/<w>_tab<n> '
            'hold the back and forward navigation list of each tab; the Tab Navigation History artifact reads '
            'them, and the Saved Tab State artifact reads the <w>tab_state file. Not reported here: the TAB_FAV_ICON '
            'blob, TAB_GROUP_COLOR, TAB_USAGE and the sync, device and account columns.'
        ),
        "paths": ('*/com.sec.android.app.sbrowser/databases/SBrowser.db*',
                  '*/com.sec.android.app.sbrowser/cache/Bitmap/Thumbnail/*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.sbrowser 28.0.4.71 | 6 rows",
            "adams_ss135dl_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "anne_a15": "Android 15 | com.sec.android.app.sbrowser | 1 row",
            "cookbook_a11": "Android 11 | com.sec.android.app.sbrowser | 1 row",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.sec.android.app.sbrowser | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.sec.android.app.sbrowser | 0 rows",
            "s20fe_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.sbrowser | 0 rows",
            "sharon_a13": "Android 13 | com.sec.android.app.sbrowser | 5 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.sbrowser | 4 rows",
        },
    },
    "samsung_internet_tab_records": {
        "name": "Samsung Internet - Tab Records (SmartTabDelete)",
        "description": "Per-tab records from the SMARTTABDELETE table of SmartTabDelete.db, including tabs that "
                       "were closed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            'One row per SMARTTABDELETE row in com.sec.android.app.sbrowser/databases/SmartTabDelete.db. '
            'Column names are the stored ones because their meanings are not sourced; the three times are '
            'read as Unix milliseconds. A stored 0, a NULL, a negative or a non-integer time is shown blank. '
            'On samsung_a166u_a16_known_20261116 the table held one row per tab number 1 to 7, including tab '
            '4, which is not in TABS: its TAB_CLOSED_STATUS was 1 and its TAB_CLOSING_TIME 15:41:54 UTC, '
            'against the tab closed at 15:41:55 UTC in the mint log; the other six rows had TAB_CLOSED_STATUS '
            '0 and a TAB_CLOSING_TIME of 0, shown blank. TAB_URL holds a host name, not a full URL. '
            'TAB_CREATION_TIME ran from 15:19:53 to 17:37:59 UTC; for the tabs opened by intent at 17:37:37 '
            'and 17:37:50 UTC it was 17:37:45 and 17:37:59 UTC, and for tab 5, whose page changed twice in '
            'the session, it was 15:40:30 UTC, so what event sets it is not established. TAB_LAUNCHED_TYPE, '
            'CUMULATIVE_COUNT and TAB_CUMULATIVE_TIME are shown as stored; their meanings are not '
            'established. The period, training, refresh and EXTRA columns are not reported. Rows were present '
            'on hc_pixel8pro_a16 (4), hc_pixel8pro_a17 (4) and s20fe_a13 (1), not checked against known data.'
        ),
        "paths": ('*/com.sec.android.app.sbrowser/databases/SmartTabDelete.db*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.sbrowser 28.0.4.71 | 7 rows",
            "s20fe_a13": "Android 13 | com.sec.android.app.sbrowser | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.sec.android.app.sbrowser | 4 rows",
            "hc_pixel8pro_a17": "Android 17 | com.sec.android.app.sbrowser | 4 rows",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.sbrowser | 0 rows",
        },
    },
    "samsung_internet_tab_navigation": {
        "name": "Samsung Internet - Tab Navigation History",
        "description": "Per-tab back and forward navigation entries from the files/<w>_tab<n> tab-state files of "
                       "Samsung Internet, stored in the Chromium WebContentsState format. One row per navigation "
                       "entry.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            'One row per navigation entry in each files/<w>_tab<n> file, in the app private data folder '
            '(data/data/com.sec.android.app.sbrowser/files/). Source File names the file; its name holds two '
            'numbers, the same pair the Tabs artifact shows as TAB_ID, and what the first number denotes is '
            'not established. On samsung_a166u_a16_known_20261116 each file held, after a short header and a '
            '4-byte big-endian content size, the tab WebContentsState as a base::Pickle, then a trailer; the '
            'size at offset 8 is used to locate and length-check the pickle, and the other header bytes and the '
            'trailer are not interpreted (the trailer on this image did not match the field order of the '
            'Chromium Android tab-state writer, so it is read as Samsung-specific and left alone). The pickle '
            'holds the is_off_the_record flag, the entry count, the current-entry index and then one '
            'length-prefixed SerializedNavigationEntry per entry. URL is virtual_url and Title is the stored '
            'title. Current Entry is Yes on the entry whose stored index equals the current-entry index in the '
            'pickle. Navigation Index is the index stored in the entry (0 to n-1 on this image). Navigation '
            'Timestamp is the entry timestamp, microseconds since 1601-01-01 UTC; a 0, a negative value or an '
            'entry that ends before the field is shown blank. Transition names the core type from the low byte '
            'and, in parentheses, the qualifier bits named in page_transition_types.h; other set bits are not '
            'shown and a core value outside 0 to 10 is shown as its number. HTTP Status, Referrer and Original '
            'URL (original_request_url) are shown as stored; Referrer and Original URL are blank when the '
            'stored string is empty, and all three are blank when the entry ends before them. Off The Record '
            'is Yes when is_off_the_record is set. On samsung_a166u_a16_known_20261116 the 6 files gave 11 '
            'entries; HTTP Status held 200 on all 11 rows and Off The Record was No on all 11 rows (no image '
            'checked had it set, so the Yes path is from source and a built test file only). Referrer was blank on 10 of '
            '11, set on the one row whose Transition is LINK (CLIENT_REDIRECT); Original URL was populated on '
            'all 11, equal to URL on 10 and equal to Referrer on that one row. The 11 timestamps fell on 16 '
            'November 2026 between 15:19 and 17:37 UTC. Not read: the encoded page state, the has-post-data '
            'mask, the referrer policy, the search terms, the user-agent override, the task ids, the extended '
            'info map, and the file header and trailer. A file is skipped and named in the run log when its '
            'size field and the pickle length disagree, the pickle runs past the file, or an entry cannot be '
            'read; an entry that ends early is still shown, with the missing columns blank. Format from '
            'Chromium (current source; Samsung Internet\'s own source was not read): '
            "'web_contents_state.cc (WriteStateHeaderToPickle, WriteSerializedNavigationsIntoPickle, "
            "ExtractNavigationEntries)', "
            'https://github.com/chromium/chromium/blob/0889dbff0b08355e11f0f6aac36ae65713f8f33f/chrome/browser/tab/web_contents_state.cc#L70-L105 '
            'and '
            'https://github.com/chromium/chromium/blob/0889dbff0b08355e11f0f6aac36ae65713f8f33f/chrome/browser/tab/web_contents_state.cc#L349-L399; '
            "'serialized_navigation_entry.cc (ReadFromPickle)', "
            'https://github.com/chromium/chromium/blob/0889dbff0b08355e11f0f6aac36ae65713f8f33f/components/sessions/core/serialized_navigation_entry.cc#L173-L278; '
            "transition types 'page_transition_types.h', "
            'https://github.com/chromium/chromium/blob/0889dbff0b08355e11f0f6aac36ae65713f8f33f/ui/base/page_transition_types.h#L29-L155; '
            "the timestamp epoch 'base/time/time.h', "
            'https://github.com/chromium/chromium/blob/0889dbff0b08355e11f0f6aac36ae65713f8f33f/base/time/time.h#L542. '
            'Checked on samsung_a166u_a16_known_20261116 only.'
        ),
        "paths": ('*/com.sec.android.app.sbrowser/files/*_tab[0-9]*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.sbrowser 28.0.4.71 | 11 rows (6 tab files)",
        },
    },
    "samsung_internet_tab_state": {
        "name": "Samsung Internet - Saved Tab State",
        "description": "Tabs listed in Samsung Internet's files/<n>tab_state file, the saved list of open tabs: URL, "
                       "title, the locked flag, whether the tab was a Secret mode tab, visit count and active seconds.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Samsung Internet",
        "notes": (
            'One row per tab in each files/<n>tab_state file in the app private data folder '
            '(data/data/com.sec.android.app.sbrowser/files/), the list of open tabs Samsung Internet '
            'saves and reads back on start. Format from the app\'s own code, decompiled with jadx from the '
            'base.apk on samsung_a166u_a16_known_20261117 (Samsung Internet 30.0.5.27 per the session '
            'record): TabStateWriter.serialize writes a version, the Secret mode tab count, the tab '
            'count, two active-tab indexes and, from version 8, a content page index, then the Secret '
            'mode tabs followed by the normal tabs; TabState.write writes each tab\'s id, URL, title, '
            'locked flag, group name and colour, two user agent options, two zoom values with their '
            'flags, visit count, active time and, for a normal tab, a group id; TabStateVersion gates '
            'each field by the file\'s version (3 to 15 are read). A file is read only when its fields end '
            'exactly at its last byte; otherwise it is skipped and named in the run log. Tab ID is the '
            'stored tab id. URL and Title are stored text; Title is blank in files older than version 14. '
            'Locked is the stored locked flag (version 7 and later). Secret Mode Tab is Yes for the tabs '
            'written before the normal ones, as many as the stored Secret mode count. Current Tab is Yes '
            'on the tab at the stored active index of its kind. Visit Count is stored from version 12. '
            'Active Seconds (as stored) is stored from version 13: in the app\'s code it is the sum of the '
            'times the tab was in the foreground, taken from System.currentTimeMillis and divided by '
            '1000, so seconds. Known data (samsung_a166u_a16_known_20261117, compared with '
            'samsung_a166u_a16_known_20261116, taken the day before): one tab was locked from the tab '
            'manager at 06:34:58 UTC and a Secret mode tab was opened at 06:35:30, then the app was '
            'force-stopped and relaunched at 06:37:24 to 06:37:27, per the session record. The file held '
            '7 tabs with Locked Yes on that tab only, and a Secret mode count of 0: the Secret mode tab '
            'was not restored on relaunch and is not in the file. The day before, the same tab was not '
            'locked. One tab held 20 active seconds on the earlier image and 0 after the restart, so the '
            'value is not a lifetime total. Secret Mode Tab was No on every row of the tested images; no '
            'file held a Secret mode tab, so the Yes path follows the code and is not exercised. Not '
            'shown: the group name, colour and id (empty or 0 on every tested tab), the user agent and '
            'zoom values, and the content page index. The <n> in the file name is the instance id the '
            'writer is given; it was 1 on every tested image. Android User is the user of the app data '
            'folder the file is in, taken from its path (data/data is user 0). On the tested images: 11 '
            'files on 10 images, versions 11, 13, 14 and 15, 28 rows; falken_a326u_a13 held a file with '
            'no tabs. Locked held No on every row but that one tab. Android User held 0 on every row of 8 '
            'of the 9 images with rows; cookbook_a11 also had user 150. Visit Count and Active Seconds '
            '(as stored) were blank on every row of cookbook_a11 and sharon_a13, whose files are version '
            '11. The pintab.db database held no rows on samsung_a166u_a16_known_20261117 after the lock.'
        ),
        "paths": ('*/com.sec.android.app.sbrowser/files/*tab_state',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.sbrowser | 7 rows (1 locked)",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.sbrowser | 6 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.sbrowser | 4 rows",
            "sharon_a13": "Android 13 | com.sec.android.app.sbrowser | 5 rows",
            "cookbook_a11": "Android 11 | com.sec.android.app.sbrowser | 2 rows (1 user 0, 1 user 150)",
            "anne_a15": "Android 15 | com.sec.android.app.sbrowser | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.sec.android.app.sbrowser | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.sec.android.app.sbrowser | 1 row",
            "s20fe_a13": "Android 13 | com.sec.android.app.sbrowser | 1 row",
            "falken_a326u_a13": "Android 13 | com.sec.android.app.sbrowser | file with no tabs | 0 rows",
        },
    },
}

import datetime
import os
import re
import sqlite3
import struct

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import canonical_path, unique_files

_PACKAGE = '/com.sec.android.app.sbrowser/'


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return ''


def _split(context, file_found):
    """(container, path inside the package) for a file, using the storage-neutral key."""
    key, _rank = canonical_path(context.get_relative_path(file_found))
    key = key.replace('\x00de:', '\x00ce:')  # one app's DE and CE copies are one container here
    if _PACKAGE not in key:
        return key, ''
    container, inner = key.split(_PACKAGE, 1)
    return container, inner


def _sniffed_extension(path):
    """An extension for the media copy, from the file's own bytes, or None."""
    try:
        with open(path, 'rb') as handle:
            head = handle.read(4096)
    except OSError:
        return None, None
    if head.startswith(b'\xff\xd8\xff'):
        return '.jpg', None
    if head.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png', None
    if b'MIME-Version:' in head and b'multipart/related' in head:
        return '.mhtml', 'multipart/related'
    return None, None


def _check_in(path, name):
    extension, mime = _sniffed_extension(path)
    return check_in_media(path, name, force_extension=extension, force_type=mime) or ''


def _select(db, table, wanted):
    present = {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
    columns = ', '.join(f'"{name}"' if name in present else f'NULL AS "{name}"' for name in wanted)
    return [dict(zip(wanted, row)) for row in db.execute(f'SELECT {columns} FROM "{table}"').fetchall()]


def _read_table(file_found, table, wanted):
    db = open_sqlite_db_readonly(file_found)
    if db is None:
        return None
    try:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if table not in tables:
            return []
        return _select(db, table, wanted)
    except sqlite3.Error as ex:
        logfunc(f'Samsung Internet: {table} not read from {file_found}: {ex}')
        return None
    finally:
        db.close()


def _databases(context):
    for file_found in unique_files(context):
        file_found = str(file_found)
        if file_found.endswith('/databases/SBrowser.db') or file_found.endswith('\\databases\\SBrowser.db'):
            yield file_found


_BOOKMARK_COLUMNS = ('_ID', 'URL', 'TITLE', 'FOLDER', 'PARENT', 'DELETED', 'CREATED', 'MODIFIED',
                     'bookmark_type', 'TAGS')


@artifact_processor
def samsung_internet_bookmarks(context):
    data_list = []
    source_paths = []
    for file_found in _databases(context):
        rows = _read_table(file_found, 'BOOKMARKS', _BOOKMARK_COLUMNS)
        if rows is None:
            continue
        source_paths.append(file_found)
        folders = {row['_ID']: row['TITLE'] for row in rows if row['FOLDER'] == 1}
        for row in rows:
            if row['FOLDER'] == 1:
                continue
            data_list.append((
                _ms_to_utc(row['CREATED']),
                _ms_to_utc(row['MODIFIED']),
                row['TITLE'] or '',
                row['URL'] or '',
                folders.get(row['PARENT'], row['PARENT']),
                row['bookmark_type'],
                row['DELETED'],
                row['TAGS'] or '',
                row['_ID'],
            ))
    data_headers = (('Created', 'datetime'), ('Modified', 'datetime'), 'Title', 'URL', 'Folder',
                    'bookmark_type (as stored)', 'Deleted (as stored)', 'Tags (as stored)', 'Row ID')
    return data_headers, data_list, '\n'.join(source_paths)


_READINGLIST_COLUMNS = ('_id', 'title', 'url', 'dir_path', 'created', 'modified', 'is_deleted', 'isReadingItem')


@artifact_processor
def samsung_internet_saved_pages(context):
    files_found = [str(f) for f in unique_files(context)]
    saved = {}
    for file_found in files_found:
        if '/files/readinglist/' in file_found.replace('\\', '/') and not os.path.isdir(file_found):
            saved[_split(context, file_found)] = file_found

    data_list = []
    source_paths = []
    for file_found in files_found:
        if not (file_found.endswith('/databases/SBrowser.db') or file_found.endswith('\\databases\\SBrowser.db')):
            continue
        rows = _read_table(file_found, 'READINGLIST', _READINGLIST_COLUMNS)
        if rows is None:
            continue
        source_paths.append(file_found)
        container, _inner = _split(context, file_found)
        for row in rows:
            media_ref = ''
            name = os.path.basename(str(row['dir_path'] or ''))
            match = None
            stored = str(row['dir_path'] or '').replace('\\', '/')
            if _PACKAGE in stored:
                match = saved.get((container, stored.split(_PACKAGE, 1)[1]))
            if match:
                source_paths.append(match)
                media_ref = _check_in(match, name)
            data_list.append((
                _ms_to_utc(row['created']),
                _ms_to_utc(row['modified']),
                row['title'] or '',
                row['url'] or '',
                media_ref,
                name,
                row['is_deleted'],
                row['isReadingItem'],
                row['_id'],
            ))
    data_headers = (('Created', 'datetime'), ('Modified', 'datetime'), 'Title', 'URL', ('Saved Page', 'media'),
                    'Saved Page File', 'is_deleted (as stored)', 'isReadingItem (as stored)', 'Row ID')
    return data_headers, data_list, '\n'.join(source_paths)


_TAB_COLUMNS = ('_ID', 'TAB_ID', 'TAB_INDEX', 'TAB_URL', 'TAB_TITLE', 'TAB_GROUP_NAME', 'TAB_ACTIVATE',
                'IS_DELETED', 'IS_INCOGNITO', 'DATE_CREATED', 'DATE_MODIFIED')


@artifact_processor
def samsung_internet_tabs(context):
    files_found = [str(f) for f in unique_files(context)]
    thumbnails = {}
    for file_found in files_found:
        container, inner = _split(context, file_found)
        parts = inner.split('/')
        # cache/Bitmap/Thumbnail/<window>/<tab number>.0
        if len(parts) == 5 and parts[:3] == ['cache', 'Bitmap', 'Thumbnail'] and parts[4].endswith('.0'):
            thumbnails[(container, f'{parts[3]}_{parts[4][:-2]}')] = file_found

    data_list = []
    source_paths = []
    for file_found in files_found:
        if not (file_found.endswith('/databases/SBrowser.db') or file_found.endswith('\\databases\\SBrowser.db')):
            continue
        rows = _read_table(file_found, 'TABS', _TAB_COLUMNS)
        if rows is None:
            continue
        source_paths.append(file_found)
        container, _inner = _split(context, file_found)
        for row in rows:
            media_ref = ''
            thumbnail = thumbnails.get((container, str(row['TAB_ID'])))
            if thumbnail:
                media_ref = _check_in(thumbnail, f'tab {row["TAB_ID"]} thumbnail')
            data_list.append((
                _ms_to_utc(row['DATE_MODIFIED']),
                _ms_to_utc(row['DATE_CREATED']),
                row['TAB_TITLE'] or '',
                row['TAB_URL'] or '',
                media_ref,
                row['TAB_ID'],
                row['TAB_INDEX'],
                row['TAB_ACTIVATE'],
                row['IS_DELETED'],
                row['IS_INCOGNITO'],
                row['TAB_GROUP_NAME'] or '',
            ))
    data_headers = (('Date Modified', 'datetime'), ('Date Created', 'datetime'), 'Title', 'URL',
                    ('Thumbnail', 'media'), 'Tab ID', 'Tab Index', 'TAB_ACTIVATE (as stored)',
                    'IS_DELETED (as stored)', 'IS_INCOGNITO (as stored)', 'Group Name')
    return data_headers, data_list, '\n'.join(source_paths)


_TAB_RECORD_COLUMNS = ('AUTO_CLOSE_KEY', 'TAB_ID', 'TAB_URL', 'TAB_LAUNCHED_TYPE', 'TAB_CREATION_TIME',
                       'TAB_LAST_ACTIVE_START_TIME', 'TAB_CLOSED_STATUS', 'TAB_CLOSING_TIME', 'CUMULATIVE_COUNT',
                       'TAB_CUMULATIVE_TIME')


@artifact_processor
def samsung_internet_tab_records(context):
    data_list = []
    source_paths = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.replace('\\', '/').endswith('/databases/SmartTabDelete.db'):
            continue
        rows = _read_table(file_found, 'SMARTTABDELETE', _TAB_RECORD_COLUMNS)
        if rows is None:
            continue
        source_paths.append(file_found)
        for row in sorted(rows, key=lambda r: (r['TAB_CREATION_TIME'] or 0, str(r['AUTO_CLOSE_KEY']))):
            data_list.append((
                _ms_to_utc(row['TAB_CREATION_TIME']),
                _ms_to_utc(row['TAB_LAST_ACTIVE_START_TIME']),
                _ms_to_utc(row['TAB_CLOSING_TIME']),
                row['TAB_URL'] or '',
                row['TAB_ID'],
                row['TAB_CLOSED_STATUS'],
                row['TAB_LAUNCHED_TYPE'] or '',
                row['CUMULATIVE_COUNT'],
                row['TAB_CUMULATIVE_TIME'],
                row['AUTO_CLOSE_KEY'] or '',
            ))
    data_headers = (('TAB_CREATION_TIME', 'datetime'), ('TAB_LAST_ACTIVE_START_TIME', 'datetime'),
                    ('TAB_CLOSING_TIME', 'datetime'), 'TAB_URL (as stored)', 'TAB_ID', 'TAB_CLOSED_STATUS (as stored)',
                    'TAB_LAUNCHED_TYPE (as stored)', 'CUMULATIVE_COUNT (as stored)', 'TAB_CUMULATIVE_TIME (as stored)',
                    'AUTO_CLOSE_KEY')
    return data_headers, data_list, '\n'.join(source_paths)


# --- Tab navigation history (Chromium WebContentsState) -------------------------
#
# A files/<window>_tab<n> file is an Android tab-state file: a short header, then
# the tab's WebContentsState as a base::Pickle, then a trailer. The pickle holds
# the tab's back/forward navigation list. base::Pickle stores 32-bit
# little-endian values, each padded to the next 4-byte boundary; a string is a
# length (bytes for 8-bit, units for 16-bit) then the bytes, padded the same way.

_WEBKIT_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
_TAB_FILE_NAME = re.compile(r'\d+_tab\d+$')

_TRANSITION_CORE = {
    0: 'LINK', 1: 'TYPED', 2: 'AUTO_BOOKMARK', 3: 'AUTO_SUBFRAME',
    4: 'MANUAL_SUBFRAME', 5: 'GENERATED', 6: 'AUTO_TOPLEVEL',
    7: 'FORM_SUBMIT', 8: 'RELOAD', 9: 'KEYWORD', 10: 'KEYWORD_GENERATED',
}
_TRANSITION_QUALIFIERS = (
    (0x00800000, 'BLOCKED'), (0x01000000, 'FORWARD_BACK'),
    (0x02000000, 'FROM_ADDRESS_BAR'), (0x04000000, 'HOME_PAGE'),
    (0x08000000, 'FROM_API'), (0x10000000, 'CHAIN_START'),
    (0x20000000, 'CHAIN_END'), (0x40000000, 'CLIENT_REDIRECT'),
    (0x80000000, 'SERVER_REDIRECT'),
)


def _webkit_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return _WEBKIT_EPOCH + datetime.timedelta(microseconds=value)
    except OverflowError:
        return ''


def _name_transition(value):
    core = _TRANSITION_CORE.get(value & 0xFF, str(value & 0xFF))
    bits = value & 0xFFFFFFFF
    quals = [name for mask, name in _TRANSITION_QUALIFIERS if bits & mask]
    return f'{core} ({", ".join(quals)})' if quals else core


class _PickleReader:
    """Read the little-endian, 4-byte-aligned payload of a base::Pickle."""

    def __init__(self, data, payload_start, payload_end):
        self._data = data
        self._base = payload_start
        self._pos = payload_start
        self._end = payload_end

    def _take(self, length):
        end = self._pos + length
        if length < 0 or end > self._end:
            raise ValueError('read past end of pickle')
        chunk = self._data[self._pos:end]
        self._pos = end
        remainder = (self._pos - self._base) % 4
        if remainder:
            self._pos += 4 - remainder
        return chunk

    def read_int(self):
        return struct.unpack('<i', self._take(4))[0]

    def read_int64(self):
        return struct.unpack('<q', self._take(8))[0]

    def read_bool(self):
        return self.read_int() != 0

    def read_string(self):
        return self._take(self.read_int()).decode('utf-8', 'replace')

    def read_string16(self):
        return self._take(self.read_int() * 2).decode('utf-16-le', 'replace')

    def read_sub_pickle(self):
        """A length-prefixed nested pickle: its own length header, then payload."""
        length = self.read_int()
        start = self._pos
        self._take(length)
        sub_len = struct.unpack_from('<I', self._data, start)[0]
        return start + 4, min(start + 4 + sub_len, start + length)


def _decode_navigation_entry(data, payload_start, payload_end):
    reader = _PickleReader(data, payload_start, payload_end)
    entry = {
        'index': reader.read_int(),
        'url': reader.read_string(),
        'title': reader.read_string16(),
    }
    reader.read_string()                       # encoded_page_state, not reported
    entry['transition'] = reader.read_int()
    try:                                       # the tail did not always exist
        reader.read_int()                      # type_mask
        entry['referrer'] = reader.read_string()
        reader.read_int()                      # referrer policy, ignored by Chromium
        entry['original_url'] = reader.read_string()
        reader.read_bool()                     # is_overriding_user_agent
        entry['timestamp'] = reader.read_int64()
        reader.read_string16()                 # search terms, removed but still written
        entry['http_status'] = reader.read_int()
    except (ValueError, struct.error, IndexError):
        pass
    return entry


def _parse_tab_file(path):
    """(off_the_record, current_index, [entries]) for a tab file, or None."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
    except OSError:
        return None
    if len(data) < 16:
        return None
    contents_size = struct.unpack_from('>I', data, 8)[0]   # WebContentsState size, big-endian
    pickle_at = 12
    payload_len = struct.unpack_from('<I', data, pickle_at)[0]
    # The outer size and the pickle's own length header must agree, and fit.
    if payload_len + 4 != contents_size or pickle_at + contents_size > len(data):
        return None
    payload_start = pickle_at + 4
    payload_end = payload_start + payload_len
    reader = _PickleReader(data, payload_start, payload_end)
    try:
        off_the_record = reader.read_bool()
        entry_count = reader.read_int()
        current_index = reader.read_int()
        if entry_count < 0 or entry_count > 100000:
            return None
        entries = []
        for _ in range(entry_count):
            start, end = reader.read_sub_pickle()
            entries.append(_decode_navigation_entry(data, start, end))
    except (ValueError, struct.error, IndexError):
        return None
    return off_the_record, current_index, entries


@artifact_processor
def samsung_internet_tab_navigation(context):
    data_list = []
    source_paths = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        normalized = file_found.replace('\\', '/')
        if _PACKAGE not in normalized or not _TAB_FILE_NAME.search(normalized.rsplit('/', 1)[-1]):
            continue
        parsed = _parse_tab_file(file_found)
        if parsed is None:
            logfunc(f'Samsung Internet: tab file not read as WebContentsState: {file_found}')
            continue
        off_the_record, current_index, entries = parsed
        source_paths.append(file_found)
        relative = context.get_relative_path(file_found)
        for entry in entries:
            data_list.append((
                _webkit_to_utc(entry.get('timestamp', 0)),
                entry.get('url', ''),
                entry.get('title', ''),
                'Yes' if entry.get('index') == current_index else 'No',
                entry.get('index', ''),
                _name_transition(entry['transition']) if 'transition' in entry else '',
                entry.get('http_status', ''),
                entry.get('referrer', ''),
                entry.get('original_url', ''),
                'Yes' if off_the_record else 'No',
                relative,
            ))
    data_headers = (
        ('Navigation Timestamp', 'datetime'),
        'URL',
        'Title',
        'Current Entry',
        'Navigation Index',
        'Transition',
        'HTTP Status',
        'Referrer',
        'Original URL',
        'Off The Record',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(source_paths)


_TAB_STATE_NAME = re.compile(r'^(\d+)tab_state$')


class _TabStateReader:
    """Big-endian reader for java.io.DataOutputStream output."""

    def __init__(self, data):
        self.data = data
        self.pos = 0

    def take(self, size):
        if self.pos + size > len(self.data):
            raise ValueError('short tab_state')
        chunk = self.data[self.pos:self.pos + size]
        self.pos += size
        return chunk

    def int(self):
        return struct.unpack('>i', self.take(4))[0]

    def long(self):
        return struct.unpack('>q', self.take(8))[0]

    def double(self):
        return struct.unpack('>d', self.take(8))[0]

    def boolean(self):
        return self.take(1) != b'\x00'

    def utf(self):
        raw = self.take(struct.unpack('>H', self.take(2))[0])
        # Java modified UTF-8: NUL as C0 80 and characters outside the BMP as surrogate pairs.
        text = raw.replace(b'\xc0\x80', b'\x00').decode('utf-8', 'surrogatepass')
        return text.encode('utf-16', 'surrogatepass').decode('utf-16', 'replace')


def _parse_tab_state(data):
    """(version, secret count, tabs) from a <n>tab_state file, or None when it does not parse to its end.

    Field order and version gates follow Samsung Internet's TabStateReader.readMetadata, TabState(...)
    and TabStateVersion (see the artifact notes).
    """
    reader = _TabStateReader(data)
    try:
        version = reader.int()
        if not 3 <= version <= 15:
            return None
        secret = reader.int() if version >= 4 else 0
        total = reader.int()
        secret_active = reader.int()
        normal_active = reader.int() - secret
        if total < 0 or secret < 0 or secret > total:
            return None
        if version >= 8:
            reader.int()  # content page tab index
        tabs = []
        for index in range(total):
            is_secret = index < secret
            tab = {'index': index, 'secret': is_secret, 'tab_id': reader.int()}
            tab['url'] = reader.utf() if version >= 5 else ''
            tab['title'] = reader.utf() if version >= 14 else ''
            tab['locked'] = reader.boolean() if version >= 7 else None
            tab['group_name'] = reader.utf() if version >= 9 else ''
            tab['group_color'] = reader.int() if version >= 11 else ''
            if version >= 6:
                reader.int()  # phone user agent option
                reader.int()  # DeX user agent option
            if version >= 10:
                reader.double()
                reader.boolean()
                reader.double()
                reader.boolean()
            tab['visit_count'] = reader.int() if version >= 12 else ''
            tab['active_seconds'] = reader.long() if version >= 13 else ''
            tab['group_id'] = reader.int() if version >= 15 and not is_secret else ''
            tab['active'] = (index == secret_active) if is_secret else (index - secret == normal_active)
            tabs.append(tab)
    except (ValueError, struct.error, UnicodeDecodeError):
        return None
    if reader.pos != len(data):
        return None
    return version, secret, tabs


@artifact_processor
def samsung_internet_tab_state(context):
    data_list = []
    source_paths = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        normalized = file_found.replace('\\', '/')
        if _PACKAGE not in normalized or not _TAB_STATE_NAME.match(normalized.rsplit('/', 1)[-1]):
            continue
        if not os.path.isfile(file_found):
            continue
        with open(file_found, 'rb') as handle:
            parsed = _parse_tab_state(handle.read())
        if parsed is None:
            logfunc(f'Samsung Internet: tab_state file not read: {file_found}')
            continue
        source_paths.append(file_found)
        key, _rank = canonical_path(context.get_relative_path(file_found))
        parts = key.split('\x00')
        user = parts[1].rsplit(':', 1)[-1] if len(parts) >= 3 else ''
        for tab in parsed[2]:
            data_list.append((
                tab['tab_id'],
                tab['url'],
                tab['title'],
                '' if tab['locked'] is None else ('Yes' if tab['locked'] else 'No'),
                'Yes' if tab['secret'] else 'No',
                'Yes' if tab['active'] else 'No',
                tab['visit_count'],
                tab['active_seconds'],
                user,
            ))
    data_headers = (
        'Tab ID',
        'URL',
        'Title',
        'Locked',
        'Secret Mode Tab',
        'Current Tab',
        'Visit Count',
        'Active Seconds (as stored)',
        'Android User',
    )
    return data_headers, data_list, '\n'.join(source_paths)
