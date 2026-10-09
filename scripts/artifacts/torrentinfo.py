# pylint: disable=W0718
__artifacts_v2__ = {
    "get_torrentinfo": {
        "name": "torrentinfo",
        "description": "Parses .torrent files: the file path, the info hash (SHA-1 of the "
                       "bencoded info dictionary, computed by this parser), the top-level keys "
                       "other than pieces as text, the keys of the info dictionary other than "
                       "pieces as text, and the path of each file a multi-file torrent lists.",
        "author": "@abrignoni",
        "creation_date": "2023-03-26",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "BitTorrent",
        "notes": "One row per .torrent file read. Each file a multi-file torrent lists is shown "
                 "once, as 'Files:' followed by the components of its path list joined with "
                 "'/'. A value that is a number is shown as stored; a list or dictionary value "
                 "is shown with its members joined by commas. The top-level creation date is "
                 "read as Unix seconds and shown in UTC, or as stored where it does not "
                 "convert; no source for that unit is cited here. The info hash is computed "
                 "after decoding and re-encoding the info dictionary; that the re-encoded bytes "
                 "equal the bytes in the file was not established. A file that does not decode "
                 "as bencoding is named in the run log and produces no row.",
        "paths": ('*/*.torrent',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "download",
        "html_columns": ['Data'],
    }
}

import bencoding
import hashlib
import datetime
import os

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.html_safe import esc


def timestampcalc(timevalue):
    timestamp = (datetime.datetime.fromtimestamp(int(timevalue), datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp


def _text(value):
    """Bencoded value as text: bytes as UTF-8 (undecodable bytes as escapes), numbers as
    stored, lists and dictionaries with their members joined by commas."""
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='backslashreplace')
    if isinstance(value, (list, tuple)):
        return ', '.join(_text(item) for item in value)
    if isinstance(value, dict):
        return ', '.join(f'{_text(k)}: {_text(v)}' for k, v in value.items())
    return str(value)


@artifact_processor
def get_torrentinfo(context):
    files_found = context.get_files_found()

    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        relative = context.get_relative_path(file_found)

        try:
            with open(file_found, 'rb') as f:
                decodedDict = bencoding.bdecode(f.read())

            aggregate = ''
            try:
                infohash = hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest()
            except Exception:
                infohash = ''

            for key, value in decodedDict.items():
                if key == b'info' and isinstance(value, dict):
                    for x, y in value.items():
                        if x == b'pieces':
                            continue
                        if x == b'files' and isinstance(y, (list, tuple)):
                            for entry in y:
                                parts = entry.get(b'path', []) if isinstance(entry, dict) else entry
                                if not isinstance(parts, (list, tuple)):
                                    parts = [parts]
                                file = '/'.join(_text(part) for part in parts)
                                aggregate = aggregate + f'Files: {esc(file)} <br>'
                        else:
                            aggregate = aggregate + f'{esc(_text(x))}: {esc(_text(y))} <br>'
                elif key == b'pieces':
                    pass
                elif key == b'creation date':
                    try:
                        created = timestampcalc(value)
                    except (TypeError, ValueError, OverflowError, OSError):
                        created = _text(value)
                    aggregate = aggregate + f'creation date: {esc(created)} <br>'
                else:
                    aggregate = aggregate + f'{esc(_text(key))}: {esc(_text(value))} <br>'

            if file_found not in sources:
                sources.append(file_found)
            data_list.append((relative, infohash, aggregate))
        except Exception as e:
            logfunc(f'torrentinfo: could not read {relative}: {e}')

    data_headers = ('File', 'InfoHash', 'Data')
    return data_headers, data_list, '\n'.join(sources)
