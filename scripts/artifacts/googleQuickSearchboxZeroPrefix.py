__artifacts_v2__ = {
    "quicksearch_personal_suggestions": {
        "name": "Google Quick Search Box - Personal Suggestions",
        "description": "Entries carrying subtype 39 (personal, in Chromium's naming) in the Google app's cached suggestion "
                       "file, with the account of the folder each was read from.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-02",
        "last_update_date": "2026-10-02",
        "requirements": "none",
        "category": "Google Now & QuickSearch",
        "notes": "Read from cache/accounts/<number>/CompleteServerZeroPrefixCache.pb in the Google app's data folder "
                 '(com.google.android.googlequicksearchbox). The app is closed source and no published schema for this '
                 'file was found, so the fields were read off the file itself, on the 32 distinct copies in the tested '
                 'images, and are taken here directly from the protobuf wire format: at the top level field 1 and '
                 'field 4 are times in milliseconds since 1970 and field 3 holds the entries as its repeated field 2, '
                 'and an entry stores its text in field 1, a type number in field 2 and subtype numbers in field 3. '
                 'The three type numbers seen (0, 35, 46) and 3 of the 27 subtype numbers seen are ones Chromium '
                 'defines for its own search suggestions; the other subtype numbers are not in that file and are shown '
                 'as stored. Reference: Chromium, third_party/omnibox_proto/types.proto, '
                 'https://github.com/chromium/chromium/blob/838812506b4ced0e8803504ca3acdf4165348d94/third_party/omnibox_proto/types.proto#L17-L30 '
                 '(SuggestType: 35 is TYPE_PERSONALIZED_QUERY, 46 is TYPE_ENTITY) and '
                 'https://github.com/chromium/chromium/blob/838812506b4ced0e8803504ca3acdf4165348d94/third_party/omnibox_proto/types.proto#L33-L65 '
                 '(SuggestSubtype: 39 is SUBTYPE_PERSONAL, 143 is SUBTYPE_TRENDS, 362 is SUBTYPE_ZERO_PREFIX). No '
                 'source says the Google app uses that vocabulary in this file. It was checked against the files: each '
                 'of the 132 entries carrying subtype 39 also stores a /complete/deleteitems address whose delq value '
                 "is the entry's own text, and none of the 495 other entries stores one. This artifact lists only the "
                 'entries carrying subtype 39. Of the 495 others, 480 carry subtype 143; they are counted per file in '
                 'Google Quick Search Box - Suggestion Cache Files, their text is not reported, and the run log gives '
                 'the number left out for each file. A row shows that the file holds this text in an entry carrying '
                 'subtype 39, in the account folder it was read from. When the text was searched for is not shown. '
                 'Every number stored in the personal entries was tested as a time between 2015 and 2030 in seconds, '
                 'milliseconds or microseconds: 3 of the 132 entries, all in one file, hold one such number (fields 4, '
                 "37, 3, 1, 1), the same on all three and about 18 hours after that file's Cache Time, and it is not "
                 'reported. Whether a personal suggestion can come from activity on another device or in another '
                 'Google product was not tested. Cache Time is field 1 and Later Write Time is field 4, both shown in '
                 'UTC. They are stored once per file, not per entry. 13 of the 32 distinct tested files store no field '
                 "4. The 20 tested tar images that hold the file keep file modification times: the file's modification "
                 'time was within one second of field 4 on the 20 files that store it and within one second of field 1 '
                 'on the 6 that do not. Across five captures of one emulator (emu_a15_oss_v1 to emu_a15_oss_v5) field '
                 '1 and the entries stayed the same while field 4 advanced. Later Write Time is blank for a file that '
                 "stores no field 4. Type shows the stored number with Chromium's name for it: 130 of the 132 rows "
                 "were 35 and 2 were 46. Subtypes shows the stored numbers in stored order. Position is the entry's "
                 'place among the entries of its file, counted from 1; in the 10 files holding personal entries those '
                 'entries came before every other entry. Account is read from files/AccountData.pb in the same app '
                 'data folder: the entry whose field 1 equals the folder number, and in it the value at fields 2, 2, '
                 "3; the value at fields 2, 2, 7 is that entry's type. On the tested images all 42 cache files "
                 'reported had such an entry, and the 10 files holding personal entries all belonged to an entry whose '
                 'type reads google. Account Folder is the <number> in the path and Android User is the user in the '
                 "path (0 for data/data, blank when the path names none). Rows read from one file share that file's "
                 'Cache Time, Later Write Time, Account, Account Folder and Android User. An extraction that carries '
                 'one file under several storage paths has it read once. A file that is empty or cannot be read as '
                 'protobuf is named in the run log and gives no row. The other files in cache/accounts/<number> '
                 '(SqliteKeyValueCache databases) are not read by this artifact.',
        "paths": ('*/com.google.android.googlequicksearchbox/cache/accounts/*/CompleteServerZeroPrefixCache.pb',
                  '*/com.google.android.googlequicksearchbox/files/AccountData.pb'),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "galaxys10_a10": "Android 10 | no cache file | 0 rows",
            "samsungs20_a13": "Android 13 | no cache file | 0 rows",
            "s20fe_a13": "Android 13 | 2 cache files, no entry with subtype 39 | 0 rows",
            "pixel7a_a14": "Android 14 | 3 rows",
            "anne_a15": "Android 15 | 30 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 cache file, no entry with subtype 39 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 1 cache file, no entry with subtype 39 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 14 rows",
            "samsunga53_a14": "Android 14 | no cache file | 0 rows",
            "sharon_a14": "Android 14 | 7 rows",
            "russell_pixel6a_a13": "Android 13 | 31 rows",
            "userb2_a13": "Android 13 | 2 cache files, no entry with subtype 39 | 0 rows",
            "df020_mavic_pro_android": "no cache file | 0 rows",
            "cookbook_a11": "Android 11 | no cache file | 0 rows",
            "sharon_a13": "Android 13 | 7 rows",
            "russell_a14": "Android 14 | 5 rows",
            "pixel3_a11": "Android 11 | no cache file | 0 rows",
            "pixel3_a12": "Android 12 | 5 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | no cache file | 0 rows",
            "falken_a326u_a13": "Android 13 | 30 rows",
            "emu_a15_oss_v1": "Android 15 | 2 cache files, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v2": "Android 15 | 2 cache files, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v3": "Android 15 | 2 cache files, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v4": "Android 15 | 2 cache files, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v5": "Android 15 | 2 cache files, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v6": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v7": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v8": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v9": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "adams_ss135dl_a13": "Android 13 | no cache file | 0 rows",
            "adams_ss134dl_a03s_logical": "no cache file | 0 rows",
            "emu_a15_oss_v10": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v11": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v12": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v13": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v14": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v15": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v16": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | no cache file | 0 rows",
            "emu_a15_oss2_v1": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss2_v2": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 1 cache file, no entry with subtype 39 | 0 rows",
            "dfrws2011_case1_a855": "no cache file | 0 rows",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | no cache file | 0 rows",
        },
    },
    "quicksearch_suggestion_caches": {
        "name": "Google Quick Search Box - Suggestion Cache Files",
        "description": "One row per cached suggestion file of the Google app, with its stored times, the account "
                       "of its folder and its entry counts.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-02",
        "last_update_date": "2026-10-02",
        "requirements": "none",
        "category": "Google Now & QuickSearch",
        "notes": "One row per readable cache/accounts/<number>/CompleteServerZeroPrefixCache.pb in the Google app's "
                 'data folder (com.google.android.googlequicksearchbox). The app is closed source and no published '
                 'schema for this file was found; the field numbers were read off the file itself and are described in '
                 'the notes of Google Quick Search Box - Personal Suggestions, which lists the personal entries. Cache '
                 'Time is field 1 and Later Write Time is field 4, both shown in UTC. They are stored once per file, '
                 'not per entry. 13 of the 32 distinct tested files store no field 4. The 20 tested tar images that '
                 "hold the file keep file modification times: the file's modification time was within one second of "
                 'field 4 on the 20 files that store it and within one second of field 1 on the 6 that do not. Across '
                 'five captures of one emulator (emu_a15_oss_v1 to emu_a15_oss_v5) field 1 and the entries stayed the '
                 'same while field 4 advanced. Later Write Time is blank for a file that stores no field 4. What '
                 'causes the app to write the file was not established. Entries is the number of entries in the file '
                 'and Personal Entries the number carrying subtype 39, which Chromium names SUBTYPE_PERSONAL. '
                 'Reference: Chromium, third_party/omnibox_proto/types.proto, '
                 'https://github.com/chromium/chromium/blob/838812506b4ced0e8803504ca3acdf4165348d94/third_party/omnibox_proto/types.proto#L35 '
                 'and, for subtype 143, SUBTYPE_TRENDS, '
                 'https://github.com/chromium/chromium/blob/838812506b4ced0e8803504ca3acdf4165348d94/third_party/omnibox_proto/types.proto#L47. '
                 'The text of the entries that do not carry subtype 39 is not reported: 480 of the 495 such entries in '
                 'the 32 distinct tested files carry subtype 143. Account Type and Account are read from '
                 'files/AccountData.pb in the same app data folder: the entry whose field 1 equals the folder number, '
                 'and in it the values at fields 2, 2, 7 and 2, 2, 3. All 42 files reported on the tested images had '
                 'such an entry: 15 read google and 27 read pseudonymous, and Account held an address on the 15 google '
                 'rows and on none of the 27 pseudonymous rows, where it is shown as stored. Personal entries were '
                 'held by 10 of the 15 google files and by none of the 27 pseudonymous files. Zero in Personal Entries '
                 'means the file holds no entry with subtype 39; it does not show that no search was made. Account '
                 'Folder is the <number> in the path and Android User is the user in the path (0 for data/data, blank '
                 'when the path names none). An extraction that carries one file under several storage paths has it '
                 'read once. A file that is empty or cannot be read as protobuf is named in the run log and gives no '
                 'row.',
        "paths": ('*/com.google.android.googlequicksearchbox/cache/accounts/*/CompleteServerZeroPrefixCache.pb',
                  '*/com.google.android.googlequicksearchbox/files/AccountData.pb'),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "galaxys10_a10": "Android 10 | no cache file | 0 rows",
            "samsungs20_a13": "Android 13 | no cache file | 0 rows",
            "s20fe_a13": "Android 13 | 2 rows",
            "pixel7a_a14": "Android 14 | 1 rows",
            "anne_a15": "Android 15 | 1 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 rows",
            "hc_pixel8pro_a17": "Android 17 | 1 rows",
            "kevin_pocox7_a15": "Android 15 | 1 rows",
            "samsunga53_a14": "Android 14 | no cache file | 0 rows",
            "sharon_a14": "Android 14 | 1 rows",
            "russell_pixel6a_a13": "Android 13 | 2 rows",
            "userb2_a13": "Android 13 | 2 rows",
            "df020_mavic_pro_android": "no cache file | 0 rows",
            "cookbook_a11": "Android 11 | no cache file | 0 rows",
            "sharon_a13": "Android 13 | 1 rows",
            "russell_a14": "Android 14 | 2 rows",
            "pixel3_a11": "Android 11 | no cache file | 0 rows",
            "pixel3_a12": "Android 12 | 1 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | no cache file | 0 rows",
            "falken_a326u_a13": "Android 13 | 2 rows",
            "emu_a15_oss_v1": "Android 15 | 2 rows",
            "emu_a15_oss_v2": "Android 15 | 2 rows",
            "emu_a15_oss_v3": "Android 15 | 2 rows",
            "emu_a15_oss_v4": "Android 15 | 2 rows",
            "emu_a15_oss_v5": "Android 15 | 2 rows",
            "emu_a15_oss_v6": "Android 15 | 1 rows",
            "emu_a15_oss_v7": "Android 15 | 1 rows",
            "emu_a15_oss_v8": "Android 15 | 1 rows",
            "emu_a15_oss_v9": "Android 15 | 1 rows",
            "adams_ss135dl_a13": "Android 13 | no cache file | 0 rows",
            "adams_ss134dl_a03s_logical": "no cache file | 0 rows",
            "emu_a15_oss_v10": "Android 15 | 1 rows",
            "emu_a15_oss_v11": "Android 15 | 1 rows",
            "emu_a15_oss_v12": "Android 15 | 1 rows",
            "emu_a15_oss_v13": "Android 15 | 1 rows",
            "emu_a15_oss_v14": "Android 15 | 1 rows",
            "emu_a15_oss_v15": "Android 15 | 1 rows",
            "emu_a15_oss_v16": "Android 15 | 1 rows",
            "emu_a15_oss_v17": "Android 15 | no cache file | 0 rows",
            "emu_a15_oss2_v1": "Android 15 | 1 rows",
            "emu_a15_oss2_v2": "Android 15 | 1 rows",
            "emu_a15_oss2_v3": "Android 15 | 1 rows",
            "dfrws2011_case1_a855": "no cache file | 0 rows",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | no cache file | 0 rows",
        },
    },
}

