__artifacts_v2__ = {
    "quicksearch_cached_search_requests": {
        "name": "Google Quick Search Box - Cached Search Requests",
        "description": "Rows of the Google app's SearchSuggestDataServiceCache and SearchResultsDataServiceCache "
                       "databases: the request text and the stored write and access times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-02",
        "last_update_date": "2026-10-02",
        "requirements": "none",
        "category": "Google Now & QuickSearch",
        "notes": 'Read from the cache_table table of the SqliteKeyValueCache databases in cache/accounts/<number> of '
                 "the Google app's data folder (com.google.android.googlequicksearchbox). Each of the 297 such "
                 'databases on the tested images has the same table, with the columns request_data, response_data, '
                 'write_ms, access_ms and invalid_flag. Write Time and Access Time are write_ms and access_ms read as '
                 "milliseconds since 1970 and shown in UTC. The names are the app's own column names; what makes the "
                 'app update access_ms was not tested. On the 143 rows read, Access Time was later than Write Time on '
                 '123 and equal to it on 20, and Invalid Flag held 0 on all 143. The app is closed source and no '
                 'published schema for the request and response blobs was found, so the fields named here were read '
                 'off the stored blobs and are taken from the protobuf wire format. The databases are opened read-only '
                 'with their write-ahead logs: 6 of the 297 gave different rows without the log, and 2 of those held '
                 'rows only in the log. The file name is SqliteKeyValueCache:<Name>.db; 62 of the 297 files on the '
                 'tested images carry an underscore in place of the colon, and both are read. Cache is the <Name>. '
                 'This artifact reports the rows of SearchSuggestDataServiceCache and SearchResultsDataServiceCache. '
                 'Request Text is field 1 of the request. A row shows that the app stored a response for that request '
                 'text in the account folder at Write Time; whether the text was typed, pasted or dictated is not '
                 'recorded in the row. Rows were present on 2 tested images, both of one test persona, and each holds '
                 'the same 34 rows: 30 from SearchSuggestDataServiceCache and 4 from SearchResultsDataServiceCache. On '
                 'those images all 8 SearchResultsDataServiceCache responses contain the feed address of a podcast '
                 'that the EpisodeDataCache of the same folder holds, so the requests seen were podcast searches; a '
                 'request of another kind was not seen in these caches. 2 of the 60 SearchSuggestDataServiceCache rows '
                 "have an empty request. Their response lists texts, shown in Listed Text separated by ' | ', and each "
                 'of the 4 texts listed equals, ignoring case, the request text of a SearchResultsDataServiceCache row '
                 'of the same folder. The responses of the other rows are not reported. Response Size is the size of '
                 'response_data in bytes; 22 of the 60 SearchSuggestDataServiceCache rows stored an empty response. '
                 'Account is read from files/AccountData.pb in the same app data folder: the entry whose field 1 '
                 'equals the folder number, and in it the value at fields 2, 2, 3. It was filled on all 143 rows. '
                 'Account Folder is the <number> in the path and Android User is the user in the path (0 for '
                 'data/data, blank when the path names none). An extraction that carries one database under several '
                 'storage paths has it read once. A database that cannot be opened or queried is named in the run log '
                 'and gives no row.',
        "paths": ('*/com.google.android.googlequicksearchbox/cache/accounts/*/SqliteKeyValueCache*.db*',
                  '*/com.google.android.googlequicksearchbox/files/AccountData.pb'),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "galaxys10_a10": "Android 10 | no cache database | 0 rows",
            "samsungs20_a13": "Android 13 | 11 cache databases, no row for this artifact | 0 rows",
            "s20fe_a13": "Android 13 | 6 cache databases, no row for this artifact | 0 rows",
            "pixel7a_a14": "Android 14 | 23 cache databases, no row for this artifact | 0 rows",
            "anne_a15": "Android 15 | 9 cache databases, no row for this artifact | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 8 cache databases, no row for this artifact | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 8 cache databases, no row for this artifact | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "samsunga53_a14": "Android 14 | 8 cache databases, no row for this artifact | 0 rows",
            "sharon_a14": "Android 14 | 18 cache databases, no row for this artifact | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 34 rows",
            "userb2_a13": "Android 13 | 20 cache databases, no row for this artifact | 0 rows",
            "df020_mavic_pro_android": "no cache database | 0 rows",
            "cookbook_a11": "Android 11 | no cache database | 0 rows",
            "sharon_a13": "Android 13 | 13 cache databases, no row for this artifact | 0 rows",
            "russell_a14": "Android 14 | 34 rows",
            "pixel3_a11": "Android 11 | no cache database | 0 rows",
            "pixel3_a12": "Android 12 | 8 cache databases, no row for this artifact | 0 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | no cache database | 0 rows",
            "falken_a326u_a13": "Android 13 | 8 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v1": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v2": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v3": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v4": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v5": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v6": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v7": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v8": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v9": "Android 15 | no cache database | 0 rows",
            "adams_ss135dl_a13": "Android 13 | no cache database | 0 rows",
            "adams_ss134dl_a03s_logical": "no cache database | 0 rows",
            "emu_a15_oss_v10": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v11": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v12": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v13": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v14": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v15": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v16": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v17": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss2_v1": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss2_v2": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "dfrws2011_case1_a855": "no cache database | 0 rows",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | no cache database | 0 rows",
        },
    },
    "quicksearch_cached_episodes": {
        "name": "Google Quick Search Box - Cached Podcast Episodes",
        "description": "Rows of the Google app's EpisodeDataCache database: the podcast episode each row holds and "
                       "the stored write and access times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-02",
        "last_update_date": "2026-10-02",
        "requirements": "none",
        "category": "Google Now & QuickSearch",
        "notes": 'Read from the cache_table table of the SqliteKeyValueCache databases in cache/accounts/<number> of '
                 "the Google app's data folder (com.google.android.googlequicksearchbox). Each of the 297 such "
                 'databases on the tested images has the same table, with the columns request_data, response_data, '
                 'write_ms, access_ms and invalid_flag. Write Time and Access Time are write_ms and access_ms read as '
                 "milliseconds since 1970 and shown in UTC. The names are the app's own column names; what makes the "
                 'app update access_ms was not tested. On the 143 rows read, Access Time was later than Write Time on '
                 '123 and equal to it on 20, and Invalid Flag held 0 on all 143. The app is closed source and no '
                 'published schema for the request and response blobs was found, so the fields named here were read '
                 'off the stored blobs and are taken from the protobuf wire format. The databases are opened read-only '
                 'with their write-ahead logs: 6 of the 297 gave different rows without the log, and 2 of those held '
                 'rows only in the log. The file name is SqliteKeyValueCache:<Name>.db; 62 of the 297 files on the '
                 'tested images carry an underscore in place of the colon, and both are read. Cache is the <Name>. '
                 'This artifact reports the rows of EpisodeDataCache. Feed URL and Episode ID are the values at fields '
                 '2, 1, 1 and 2, 1, 3 of the request. Episode Title, Audio URL, Published and Show are the values at '
                 'fields 1, 3, 7 and 20, 1 of the message at fields 2, 1, 2 of the response. 10 rows were read, on 3 '
                 'tested images. The response also stores the episode ID (field 11) and the feed address (fields 20, '
                 "7), and they equal the request's on all 10 rows. Published is field 7 read as seconds since 1970 and "
                 'shown in UTC. One row was checked against the publisher: the row for the thisweekin4n6.com feed on '
                 'pixel3_a12 stores 2021-11-28 06:47:09, and the page of that post gives the same '
                 'article:published_time (https://thisweekin4n6.com/2021/11/28/week-48-2021/ read on 2026-10-02). '
                 'Write Time was later than Published on all 10 rows. A row shows that the app stored the details of '
                 'this episode in the account folder at Write Time. It does not show that the episode was played: what '
                 'causes the app to store an episode was not tested. Account is read from files/AccountData.pb in the '
                 'same app data folder: the entry whose field 1 equals the folder number, and in it the value at '
                 'fields 2, 2, 3. It was filled on all 143 rows. Account Folder is the <number> in the path and '
                 'Android User is the user in the path (0 for data/data, blank when the path names none). An '
                 'extraction that carries one database under several storage paths has it read once. A database that '
                 'cannot be opened or queried is named in the run log and gives no row.',
        "paths": ('*/com.google.android.googlequicksearchbox/cache/accounts/*/SqliteKeyValueCache*.db*',
                  '*/com.google.android.googlequicksearchbox/files/AccountData.pb'),
        "output_types": "standard",
        "artifact_icon": "headphones",
        "sample_data": {
            "galaxys10_a10": "Android 10 | no cache database | 0 rows",
            "samsungs20_a13": "Android 13 | 11 cache databases, no row for this artifact | 0 rows",
            "s20fe_a13": "Android 13 | 6 cache databases, no row for this artifact | 0 rows",
            "pixel7a_a14": "Android 14 | 23 cache databases, no row for this artifact | 0 rows",
            "anne_a15": "Android 15 | 9 cache databases, no row for this artifact | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 8 cache databases, no row for this artifact | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 8 cache databases, no row for this artifact | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "samsunga53_a14": "Android 14 | 8 cache databases, no row for this artifact | 0 rows",
            "sharon_a14": "Android 14 | 18 cache databases, no row for this artifact | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 2 rows",
            "userb2_a13": "Android 13 | 20 cache databases, no row for this artifact | 0 rows",
            "df020_mavic_pro_android": "no cache database | 0 rows",
            "cookbook_a11": "Android 11 | no cache database | 0 rows",
            "sharon_a13": "Android 13 | 13 cache databases, no row for this artifact | 0 rows",
            "russell_a14": "Android 14 | 2 rows",
            "pixel3_a11": "Android 11 | no cache database | 0 rows",
            "pixel3_a12": "Android 12 | 6 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | no cache database | 0 rows",
            "falken_a326u_a13": "Android 13 | 8 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v1": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v2": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v3": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v4": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v5": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v6": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v7": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v8": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v9": "Android 15 | no cache database | 0 rows",
            "adams_ss135dl_a13": "Android 13 | no cache database | 0 rows",
            "adams_ss134dl_a03s_logical": "no cache database | 0 rows",
            "emu_a15_oss_v10": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v11": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v12": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v13": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v14": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v15": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v16": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v17": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss2_v1": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss2_v2": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "dfrws2011_case1_a855": "no cache database | 0 rows",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | no cache database | 0 rows",
        },
    },
    "quicksearch_cached_requests": {
        "name": "Google Quick Search Box - Other Cached Requests",
        "description": "Rows of the Google app's other SqliteKeyValueCache databases, one row per cached request, "
                       "with the stored write and access times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-02",
        "last_update_date": "2026-10-02",
        "requirements": "none",
        "category": "Google Now & QuickSearch",
        "notes": 'Read from the cache_table table of the SqliteKeyValueCache databases in cache/accounts/<number> of '
                 "the Google app's data folder (com.google.android.googlequicksearchbox). Each of the 297 such "
                 'databases on the tested images has the same table, with the columns request_data, response_data, '
                 'write_ms, access_ms and invalid_flag. Write Time and Access Time are write_ms and access_ms read as '
                 "milliseconds since 1970 and shown in UTC. The names are the app's own column names; what makes the "
                 'app update access_ms was not tested. On the 143 rows read, Access Time was later than Write Time on '
                 '123 and equal to it on 20, and Invalid Flag held 0 on all 143. The app is closed source and no '
                 'published schema for the request and response blobs was found, so the fields named here were read '
                 'off the stored blobs and are taken from the protobuf wire format. The databases are opened read-only '
                 'with their write-ahead logs: 6 of the 297 gave different rows without the log, and 2 of those held '
                 'rows only in the log. The file name is SqliteKeyValueCache:<Name>.db; 62 of the 297 files on the '
                 'tested images carry an underscore in place of the colon, and both are read. Cache is the <Name>. '
                 'This artifact reports the rows of every SqliteKeyValueCache database except '
                 'SearchSuggestDataServiceCache, SearchResultsDataServiceCache and EpisodeDataCache, which have their '
                 'own artifacts. On the tested images 65 rows came from 15 caches on 15 images, and 11 of the 29 cache '
                 'names found held no row on any image. Request Text is filled for four caches, from field paths found '
                 'on the tested rows: BistoDeviceStatusCache and BistoDeviceCustomizeInfoCache (request field 1, '
                 'shaped like a Bluetooth address on all 4 rows), XBlendResponseCache (request field 1, the address of '
                 'a Google weather service on all 4 rows) and GoogleOnContentGwsCache2 (request fields 1, 2, 1, 1, a '
                 'web page address on the 1 row read). Response Text is filled for BistoDeviceCustomizeInfoCache from '
                 "response fields 2, 1, 2; it held a text on both rows read, 'Pixel Buds A-Series' on pixel7a_a14. For "
                 'the other caches both columns are blank and their responses are not reported. Request Size and '
                 'Response Size are the sizes of request_data and response_data in bytes. A row shows that the app '
                 'stored a response for the request in the account folder at Write Time; what caused the request was '
                 'not established. Account is read from files/AccountData.pb in the same app data folder: the entry '
                 'whose field 1 equals the folder number, and in it the value at fields 2, 2, 3. It was filled on all '
                 '143 rows. Account Folder is the <number> in the path and Android User is the user in the path (0 for '
                 'data/data, blank when the path names none). An extraction that carries one database under several '
                 'storage paths has it read once. A database that cannot be opened or queried is named in the run log '
                 'and gives no row.',
        "paths": ('*/com.google.android.googlequicksearchbox/cache/accounts/*/SqliteKeyValueCache*.db*',
                  '*/com.google.android.googlequicksearchbox/files/AccountData.pb'),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "galaxys10_a10": "Android 10 | no cache database | 0 rows",
            "samsungs20_a13": "Android 13 | 5 rows",
            "s20fe_a13": "Android 13 | 3 rows",
            "pixel7a_a14": "Android 14 | 5 rows",
            "anne_a15": "Android 15 | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | 5 rows",
            "hc_pixel8pro_a17": "Android 17 | 5 rows",
            "kevin_pocox7_a15": "Android 15 | 3 rows",
            "samsunga53_a14": "Android 14 | 5 rows",
            "sharon_a14": "Android 14 | 1 rows",
            "russell_pixel6a_a13": "Android 13 | 7 rows",
            "userb2_a13": "Android 13 | 5 rows",
            "df020_mavic_pro_android": "no cache database | 0 rows",
            "cookbook_a11": "Android 11 | no cache database | 0 rows",
            "sharon_a13": "Android 13 | 1 rows",
            "russell_a14": "Android 14 | 9 rows",
            "pixel3_a11": "Android 11 | no cache database | 0 rows",
            "pixel3_a12": "Android 12 | 1 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | no cache database | 0 rows",
            "falken_a326u_a13": "Android 13 | 7 rows",
            "emu_a15_oss_v1": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v2": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v3": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v4": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v5": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v6": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v7": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v8": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss_v9": "Android 15 | no cache database | 0 rows",
            "adams_ss135dl_a13": "Android 13 | no cache database | 0 rows",
            "adams_ss134dl_a03s_logical": "no cache database | 0 rows",
            "emu_a15_oss_v10": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v11": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v12": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v13": "Android 15 | 5 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v14": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v15": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v16": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss_v17": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss2_v1": "Android 15 | no cache database | 0 rows",
            "emu_a15_oss2_v2": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 10 cache databases, no row for this artifact | 0 rows",
            "dfrws2011_case1_a855": "no cache database | 0 rows",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | no cache database | 0 rows",
        },
    },
}

