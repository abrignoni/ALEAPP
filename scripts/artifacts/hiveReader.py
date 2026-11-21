"""LEAPP-side adapter for the Hive reader.

The reader itself is vendored as ``scripts/hive_parser.py`` from
github.com/abrignoni/hive-parser. This module keeps the shape the artifact
modules already call, and owns the two things that belong to this tool rather
than to the reader: turning an unreadable file into an empty result instead of
an exception, and saying in the log when a box was not read to its end, with
the reason.
"""

import os

from scripts.ilapfuncs import logfunc
from scripts.hive_parser import looks_encrypted, read_frames, read_value

__all__ = ['hive_entries', 'read_value']


def hive_entries(path):
    """The live entries of a Hive box, plus how many superseded frames each key has.

    Every frame carries a CRC32 of itself, so a frame that does not match is not
    read and the walk stops there rather than guessing at the rest of the file.
    """
    name = os.path.basename(path)
    try:
        frames = read_frames(path)
        size = os.path.getsize(path)
    except OSError as ex:
        logfunc(f'Hive: could not read {name}: {ex}')
        return {}, {}

    if looks_encrypted(frames):
        logfunc(f'Hive: every frame of {name} failed its own CRC while its keys '
                f'read cleanly, which is how an encrypted box reads. '
                f'{len(frames)} key(s) recovered; the values are not decoded.')
        return {}, {}

    # Why the walk ended before the end of the file, if it did. A truncated
    # frame has no CRC to check, so it is not a checksum failure and is not
    # reported as one, and a frame length the format cannot hold stops the walk
    # without producing a frame at all.
    truncated = next((f for f in frames if f['truncated']), None)
    failed = next((f for f in frames if not f['crc_ok'] and not f['truncated']), None)
    if truncated is not None:
        logfunc(f'Hive: frame at offset {truncated["offset"]} of {name} is cut '
                f'short: it declares {truncated["length"]} bytes and '
                f'{size - truncated["offset"]} are present; stopping there')
    elif failed is not None:
        logfunc(f'Hive: frame at offset {failed["offset"]} of {name} failed its '
                f'own CRC, stopping there')
    else:
        read_to = sum(f['length'] for f in frames)
        if read_to != size:
            logfunc(f'Hive: {name} stopped reading at offset {read_to} of {size}: '
                    f'what follows does not begin a frame this format can hold')

    unreadable = [f for f in frames if f['error'] and f['crc_ok']]
    if unreadable:
        logfunc(f'Hive: {len(unreadable)} value(s) in {name} could not be '
                f'decoded; the rest of the box was still read')

    # This module keeps the contract the artifact modules were written against:
    # a deleted key stays in live with a value of None, and a deletion counts as
    # a supersession of the key it removes. hive_parser.live_entries models what
    # the app would read instead, which drops the key. The two differ only for a
    # box that holds a deletion.
    live, earlier = {}, {}
    for f in frames:
        if f['key'] is None or not f['crc_ok']:
            continue
        if f['error'] is not None and not f['deleted']:
            continue
        if f['key'] in live:
            earlier[f['key']] = earlier.get(f['key'], 0) + 1
        live[f['key']] = None if f['deleted'] else f['value']
    return live, earlier