import os
import re
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_PACKAGE = 'com.google.android.googlequicksearchbox'
_CACHE_TAIL = re.compile(r'^cache/accounts/([^/]+)/CompleteServerZeroPrefixCache\.pb$')
_ACCOUNT_TAIL = 'files/AccountData.pb'
_STORAGE_USER = re.compile(r'\x00[a-z]+:(\d+)\x00')

# The Google app is closed source, so the field numbers below were read off the files
# themselves, on the 32 distinct copies in the registered corpora:
#   cache file    1 time in ms, 3 response, 4 time in ms (not always present)
#   response      2 suggestion (repeated)
#   suggestion    1 text, 2 type, 3 subtype (repeated)
#   AccountData   2 entry (repeated)
#   entry         1 number, 2 record
#   record        2 account
#   account       2 display name, 3 account name, 7 type
_CACHE_FIELDS = {1, 3, 4}
_RESPONSE_FIELDS = {2}
_SUGGESTION_FIELDS = {1, 2, 3}
_ACCOUNTDATA_FIELDS = {2}
_ENTRY_FIELDS = {1, 2}
_RECORD_FIELDS = {2}
_ACCOUNT_FIELDS = {3, 7}

# The type and subtype numbers match Chromium's omnibox vocabulary. Names are from
# third_party/omnibox_proto/types.proto, enum SuggestType, at commit
# 838812506b4ced0e8803504ca3acdf4165348d94.
_SUGGEST_TYPES = {
    0: 'TYPE_QUERY',
    5: 'TYPE_NAVIGATION',
    6: 'TYPE_CALCULATOR',
    33: 'TYPE_TAIL',
    35: 'TYPE_PERSONALIZED_QUERY',
    44: 'TYPE_PROFILE',
    46: 'TYPE_ENTITY',
    69: 'TYPE_NATIVE_CHROME',
    83: 'TYPE_PERSONALIZED_NAVIGATION',
    171: 'TYPE_CHROME_QUERY_TILES',
    185: 'TYPE_CATEGORICAL_QUERY',
    203: 'TYPE_FUSEBOX_ACTION',
}
# SUBTYPE_PERSONAL in the same file's enum SuggestSubtype.
_SUBTYPE_PERSONAL = 39


