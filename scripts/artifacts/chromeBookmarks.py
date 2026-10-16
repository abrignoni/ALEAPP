# pylint: disable=W0612
__artifacts_v2__ = {
    "get_chromeBookmarks": {
        "name": "Bookmarks",
        "description": "Parses bookmark and folder entries under each root of Chromium based browser Bookmarks files, including descendants and their immediate parent and ancestor context.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2020-03-20",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Rows follow source, root and child-array depth-first order, not chronology. "
                 "Folder rows and duplicate occurrences are retained. Added Date keeps the existing "
                 "1601-epoch microsecond conversion; invalid dates remain blank with the raw value. "
                 "Stored IDs are input-local context and do not establish ownership or browser visits. "
                 "Integers outside SQLite range retain their decimal text for export. "
                 "Canonical alias state conflicts, broader profile coverage and sync semantics remain "
                 "unresolved. Source File appears only for actual combined row origins.",
        "paths": ('*/app_chrome/Default/Bookmarks*', '*/app_sbrowser/Default/Bookmarks*', '*/app_opera/Bookmarks*', '*/app_webview/Default/Bookmarks*'),
        "output_types": "standard",
        "artifact_icon": "bookmark",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.android.chrome vc 616710133, com.microsoft.emmx vc 259210005, com.opera.browser vc 1908324306 | 0 rows",
            "samsungs20_a13": "Android 13 | com.microsoft.emmx vc 365012523 | 4 rows",
            "sharon_a14": "Android 14 | com.android.chrome vc 653310333 | 7 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.chrome vc 573513033 | 0 rows",
        },
    }
}

import datetime
import json
import os

from scripts.ilapfuncs import logfunc, artifact_processor
from scripts.artifacts.chrome import get_browser_name
from scripts.artifacts.storagePathViews import unique_files


def _bookmark_children(node, relative, location):
    """Only arrays contain descendant occurrences; malformed metadata is not iterable."""
    children = node.get('children')
    if children is None:
        return []
    if not isinstance(children, list):
        logfunc(f'Bookmarks: non-list children in {relative[:200]} at {location[:200]}')
        return []
    return children


def _bookmark_nodes(data, relative):
    """Yield dictionary child occurrences in structural preorder without recursion."""
    if not isinstance(data, dict) or not isinstance(data.get('roots'), dict):
        logfunc(f'Bookmarks: unsupported roots object in {relative[:200]}')
        return
    for root_index, (root_key, root) in enumerate(data['roots'].items()):
        location = f'roots[{root_index}]'
        if not isinstance(root, dict):
            logfunc(f'Bookmarks: non-object root in {relative[:200]} at {location}')
            continue
        ancestors = [root.get('name', '')]
        children = _bookmark_children(root, relative, location)
        stack = [(children[index], root, ancestors, f'{location}.children[{index}]')
                 for index in range(len(children) - 1, -1, -1)]
        while stack:
            node, parent, names, occurrence = stack.pop()
            if not isinstance(node, dict):
                logfunc(f'Bookmarks: non-object child in {relative[:200]} at {occurrence[:200]}')
                continue
            yield root_key, node, parent, names, occurrence
            descendants = _bookmark_children(node, relative, occurrence)
            next_names = names + [node.get('name', '')]
            for index in range(len(descendants) - 1, -1, -1):
                stack.append((descendants[index], node, next_names,
                              f'{occurrence}.children[{index}]'))


def _bookmark_raw_value(value):
    """Keep oversized JSON integers losslessly exportable through SQLite TEXT."""
    if isinstance(value, int) and not -(2 ** 63) <= value < 2 ** 63:
        return str(value)
    return value


def _bookmark_date(raw, relative, location):
    """Retain the existing conversion for accepted values, including zero."""
    try:
        return datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=int(raw))
    except (TypeError, ValueError, OverflowError):
        logfunc(f'Bookmarks: invalid date_added in {relative[:200]} at {location[:200]}; date left blank')
        return ''


@artifact_processor
def get_chromeBookmarks(context):
    files_found = unique_files(context)
    all_data = []
    sources = {}
    data_headers = [('Added Date', 'datetime'), 'Added Date (as stored)', 'URL', 'Name',
                    'Parent', 'Type', 'Browser Name', 'Folder Path (names)',
                    'Bookmark ID (as stored)', 'Parent ID (as stored)', 'Root Folder Key']

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Bookmarks':  # skip -journal and other files
            continue
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data

        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        relative = context.get_relative_path(file_found)
        try:
            with open(file_found, "r", encoding='utf-8') as handle:
                data = json.load(handle)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
            logfunc(f'Bookmarks: unavailable JSON in {relative[:200]} ({type(error).__name__}); skipping source')
            continue

        for root_key, node, parent, names, location in _bookmark_nodes(data, relative):
            raw_date = node.get('date_added', '')
            added_date = _bookmark_date(raw_date, relative, location)
            all_data.append((added_date, _bookmark_raw_value(raw_date),
                             _bookmark_raw_value(node.get('url', '')),
                             _bookmark_raw_value(node.get('name', '')),
                             _bookmark_raw_value(parent.get('name', '')),
                             _bookmark_raw_value(node.get('type', '')), browser_name,
                             json.dumps(names, ensure_ascii=False),
                             _bookmark_raw_value(node.get('id')),
                             _bookmark_raw_value(parent.get('id')), root_key, relative))
            sources[file_found] = None

    if len(sources) > 1:
        data_headers.append('Source File')
    else:
        all_data = [row[:-1] for row in all_data]
    return data_headers, all_data, '\n'.join(sources)
