__artifacts_v2__ = {
    "tiktok_search_history": {
        "name": "TikTok - Search History",
        "description": "Searches TikTok kept in its local search history, read from the search "
                       "repository of its Keva key-value store.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "TikTok",
        "notes": "Read from the files/keva/repo/search folder of com.zhiliaoapp.musically. The same "
                 "path under com.ss.android.ugc.trill is matched but no tested image held it. Keva "
                 "(com.bytedance.keva) is the key-value store library TikTok uses. The store layout "
                 "follows the app's libkeva.so (versionCode 2024701040, disassembled) and the field "
                 "names its decompiled SearchHistory class. A list is in search.blk, or in <key>.sgv "
                 "once it no longer fits there, as on kevin_pocox7_a15. Chunks in the variable-width "
                 "part of search.chk are read by the library's type widths, but no tested store used "
                 "that part. Keva Key is recent_history_v2, ecommerce_history or a "
                 "<number>_ec_search_history key. Every Current row on the tested images came from "
                 "recent_history_v2. ecommerce_history was present on 1 tested image and held no "
                 "records, and no tested store held a <number>_ec_search_history key. Each list "
                 "holds pairs of a user id and that user's search records. The app writes its "
                 "current user id as the first value, or FAKE_USER when no account is logged in (no "
                 "tested row held FAKE_USER). Keyword, Enter Method, History Intent (as stored), "
                 "Author Name and Music ID are the record's keyword, enter_method, history_intent, "
                 "author_name and music_id values. The meanings of Enter Method and History Intent "
                 "values are not established. Search Time is the record's timestamp in milliseconds. "
                 "In versionCode 2024701040 the recording method sets it from the phone's clock, and "
                 "recording a search again with the same keyword, uid and music id replaces the earlier record, so the time is the latest one. Search Time was blank on 1 russell_a14 row, where the stored timestamp "
                 "was 0. Stored Copy is Current when the row is in the value the key now points to. "
                 "It is Freed block when the row is only in a block whose 4-byte header is zero, the "
                 "state libkeva's Erase leaves. Freed block rows have no Keva Key because the block "
                 "does not name its key. libkeva frees the old block every time a list is rewritten, "
                 "so a Freed block row does not establish that a user deleted a search. A freed copy "
                 "with the same user id, keyword and timestamp as a row already reported is not "
                 "reported again. kevin_pocox7_a15 has 30 Current rows and 1 Freed block row. Stored "
                 "Copy held one value on each other tested image with rows, and User ID held one "
                 "value on each tested image with rows. Author Name was empty on all tested rows. "
                 "The record's int field held 0 on the rows read and is not reported. The "
                 "is_original_music, is_valid_music, search_extra_params, cover_image_url and uid "
                 "fields are also not reported. A row records a search kept by the app and does not "
                 "by itself establish that the user typed the keyword. The other 1,147 Keva block "
                 "files under files/keva/repo on dragna_pixel9a_a16 are not read.",
        "paths": ('*/com.zhiliaoapp.musically/files/keva/repo/search/*',
                  '*/com.ss.android.ugc.trill/files/keva/repo/search/*'),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.zhiliaoapp.musically versionCode 2024701040 | 9 rows",
            "kevin_pocox7_a15": "Android 15 | 31 rows (30 Current, 1 Freed block)",
            "russell_a14": "Android 14 | 3 rows",
            "anne_a15": "Android 15 | 2 rows",
            "sharon_a14": "Android 14 | 1 row",
            "galaxys10_a10": "Android 10 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | 0 rows",
        },
    },
}

import json
import os
import re
import struct
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

_LIST_KEY = re.compile(r'(?:recent_history_v2|ecommerce_history|\d+_ec_search_history)\Z')
_BLOCK_MAGIC = b'keva-blk'
_CHUNK_MAGIC = b'keva-chk'
_VALUE_MAGIC = b'keva-sgv'
_LIST_START = b'[{"first"'
_STRING_TYPE = 1            # low nibble of a block or single-value word: a UTF-8 string
_CHUNK_SET = 0x80           # set on the top byte of a live chunk
_CHUNK_STRING = 6
_VALUE_IN_BLOCK = 0x01      # top byte of a string chunk's value word
_VALUE_EMPTY = 0x81
_VALUE_IN_FILE = 0x41       # the value is in <key>.sgv beside the block file
_CHUNK_UNITS = {1: 2, 2: 1, 3: 3, 4: 2, 5: 3, 6: 2, 7: 2}   # width of each chunk type, in 4 bytes


