# pylint: disable=W0718
__artifacts_v2__ = {
    "get_quicksearch": {
        "name": "Google Quick Search Queries",
        "description": "Query text and an embedded audio blob read from the Google app session files (com.google.android.googlequicksearchbox/app_session/*.binarypb), with the modification time the extraction recorded for each file. What causes the app to write a session file is not established.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2020-03-22",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Google Now & QuickSearch",
        "notes": "File Modified Time is the modification time the extraction recorded for the session file "
                 "as an epoch value, shown in UTC: the extended timestamp field (0x5455) of a zip member, the "
                 "mtime of a tar member, or the file's own modification time when the input is a folder. It "
                 "is blank when the extraction recorded no such value. Archive Time Modified (No Zone) is "
                 "filled only in that case, for a zip member, with the date and time in the member's zip "
                 "directory entry, shown as stored. A zip directory entry records no time zone, so that "
                 "reading is not converted and which zone it is in is not established. The time of the "
                 "staged copy the tool extracts is not used. No time is read from inside a session file. "
                 "On the registered images checked on 2026-10-04, both matched zip members on "
                 "russell_pixel6a_a13 carried the extended timestamp, and the zip directory reading was "
                 "4 hours earlier than it to within 1 second; the one matched member on sharon_a14 "
                 "carried none. Extraction and acquisition handling can disturb file timestamps, so "
                 "validate the value against other sources.",
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


def _recorded_times(seeker, file_found):
    """Return (epoch modification time as UTC, zone-less zip directory time as stored).

    The staged copy's own time is not used: for a zip member the seeker sets it from the
    member's zone-less date and time read in the examiner machine's zone.
    """
    info = seeker.file_infos.get(file_found) if seeker else None
    if not info:
        return '', ''
    if info.modification_date:
        try:
            return datetime.datetime.fromtimestamp(
                float(info.modification_date), datetime.timezone.utc), ''
        except (ValueError, OverflowError, OSError, TypeError):
            return '', ''
    zip_file = getattr(seeker, 'zip_file', None)
    # A name stored more than once with different content is staged from a
    # chosen entry, which getinfo() does not necessarily return.
    if zip_file is None or info.source_path in getattr(seeker, '_chosen', {}):
        return '', ''
    try:
        stored = zip_file.getinfo(info.source_path).date_time
    except KeyError:
        return '', ''
    return '', '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*stored)


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
        modified, modified_as_stored = _recorded_times(seeker, file_found)
        data_list.append((modified, modified_as_stored, session_type,
                          ', '.join(queries), response, context.get_relative_path(file_found)))

    data_headers = (('File Modified Time', 'datetime'), 'Archive Time Modified (No Zone)', 'Type', 'Queries',
                    ('Response', 'media'), 'Source File')
    return data_headers, data_list, context.get_relative_path(source_path)
