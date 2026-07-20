# pylint: disable=W0718
__artifacts_v2__ = {
    "get_quicksearch": {
        "name": "Google Quick Search Queries",
        "description": "Search query sessions from the Google Search widget / Assistant (Google Now)",
        "author": "",
        "creation_date": "2020-03-22",
        "last_update_date": "2020-03-22",
        "requirements": "none",
        "category": "Google Now & QuickSearch",
        "notes": "",
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

import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor, check_in_embedded_media


def _read_unix_time(value):
    if value in (0, None, ''):
        return ''
    try:
        return datetime.datetime.fromtimestamp(float(value), datetime.timezone.utc)
    except (ValueError, OverflowError, TypeError, OSError):
        return ''


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
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if '/mirror/' in file_found.replace('\\', '/') or os.path.isdir(file_found):
            continue
        source_path = os.path.dirname(file_found)
        try:
            with open(file_found, 'rb') as f:
                values, _ = blackboxprotobuf.decode_message(f.read())
        except Exception:
            continue
        session_type, queries, mp3_data = _parse_session(values)
        response = ''
        if mp3_data:
            name = os.path.splitext(os.path.basename(file_found))[0] + '.mp3'
            response = check_in_embedded_media(file_found, mp3_data, name,
                                               force_type='audio/mpeg', force_extension='mp3')
        data_list.append((_read_unix_time(os.path.getmtime(file_found)), session_type,
                          ', '.join(queries), response, context.get_relative_path(file_found)))

    data_headers = (('File Timestamp', 'datetime'), 'Type', 'Queries', ('Response', 'media'), 'Source File')
    return data_headers, data_list, context.get_relative_path(source_path)
