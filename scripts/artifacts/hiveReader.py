"""Reader for the Hive key-value boxes Flutter apps write.

Shared by more than one artifact module, so it lives on its own rather than being copied.
A box is a flat log of frames, each `[len u32 LE][key][value][crc32 LE]`, and a later frame
for the same key supersedes an earlier one. Every frame carries its own CRC32, which is what
tells a real frame from the tail of a partly overwritten file, so the read stops at the first
frame whose checksum does not match rather than guessing.

Values are self describing: a type id then the payload. A registered class is written as a
field count and then numbered fields, and the field NAMES live only in the app's compiled
Dart, so a caller has to map the numbers itself against data it created deliberately.
"""

import os
import struct
import zlib

from scripts.ilapfuncs import logfunc

# Hive value type ids, from the format's own writer.
_NULL, _INT, _DOUBLE, _BOOL, _STRING, _BYTELIST = 0, 1, 2, 3, 4, 5
_INTLIST, _DOUBLELIST, _BOOLLIST, _STRINGLIST, _LIST, _MAP = 6, 7, 8, 9, 10, 11
_HIVELIST, _DATETIME = 12, 13


def read_value(buf, index):
    """One Hive value at `index`, returning it and the index after it."""
    kind = buf[index]
    index += 1
    if kind == _NULL:
        return None, index
    if kind in (_INT, _DOUBLE, _DATETIME):
        number, = struct.unpack('<d', buf[index:index + 8])
        return (number if kind == _DOUBLE else int(number)), index + 8
    if kind == _BOOL:
        return bool(buf[index]), index + 1
    if kind in (_STRING, _BYTELIST):
        length, = struct.unpack('<I', buf[index:index + 4])
        index += 4
        chunk = buf[index:index + length]
        return (chunk.decode('utf-8', 'replace') if kind == _STRING else chunk), index + length
    if kind in (_INTLIST, _DOUBLELIST, _BOOLLIST, _STRINGLIST, _LIST, _MAP, _HIVELIST):
        count, = struct.unpack('<I', buf[index:index + 4])
        index += 4
        items = []
        for _ in range(count):
            if kind in (_INTLIST, _DOUBLELIST):
                number, = struct.unpack('<d', buf[index:index + 8])
                items.append(int(number) if kind == _INTLIST else number)
                index += 8
            elif kind == _BOOLLIST:
                items.append(bool(buf[index]))
                index += 1
            elif kind == _STRINGLIST:
                length, = struct.unpack('<I', buf[index:index + 4])
                index += 4
                items.append(buf[index:index + length].decode('utf-8', 'replace'))
                index += length
            else:
                item, index = read_value(buf, index)
                items.append(item)
        return items, index
    # A registered class: a field count, then that many (field number, value) pairs.
    count = buf[index]
    index += 1
    obj = {}
    for _ in range(count):
        field = buf[index]
        index += 1
        obj[field], index = read_value(buf, index)
    return obj, index


def hive_entries(path):
    """The live entries of a Hive box, plus how many superseded frames each key has.

    Every frame carries a CRC32 of itself, so a frame that does not match is not read and
    the walk stops there rather than guessing at the rest of the file.
    """
    try:
        with open(path, 'rb') as handle:
            buf = handle.read()
    except OSError as ex:
        logfunc(f'HERE WeGo: could not read {os.path.basename(path)}: {ex}')
        return {}, {}
    live = {}
    earlier = {}
    offset = 0
    try:
        while offset + 4 <= len(buf):
            length, = struct.unpack('<I', buf[offset:offset + 4])
            if length < 8 or offset + length > len(buf):
                break
            frame = buf[offset:offset + length]
            stored, = struct.unpack('<I', frame[-4:])
            if (zlib.crc32(frame[:-4]) & 0xffffffff) != stored:
                logfunc(f'HERE WeGo: frame at offset {offset} of '
                        f'{os.path.basename(path)} failed its own CRC, stopping there')
                break
            index = 4
            key_kind = frame[index]
            index += 1
            if key_kind == 0:
                key, = struct.unpack('<I', frame[index:index + 4])
                index += 4
            else:
                key_length = frame[index]
                index += 1
                key = frame[index:index + key_length].decode('utf-8', 'replace')
                index += key_length
            value = None
            if index < length - 4:
                value, index = read_value(frame, index)
            if key in live:
                earlier[key] = earlier.get(key, 0) + 1
            live[key] = value
            offset += length
    except (IndexError, struct.error, ValueError) as ex:
        logfunc(f'HERE WeGo: stopped reading {os.path.basename(path)} at offset {offset}: {ex}')
    return live, earlier
