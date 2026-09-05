__artifacts_v2__ = {
    "solid_explorer_recent_files": {
        "name": "Solid Explorer Recent Files",
        "description": "Files Solid Explorer recorded as recently opened, with the time of each",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Solid Explorer",
        "sample_data": {
            "emu_a15_oss_v14": "Solid Explorer 3.5.20 | 2 rows",
        },
        "notes": "One row per row of the recent_files table in "
                 "pl.solidexplorer2/databases/explorer.db. Opened is Unix milliseconds and is "
                 "reported as UTC. Path is the full path the app recorded, as stored. "
                 "On the tested device a row appeared when a file was opened from the app and "
                 "was handled by one of Solid Explorer's own built-in viewers, the text editor "
                 "and the image viewer. Whether a file opened into a different application is "
                 "recorded here was not established, so the absence of a row is not evidence a "
                 "file was never opened. "
                 "The path is what the app wrote and is not resolved against the extraction, so "
                 "a row is evidence the app opened that path, not that the file is still there.",
        "paths": ('*/pl.solidexplorer2/databases/explorer.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
    "solid_explorer_bookmarks": {
        "name": "Solid Explorer Bookmarks",
        "description": "Bookmarked locations in Solid Explorer, with how often each was opened",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Solid Explorer",
        "sample_data": {
            "emu_a15_oss_v14": "Solid Explorer 3.5.20 | 2 rows",
        },
        "notes": "One row per row of the bookmarks table in "
                 "pl.solidexplorer2/databases/explorer.db. Name is the label shown in the app's "
                 "drawer and Path is the location it points at. "
                 "Times Opened is the hitcount column and counts uses of the bookmark. That was "
                 "measured rather than assumed: on the tested device a bookmark was added and "
                 "then opened from the drawer twice, and its hitcount went 0, then 1, then 2, "
                 "while a second bookmark that was never opened stayed at 0. A bookmark can "
                 "therefore be present and unused, which the column separates. "
                 "The app ships with a bookmark already present, so a row is not by itself "
                 "evidence anyone created it; on the tested device the Download bookmark was "
                 "there before anything was done and is the one that stayed at 0. "
                 "File System is the id of the row in the file_systems table the bookmark "
                 "belongs to, which is the link the database itself records, and is what "
                 "separates a bookmark on local storage from one on a remote connection. "
                 "Position is reported as stored.",
        "paths": ('*/pl.solidexplorer2/databases/explorer.db*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
    },
    "solid_explorer_searches": {
        "name": "Solid Explorer Searches",
        "description": "Search terms submitted in Solid Explorer",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Solid Explorer",
        "sample_data": {
            "emu_a15_oss_v14": "Solid Explorer 3.5.20 | 4 rows",
        },
        "notes": "One row per row of the search_suggestions and suggestions tables in "
                 "pl.solidexplorer2/databases/explorer.db. Table says which of the two a row "
                 "came from. Neither table carries a timestamp, so these terms cannot be placed "
                 "in time from this store. "
                 "Search Term is the literal string submitted. It is worth reading literally: on "
                 "the tested device the app did not clear the search box between searches, so "
                 "two of the four stored terms are the previous term with the next one appended. "
                 "That is what the app recorded and it is reported unchanged rather than split. "
                 "Counter is reported as stored. It read 0 on every row of the tested device, "
                 "where four terms were submitted and none of them incremented it past zero. "
                 "Type belongs to the suggestions table only and is blank for rows "
                 "from search_suggestions. The suggestions table was empty on the tested device.",
        "paths": ('*/pl.solidexplorer2/databases/explorer.db*',),
        "output_types": "standard",
        "artifact_icon": "search",
    },
    "solid_explorer_connections": {
        "name": "Solid Explorer Connections",
        "description": "Storage connections Solid Explorer holds, local and remote",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Solid Explorer",
        "sample_data": {
            "emu_a15_oss_v14": "Solid Explorer 3.5.20 | 1 rows",
        },
        "notes": "One row per row of the file_systems table in "
                 "pl.solidexplorer2/databases/explorer.db. This is where a remote connection "
                 "lives: the app supports FTP, SFTP, SMB, WebDAV and cloud accounts, and each "
                 "one adds a row carrying its server, port, user name and remote path. "
                 "Password Stored reports only whether the password column holds a value. The "
                 "password itself is not printed. "
                 "Connection Type and Connection Mode are reported as stored, being undocumented "
                 "in anything published. "
                 "The tested device had only the built-in local storage entry. On that single row "
                 "Server, User, Charset and Extra were empty, Password Stored read No, Port and "
                 "both Connection columns read 0, and Remote Path read a single slash. Those "
                 "columns are reported because they are the substance of this table "
                 "on a device that has a remote connection configured, which is the case worth "
                 "having. Package Name on that row read as a local storage identifier rather "
                 "than an Android package.",
        "paths": ('*/pl.solidexplorer2/databases/explorer.db*',),
        "output_types": "standard",
        "artifact_icon": "server",
    },
    "solid_explorer_folders_viewed": {
        "name": "Solid Explorer Folders Viewed",
        "description": "Folders Solid Explorer holds display settings for",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Solid Explorer",
        "sample_data": {
            "emu_a15_oss_v14": "Solid Explorer 3.5.20 | 4 rows",
        },
        "notes": "One row per row of the dirinfo table in "
                 "pl.solidexplorer2/databases/explorer.db. The table exists to remember how a "
                 "folder should be displayed, so a row means the app kept settings for that "
                 "folder rather than that someone deliberately configured it. "
                 "A row is not written for every folder opened, which was tested rather than "
                 "assumed: a folder was opened twice from a bookmark during the session that "
                 "built the sample and gained no row, while four other folders had rows "
                 "throughout. So a row shows the app held settings for that folder, and the "
                 "absence of one is not evidence the folder was never opened. No timestamp is "
                 "stored either, so nothing here can be placed in time. "
                 "Sort Mode, View Mode, View Scale and Grouped are the display settings and are "
                 "reported as stored. Hidden Files Shown reports whether hidden files were "
                 "displayed in that folder; it read No on every row of the tested device, "
                 "where the setting was never turned on, and is reported because it "
                 "separates folders on a device where it was. File System is the id of the "
                 "file_systems row the folder belongs to, which is the link the database "
                 "itself records.",
        "paths": ('*/pl.solidexplorer2/databases/explorer.db*',),
        "output_types": "standard",
        "artifact_icon": "folder",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, \
    get_sqlite_db_records, null_absent_columns
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/explorer.db'


def _db_files(context):
    # The pattern also matches the -journal sidecar, which is not opened directly.
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    """A Unix millisecond value as UTC, blank when absent or zero."""
    if not value:
        return ''
    try:
        value = int(value)
        if value <= 0:
            return ''
        return convert_unix_ts_to_utc(value // 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _rows(context, query, build, headers):
    """Run one query over every explorer.db and build the rows with `build`."""
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, null_absent_columns(db_path, query))
        for record in records:
            data_list.append(build(record) + (context.get_relative_path(db_path),))
        if records and db_path not in sources:
            sources.append(db_path)
    return headers, data_list, '\n'.join(sources)


@artifact_processor
def solid_explorer_recent_files(context):
    query = 'SELECT time, path FROM recent_files ORDER BY time DESC'
    headers = (('Opened', 'datetime'), 'Path', 'Source File')
    return _rows(context, query, lambda r: (_ms(r[0]), r[1] or ''), headers)


@artifact_processor
def solid_explorer_bookmarks(context):
    query = '''SELECT name, path, hitcount, file_system, parent_id, position
               FROM bookmarks ORDER BY hitcount DESC, name'''
    headers = ('Name', 'Path', 'Times Opened', 'File System', 'Parent Path',
               'Position', 'Source File')
    return _rows(context, query,
                 lambda r: (r[0] or '', r[1] or '', r[2], r[3], r[4] or '', r[5]),
                 headers)


@artifact_processor
def solid_explorer_searches(context):
    query = '''SELECT suggestion, counter, '' AS type, 'search_suggestions' AS src
               FROM search_suggestions
               UNION ALL
               SELECT suggestion, counter, type, 'suggestions' AS src
               FROM suggestions'''
    headers = ('Search Term', 'Counter (as stored)', 'Type (as stored)', 'Table', 'Source File')
    return _rows(context, query,
                 lambda r: (r[0] or '', r[1], r[2] if r[2] is not None else '', r[3]),
                 headers)


@artifact_processor
def solid_explorer_connections(context):
    query = '''SELECT name, server, port, user, path, package_name, conn_type, conn_mode,
                      password, charset, extra
               FROM file_systems ORDER BY name'''
    headers = ('Name', 'Server', 'Port', 'User', 'Remote Path', 'Package Name',
               'Connection Type (as stored)', 'Connection Mode (as stored)',
               'Password Stored', 'Charset', 'Extra', 'Source File')
    return _rows(context, query,
                 lambda r: (r[0] or '', r[1] or '', r[2], r[3] or '', r[4] or '',
                            r[5] or '', r[6], r[7], 'Yes' if r[8] else 'No',
                            r[9] or '', r[10] or ''),
                 headers)


@artifact_processor
def solid_explorer_folders_viewed(context):
    query = '''SELECT file_id, file_system, sort_mode, view_mode, view_scale, grouped, hidden
               FROM dirinfo ORDER BY file_id'''
    headers = ('Folder', 'File System', 'Sort Mode (as stored)', 'View Mode (as stored)',
               'View Scale (as stored)', 'Grouped', 'Hidden Files Shown', 'Source File')
    return _rows(context, query,
                 lambda r: (r[0] or '', r[1], r[2], r[3], r[4],
                            'Yes' if r[5] else 'No', 'Yes' if r[6] else 'No'),
                 headers)