def _varint(data, pos):
    result = shift = 0
    while True:
        byte = data[pos]
        pos += 1
        result |= (byte & 0x7f) << shift
        shift += 7
        if not byte & 0x80:
            return result, pos


def _wire_fields(data, want):
    """Fields of one protobuf message, {field number: [values in file order]}.

    Reads the wire format directly (varint 0, 64-bit 1, length-delimited 2, 32-bit 5) and
    skips every field not in `want` by its length. A malformed message raises IndexError or
    ValueError."""
    out = {}
    pos, end = 0, len(data)
    while pos < end:
        tag, pos = _varint(data, pos)
        field, wire = tag >> 3, tag & 7
        if field == 0:
            raise ValueError(f'field number 0 at offset {pos}')
        if wire == 0:
            value, pos = _varint(data, pos)
        elif wire == 1:
            value, pos = data[pos:pos + 8], pos + 8
        elif wire == 2:
            length, pos = _varint(data, pos)
            value, pos = data[pos:pos + length], pos + length
            if pos > end:
                raise ValueError(f'field {field} runs past the end of its message')
        elif wire == 5:
            value, pos = data[pos:pos + 4], pos + 4
        else:
            raise ValueError(f'unsupported wire type {wire} at offset {pos}')
        if field in want:
            out.setdefault(field, []).append(value)
    return out


