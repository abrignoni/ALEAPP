__artifacts_v2__ = {
    "chromiumCacheEntries": {
        "name": "Chromium Browsers - HTTP Cache Entries",
        "description": "The URLs held in a Chromium browser's HTTP disk cache, with the time each response was "
                       "received, the time the entry was last used, the HTTP status, content type and length the "
                       "server returned, and the size of the cached body.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Read from the Simple Cache entry files (<16 hex digits>_0 and _1) under a browser's "
                 "cache/Cache/Cache_Data folder, and under cache/WebView/<profile>/HTTP Cache/Cache_Data for "
                 "DuckDuckGo, which renders pages in a WebView. On the tested images that first layout was used "
                 "only by browsers (Chrome, Samsung Internet, Brave, Cromite, Edge and, spelled cache/cache, "
                 "Opera); the apps that embed a WebView keep theirs under cache/WebView and are not read here. "
                 "The file layout is Chromium's: a SimpleFileHeader (magic 0xfcfb6d1ba7725c30, version, key "
                 "length, key hash), the key, stream 1, an EOF record, stream 0, an optional SHA-256 of the key "
                 "and a second EOF record (magic 0xf4fa6f45970d41d8, flags, CRC, stream size); the _1 file holds "
                 "stream 2 behind the same header. Reference: Chromium, net/disk_cache/simple/simple_entry_format.h "
                 "at commit 5babd82a3403ae4c580afc34df4c677d70779b52. Stream 0 is the pickled HttpResponseInfo: "
                 "flags, an extra-flags word when flag bit 31 is set, request time and response time as microseconds "
                 "since 1601-01-01 UTC, an original response time when extra-flag bit 2 is set, then the raw "
                 "response headers separated by NUL. Reference: net/http/http_response_info.cc "
                 "(InitFromPickle) and net/http/http_response_headers.cc at the same commit; base/time/time.h "
                 "for the epoch. Response Time and Request Time are those two values rendered in UTC; they and "
                 "the header columns are blank on an entry whose stream 0 is empty, 28 of the 147,256 "
                 "entries on the tested images. Last Used comes from the folder's index-dir/the-real-index, "
                 "which lists each entry hash with its last used time and size "
                 "(net/disk_cache/simple/simple_index_file.cc and simple_index.cc, version 9 on every tested "
                 "index); it is blank when the folder has no index (19,826 entries in 5 caches on the "
                 "tested images, 19,653 of them one Chrome cache whose index-dir was empty) or "
                 "when the index does not list the entry (90 entries). 5 entry files of the tested "
                 "images were skipped because they ended without an EOF record. The key is "
                 "credential_key/post_key/[isolation_key]url; when the third part starts with _dk_ the URL is "
                 "the text after its last space and the text before it is the network isolation key "
                 "(net/http/http_cache.cc, GenerateCacheKey). URL and Isolation Key are read that way and Cache "
                 "Key is the whole key as stored. HTTP Status, Content Type, Content Length, Date and "
                 "Last-Modified are the response's own status line and header values as stored, blank where the "
                 "header is absent. Body Bytes is the stream 1 size plus the stream 2 size when a _1 file is "
                 "present; the body itself is not decoded or rendered, and is stored as the server sent it "
                 "(Content-Encoding applies). Entry Version is the header's version field as stored, 5 on every "
                 "tested entry. An entry records that the browser fetched or revalidated the URL at Response "
                 "Time; it does not by itself show that a page was displayed, and Chromium evicts entries as "
                 "the cache fills, so this is the recent working set rather than a history.",
        "paths": ('*/cache/[Cc]ache/Cache_Data/*',
                  '*/com.duckduckgo.mobile.android/cache/WebView/*/HTTP Cache/Cache_Data/*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 22696 rows",
            "cookbook_a11": "Android 11 | 1254 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "emu_a15_oss_v2": "Android 15 | 0 rows",
            "emu_a15_oss_v3": "Android 15 | 38 rows",
            "emu_a15_oss_v4": "Android 15 | 38 rows",
            "emu_a15_oss_v5": "Android 15 | 309 rows",
            "emu_a15_oss_v6": "Android 15 | 224 rows",
            "emu_a15_oss_v7": "Android 15 | 137 rows",
            "emu_a15_oss_v8": "Android 15 | 69 rows",
            "emu_a15_oss_v9": "Android 15 | 69 rows",
            "falken_a326u_a13": "Android 13 | 1013 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 4879 rows",
            "hc_pixel8pro_a17": "Android 17 | 5047 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 39865 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 6737 rows",
            "russell_a14": "Android 14 | 19653 rows",
            "russell_pixel6a_a13": "Android 13 | 12177 rows",
            "s20fe_a13": "Android 13 | 1171 rows",
            "samsunga53_a14": "Android 14 | 1701 rows",
            "samsungs20_a13": "Android 13 | 1311 rows",
            "sharon_a13": "Android 13 | 9818 rows",
            "sharon_a14": "Android 14 | 17793 rows",
            "userb2_a13": "Android 13 | 1257 rows",
        },
    },
    "chromiumCacheIndexes": {
        "name": "Chromium Browsers - HTTP Cache Indexes",
        "description": "One row per Chromium browser HTTP cache, with the time the cache was last modified, the "
                       "number of entries its index lists, the size it records and the entry files present.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Read from index-dir/the-real-index in each Cache_Data folder the Entries artifact covers. The "
                 "file is a base::Pickle with a CRC header, then magic 0x656e74657220796f, version, entry count, "
                 "cache size and the reason the index was written, then one record per entry (hash, last used "
                 "time, packed size) and the cache's last modified time. Reference: Chromium, "
                 "net/disk_cache/simple/simple_index_file.h and .cc at commit "
                 "5babd82a3403ae4c580afc34df4c677d70779b52. Cache Last Modified and the counts are those "
                 "values; Write Reason is the stored integer, whose names are Chromium's own enum and are not "
                 "interpreted here. Entry Files Present counts the _0 files beside the index, so a difference "
                 "from Entries Listed shows entries added or removed since the index was written; on the tested "
                 "images 5 of 55 indexes differed, one listing 6,233 entries beside no entry "
                 "files, and one Chrome cache had an index-dir folder with no index file at all.",
        "paths": ('*/cache/[Cc]ache/Cache_Data/index-dir/the-real-index',
                  '*/com.duckduckgo.mobile.android/cache/WebView/*/HTTP Cache/Cache_Data/index-dir/the-real-index'),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 2 rows",
            "cookbook_a11": "Android 11 | 2 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 1 row",
            "emu_a15_oss_v2": "Android 15 | 1 row",
            "emu_a15_oss_v3": "Android 15 | 1 row",
            "emu_a15_oss_v4": "Android 15 | 2 rows",
            "emu_a15_oss_v5": "Android 15 | 5 rows",
            "emu_a15_oss_v6": "Android 15 | 4 rows",
            "emu_a15_oss_v7": "Android 15 | 3 rows",
            "emu_a15_oss_v8": "Android 15 | 2 rows",
            "emu_a15_oss_v9": "Android 15 | 2 rows",
            "falken_a326u_a13": "Android 13 | 2 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 4 rows",
            "hc_pixel8pro_a17": "Android 17 | 4 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 5 rows",
            "russell_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 3 rows",
            "s20fe_a13": "Android 13 | 2 rows",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 4 rows",
            "sharon_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 2 rows",
            "userb2_a13": "Android 13 | 1 row",
        },
    },
}

