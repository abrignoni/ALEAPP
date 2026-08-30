__artifacts_v2__ = {
    "mibrowser_history": {
        "name": "Mi Browser - History",
        "description": "Rows from the history table of the browser's browser2.db, each a page "
                       "with its title, address, visit count and the recorded times",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Mi Browser",
        "notes": "com.mi.globalbrowser is the browser shipped on Xiaomi devices. date and "
                 "created are Unix milliseconds. Visits is the table's own counter, so one row "
                 "can stand for several visits and the row count is not a count of page views. "
                 "The user_entered column, reported here under that name, held 0 on "
                 "every row of the corpus below, so it separates nothing there; "
                 "it is kept because another value would. The same "
                 "database holds a historysync table with more rows, 342 against 247 here, but "
                 "it is a sync mirror rather than a separate record: its deleted column was 0 on "
                 "every row and both tables held the same 214 distinct addresses with none "
                 "present in only one of them, so reporting it as well would repeat this "
                 "artifact's rows and it is not read. The bookmarks and bookmarks2 tables each "
                 "held a single row, the root folder, with no saved bookmark, and "
                 "preload_website_list holds 249 addresses the application ships rather than "
                 "ones the user visited; neither is reported.",
        "paths": ('*/com.mi.globalbrowser/databases/browser2.db*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | com.mi.globalbrowser | 247 rows",
        },
    },
    "mibrowser_searches": {
        "name": "Mi Browser - Searches and Top Sites",
        "description": "Rows from the mostvisited table of browser2.db, each carrying a title "
                       "and an address with a recorded date, the titles being search terms where "
                       "the row's type says search",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Mi Browser",
        "notes": "The table is named mostvisited but its type column distinguishes the rows: on "
                 "the corpus below 39 of 40 rows had type search and one had type website. On "
                 "the search rows the Title column holds the term that was searched for and the "
                 "address is the corresponding search engine request, so those rows record what "
                 "was searched rather than a page that was visited repeatedly. Type (as stored) "
                 "carries the value so the two kinds stay distinguishable. date is Unix "
                 "milliseconds; which event it records, whether first or most recent, is not "
                 "established, so the column is named for the field. Sub Title, Doc Type and Ads "
                 "Info are columns the table carries for served content; all three were empty on "
                 "every row below, so nothing on this corpus came from a served list, and they "
                 "are kept because a populated value would show that a row did. Web URL "
                 "was empty on every row below as well, the URL column carrying the "
                 "address on all of them.",
        "paths": ('*/com.mi.globalbrowser/databases/browser2.db*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | com.mi.globalbrowser | 40 rows",
        },
    },
    "mibrowser_downloads": {
        "name": "Mi Browser - Downloads",
        "description": "Rows from the downloadmanagement table of browser2.db, each a file the "
                       "browser downloaded with the address it came from, the page that referred "
                       "it and where it was written",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Mi Browser",
        "notes": "createtime, update_time and ordertime are Unix milliseconds. Local URI is the "
                 "path the file was written to on the device, so it can be looked for there, and "
                 "Referer is the page the download was started from, which the history table "
                 "does not record. Status and the two size columns are reported as stored; no "
                 "source for the status code list was located, and on the corpus below the one "
                 "row had a status of 3 with the downloaded size equal to the total size. "
                 "Current Download Size (as stored) holds the per-part progress string the "
                 "column carries rather than a single number. One row was present on the corpus "
                 "below, so this artifact is exercised but only against a single download. "
                 "Download ID was empty on that row, the table's own row id being the "
                 "only identifier present.",
        "paths": ('*/com.mi.globalbrowser/databases/browser2.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | com.mi.globalbrowser | 1 row",
        },
    },
}

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records

SIDECARS = ('-wal', '-shm', '-journal')


def _databases(context):
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or file_found.endswith(SIDECARS):
            continue
        if os.path.basename(file_found) == 'browser2.db':
            found.append(file_found)
    return found


def _ms(value):
    return convert_unix_ts_to_utc(value / 1000) if value else ''


@artifact_processor
def mibrowser_history(context):
    data_list = []
    source_paths = []
    for db_path in _databases(context):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT date, created, title, url, visits, user_entered, _id
            FROM history ORDER BY date DESC
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for date, created, title, url, visits, entered, row_id in rows:
            data_list.append((
                _ms(date), _ms(created), title or '', url or '',
                visits if visits is not None else '',
                entered if entered is not None else '',
                row_id if row_id is not None else '',
            ))
    data_headers = (
        ('Date', 'datetime'),
        ('Created', 'datetime'),
        'Title',
        'URL',
        'Visits',
        'user_entered (as stored)',
        'Row ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def mibrowser_searches(context):
    data_list = []
    source_paths = []
    for db_path in _databases(context):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT date, title, type, url, web_url, sub_title, doc_type, ads_info, _id
            FROM mostvisited ORDER BY date DESC
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for date, title, kind, url, web_url, sub_title, doc_type, ads, row_id in rows:
            data_list.append((
                _ms(date), title or '', kind or '', url or '', web_url or '',
                sub_title or '', doc_type or '', ads or '',
                row_id if row_id is not None else '',
            ))
    data_headers = (
        ('Date', 'datetime'),
        'Title',
        'Type (as stored)',
        'URL',
        'Web URL',
        'Sub Title',
        'Doc Type (as stored)',
        'Ads Info (as stored)',
        'Row ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def mibrowser_downloads(context):
    data_list = []
    source_paths = []
    for db_path in _databases(context):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT createtime, update_time, ordertime, filename, url, referer, localuri,
                   mimetype, totalsize, downloadedsize, currentdownloadsize, status,
                   useragent, download_id, _id
            FROM downloadmanagement ORDER BY createtime DESC
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            (created, updated, ordered, filename, url, referer, local_uri, mimetype,
             total, downloaded, current, status, agent, download_id, row_id) = row
            data_list.append((
                _ms(created), _ms(updated), _ms(ordered), filename or '', url or '',
                referer or '', local_uri or '', mimetype or '',
                total if total is not None else '',
                downloaded if downloaded is not None else '',
                current or '',
                status if status is not None else '',
                agent or '',
                download_id if download_id is not None else '',
                row_id if row_id is not None else '',
            ))
    data_headers = (
        ('Create Time', 'datetime'),
        ('Update Time', 'datetime'),
        ('Order Time', 'datetime'),
        'File Name',
        'URL',
        'Referer',
        'Local URI',
        'MIME Type',
        'Total Size',
        'Downloaded Size',
        'Current Download Size (as stored)',
        'Status (as stored)',
        'User Agent',
        'Download ID',
        'Row ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)