import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.artifacts.googleQuickSearchboxZeroPrefix import (
    _accounts, _by_time, _first, _locate, _ms, _read, _text, _wire_fields)
from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_ACCOUNT_TAIL = 'files/AccountData.pb'
# cache/accounts/<number>/SqliteKeyValueCache:<Name>.db. The character between the prefix
# and the name is a colon on the device and an underscore in some extractions.
_CACHE_TAIL = re.compile(r'^cache/accounts/([^/]+)/SqliteKeyValueCache[^A-Za-z0-9/]([A-Za-z0-9]+)\.db$')
_QUERY = ('SELECT request_data, response_data, write_ms, access_ms, invalid_flag '
          'FROM cache_table ORDER BY write_ms, rowid')

_SUGGEST = 'SearchSuggestDataServiceCache'
_RESULTS = 'SearchResultsDataServiceCache'
_EPISODES = 'EpisodeDataCache'
_SEARCH_CACHES = (_SUGGEST, _RESULTS)

# The Google app is closed source. The field paths below were read off the stored requests
# and responses on the tested images; a cache that is not listed has its text left blank.
_REQUEST_TEXT = {
    'BistoDeviceCustomizeInfoCache': (1,),
    'BistoDeviceStatusCache': (1,),
    'GoogleOnContentGwsCache2': (1, 2, 1, 1),
    'XBlendResponseCache': (1,),
}
_RESPONSE_TEXT = {
    'BistoDeviceCustomizeInfoCache': (2, 1, 2),
}