import os
import re
import struct
from datetime import datetime, timedelta, timezone

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import canonical_path, unique_files

_INITIAL_MAGIC = 0xfcfb6d1ba7725c30
_FINAL_MAGIC = 0xf4fa6f45970d41d8
_INDEX_MAGIC = 0x656e74657220796f
_FLAG_HAS_KEY_SHA256 = 1 << 1
_EXTRA_FLAGS = 1 << 31
_ORIGINAL_RESPONSE_TIME = 1 << 2   # RESPONSE_EXTRA_INFO_HAS_ORIGINAL_RESPONSE_TIME in http_response_info.cc
_HEADER = struct.Struct('<QIIII')   # SimpleFileHeader: magic, version, key_length, key_hash, padding
_EOF = struct.Struct('<QIIII')      # SimpleFileEOF: magic, flags, data_crc32, stream_size, padding
_CHROME_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)
_ENTRY_NAME = re.compile(r'^[0-9a-f]{16}_[01]$')


def _chrome_time(micros):
    try:
        return _CHROME_EPOCH + timedelta(microseconds=int(micros)) if micros else ''
    except (TypeError, ValueError, OverflowError):
        return ''


class _Pickle:
    """Sequential reader over a base::Pickle payload: fields start on 4-byte boundaries."""

    def __init__(self, data, offset):
        self.data = data
        self.offset = offset

    def read(self, fmt):
        size = struct.calcsize(fmt)
        if self.offset + size > len(self.data):
            raise ValueError('pickle ended early')
        value = struct.unpack_from('<' + fmt, self.data, self.offset)[0]
        self.offset = (self.offset + size + 3) & ~3
        return value

    def string(self):
        length = self.read('i')
        if length < 0 or self.offset + length > len(self.data):
            raise ValueError('pickle string overruns the payload')
        value = self.data[self.offset:self.offset + length]
        self.offset = (self.offset + length + 3) & ~3
        return value