class _BlockFile:
    """Block lookup in a Keva .blk file, following libkeva's GetBlockPointer."""

    def __init__(self, data):
        if data[:8] != _BLOCK_MAGIC or len(data) < 0x20:
            raise ValueError('not a Keva block file')
        self.data = data
        self.block_size, self.fixed_count, dimensions = struct.unpack_from('<III', data, 0x14)
        if not self.block_size or not 1 <= dimensions <= 8:
            raise ValueError('unexpected Keva block header')
        counts = struct.unpack_from(f'<{dimensions}I', data, 0x20)
        sizes = struct.unpack_from(f'<{dimensions}I', data, 0x20 + 4 * dimensions)
        offset = 0x20 + 8 * dimensions
        self.regions = []
        first_index = 0
        for count, size in zip(counts, sizes):
            self.regions.append((first_index, count, size, offset))
            first_index += count
            offset += count * size
        self.first_fixed = first_index
        self.fixed_offset = offset

    def offset(self, index):
        for first_index, count, size, start in self.regions:
            if first_index <= index < first_index + count:
                return start + (index - first_index) * size
        if self.first_fixed <= index < self.first_fixed + self.fixed_count:
            return self.fixed_offset + (index - self.first_fixed) * self.block_size
        return None

    def read(self, index):
        """The bytes of the string block at index, or None."""
        offset = self.offset(index)
        if offset is None or offset + 4 > len(self.data):
            return None
        word = struct.unpack_from('<I', self.data, offset)[0]
        size = word & 0xffffff
        if (word >> 24) & 0x0f != _STRING_TYPE or offset + 4 + size > len(self.data):
            return None
        return self.data[offset + 4:offset + 4 + size]

    def freed_lists(self):
        """(lists, unreadable count) from fixed blocks whose header libkeva's Erase zeroed."""
        decoder = json.JSONDecoder()
        lists, unreadable = [], 0
        for index in range(self.first_fixed, self.first_fixed + self.fixed_count):
            offset = self.offset(index)
            if offset + 4 + len(_LIST_START) > len(self.data):
                break
            if self.data[offset:offset + 4] != b'\0\0\0\0':
                continue
            if self.data[offset + 4:offset + 4 + len(_LIST_START)] != _LIST_START:
                continue
            try:
                value, _ = decoder.raw_decode(self.data[offset + 4:].decode('utf-8', 'replace'))
                lists.append(value)
            except ValueError:
                unreadable += 1
        return lists, unreadable


def _string_chunks(chunks):
    """(key block index, value word) of each live string chunk in a Keva .chk file."""
    if chunks[:8] != _CHUNK_MAGIC or len(chunks) < 0x28:
        raise ValueError('not a Keva chunk file')
    dimensions = struct.unpack_from('<I', chunks, 0x18)[0]
    if dimensions != 3:
        raise ValueError('unexpected Keva chunk header')
    fixed32, fixed64, fixed96 = struct.unpack_from('<III', chunks, 0x1c)
    start = 0x1c + 4 * dimensions
    fixed64_start = start + fixed32 * 4
    fixed96_start = fixed64_start + fixed64 * 8
    unfixed_start = fixed96_start + fixed96 * 12
    for offset in range(fixed64_start, min(fixed96_start, len(chunks) - 7), 8):
        word, value = struct.unpack_from('<II', chunks, offset)
        if word >> 24 == _CHUNK_SET | _CHUNK_STRING:
            yield word & 0xffffff, value
    offset = unfixed_start
    while offset + 8 <= len(chunks):
        word, value = struct.unpack_from('<II', chunks, offset)
        top = word >> 24
        units = _CHUNK_UNITS.get(top & 0x0f) if top & _CHUNK_SET else None
        if units is None:
            offset += 4
            continue
        if top == _CHUNK_SET | _CHUNK_STRING:
            yield word & 0xffffff, value
        offset += units * 4