def _first(fields, number, default=None):
    values = fields.get(number)
    return values[0] if values else default


def _message(fields, number, want):
    """The first value of a field read as a nested message, {} when absent or not a message."""
    value = _first(fields, number)
    if not isinstance(value, (bytes, bytearray)):
        return {}
    return _wire_fields(value, want)


def _text(value):
    if isinstance(value, (bytes, bytearray)):
        return value.decode('utf-8', errors='replace')
    return '' if value is None else str(value)


def _ms(value):
    if not isinstance(value, int) or not value:
        return ''
    try:
        return _EPOCH + timedelta(milliseconds=value)
    except (ValueError, OverflowError):
        return ''


def _by_time(row):
    """Newest first, a row with no readable time last, file order kept inside one file."""
    return (row[0] == '', -(row[0] - _EPOCH).total_seconds() if row[0] != '' else 0)


def _subtypes(values):
    """Subtype numbers in stored order, whether written one per field or packed."""
    out = []
    for value in values or []:
        if isinstance(value, int):
            out.append(value)
            continue
        pos = 0
        while pos < len(value):
            number, pos = _varint(value, pos)
            out.append(number)
    return out


def _type_label(value):
    if value is None:
        value = 0   # proto leaves a zero off the wire
    name = _SUGGEST_TYPES.get(value)
    return f'{value} ({name})' if name else str(value)