def _package_of(path):
    """The package segment before /cache/ in a staged path, as stored."""
    parts = path.replace('\\', '/').split('/')
    for i, part in enumerate(parts):
        if part == 'cache' and i > 0:
            return parts[i - 1]
    return ''


def _read_entry(path):
    """Header, key, stream sizes and the stream 0 bytes of a _0 file; None with a log line when malformed."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
    except OSError as error:
        logfunc(f'Chromium HTTP cache: could not read {os.path.basename(path)}: {error}')
        return None
    if len(data) < _HEADER.size + _EOF.size * 2:
        return None
    magic, version, key_length, _key_hash, _pad = _HEADER.unpack_from(data, 0)
    if magic != _INITIAL_MAGIC or key_length > len(data) - _HEADER.size:
        logfunc(f'Chromium HTTP cache: {os.path.basename(path)} does not start with a Simple Cache header')
        return None
    key = data[_HEADER.size:_HEADER.size + key_length].decode('utf-8', errors='replace')
    eof0_at = len(data) - _EOF.size
    magic0, flags0, _crc0, size0, _pad0 = _EOF.unpack_from(data, eof0_at)
    if magic0 != _FINAL_MAGIC:
        logfunc(f'Chromium HTTP cache: {os.path.basename(path)} has no stream 0 EOF record')
        return None
    sha = 32 if flags0 & _FLAG_HAS_KEY_SHA256 else 0
    stream0_at = eof0_at - sha - size0
    eof1_at = stream0_at - _EOF.size
    if eof1_at < _HEADER.size + key_length:
        logfunc(f'Chromium HTTP cache: {os.path.basename(path)} stream sizes overrun the file')
        return None
    magic1, _flags1, _crc1, size1, _pad1 = _EOF.unpack_from(data, eof1_at)
    if magic1 != _FINAL_MAGIC:
        logfunc(f'Chromium HTTP cache: {os.path.basename(path)} has no stream 1 EOF record')
        return None
    return {'version': version, 'key': key, 'stream0': data[stream0_at:stream0_at + size0], 'stream1_size': size1}


def _response_info(stream0):
    """(request time, response time, header lines) from a pickled HttpResponseInfo; blanks when unreadable."""
    try:
        pickle = _Pickle(stream0, 0)
        pickle.read('I')  # payload size
        flags = pickle.read('i')
        extra = pickle.read('i') if flags & _EXTRA_FLAGS else 0
        request_time = pickle.read('q')
        response_time = pickle.read('q')
        if extra & _ORIGINAL_RESPONSE_TIME:
            pickle.read('q')
        headers = pickle.string().decode('utf-8', errors='replace').split('\x00')
    except (ValueError, struct.error):
        return '', '', []
    return _chrome_time(request_time), _chrome_time(response_time), [h for h in headers if h]


def _header_value(headers, name):
    for line in headers[1:]:
        key, sep, value = line.partition(':')
        if sep and key.strip().lower() == name:
            return value.strip()
    return ''


def _split_key(key):
    """(url, isolation key) from credential_key/post_key/[isolation_key]url."""
    parts = key.split('/', 2)
    rest = parts[2] if len(parts) == 3 else key
    if rest.startswith('_dk_') and ' ' in rest:
        isolation, _, url = rest.rpartition(' ')
        return url, isolation
    return rest, ''


def _stream2_size(path_1):
    """Bytes of stream 2 in a _1 file: the file minus its header, key and EOF record."""
    try:
        with open(path_1, 'rb') as handle:
            head = handle.read(_HEADER.size)
        size = os.path.getsize(path_1)
    except OSError:
        return 0
    if len(head) < _HEADER.size:
        return 0
    magic, _version, key_length, _key_hash, _pad = _HEADER.unpack_from(head, 0)
    if magic != _INITIAL_MAGIC:
        return 0
    return max(0, size - _HEADER.size - key_length - _EOF.size)


def _read_index(path):
    """Metadata and {hash: (last used, size)} of a the-real-index file; None with a log line when unreadable."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
    except OSError as error:
        logfunc(f'Chromium HTTP cache: could not read the index {path}: {error}')
        return None
    try:
        pickle = _Pickle(data, 8)  # PickleHeader: payload size, crc
        magic = pickle.read('Q')
        version = pickle.read('I')
        count = pickle.read('Q')
        cache_size = pickle.read('Q')
        reason = pickle.read('I')
        if magic != _INDEX_MAGIC:
            logfunc(f'Chromium HTTP cache: {path} does not carry the Simple Cache index magic')
            return None
        entries = {}
        for _ in range(count):
            entry_hash = pickle.read('Q')
            last_used = pickle.read('q')
            packed = pickle.read('Q')
            entries[f'{entry_hash:016x}'] = (_chrome_time(last_used), (packed >> 8) << 8)
        last_modified = _chrome_time(pickle.read('q'))
    except (ValueError, struct.error) as error:
        logfunc(f'Chromium HTTP cache: the index {path} did not parse: {error}')
        return None
    return {'version': version, 'count': count, 'cache_size': cache_size, 'reason': reason,
            'last_modified': last_modified, 'entries': entries}