def _single_value(path):
    """The string in a Keva single-value (.sgv) file, or None."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
    except OSError:
        return None
    if data[:8] != _VALUE_MAGIC or len(data) < 0x1c:
        return None
    word = struct.unpack_from('<I', data, 0x18)[0]
    size = word & 0xffffff
    if (word >> 24) & 0x0f != _STRING_TYPE or 0x1c + size > len(data):
        return None
    return data[0x1c:0x1c + size]


def _list_records(value):
    """[(user id, record)] from a stored search history value, or None if it is not one."""
    if not isinstance(value, list):
        return None
    rows = []
    for entry in value:
        if not isinstance(entry, dict) or 'first' not in entry or 'second' not in entry:
            return None
        items = entry['second']
        if not isinstance(items, list):
            return None
        rows.extend((str(entry['first']), item) for item in items
                    if isinstance(item, dict) and 'keyword' in item)
    return rows


def _records(body):
    try:
        return _list_records(json.loads(body.decode('utf-8')))
    except (UnicodeDecodeError, ValueError):
        return None


def _time(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _row(user_id, item, key_name, copy):
    return (_time(item.get('timestamp')), item.get('keyword') or '', key_name, copy, user_id,
            item.get('enter_method') or '', item.get('history_intent', ''),
            item.get('author_name') or '', item.get('music_id') or '')


def _read_store(block_path, chunk_path, sources):
    with open(block_path, 'rb') as handle:
        blocks = _BlockFile(handle.read())
    with open(chunk_path, 'rb') as handle:
        chunks = handle.read()
    rows, seen = [], set()
    for key_index, value_word in _string_chunks(chunks):
        key = blocks.read(key_index)
        name = key.decode('utf-8', 'replace') if key else ''
        if not _LIST_KEY.match(name):
            continue
        flag = value_word >> 24
        if flag == _VALUE_EMPTY:
            continue
        if flag == _VALUE_IN_BLOCK:
            body = blocks.read(value_word & 0xffffff)
        elif flag == _VALUE_IN_FILE:
            value_path = os.path.join(os.path.dirname(block_path), f'{name}.sgv')
            body = _single_value(value_path)
            if body is not None:
                sources.append(value_path)
        else:
            body = None
        records = _records(body) if body else None
        if records is None:
            logfunc(f'TikTok - Search History: could not read the current value of {name}')
            continue
        for user_id, item in records:
            seen.add((user_id, item.get('keyword'), item.get('timestamp')))
            rows.append(_row(user_id, item, name, 'Current'))
    freed, unreadable = blocks.freed_lists()
    if unreadable:
        logfunc(f'TikTok - Search History: {unreadable} freed list(s) could not be parsed')
    for value in freed:
        for user_id, item in _list_records(value) or []:
            record = (user_id, item.get('keyword'), item.get('timestamp'))
            if record not in seen:
                seen.add(record)
                rows.append(_row(user_id, item, '', 'Freed block'))
    return rows


@artifact_processor
def tiktok_search_history(context):
    data_headers = (('Search Time', 'datetime'), 'Keyword', 'Keva Key', 'Stored Copy', 'User ID',
                    'Enter Method', 'History Intent (as stored)', 'Author Name', 'Music ID')
    data_list, sources = [], []
    for file_found in unique_files(context):
        block_path = str(file_found)
        if os.path.basename(block_path) != 'search.blk':
            continue
        chunk_path = block_path[:-3] + 'chk'
        if not os.path.isfile(chunk_path):
            logfunc('TikTok - Search History: search.blk has no search.chk beside it')
            continue
        sources.extend((block_path, chunk_path))
        try:
            data_list.extend(_read_store(block_path, chunk_path, sources))
        except (OSError, ValueError, struct.error) as error:
            logfunc(f'TikTok - Search History: could not read the store: {type(error).__name__}')
    data_list.sort(key=lambda row: (row[0] == '', str(row[0])))
    return data_headers, data_list, '\n'.join(sources)