def _at(data, path):
    """The first value found by following field numbers into nested messages, or None."""
    value = data
    for number in path:
        if not isinstance(value, (bytes, bytearray)):
            return None
        try:
            value = _first(_wire_fields(value, {number}), number)
        except (IndexError, ValueError):
            return None
    return value


def _text_at(data, path):
    value = _at(data, path)
    return _text(value) if isinstance(value, (bytes, bytearray)) else ''


def _seconds(value):
    if not isinstance(value, int) or not value:
        return ''
    try:
        return _EPOCH + timedelta(seconds=value)
    except (ValueError, OverflowError):
        return ''


def _listed_text(response):
    """Field 1 of each repeated field 1 message of a suggest response, in stored order."""
    try:
        entries = _wire_fields(response, {1}).get(1, [])
    except (IndexError, ValueError):
        return []
    return [_text_at(entry, (1,)) for entry in entries if isinstance(entry, (bytes, bytearray))]


def _cache_rows(file_found):
    """Rows of cache_table, or None when the database could not be read (logged)."""
    db = open_sqlite_db_readonly(file_found)
    if db is None:
        return None
    try:
        return [(bytes(request or b''), bytes(response or b''), write_ms, access_ms, invalid)
                for request, response, write_ms, access_ms, invalid in db.execute(_QUERY)]
    except (sqlite3.Error, TypeError) as error:
        logfunc(f'Could not read cache_table in {file_found}: {error}')
        return None
    finally:
        db.close()


