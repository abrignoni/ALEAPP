__artifacts_v2__ = {
    "mmkv_carved_records": {
        "name": "MMKV - Recovered Records",
        "description": "Records recovered from the device's MMKV stores, carved from the space past the recorded data region or read from a store whose recorded size is zero. Carved rows are inferences and some are wrong.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-07",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "MMKV",
        "notes": "Most of the rows here are carved, which is inference rather than parsing, and some of those rows are wrong. The Corroboration column separates them from the one case below that is not inferred. MMKV compacts a store by moving the surviving entries to the front of its data region with a memmove and lowering the recorded size (Tencent/MMKV at tag v2.3.0, Core/MMKV_IO.cpp, memmoveDictionary and doFullWriteBack: https://github.com/Tencent/MMKV/blob/381b96926b73f7394d9fd0905d2753bd5205ff59/Core/MMKV_IO.cpp#L1131-L1161 and https://github.com/Tencent/MMKV/blob/381b96926b73f7394d9fd0905d2753bd5205ff59/Core/MMKV_IO.cpp#L1292-L1315), and nothing zeroes what the move leaves behind. Space added to the file is zero filled straight after the ftruncate that adds it (https://github.com/Tencent/MMKV/blob/381b96926b73f7394d9fd0905d2753bd5205ff59/Core/MemoryFile.cpp#L192-L198), so what sits past the recorded size is content this store wrote earlier and not unrelated data left behind in the filesystem. This artifact reads records out of that space. There is no marker to synchronise on, so every byte offset is tested on its own and anything record-shaped is accepted: a key of 5 to 64 bytes that decodes as UTF-8 and is made only of letters, digits, underscore, hyphen, dollar, dot, slash and colon, followed by a value container that accounts for its own length, is a bare varint, or is the 4 or 8 bytes a float and a double are written as. A row is reported only where something corroborates it, and the Corroboration column says which: the key is also in that store's live region, or the same key was recovered more than once from that store. Uncorroborated single hits are not reported. Measured against data holding no MMKV structure at all, the same test returned nothing on zero-filled, natural-language and JSON input and returned false records on base64 and hexadecimal text. The rates recorded here earlier and the rates in the reader's own documentation differ and have not been re-measured, so no figure is given. A store whose values are encoded blobs would otherwise fill this table with records corresponding to nothing. Hexadecimal text produces false records because a decimal digit is itself a byte in the range a key length may take and the digits that follow it satisfy the character set. The space is deliberately absent from that character set: a space is byte 32, which is itself a valid key length, so allowing it makes running text read as records. A store whose recorded size is zero is a different case and is not carved. At the same tag, clearing a store and loading a file that fails its validity check both write a zero size into the meta file (clearAll and loadFromFile in Core/MMKV_IO.cpp, https://github.com/Tencent/MMKV/blob/381b96926b73f7394d9fd0905d2753bd5205ff59/Core/MMKV_IO.cpp#L1479-L1510 and https://github.com/Tencent/MMKV/blob/381b96926b73f7394d9fd0905d2753bd5205ff59/Core/MMKV_IO.cpp#L127-L139) and leave the records in place, so that region is read by an ordinary walk of the layout and is reported only when the walk consumes whole entries and then meets nothing but the file's zero padding. Those rows say so in the Corroboration column and carry no offset, because nothing about them was inferred. A recovered record is not a deleted value. It is a write that was superseded or removed at some point before the store was last compacted, and nothing in the file establishes which of the two, or when. Offset gives the record's position in the source file so it can be located there. Values are reported as text exactly as stored: MMKV records a value's type in the calling code rather than in the file, so nothing here types them. A record whose header the compaction wrote over cannot be recovered at all: its key and lengths are gone and only a fragment of its value remains, with nothing to attribute it to. Those are not reported, so this table is not a complete account of what the space holds. A store whose recorded region does not read as plaintext records, which is an encrypted or a damaged store, is skipped without a row, as is a file that is not an MMKV store or cannot be read; the run log names each skipped file with the reader's reason, which does not establish whether that store is encrypted or damaged. A record with an empty value container is accepted and shown as <removed>.",
        "paths": ('*/mmkv/*', '*/mmkv_private/*'),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | 16,840 rows",
            "pixel7a_a14": "Android 14 | 11 rows",
            "samsungs20_a13": "Android 13 | 871 rows",
            "sharon_a14": "Android 14 | 1,657 rows",
        },
    },
}

import os
from collections import Counter

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.mmkv_parser import MMKVError, carve_slack, decode_value, read_entries

RESET = 'the store\'s recorded size is zero and the region walked cleanly to its padding'


def _render(container):
    """The value as text for the report; a removal marker says so.

    Everything is rendered as text. MMKV records a value's type in the calling code
    rather than in the file, so a carved container carries no type to honour, and a
    varint here can hold a number wider than a database integer column takes.
    """
    value = decode_value(container)
    if value is None:
        return '<removed>'
    if isinstance(value, bytes):
        return value.hex()
    return str(value)


def _reason(error):
    """Why a store was skipped, for the run log, without the path the error may carry."""
    if isinstance(error, OSError):
        return f'{type(error).__name__}: {error.strerror or "could not be read"}'
    return f'{type(error).__name__}: {error}'


def _store_rows(file_found, relative_path):
    """Rows for one store, or an empty list when there is nothing to report."""
    if os.path.isdir(file_found) or file_found.endswith('.crc'):
        return []
    try:
        live_entries = read_entries(file_found)
    except (MMKVError, OSError) as ex:
        # not an MMKV store, encrypted, or unreadable; no row, and the run log says so
        logfunc(f'MMKV - Recovered Records: skipped {relative_path}: {_reason(ex)}')
        return []

    if not live_entries:
        # A cleared store, or one whose CRC failed, keeps its records and reports a
        # size of zero. Reading those is a walk of the ordinary layout rather than a
        # carve, so they are reported whole and are not put through the tests below.
        try:
            recovered = read_entries(file_found, recover=True)
        except (MMKVError, OSError) as ex:
            logfunc(f'MMKV - Recovered Records: zero-size store not read {relative_path}: '
                    f'{_reason(ex)}')
            recovered = []
        return [(key, _render(container), RESET, '', relative_path)
                for key, container in recovered]

    try:
        carved = carve_slack(file_found)
    except (MMKVError, OSError) as ex:
        logfunc(f'MMKV - Recovered Records: not carved {relative_path}: {_reason(ex)}')
        return []
    counts = Counter(record.key for record in carved)
    rows = []
    for record in carved:
        if record.live_key:
            why = 'the key is also in the live region'
        elif counts[record.key] > 1:
            why = f'the key was recovered {counts[record.key]} times from this store'
        else:
            continue
        rows.append((record.key, _render(record.container), why,
                     record.offset, relative_path))
    return rows

from scripts.artifacts.storagePathViews import unique_files


@artifact_processor
def mmkv_carved_records(context):
    data_headers = (
        'Key',
        'Value',
        'Corroboration',
        'Offset',
        'Source File',
    )
    data_list = []
    sources = []
    for file_found in unique_files(context):
        rows = _store_rows(file_found, context.get_relative_path(file_found))
        if rows:
            data_list.extend(rows)
            sources.append(file_found)
    return data_headers, data_list, '\n'.join(sources)
