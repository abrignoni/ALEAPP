# pylint: disable=W0718
__artifacts_v2__ = {
    "get_quicksearch": {
        "name": "Google Quick Search Queries",
        "description": "Query text and an embedded audio blob read from the Google app session files (com.google.android.googlequicksearchbox/app_session/*.binarypb), with the modification time the extraction recorded for each file. What causes the app to write a session file is not established.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2020-03-22",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Google Now & QuickSearch",
        "notes": "File Modified Time is the modification time the tool reads from the input for the file as a "
                 "UTC time, such as from a tar header, a zip entry's NTFS (0x000a) or extended timestamp "
                 "(0x5455) field, or the file system of a disk image. When the tool reads no UTC time, File "
                 "Modified Time is blank and Modified (no zone, as stored) shows the date and time the input "
                 "holds, with no zone conversion. That is the case for a FAT directory entry, an exFAT "
                 "directory entry (its stored UTC offset is not applied or shown here) and a zip entry with "
                 "only its DOS date and time. Which zone such a reading is in is not established. Both columns"
                 " are blank when the input holds neither, and a recorded time of 0 is treated as no time. For"
                 " a folder or single-file input File Modified Time is the time the operating system reports "
                 "for that file on the examiner's machine, including any conversion it applied, and whatever "
                 "copied the file there may have set it. The staged copy's own time is not reported. No time "
                 "is read from inside a session file. On the registered images checked on 2026-10-04, both "
                 "matched zip members on russell_pixel6a_a13 carried the extended timestamp, and the zip "
                 "directory reading was 4 hours earlier than it to within 1 second; the one matched member on "
                 "sharon_a14 carried none and records the NTFS field instead, and on a run of 2026-10-23 the "
                 "zip directory reading was 4 hours earlier than it to within 1 second. Extraction and "
                 "acquisition handling can disturb file timestamps, so validate the value against other "
                 "sources.",
        "paths": ('*/com.google.android.googlequicksearchbox/app_session/*.binarypb',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "sharon_a14": "Android 14 | com.google.android.googlequicksearchbox vc 301381725 | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.google.android.googlequicksearchbox vc 301246250 | 2 rows",
        },
    }
}

import datetime
import os
import struct

from scripts.ilapfuncs import decode_protobuf

from scripts.ilapfuncs import artifact_processor, check_in_embedded_media
from scripts.artifacts.storagePathViews import unique_files


def _recorded_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(float(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _usable(value):
    """Whether a recorded time is a nonzero, finite number."""
    return isinstance(value, (int, float)) and value != 0 and value == value and abs(value) != float('inf')


def _file_times(seeker, path):
    """(UTC seconds, reading with no zone) the input records for a staged file.

    The staged copy's own time is not used: for a FAT, exFAT or DOS-only zip reading it is
    that reading placed in the examiner's time zone.
    """
    infos = getattr(seeker, 'file_infos', None) or {}
    windows = str(path).replace('/', '\\')
    bare = windows.removeprefix('\\\\?\\')
    info = next((infos[name] for name in (str(path), windows, bare, '\\\\?\\' + bare)
                 if name in infos), None)
    times = getattr(info, 'times', None)
    modified = getattr(times, 'modified', None)
    if _usable(modified):
        return modified, ''
    # a reading with no zone comes before the older field, which is never read as its UTC time
    reading = getattr(times, 'modified_no_zone', None)
    if reading:
        return None, reading
    modified = getattr(info, 'modification_date', None)
    if _usable(modified):
        return modified, ''
    return None, ''


def _get_search_query_from_blob(data):
    term = 'com.google.android.apps.gsa.shared.search.Query'.encode('utf-16')[2:]
    query = ''
    pos = data.find(term + b'\0\0')
    if pos > 0:
        if pos % 4:
            pos += 2
        pos += 96  # skip term
        if data[pos: pos + 2] != b'\x03\x00':
            pos += 20
            str_len = struct.unpack('<I', data[pos:pos + 4])[0]
            if str_len > 0:
                pos += 4
                query = data[pos: pos + str_len * 2]
                if data[pos + str_len: pos + str_len + 1] == b'\0':  # utf8
                    query = query[:str_len].decode('utf8', 'ignore')
                else:
                    query = query.decode('utf-16', 'backslashreplace')
    return query


def _parse_session(values):
    session_type = values.get('3', b'').decode('utf8', 'ignore')
    session_queries = []
    main_query = ''
    mp3_data = b''

    try:
        item = values['132269847']['1']['2']
        if isinstance(item, bytes):
            main_query = item.decode('utf8', 'backslashreplace')
    except (KeyError, ValueError, TypeError):
        pass

    try:
        items = values['132269847']['2']
        if isinstance(items, list):
            for item in items:
                if isinstance(item, bytes):
                    term = _get_search_query_from_blob(item)
                    if term:
                        session_queries.append(term)
    except (KeyError, ValueError, TypeError):
        pass

    if main_query and main_query not in session_queries:
        session_queries.append(main_query)
    session_queries = [f'"{x}"' for x in session_queries]

    try:
        data = values['132269388']['1']
        if isinstance(data, bytes):
            mp3_data = data
    except (KeyError, ValueError, TypeError):
        pass

    return session_type, session_queries, mp3_data


@artifact_processor
def get_quicksearch(context):
    files_found = unique_files(context)
    seeker = context.get_seeker()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if '/mirror/' in file_found.replace('\\', '/') or os.path.isdir(file_found):
            continue
        source_path = os.path.dirname(file_found)
        try:
            with open(file_found, 'rb') as f:
                values, _ = decode_protobuf(f.read())
        except Exception:
            continue
        session_type, queries, mp3_data = _parse_session(values)
        response = ''
        if mp3_data:
            name = os.path.splitext(os.path.basename(file_found))[0] + '.mp3'
            response = check_in_embedded_media(file_found, mp3_data, name,
                                               force_type='audio/mpeg', force_extension='mp3')
        recorded, modified_as_stored = _file_times(seeker, file_found)
        modified = _recorded_utc(recorded)
        data_list.append((modified, modified_as_stored, session_type,
                          ', '.join(queries), response, context.get_relative_path(file_found)))

    data_headers = (('File Modified Time', 'datetime'), 'Modified (no zone, as stored)', 'Type', 'Queries',
                    ('Response', 'media'), 'Source File')
    return data_headers, data_list, context.get_relative_path(source_path)