def _locate(context, path):
    """(container key, Android user, path below the package folder) or None.

    The container key is the evidence path above the package folder with the storage view
    folded, so a cache file and the AccountData.pb of the same app data directory share it
    and another Android user's do not."""
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    key, _rank = canonical_path(relative)
    head, found, tail = key.partition(f'/{_PACKAGE}/')
    if not found:
        return None
    user = _STORAGE_USER.search(head)
    return head, user.group(1) if user else '', tail


def _read(path):
    try:
        with open(path, 'rb') as handle:
            return handle.read()
    except OSError as error:
        logfunc(f'Could not read {path}: {error}')
        return None


def _accounts(data):
    """{entry number: (account type, account name)} from AccountData.pb."""
    out = {}
    for entry_raw in _wire_fields(data, _ACCOUNTDATA_FIELDS).get(2, []):
        if not isinstance(entry_raw, (bytes, bytearray)):
            continue
        entry = _wire_fields(entry_raw, _ENTRY_FIELDS)
        number = _first(entry, 1)
        account = _message(_message(entry, 2, _RECORD_FIELDS), 2, _ACCOUNT_FIELDS)
        if isinstance(number, int):
            out[number] = (_text(_first(account, 7)), _text(_first(account, 3)))
    return out


def _suggestions(response):
    """[(position, text, type label, subtype numbers)] in file order."""
    out = []
    for position, raw in enumerate(response.get(2, []), start=1):
        if not isinstance(raw, (bytes, bytearray)):
            continue
        fields = _wire_fields(raw, _SUGGESTION_FIELDS)
        out.append((
            position,
            _text(_first(fields, 1)),
            _type_label(_first(fields, 2)),
            _subtypes(fields.get(3)),
        ))
    return out


