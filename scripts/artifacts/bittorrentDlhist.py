__artifacts_v2__ = {
    "get_bittorrentDlhist": {
        "name": "bittorrentDlhist",
        "description": "Records of BitTorrent dlhistory config files, one row per entry of each file's records list, with the a, n and s values of each entry.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-03-26",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "BitTorrent",
        "notes": "Each file is bencoded and holds a records list. Every entry of that list is reported in file order. "
                 "The columns a, n and s (as stored) hold the entry's values under those keys as the file stores them; "
                 "what the app records in each key is not sourced here. "
                 "The first column is the a value read as Unix milliseconds and shown in UTC; that reading is not sourced, "
                 "and the column is blank when a is absent or is not a number in the datetime range. "
                 "No registered corpus holds a dlhistory file, so the module was checked on a constructed bencoded file "
                 "only (three records, an empty records list and a record with no a key).",
        "paths": ('*/dlhistory*.config.bak', '*/dlhistory*.config'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "download",
    }
}

import os
import bencoding
import datetime

from scripts.ilapfuncs import artifact_processor


def timestampcalc(timevalue):
    try:
        timestamp = datetime.datetime.fromtimestamp(int(timevalue)/1000, datetime.timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''
    return timestamp


def _stored(value):
    if value is None:
        return ''
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return str(value)


@artifact_processor
def get_bittorrentDlhist(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue

        with open(file_found, 'rb') as f:
            decodedDict = bencoding.bdecode(f.read())

        if not isinstance(decodedDict, dict):
            continue
        relative_path = context.get_relative_path(file_found)
        if relative_path not in source_paths:
            source_paths.append(relative_path)

        for key, value in decodedDict.items():
            if key == b'records' and isinstance(value, list):
                for x in value:
                    if not isinstance(x, dict):
                        continue
                    a_value = x.get(b'a')
                    data_list.append((
                        timestampcalc(a_value),
                        _stored(a_value),
                        _stored(x.get(b'n')),
                        _stored(x.get(b's')),
                        relative_path))

    data_headers = (
        ('a read as Unix milliseconds', 'datetime'),
        'a (as stored)',
        'n (as stored)',
        's (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(source_paths)
