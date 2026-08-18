__artifacts_v2__ = {
    "prime_video_playback_history": {
        "name": "Prime Video - Playback History",
        "description": "Parses the playback history stored by the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "Read from the playbackHistory table of the app's dbplaybackhistory "
                 "database. lastAccessed is Unix milliseconds; watched_position, runtime "
                 "and credits_start_time_millis are milliseconds of media time, not "
                 "timestamps, and are reported as stored. On one tested sample a row's "
                 "watched_position matched the timecode the bookmark database held for the "
                 "same title exactly, which is what establishes that column as a media "
                 "offset. contenttype and video_material_type are reported as stored. "
                 "Field mapping was done against private samples provided by Mattia; no "
                 "sample data is recorded for them.",
        "paths": ('*/com.amazon.avod.thirdpartyclient/files/databases/dbplaybackhistory*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "player-play"
    },
    "prime_video_resume_points": {
        "name": "Prime Video - Playback Resume Points",
        "description": "Parses the playback resume points stored by the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "Read from the bookmark_cache table of the app's bookmark database. "
                 "last_update is Unix milliseconds and timecode is milliseconds of media "
                 "time. The table declares UNIQUE (user_id, asin, timecode_type, "
                 "profile_id) ON CONFLICT REPLACE, so each new position for a title "
                 "replaces the previous row under a new row id. The database is read twice, "
                 "immutable=1 to ignore the write-ahead log and mode=ro to apply it, and the "
                 "two reads are compared on row id rather than on row count. On one tested "
                 "sample both reads returned four rows while the row ids differed, and the "
                 "row present only in the first read held an earlier position for a title "
                 "the committed state also carries; those rows are reported with a Source "
                 "View of Pre-checkpoint. timecode_type is undocumented and is reported as "
                 "stored. Field mapping was done against private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": ('*/com.amazon.avod.thirdpartyclient/files/databases/bookmark*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "clock"
    },
    "prime_video_continue_watching": {
        "name": "Prime Video - Continue Watching",
        "description": "Parses the saved Continue Watching collection of the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "continueWatchingSaveFile holds a Java serialised "
                 "com.amazon.avod.discovery.collections.CollectionModelV3. The stream "
                 "carries its own class and field names, so the members read here are "
                 "named by the file itself rather than inferred. Each tile is a "
                 "TitleCardModel giving the title id, title, content type, season and "
                 "episode numbers and mRemainingTimeInSeconds. The collection's own "
                 "mIsWatchList flag is reported as stored, so a saved watchlist collection "
                 "in the same format is reported alongside a Continue Watching one. On the "
                 "one tested sample that carried this file the flag was false and the "
                 "single tile named a title the playback history table did not hold. Field "
                 "mapping was done against private samples provided by Mattia; no sample "
                 "data is recorded for them.",
        "paths": ('*/com.amazon.avod.thirdpartyclient/files/continueWatchingSaveFile',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-tv"
    },
    "prime_video_search_history": {
        "name": "Prime Video - Search History",
        "description": "Parses the search queries stored by the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "Read from the LocalSearchQuery table of search_query.db. queryTimeMillis "
                 "is Unix milliseconds. The table's primary key is the query text together "
                 "with the account and profile, so a repeated query carries only its most "
                 "recent time. On the one tested sample holding this database the table "
                 "existed only in the write-ahead log and the main file carried no schema "
                 "at all, so the log has to travel with the database. Field mapping was "
                 "done against private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": ('*/com.amazon.avod.thirdpartyclient/databases/search_query.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search"
    },
    "prime_video_profiles": {
        "name": "Prime Video - Profiles and Household",
        "description": "Parses the household profiles stored by the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "The aiv.UserManagerConfig:householdInfo key of InternalPreferences.xml "
                 "holds a base64 Java serialised com.amazon.avod.identity.HouseholdInfo. "
                 "The stream carries its own class descriptors, field names and enum "
                 "constant names, so the profile age group, the account role and the "
                 "profiles status are read as the literal names the file stores rather "
                 "than mapped from an integer. Two tested samples serialised different "
                 "class shapes and both are read from their own descriptors. The parsed "
                 "profile ids were confirmed against two independent stores in the same "
                 "extraction: every one also appeared in the map_data_storage token and "
                 "userdata keys, and the current profile matched current_profile_id in "
                 "IdentityPreferences.xml. Field mapping was done against private samples "
                 "provided by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.amazon.avod.thirdpartyclient/shared_prefs/InternalPreferences.xml',
            '*/com.amazon.avod.thirdpartyclient/shared_prefs/IdentityPreferences.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users"
    },
    "prime_video_account_store": {
        "name": "Prime Video - Account Store",
        "description": "Parses the Amazon account store of the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "map_data_storage.db is the Amazon account store, holding the accounts, "
                 "userdata, tokens and device_data tables. Every row is reported with its "
                 "own timestamp in Unix milliseconds. On the tested sample that held a "
                 "registered account, every value across those four tables began with the "
                 "literal characters AES-GCM followed by base64, the display name "
                 "included, so values are reported as stored and no decryption is "
                 "attempted here. On the tested sample with no registered account the only "
                 "values present were three device_data entries and none of them carried "
                 "that prefix, so the wrapping should not be assumed. The key names are "
                 "plaintext either way and name what each value holds. Field mapping was "
                 "done against private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": ('*/com.amazon.avod.thirdpartyclient/databases/map_data_storage.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "key"
    },
    "prime_video_downloads": {
        "name": "Prime Video - Downloads",
        "description": "Parses downloaded titles recorded by the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "Read from the download table of the app's downloads database, joined to "
                 "title, season, series and drm through the foreign keys those tables "
                 "declare. No tested sample held a download row, so the epoch and unit of "
                 "the time columns could not be established from data and every one of "
                 "them, including expiry_ms and the drm expiry, is reported as stored "
                 "rather than converted. Download state, download type, error code and "
                 "media quality are reported as stored. Because no sample exercised it, "
                 "the query was run against two databases built to the two download "
                 "schemas the samples themselves carry, which differ by three columns, "
                 "with rows authored for the purpose; both returned every value under its "
                 "own column and the older schema's three absent columns came back empty "
                 "rather than failing. That is a constructed check, not corpus "
                 "validation, so treat the column mapping as unconfirmed against real "
                 "download data. Field mapping was done against private samples provided "
                 "by Mattia; no sample data is recorded for them.",
        "paths": ('*/com.amazon.avod.thirdpartyclient/files/global/databases/downloads*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "download"
    },
    "prime_video_streaming_cache": {
        "name": "Prime Video - Streaming Cache",
        "description": "Parses the cached playback content records of the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "Read from the cached_content_table of the dbcachedcontent database, which "
                 "records a playback request per title. accessed_time_seconds is Unix "
                 "seconds. request_submission_time_ms is not: on the tested sample it held "
                 "a value that decodes to 1970 as a millisecond epoch while the row's own "
                 "accessed time was current, so it is reported as stored. Status, source, "
                 "media quality, audio format, cache level, content type and entitlement "
                 "type are reported as stored. The database is read twice, immutable=1 and "
                 "mode=ro, and compared on row id; on one tested sample the file alone "
                 "carried two rows the committed state no longer held, and those are "
                 "reported with a Source View of Pre-checkpoint. Field mapping was done "
                 "against private samples provided by Mattia; no sample data is recorded "
                 "for them.",
        "paths": ('*/com.amazon.avod.thirdpartyclient/files/global/databases/dbcachedcontent*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "database"
    },
    "prime_video_cached_titles": {
        "name": "Prime Video - Cached Title Data",
        "description": "Inventories the per title streaming caches of the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "The app keeps two caches whose directory names are title ids: "
                 "files/streaming-plugins holds trickplay images, subtitles and X-Ray data, "
                 "and files/global/global_video_cache holds streaming manifests and media "
                 "fragments. One row is reported per title id with what each cache holds. "
                 "On the tested samples these directories named far more titles than the "
                 "playback history table did, and most of them held no files, so a row with "
                 "no counted files means the directory carried the title id and nothing "
                 "else. The media fragments are reported as an inventory and not checked in "
                 "as media: on the tested sample none of them carried an initialisation "
                 "segment and most carried a senc sample encryption box, so they are "
                 "neither standalone nor playable as extracted. "
                 "Directory entries are only reported for extraction types whose seeker "
                 "returns them. Field mapping was done against private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.amazon.avod.thirdpartyclient/files/streaming-plugins/*',
            '*/com.amazon.avod.thirdpartyclient/files/global/global_video_cache/*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list"
    },
    "prime_video_cached_images": {
        "name": "Prime Video - Cached Title Images",
        "description": "Checks in the cached title images of the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "Images cached under files/streaming-plugins are checked in and rendered. "
                 "The title id is the directory the app named after it, which is the "
                 "recorded link between an image and a title; no correlation is used. For a "
                 "trickplay frame the file name is the media offset in milliseconds. The "
                 "trickplay index file that sits beside the frames is a BIF, and its header "
                 "declares an image count and a frame separation; on all four tested titles "
                 "the declared count equalled the number of frames on disk and the declared "
                 "separation equalled the spacing of the file names, which is what "
                 "establishes the offset unit. The app fetches the whole trickplay index "
                 "for a title, so a frame at a given offset does not establish that the "
                 "offset was played. X-Ray images carry no offset and their file names were "
                 "not resolved to anything recorded elsewhere, so only the title id is "
                 "reported for them. File type comes from the leading bytes rather than the "
                 "extension. Field mapping was done against private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": ('*/com.amazon.avod.thirdpartyclient/files/streaming-plugins/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "photo"
    },
    "prime_video_app_events": {
        "name": "Prime Video - App Events",
        "description": "Parses the client event log of the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "Read from the events table of the app's event database. Timestamp is Unix "
                 "milliseconds. Type, Name, Priority and Processed are reported as stored. "
                 "Event Type and Event Subtype are read from the row's own JSON body where "
                 "it holds them. The body itself is not reported: it is large and holds "
                 "device and session detail rather than a further activity record. On the "
                 "tested samples the ASIN column named more titles than the playback "
                 "history table did. The database is read twice, immutable=1 and mode=ro, "
                 "and compared on row id, and rows present only in the first read are "
                 "reported with a Source View of Pre-checkpoint. Field mapping was done "
                 "against private samples provided by Mattia; no sample data is recorded "
                 "for them.",
        "paths": ('*/com.amazon.avod.thirdpartyclient/files/databases/event*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list"
    },
    "prime_video_app_settings": {
        "name": "Prime Video - App Settings",
        "description": "Parses the preference files of the Amazon Prime Video Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Prime Video",
        "notes": "Reports the app's own preference files together with the install referrer "
                 "records in AppEventsJsonFile. Keys whose name ends in Millis, Time, "
                 "TimeMs or Timestamp and whose value is a 13 digit number are rendered as "
                 "Unix milliseconds in a separate column beside the stored value; keys "
                 "ending in Epoch held a 10 digit value on the tested samples and are "
                 "rendered as Unix seconds. Every other value is reported as stored. "
                 "Rendering is decided per key rather than per file because the same file "
                 "carried both units. The base64 serialised household blob is not repeated "
                 "here; it is parsed by the Profiles and Household artifact. Field mapping "
                 "was done against private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": (
            '*/com.amazon.avod.thirdpartyclient/shared_prefs/InternalPreferences.xml',
            '*/com.amazon.avod.thirdpartyclient/shared_prefs/PersistentPreferences.xml',
            '*/com.amazon.avod.thirdpartyclient/shared_prefs/IdentityPreferences.xml',
            '*/com.amazon.avod.thirdpartyclient/shared_prefs/LocalizationPreferences.xml',
            '*/com.amazon.avod.thirdpartyclient/shared_prefs/com.amazon.avod.thirdpartyclient_preferences.xml',
            '*/com.amazon.avod.thirdpartyclient/files/AppEventsJsonFile',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
}

import json
import os
import re
import sqlite3
import struct
import xml.etree.ElementTree as ET
from base64 import b64decode
from binascii import Error as BinasciiError
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    get_sqlite_db_path,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_PACKAGE = 'com.amazon.avod.thirdpartyclient'
_HOUSEHOLD_KEY = 'aiv.UserManagerConfig:householdInfo'

# Rendered as a timestamp only where the key names its own unit. Both appear in one file.
_MS_KEY_RE = re.compile(r'(Millis|Time|TimeMs|Timestamp)$')
_SECONDS_KEY_RE = re.compile(r'Epoch$')

_IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'JPEG', 'jpg', 'image/jpeg'),
    (b'\x89PNG\r\n\x1a\n', 'PNG', 'png', 'image/png'),
    (b'GIF8', 'GIF', 'gif', 'image/gif'),
)


def _rows(source_path, sql):
    '''Rows for sql, with the write-ahead log applied. Empty on any SQLite error.'''
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if not db:
        return []
    cursor = db.cursor()
    try:
        rows = cursor.execute(sql).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Could not query {os.path.basename(source_path)}: {ex}')
        rows = []
    db.close()
    return rows


def _rows_pre_wal(source_path, sql):
    '''Rows for sql as of the file's last checkpoint, ignoring the write-ahead log.

    immutable=1 is strictly read-only. Unlike mode=ro it does not even create a -shm
    sidecar, so no evidence file is altered. Path handling goes through the same
    get_sqlite_db_path() that open_sqlite_db_readonly() uses, so Windows long paths and
    URI-special characters behave identically.
    '''
    if not source_path:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?immutable=1', uri=True)
    except sqlite3.Error:
        return []
    cursor = db.cursor()
    try:
        rows = cursor.execute(sql).fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _superseded(source_path, sql, key_index):
    '''Pre-checkpoint rows whose key the committed read no longer holds.

    Keyed on the row's own primary key rather than on a row count. A table that replaces
    a row keeps the same count while holding different rows, which a count comparison
    cannot see.
    '''
    committed = {row[key_index] for row in _rows(source_path, sql)}
    return [row for row in _rows_pre_wal(source_path, sql) if row[key_index] not in committed]


def _table_columns(source_path, table):
    '''The column names the file's own schema declares for table.'''
    return {row[1] for row in _rows(source_path, f'PRAGMA table_info(`{table}`)')}


def _select(source_path, table, columns, tail=''):
    '''A SELECT naming every column, substituting NULL for the ones this schema lacks.

    Keeps the result shape and the column names identical across app versions that do not
    declare the same columns, so callers can index by position.
    '''
    present = _table_columns(source_path, table)
    if not present:
        return ''
    select_list = ', '.join(
        f'`{column}`' if column in present else f'NULL AS `{column}`' for column in columns)
    return f'SELECT {select_list} FROM `{table}` {tail}'


def _named(context, *basenames):
    '''The matched files with these basenames, one per storage view.'''
    wanted = set(basenames)
    return [path for path in unique_files(context)
            if os.path.basename(str(path).replace('\\', '/')) in wanted]


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.

    Converted here rather than through convert_unix_ts_to_utc because every column routed
    through this is known to be milliseconds. The shared helper infers the unit from the
    value's magnitude, which cannot separate milliseconds from seconds near the epoch, and
    it says so itself: a caller that knows the unit should convert it rather than rely on
    the inference.
    '''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _seconds(value):
    '''A Unix second value as a UTC datetime, or '' when absent or zero.

    Kept separate from _ms() for the same reason: the unit comes from the column, which is
    known, rather than from the value's magnitude, which cannot decide it.
    '''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(seconds=value)


def _yes_no(value):
    return 'YES' if value else 'NO'


def _relative(context, path):
    return context.get_relative_path(path)


# ---------------------------------------------------------------------------
# Java Object Serialization Stream Protocol
#
# Two of the app's stores are Java serialised objects rather than a database or XML. The
# stream declares its own class names, field names and enum constant names ahead of the
# values, so reading it needs no mapping supplied from outside the evidence.
# ---------------------------------------------------------------------------

_TC_NULL = 0x70
_TC_REFERENCE = 0x71
_TC_CLASSDESC = 0x72
_TC_OBJECT = 0x73
_TC_STRING = 0x74
_TC_ARRAY = 0x75
_TC_CLASS = 0x76
_TC_BLOCKDATA = 0x77
_TC_ENDBLOCKDATA = 0x78
_TC_RESET = 0x79
_TC_BLOCKDATALONG = 0x7A
_TC_LONGSTRING = 0x7C
_TC_PROXYCLASSDESC = 0x7D
_TC_ENUM = 0x7E
_BASE_HANDLE = 0x7E0000
_SC_WRITE_METHOD = 0x01
_SC_EXTERNALIZABLE = 0x04
_SC_BLOCK_DATA = 0x08


class _JavaObject:
    def __init__(self, classname):
        self.classname = classname
        self.fields = {}


class _JavaEnum:
    def __init__(self, classname):
        self.classname = classname
        self.name = ''


class _JavaClassDesc:
    def __init__(self):
        self.name = ''
        self.flags = 0
        self.fields = []
        self.superclass = None


class _JavaReader:
    '''Reads the subset of the serialization protocol these two files use.'''

    def __init__(self, data):
        self.data = data
        self.offset = 0
        self.handles = []

    def _u1(self):
        value = self.data[self.offset]
        self.offset += 1
        return value

    def _u2(self):
        value = struct.unpack_from('>H', self.data, self.offset)[0]
        self.offset += 2
        return value

    def _utf(self, long_form=False):
        if long_form:
            length = struct.unpack_from('>Q', self.data, self.offset)[0]
            self.offset += 8
        else:
            length = self._u2()
        value = self.data[self.offset:self.offset + length].decode('utf-8', 'replace')
        self.offset += length
        return value

    def _handle(self, obj):
        self.handles.append(obj)
        return obj

    def _primitive(self, code):
        formats = {'B': ('>b', 1), 'C': ('>H', 2), 'D': ('>d', 8), 'F': ('>f', 4),
                   'I': ('>i', 4), 'J': ('>q', 8), 'S': ('>h', 2), 'Z': ('>?', 1)}
        if code not in formats:
            raise ValueError(f'unsupported field type {code}')
        fmt, size = formats[code]
        value = struct.unpack_from(fmt, self.data, self.offset)[0]
        self.offset += size
        return chr(value) if code == 'C' else value

    def parse(self):
        if self._u2() != 0xACED:
            raise ValueError('not a Java serialization stream')
        self._u2()
        return self._content()

    def _content(self):
        marker = self._u1()
        if marker == _TC_NULL:
            return None
        if marker == _TC_REFERENCE:
            return self._reference()
        if marker == _TC_STRING:
            return self._handle(self._utf())
        if marker == _TC_LONGSTRING:
            return self._handle(self._utf(long_form=True))
        if marker in (_TC_CLASSDESC, _TC_PROXYCLASSDESC):
            self.offset -= 1  # _classdesc() reads the marker itself
            return self._classdesc()
        if marker == _TC_CLASS:
            return self._handle(self._classdesc())
        if marker == _TC_OBJECT:
            return self._object()
        if marker == _TC_ARRAY:
            return self._array()
        if marker == _TC_ENUM:
            return self._enum()
        if marker == _TC_BLOCKDATA:
            length = self._u1()
            value = self.data[self.offset:self.offset + length]
            self.offset += length
            return value
        if marker == _TC_BLOCKDATALONG:
            length = struct.unpack_from('>I', self.data, self.offset)[0]
            self.offset += 4
            value = self.data[self.offset:self.offset + length]
            self.offset += length
            return value
        if marker == _TC_ENDBLOCKDATA:
            return _TC_ENDBLOCKDATA
        if marker == _TC_RESET:
            self.handles = []
            return self._content()
        raise ValueError(f'unsupported stream marker {marker:#x}')

    def _reference(self):
        handle = struct.unpack_from('>i', self.data, self.offset)[0]
        self.offset += 4
        return self.handles[handle - _BASE_HANDLE]

    def _classdesc(self):
        marker = self._u1()
        if marker == _TC_NULL:
            return None
        if marker == _TC_REFERENCE:
            return self._reference()
        descriptor = _JavaClassDesc()
        if marker == _TC_PROXYCLASSDESC:
            self._handle(descriptor)
            count = struct.unpack_from('>i', self.data, self.offset)[0]
            self.offset += 4
            for _ in range(count):
                self._utf()
            self._annotation()
            descriptor.superclass = self._classdesc()
            return descriptor
        if marker != _TC_CLASSDESC:
            raise ValueError(f'expected a class descriptor, got {marker:#x}')
        descriptor.name = self._utf()
        self.offset += 8
        descriptor.flags = self._u1()
        self._handle(descriptor)
        for _ in range(self._u2()):
            code = chr(self._u1())
            name = self._utf()
            if code in 'L[':
                self._content()
            descriptor.fields.append((code, name))
        self._annotation()
        descriptor.superclass = self._classdesc()
        return descriptor

    def _annotation(self):
        while self.data[self.offset] != _TC_ENDBLOCKDATA:
            self._content()
        self.offset += 1

    def _object(self):
        descriptor = self._classdesc()
        obj = _JavaObject(descriptor.name if descriptor else '')
        self._handle(obj)
        chain = []
        current = descriptor
        while current:
            chain.append(current)
            current = current.superclass
        for level in reversed(chain):
            if level.flags & _SC_EXTERNALIZABLE:
                if level.flags & _SC_BLOCK_DATA:
                    self._annotation()
                continue
            for code, name in level.fields:
                obj.fields[name] = (self._content() if code in 'L['
                                    else self._primitive(code))
            if level.flags & _SC_WRITE_METHOD:
                self._annotation()
        return obj

    def _array(self):
        descriptor = self._classdesc()
        values = []
        self._handle(values)
        count = struct.unpack_from('>i', self.data, self.offset)[0]
        self.offset += 4
        code = descriptor.name[1] if descriptor and len(descriptor.name) > 1 else 'L'
        for _ in range(count):
            values.append(self._content() if code in 'L[' else self._primitive(code))
        return values

    def _enum(self):
        descriptor = self._classdesc()
        constant = _JavaEnum(descriptor.name if descriptor else '')
        self._handle(constant)
        constant.name = self._content()
        return constant


def _java_loads(data):
    return _JavaReader(data).parse()


def _unwrap(value):
    '''The value inside a Guava Optional, or the value itself.'''
    while isinstance(value, _JavaObject) and value.classname.startswith('com.google.common.base.'):
        value = value.fields.get('reference')
    return value


def _elements(value):
    '''The members of a Guava immutable collection's serialized form, or [].'''
    value = _unwrap(value)
    if isinstance(value, _JavaObject) and 'SerializedForm' in value.classname:
        for name in ('elements', 'values'):
            if isinstance(value.fields.get(name), list):
                return value.fields[name]
        return []
    return value if isinstance(value, list) else []


def _enum_name(value):
    value = _unwrap(value)
    if isinstance(value, _JavaEnum):
        return value.name or ''
    return value if isinstance(value, str) else ''


def _value(obj, name, default=None):
    '''The field's value with any Optional unwrapped, objects and lists included.'''
    if not isinstance(obj, _JavaObject):
        return default
    value = _unwrap(obj.fields.get(name))
    return default if value is None else value


def _field(obj, name, default=''):
    '''A field flattened to something printable: text, a number or an enum name.

    An object-valued field that is not a boxed primitive has no scalar form, so it
    yields the default. Use _value() to reach the object itself.
    '''
    value = _value(obj, name)
    if value is None:
        return default
    if isinstance(value, _JavaEnum):
        return value.name or default
    if isinstance(value, _JavaObject):
        # java.lang.Integer and its siblings keep their payload under 'value'.
        if 'value' in value.fields:
            return value.fields['value']
        return default
    if isinstance(value, (list, bytes)):
        return default
    return value


def _prefs(source_path):
    '''The name to value mapping of an Android shared preferences file.'''
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError, ValueError) as ex:
        logfunc(f'Could not parse {os.path.basename(source_path)}: {ex}')
        return {}
    values = {}
    for node in root:
        name = node.attrib.get('name')
        if name is None:
            continue
        values[name] = node.attrib.get('value', node.text)
    return values


# ---------------------------------------------------------------------------
# Artifacts
# ---------------------------------------------------------------------------

_HISTORY_COLUMNS = (
    'lastAccessed', 'asin', 'contenttype', 'title', 'seriestitle', 'seasontitle',
    'seasonNumber', 'episodeNumber', 'watched_position', 'runtime',
    'credits_start_time_millis', 'regulatoryrating', 'is_adult_content',
    'has_closed_captions', 'content_playable', 'show_in_launcher', 'supports_explore',
    'video_material_type', 'season_asin', 'next_up_title_id', 'related_asins',
    'profile_id', 'user_id', 'image_url', 'hero_image_url', 'last_played_frame_image_url',
)


@artifact_processor
def prime_video_playback_history(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'dbplaybackhistory'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        sql = _select(file_found, 'playbackHistory', _HISTORY_COLUMNS,
                      'ORDER BY lastAccessed DESC')
        for row in _rows(file_found, sql):
            data_list.append((
                _ms(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                row[8], row[9], row[10], row[11], _yes_no(row[12]), _yes_no(row[13]),
                _yes_no(row[14]), _yes_no(row[15]), _yes_no(row[16]), row[17], row[18],
                row[19], row[20], row[21], row[22], row[23], row[24], row[25],
                source_file))

    data_headers = (
        ('Last Accessed', 'datetime'), 'Title ID', 'Content Type (as stored)', 'Title',
        'Series Title', 'Season Title', 'Season Number', 'Episode Number',
        'Watched Position (ms)', 'Runtime (ms)', 'Credits Start (ms)',
        'Regulatory Rating', 'Adult Content', 'Has Closed Captions', 'Content Playable',
        'Show In Launcher', 'Supports Explore', 'Video Material Type (as stored)',
        'Season Title ID', 'Next Up Title ID', 'Related Title IDs', 'Profile ID',
        'User ID', 'Image URL', 'Hero Image URL', 'Last Played Frame Image URL',
        'Source File')
    return data_headers, data_list, source_path


_BOOKMARK_SQL = ('SELECT `_id`, `last_update`, `asin`, `timecode`, `timecode_type`, '
                 '`profile_id`, `user_id` FROM `bookmark_cache`')


@artifact_processor
def prime_video_resume_points(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'bookmark'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        for view, rows in (('Committed', _rows(file_found, _BOOKMARK_SQL)),
                           ('Pre-checkpoint', _superseded(file_found, _BOOKMARK_SQL, 0))):
            for row in rows:
                data_list.append((
                    _ms(row[1]), row[2], row[3], row[4], row[5], row[6], row[0], view,
                    source_file))

    data_headers = (
        ('Last Update', 'datetime'), 'Title ID', 'Timecode (ms)',
        'Timecode Type (as stored)', 'Profile ID', 'User ID', 'Row ID', 'Source View',
        'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def prime_video_continue_watching(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'continueWatchingSaveFile'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        try:
            with open(file_found, 'rb') as handle:
                collection = _java_loads(handle.read())
        except (OSError, ValueError, IndexError, struct.error) as ex:
            logfunc(f'Could not read {os.path.basename(file_found)}: {ex}')
            continue
        is_watchlist = _yes_no(_field(collection, 'mIsWatchList', False))
        header = _field(collection, 'mHeaderText')
        for entry in _elements(collection.fields.get('mTileData')
                               if isinstance(collection, _JavaObject) else None):
            entry = _unwrap(entry)
            model = _value(entry, 'mModel')
            if not isinstance(model, _JavaObject):
                continue
            data_list.append((
                _field(model, 'mAsin'), _enum_name(model.fields.get('mContentType')),
                _field(model, 'mTitle'), _field(model, 'mSeriesTitle'),
                _field(model, 'mSeasonTitle'), _field(model, 'mSeasonNumber'),
                _field(model, 'mEpisodeNumber'), _field(model, 'mTotalSeasons'),
                _field(model, 'mTotalEpisodes'), _field(model, 'mRemainingTimeInSeconds'),
                _field(model, 'mTitleLengthMillis'),
                _ms(_field(model, 'mReleaseDateEpochMillis', 0)),
                _field(model, 'mRentalExpiresInMillis'),
                _field(model, 'mAmazonMaturityRating'),
                _yes_no(_field(model, 'mIsAdultContent', False)),
                _yes_no(_field(model, 'mHasSubtitles', False)),
                _yes_no(_field(model, 'mIsPlayable', False)),
                _field(model, 'mSeasonTitleId'), _enum_name(entry.fields.get('mType')
                                                            if isinstance(entry, _JavaObject)
                                                            else None),
                header, is_watchlist, source_file))

    data_headers = (
        'Title ID', 'Content Type (as stored)', 'Title', 'Series Title', 'Season Title',
        'Season Number', 'Episode Number', 'Total Seasons', 'Total Episodes',
        'Remaining Time (seconds)', 'Title Length (ms)', ('Release Date', 'datetime'),
        'Rental Expires In (ms)', 'Maturity Rating', 'Adult Content', 'Has Subtitles',
        'Playable', 'Season Title ID', 'Tile Type (as stored)', 'Collection Header',
        'Is Watchlist', 'Source File')
    return data_headers, data_list, source_path


_SEARCH_SQL = ('SELECT `queryTimeMillis`, `queryText`, `accountId`, `profileId` '
               'FROM `LocalSearchQuery` ORDER BY `queryTimeMillis` DESC')


@artifact_processor
def prime_video_search_history(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'search_query.db'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        for view, rows in (('Committed', _rows(file_found, _SEARCH_SQL)),
                           ('Pre-checkpoint', _superseded(file_found, _SEARCH_SQL, 1))):
            for row in rows:
                data_list.append((_ms(row[0]), row[1], row[2], row[3], view, source_file))

    data_headers = (('Query Time', 'datetime'), 'Query Text', 'Account ID', 'Profile ID',
                    'Source View', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def prime_video_profiles(context):
    data_list = []
    source_path = ''
    identity = {}
    for file_found in _named(context, 'IdentityPreferences.xml'):
        identity = _prefs(file_found)
        source_path = source_path or file_found

    for file_found in _named(context, 'InternalPreferences.xml'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        raw = _prefs(file_found).get(_HOUSEHOLD_KEY)
        if not raw:
            continue
        try:
            household = _java_loads(b64decode(raw))
        except (BinasciiError, ValueError, IndexError, struct.error, TypeError) as ex:
            logfunc(f'Could not read the household blob in '
                    f'{os.path.basename(file_found)}: {ex}')
            continue
        if not isinstance(household, _JavaObject):
            continue

        marketplace = _field(household, 'mAvMarketplace')
        country = _field(household, 'mCurrentCountryString')
        country_of_record = _field(household, 'mVideoCountryOfRecordString')
        profiles = _unwrap(household.fields.get('mProfiles'))
        users = _unwrap(household.fields.get('mUsers'))
        status = _enum_name(profiles.fields.get('mStatus')
                            if isinstance(profiles, _JavaObject) else None)
        current = _value(profiles, 'mCurrentProfile')
        current_id = _field(current, 'mProfileId') if isinstance(current, _JavaObject) else ''

        accounts = []
        for user in _elements(users.fields.get('mAllRegisteredUsers')
                              if isinstance(users, _JavaObject) else None):
            user = _unwrap(user)
            if isinstance(user, _JavaObject):
                accounts.append((_field(user, 'mAccountId'),
                                 _enum_name(user.fields.get('mRole'))))
        account_id, account_role = accounts[0] if accounts else ('', '')

        for profile in _elements(profiles.fields.get('mProfiles')
                                 if isinstance(profiles, _JavaObject) else None):
            profile = _unwrap(profile)
            if not isinstance(profile, _JavaObject):
                continue
            avatar = _value(profile, 'mAvatar')
            urls = _value(avatar, 'mAvatarUrls')
            profile_id = _field(profile, 'mProfileId')
            data_list.append((
                _field(profile, 'mName'), profile_id,
                _enum_name(profile.fields.get('mProfileAgeGroup')),
                _yes_no(_field(profile, 'mIsDefaultProfile', False)),
                _yes_no(profile_id and profile_id == current_id),
                _field(profile, 'mProgramId'),
                _field(avatar, 'mAvatarId') if isinstance(avatar, _JavaObject) else '',
                _field(urls, 'mRound') if isinstance(urls, _JavaObject) else '',
                _field(urls, 'mSquare') if isinstance(urls, _JavaObject) else '',
                account_id, account_role, marketplace, country, country_of_record,
                status, identity.get('current_directed_id', ''), source_file))

        if not data_list and (account_id or status):
            data_list.append((
                '', '', '', 'NO', 'NO', '', '', '', '', account_id, account_role,
                marketplace, country, country_of_record, status,
                identity.get('current_directed_id', ''), source_file))

    data_headers = (
        'Profile Name', 'Profile ID', 'Age Group (as stored)', 'Default Profile',
        'Current Profile', 'Program ID', 'Avatar ID', 'Avatar Round URL',
        'Avatar Square URL', 'Account ID', 'Account Role (as stored)', 'Marketplace ID',
        'Country', 'Video Country Of Record', 'Profiles Status (as stored)',
        'Current Directed ID', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def prime_video_account_store(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'map_data_storage.db'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        for row in _rows(file_found, '''
                SELECT `account_timestamp`, `directed_id`, `display_name`,
                       `account_deleted`, `account_dirty` FROM `accounts`'''):
            data_list.append((_ms(row[0]), 'accounts', row[1], 'display_name', row[2],
                              _yes_no(row[3]), _yes_no(row[4]), source_file))

        for table, account, key, value, stamp in (
                ('userdata', 'userdata_account_id', 'userdata_key', 'userdata_value',
                 'userdata_timestamp'),
                ('tokens', 'token_account_id', 'token_key', 'token_value',
                 'token_timestamp'),
                ('device_data', 'device_data_namespace', 'device_data_key',
                 'device_data_value', 'device_data_timestamp')):
            prefix = 'device_data' if table == 'device_data' else table.rstrip('s')
            for row in _rows(file_found, f'''
                    SELECT `{stamp}`, `{account}`, `{key}`, `{value}`,
                           `{prefix}_deleted`, `{prefix}_dirty` FROM `{table}`'''):
                data_list.append((_ms(row[0]), table, row[1], row[2], row[3],
                                  _yes_no(row[4]), _yes_no(row[5]), source_file))

    data_headers = (('Timestamp', 'datetime'), 'Table', 'Account ID / Namespace', 'Key',
                    'Value (as stored)', 'Deleted', 'Dirty', 'Source File')
    return data_headers, data_list, source_path


# (header, expression). The order is the report's order, so the SELECT and the row it
# produces cannot drift apart the way a separate index mapping can. Only the download
# table's own columns vary between schema versions, so only those are resolved.
_DOWNLOAD_FIELDS = (
    ('Title ID', 'd.`offer_asin`'),
    ('Title', 't.`title`'),
    ('Content Type (as stored)', 't.`contenttype`'),
    ('Series Title', 'sr.`series_title`'),
    ('Season Title', 'se.`season_title`'),
    ('Season Number', 'se.`season_number`'),
    ('Episode Number', 't.`episode_number`'),
    ('Runtime (ms)', 't.`runtime`'),
    ('MPAA Rating', 't.`mpaa_rating`'),
    ('Download State (as stored)', 'download_state'),
    ('Download Type (as stored)', 'download_type'),
    ('Download Error Code (as stored)', 'download_error_code'),
    ('Media Quality (as stored)', 'media_quality'),
    ('Audio Format (as stored)', 'audio_format'),
    ('File Size (KB)', 'file_size_kb'),
    ('Percent Downloaded', 'percent_downloaded'),
    ('Ready To Watch', 'is_ready_to_watch'),
    ('Fully Watched', 'is_fully_watched'),
    ('Auto Download', 'is_auto_download'),
    ('Visibility (as stored)', 'visibility'),
    ('Storage Path Type (as stored)', 'storage_path_type'),
    ('Storage Path', 'storage_path'),
    ('Relative Storage Path', 'relative_storage_path'),
    ('Expiry (as stored)', 'expiry_ms'),
    ('Queue Time (as stored)', 'queue_time'),
    ('Queued Timestamp (as stored)', 'queued_timestamp_ms'),
    ('Execution Timestamp (as stored)', 'execution_timestamp_ms'),
    ('Last Retry Time (as stored)', 'last_retry_time_ms'),
    ('Ready To Play Time (as stored)', 'ready_to_play_time'),
    ('First Play Time (as stored)', 'first_play_time'),
    ('Actual Runtime (ms)', 'actual_runtime_ms'),
    ('DRM Type (as stored)', 'm.`type`'),
    ('DRM Expiry (as stored)', 'm.`expiry`'),
    ('DRM View Hours', 'm.`view_hours`'),
    ('DRM Scheme (as stored)', 'm.`drm_scheme`'),
    ('DRM Asset ID', 'd.`drm_asset_id`'),
    ('Profile ID', 'profile_id'),
    ('User ID', 'user_id'),
    ('Owning App Package', 'owning_app_package_name'),
)
_DOWNLOAD_YES_NO = {'Ready To Watch', 'Fully Watched', 'Auto Download'}


@artifact_processor
def prime_video_downloads(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'downloads'):
        columns = _table_columns(file_found, 'download')
        if not columns:
            continue
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        select_list = []
        for header, expression in _DOWNLOAD_FIELDS:
            if '.' in expression:
                select_list.append(expression)
            elif expression in columns:
                select_list.append(f'd.`{expression}`')
            else:
                select_list.append(f'NULL AS `{expression}`')
        rows = _rows(file_found, f'''
            SELECT {', '.join(select_list)}
            FROM `download` d
            LEFT JOIN `title_offer` tof ON tof.`offer_asin` = d.`offer_asin`
            LEFT JOIN `title` t ON t.`asin` = tof.`asin`
            LEFT JOIN `season_offer` so ON so.`season_offer_asin` = t.`season_offer_asin`
            LEFT JOIN `season` se ON se.`season_asin` = so.`season_asin`
            LEFT JOIN `series_offer` sro
                   ON sro.`series_offer_asin` = se.`series_offer_asin`
            LEFT JOIN `series` sr ON sr.`series_asin` = sro.`series_asin`
            LEFT JOIN `drm` m ON m.`drm_asset_id` = d.`drm_asset_id`''')
        for row in rows:
            data_list.append(tuple(
                _yes_no(value) if header in _DOWNLOAD_YES_NO else value
                for (header, _), value in zip(_DOWNLOAD_FIELDS, row)) + (source_file,))

    data_headers = tuple(header for header, _ in _DOWNLOAD_FIELDS) + ('Source File',)
    return data_headers, data_list, source_path


_CACHE_COLUMNS = (
    '_id', 'accessed_time_seconds', 'title_id', 'content_type', 'is_trailer', 'status',
    'source', 'initial_source', 'media_quality', 'audio_format', 'cache_level',
    'cache_priority', 'entitlement_type', 'benefit_tier', 'is_licensable',
    'is_deferrable', 'start_position', 'end_position', 'target_duration', 'filesize_kb',
    'download_time_seconds', 'retry_attempts', 'cdn', 'encode_version', 'session_id',
    'correlation_id', 'offline_keyid', 'request_submission_time_ms', 'url',
)


@artifact_processor
def prime_video_streaming_cache(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'dbcachedcontent'):
        sql = _select(file_found, 'cached_content_table', _CACHE_COLUMNS,
                      'ORDER BY `accessed_time_seconds` DESC')
        if not sql:
            continue
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        for view, rows in (('Committed', _rows(file_found, sql)),
                           ('Pre-checkpoint', _superseded(file_found, sql, 0))):
            for row in rows:
                data_list.append((
                    _seconds(row[1]), row[2], row[3], row[4], row[5], row[6], row[7],
                    row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                    row[16], row[17], row[18], row[19], row[20], row[21], row[22],
                    row[23], row[24], row[25], row[26], row[27], row[28], row[0], view,
                    source_file))

    data_headers = (
        ('Accessed Time', 'datetime'), 'Title ID', 'Content Type (as stored)',
        'Is Trailer', 'Status (as stored)', 'Source (as stored)',
        'Initial Source (as stored)', 'Media Quality (as stored)',
        'Audio Format (as stored)', 'Cache Level (as stored)',
        'Cache Priority (as stored)', 'Entitlement Type (as stored)',
        'Benefit Tier (as stored)', 'Is Licensable', 'Is Deferrable', 'Start Position',
        'End Position', 'Target Duration', 'File Size (KB)', 'Download Time (seconds)',
        'Retry Attempts', 'CDN', 'Encode Version', 'Session ID', 'Correlation ID',
        'Offline Key ID', 'Request Submission Time (as stored)', 'URL', 'Row ID',
        'Source View', 'Source File')
    return data_headers, data_list, source_path


_TITLE_ID_RE = re.compile(
    r'/(streaming-plugins|global_video_cache)/([^/]+)(/(.*))?$')


def _cached_title_entries(context):
    '''(cache, title id, remainder, path) for every matched cache path.'''
    entries = []
    for path in unique_files(context):
        relative = str(_relative(context, path)).replace('\\', '/')
        match = _TITLE_ID_RE.search(relative)
        if match:
            entries.append((match.group(1), match.group(2), match.group(4) or '', path))
    return entries


@artifact_processor
def prime_video_cached_titles(context):
    titles = {}
    source_path = ''
    for cache, title_id, remainder, path in _cached_title_entries(context):
        source_path = source_path or path
        relative = str(_relative(context, path)).replace('\\', '/')
        record = titles.setdefault(title_id, {
            'plugins': set(), 'locales': set(), 'files': 0, 'bytes': 0,
            'trickplay': 0, 'xray': 0, 'subtitles': 0, 'manifests': 0, 'fragments': 0,
            'source': relative[:relative.index(f'/{cache}/') + len(cache) + 2],
        })
        if not remainder:
            continue
        parts = remainder.split('/')
        if cache == 'streaming-plugins':
            record['plugins'].add(parts[0])
        else:
            record['locales'].add(parts[0])
        if not os.path.isfile(path):
            continue
        record['files'] += 1
        try:
            record['bytes'] += os.path.getsize(path)
        except OSError:
            pass
        name = parts[-1]
        if cache == 'streaming-plugins':
            if parts[0] == 'trickplay' and name.lower().endswith('.jpg'):
                record['trickplay'] += 1
            elif parts[0] == 'xray':
                record['xray'] += 1
            elif parts[0] == 'subtitles':
                record['subtitles'] += 1
        elif name == 'manif.atv':
            record['manifests'] += 1
        elif name.endswith('.atv'):
            record['fragments'] += 1

    data_list = []
    for title_id, record in sorted(titles.items()):
        data_list.append((
            title_id, ', '.join(sorted(record['plugins'])),
            ', '.join(sorted(record['locales'])), record['files'], record['bytes'],
            record['trickplay'], record['xray'], record['subtitles'],
            record['manifests'], record['fragments'], record['source']))

    data_headers = (
        'Title ID', 'Streaming Plugin Data', 'Video Cache Locales', 'Files On Disk',
        'Bytes On Disk', 'Trickplay Frames', 'X-Ray Files', 'Subtitle Files',
        'Cached Manifests', 'Cached Media Fragments', 'Source Folder')
    return data_headers, data_list, source_path


def _image_kind(path):
    '''(label, extension, mime) from the leading bytes, or None when not an image.'''
    try:
        with open(path, 'rb') as handle:
            head = handle.read(16)
    except OSError:
        return None
    for magic, label, extension, mime in _IMAGE_MAGIC:
        if head.startswith(magic):
            return label, extension, mime
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'WEBP', 'webp', 'image/webp'
    return None


@artifact_processor
def prime_video_cached_images(context):
    data_list = []
    source_path = ''
    for cache, title_id, remainder, path in _cached_title_entries(context):
        if cache != 'streaming-plugins' or not remainder or not os.path.isfile(path):
            continue
        parts = remainder.split('/')
        if parts[0] == 'trickplay':
            kind = 'Trickplay Frame'
        elif parts[0] == 'xray':
            kind = 'X-Ray Image'
        else:
            continue
        image = _image_kind(path)
        if not image:
            continue
        label, extension, mime = image
        name = os.path.splitext(parts[-1])[0]
        offset = int(name) if kind == 'Trickplay Frame' and name.isdigit() else ''
        source_path = source_path or path
        media = check_in_media(path, f'{title_id} {parts[-1]}', force_type=mime,
                               force_extension=extension)
        data_list.append((
            media or '', title_id, kind, offset, label, parts[-1],
            os.path.getsize(path), _relative(context, path)))

    data_list.sort(key=lambda row: (row[1], row[2], row[3] if row[3] != '' else -1))

    data_headers = (
        ('Image', 'media'), 'Title ID', 'Image Type', 'Media Offset (ms)', 'File Type',
        'File Name', 'Size (bytes)', 'Source File')
    return data_headers, data_list, source_path


_EVENT_SQL = ('SELECT `_id`, `Timestamp`, `Type`, `Name`, `ASIN`, `SessionId`, '
              '`AccountId`, `ProfileId`, `Priority`, `Processed`, `RetryCount`, `Body` '
              'FROM `events`')


def _event_kinds(body):
    '''(eventType, eventSubtype) from the row's own JSON body, or ('', '').'''
    if not body or not isinstance(body, str) or not body.startswith('{'):
        return '', ''
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        return '', ''
    if not isinstance(payload, dict):
        return '', ''
    return str(payload.get('eventType', '')), str(payload.get('eventSubtype', ''))


@artifact_processor
def prime_video_app_events(context):
    data_list = []
    source_path = ''
    for file_found in _named(context, 'event'):
        if not _table_columns(file_found, 'events'):
            continue
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        for view, rows in (('Committed', _rows(file_found, _EVENT_SQL)),
                           ('Pre-checkpoint', _superseded(file_found, _EVENT_SQL, 0))):
            for row in rows:
                event_type, event_subtype = _event_kinds(row[11])
                data_list.append((
                    _ms(row[1]), row[2], row[3], event_type, event_subtype, row[4],
                    row[5], row[6], row[7], row[8], row[9], row[10], row[0], view,
                    source_file))

    data_headers = (
        ('Timestamp', 'datetime'), 'Type (as stored)', 'Name (as stored)',
        'Event Type (as stored)', 'Event Subtype (as stored)', 'Title ID', 'Session ID',
        'Account ID', 'Profile ID', 'Priority (as stored)', 'Processed (as stored)',
        'Retry Count', 'Row ID', 'Source View', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def prime_video_app_settings(context):
    data_list = []
    source_path = ''
    for file_found in _named(
            context, 'InternalPreferences.xml', 'PersistentPreferences.xml',
            'IdentityPreferences.xml', 'LocalizationPreferences.xml',
            f'{_PACKAGE}_preferences.xml'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        name = os.path.basename(str(file_found).replace('\\', '/'))
        for key, value in _prefs(file_found).items():
            if key == _HOUSEHOLD_KEY:
                continue
            value = '' if value is None else str(value)
            rendered = ''
            digits = value.lstrip('-').isdigit()
            if digits and _MS_KEY_RE.search(key) and len(value.lstrip('-')) == 13:
                rendered = _ms(value)
            elif digits and _SECONDS_KEY_RE.search(key) and len(value.lstrip('-')) == 10:
                rendered = _seconds(value)
            data_list.append((rendered, name, key, value, source_file))

    for file_found in _named(context, 'AppEventsJsonFile'):
        source_path = source_path or file_found
        source_file = _relative(context, file_found)
        name = os.path.basename(str(file_found).replace('\\', '/'))
        try:
            with open(file_found, 'r', encoding='utf-8', errors='replace') as handle:
                lines = handle.read().splitlines()
        except OSError as ex:
            logfunc(f'Could not read {name}: {ex}')
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                data_list.append(('', name, 'unparsed line', line, source_file))
                continue
            stamp = _ms(event.get('ts', 0))
            for key, value in event.items():
                if key == 'ts':
                    continue
                data_list.append((stamp, name, key, str(value), source_file))

    data_headers = (('Rendered Timestamp', 'datetime'), 'File', 'Key',
                    'Value (as stored)', 'Source File')
    return data_headers, data_list, source_path