def _rows(context, wanted):
    """(rows, source paths) for the caches `wanted(cache name)` accepts.

    One dict per cache_table row, each carrying the account that files/AccountData.pb of the
    same app data folder records for the row's account folder."""
    rows, account_maps, sources = [], {}, []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        located = _locate(context, file_found)
        if located is None:
            continue
        container, user, tail = located
        if tail == _ACCOUNT_TAIL:
            data = _read(file_found)
            if data is None:
                continue
            try:
                account_maps[container] = _accounts(data)
                sources.append(file_found)
            except (IndexError, ValueError) as error:
                logfunc(f'Could not read the account list {file_found}: {error}')
            continue
        cache = _CACHE_TAIL.match(tail)
        if not cache or not wanted(cache.group(2)):
            continue
        found = _cache_rows(file_found)
        if found is None:
            continue
        if found:
            sources.append(file_found)
        for request, response, write_ms, access_ms, invalid in found:
            rows.append({
                'container': container,
                'user': user,
                'folder': cache.group(1),
                'cache': cache.group(2),
                'request': request,
                'response': response,
                'write': _ms(write_ms),
                'access': _ms(access_ms),
                'invalid': invalid,
            })
    for row in rows:
        accounts = account_maps.get(row['container'], {})
        number = int(row['folder']) if row['folder'].isdigit() else None
        row['account'] = accounts.get(number, ('', ''))[1]
    if not rows:
        sources = []
    return rows, sources