def _caches(context):
    """(cache files, source paths). One dict per cache file that could be read."""
    cache_files, account_maps, sources = [], {}, []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        located = _locate(context, file_found)
        if located is None:
            continue
        container, user, tail = located
        folder = _CACHE_TAIL.match(tail)
        if not folder and tail != _ACCOUNT_TAIL:
            continue
        data = _read(file_found)
        if data is None:
            continue
        if not folder:
            try:
                account_maps[container] = _accounts(data)
                sources.append(file_found)
            except (IndexError, ValueError) as error:
                logfunc(f'Could not read the account list {file_found}: {error}')
            continue
        if not data:
            logfunc(f'Suggestion cache is empty: {file_found}')
            continue
        try:
            top = _wire_fields(data, _CACHE_FIELDS)
            suggestions = _suggestions(_message(top, 3, _RESPONSE_FIELDS))
        except (IndexError, ValueError) as error:
            logfunc(f'Could not read the suggestion cache {file_found}: {error}')
            continue
        sources.append(file_found)
        cache_files.append({
            'container': container,
            'user': user,
            'folder': folder.group(1),
            'first': _ms(_first(top, 1)),
            'later': _ms(_first(top, 4)),
            'suggestions': suggestions,
        })
    for cache in cache_files:
        accounts = account_maps.get(cache['container'], {})
        number = int(cache['folder']) if cache['folder'].isdigit() else None
        cache['account_type'], cache['account'] = accounts.get(number, ('', ''))
    return cache_files, sources


@artifact_processor
def quicksearch_personal_suggestions(context):
    data_headers = (
        ('Cache Time', 'datetime'),
        ('Later Write Time', 'datetime'),
        'Suggestion',
        'Type',
        'Subtypes',
        'Position',
        'Account',
        'Account Folder',
        'Android User',
    )
    data_list = []
    cache_files, sources = _caches(context)
    for cache in cache_files:
        other = 0
        for position, text, type_label, subtypes in cache['suggestions']:
            if _SUBTYPE_PERSONAL not in subtypes:
                other += 1
                continue
            data_list.append((
                cache['first'],
                cache['later'],
                text,
                type_label,
                ', '.join(str(number) for number in subtypes),
                position,
                cache['account'],
                cache['folder'],
                cache['user'],
            ))
        if other:
            logfunc(f"Suggestion cache of account folder {cache['folder']}"
                    f"{' of Android user ' + cache['user'] if cache['user'] else ''}: {other} of "
                    f"{len(cache['suggestions'])} entries are not marked personal and are counted in "
                    'Google Quick Search Box - Suggestion Cache Files, not listed here.')
    data_list.sort(key=_by_time)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def quicksearch_suggestion_caches(context):
    data_headers = (
        ('Cache Time', 'datetime'),
        ('Later Write Time', 'datetime'),
        'Account Type',
        'Account',
        'Account Folder',
        'Android User',
        'Entries',
        'Personal Entries',
    )
    data_list = []
    cache_files, sources = _caches(context)
    for cache in cache_files:
        data_list.append((
            cache['first'],
            cache['later'],
            cache['account_type'],
            cache['account'],
            cache['folder'],
            cache['user'],
            len(cache['suggestions']),
            sum(1 for entry in cache['suggestions'] if _SUBTYPE_PERSONAL in entry[3]),
        ))
    data_list.sort(key=_by_time)
    return data_headers, data_list, '\n'.join(sources)