def _cache_dirs(context, files):
    """{Cache_Data folder: {'index': path or None, 'entries': {hash: {'0': path, '1': path}}}}.

    Folders are keyed by their storage-view canonical path, so an index and its entries staged
    from two spellings of one folder (data/data, data/user/0, data_mirror) pair up.
    """
    dirs = {}
    by_key = {}
    for file_found in files:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        base = os.path.basename(file_found)
        parent = os.path.dirname(file_found)
        if base == 'the-real-index' and os.path.basename(parent) == 'index-dir':
            folder = os.path.dirname(parent)
        elif _ENTRY_NAME.match(base):
            folder = parent
        else:
            continue
        key = canonical_path(context.get_relative_path(folder))[0]
        folder = by_key.setdefault(key, folder)
        entry = dirs.setdefault(folder, {'index': None, 'entries': {}})
        if base == 'the-real-index':
            entry['index'] = file_found
        else:
            entry['entries'].setdefault(base[:16], {})[base[-1]] = file_found
    return dirs


@artifact_processor
def chromiumCacheEntries(context):
    data_headers = (
        ('Response Time', 'datetime'),
        ('Request Time', 'datetime'),
        ('Last Used', 'datetime'),
        'Package',
        'URL',
        'HTTP Status',
        'Content Type',
        'Content Length',
        'Date (as stored)',
        'Last-Modified (as stored)',
        'Body Bytes',
        'Isolation Key (as stored)',
        'Entry Version',
        'Entry Hash',
        'Cache Key (as stored)',
        'Source File',
    )
    data_list = []
    sources = []
    skipped = 0
    for folder, contents in sorted(_cache_dirs(context, unique_files(context)).items()):
        index = _read_index(contents['index']) if contents['index'] else None
        index_entries = index['entries'] if index else {}
        package = _package_of(folder)
        for entry_hash, files in sorted(contents['entries'].items()):
            if '0' not in files:
                continue
            entry = _read_entry(files['0'])
            if entry is None:
                skipped += 1
                continue
            request_time, response_time, headers = _response_info(entry['stream0'])
            url, isolation = _split_key(entry['key'])
            last_used = index_entries.get(entry_hash, ('', 0))[0]
            body = entry['stream1_size'] + (_stream2_size(files['1']) if '1' in files else 0)
            data_list.append((
                response_time, request_time, last_used, package, url,
                headers[0] if headers else '',
                _header_value(headers, 'content-type'), _header_value(headers, 'content-length'),
                _header_value(headers, 'date'), _header_value(headers, 'last-modified'),
                body, isolation, entry['version'], entry_hash, entry['key'],
                context.get_relative_path(files['0']),
            ))
            sources.append(files['0'])
    if skipped:
        logfunc(f'Chromium HTTP cache: {skipped} entry files were skipped as malformed or truncated')
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def chromiumCacheIndexes(context):
    data_headers = (
        ('Cache Last Modified', 'datetime'),
        'Package',
        'Entries Listed',
        'Entry Files Present',
        'Cache Size (bytes)',
        'Index Version',
        'Write Reason (as stored)',
        'Source File',
    )
    data_list = []
    sources = []
    for folder, contents in sorted(_cache_dirs(context, unique_files(context)).items()):
        if not contents['index']:
            continue
        index = _read_index(contents['index'])
        if index is None:
            continue
        present = sum(1 for files in contents['entries'].values() if '0' in files)
        if not present:
            # the index artifact's own glob stages only the index; count the siblings on disk
            try:
                present = sum(1 for name in os.listdir(folder) if _ENTRY_NAME.match(name) and name.endswith('_0'))
            except OSError:
                present = ''
        data_list.append((
            index['last_modified'], _package_of(folder), index['count'], present, index['cache_size'],
            index['version'], index['reason'], context.get_relative_path(contents['index']),
        ))
        sources.append(contents['index'])
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)