@artifact_processor
def quicksearch_cached_search_requests(context):
    data_headers = (
        ('Write Time', 'datetime'),
        ('Access Time', 'datetime'),
        'Request Text',
        'Cache',
        'Listed Text',
        'Response Size',
        'Invalid Flag',
        'Account',
        'Account Folder',
        'Android User',
    )
    data_list = []
    rows, sources = _rows(context, lambda name: name in _SEARCH_CACHES)
    for row in rows:
        request_text = _text_at(row['request'], (1,))
        listed = ''
        if row['cache'] == _SUGGEST and not row['request']:
            listed = ' | '.join(_listed_text(row['response']))
        data_list.append((
            row['write'], row['access'], request_text, row['cache'], listed, len(row['response']),
            row['invalid'], row['account'], row['folder'], row['user'],
        ))
    data_list.sort(key=_by_time)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def quicksearch_cached_episodes(context):
    data_headers = (
        ('Write Time', 'datetime'),
        ('Access Time', 'datetime'),
        ('Published', 'datetime'),
        'Episode Title',
        'Show',
        'Episode ID',
        'Feed URL',
        'Audio URL',
        'Invalid Flag',
        'Account',
        'Account Folder',
        'Android User',
    )
    data_list = []
    rows, sources = _rows(context, lambda name: name == _EPISODES)
    for row in rows:
        episode = _at(row['response'], (2, 1, 2))
        if not isinstance(episode, (bytes, bytearray)):
            episode = b''
        data_list.append((
            row['write'], row['access'], _seconds(_at(episode, (7,))), _text_at(episode, (1,)),
            _text_at(episode, (20, 1)), _text_at(row['request'], (2, 1, 3)),
            _text_at(row['request'], (2, 1, 1)), _text_at(episode, (3,)), row['invalid'],
            row['account'], row['folder'], row['user'],
        ))
    data_list.sort(key=_by_time)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def quicksearch_cached_requests(context):
    data_headers = (
        ('Write Time', 'datetime'),
        ('Access Time', 'datetime'),
        'Cache',
        'Request Text',
        'Response Text',
        'Request Size',
        'Response Size',
        'Invalid Flag',
        'Account',
        'Account Folder',
        'Android User',
    )
    data_list = []
    rows, sources = _rows(context, lambda name: name not in _SEARCH_CACHES and name != _EPISODES)
    for row in rows:
        request_path = _REQUEST_TEXT.get(row['cache'])
        response_path = _RESPONSE_TEXT.get(row['cache'])
        data_list.append((
            row['write'], row['access'], row['cache'],
            _text_at(row['request'], request_path) if request_path else '',
            _text_at(row['response'], response_path) if response_path else '',
            len(row['request']), len(row['response']), row['invalid'],
            row['account'], row['folder'], row['user'],
        ))
    data_list.sort(key=_by_time)
    return data_headers, data_list, '\n'.join(sources)
