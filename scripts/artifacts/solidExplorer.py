__artifacts_v2__ = {
    "solid_explorer_recent_files": {
        "name": "Solid Explorer Recent Files",
        "description": "Files Solid Explorer recorded as recently opened, with one stored time per path",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Solid Explorer",
        "sample_data": {
            "emu_a15_oss_v14": "Solid Explorer 3.5.20 | 2 rows",
        },
        "notes": "One row per row of the recent_files table in pl.solidexplorer2/databases/explorer.db. Opened is Unix milliseconds and is reported as UTC. Path is the full path the app recorded, as stored. The schema declares path UNIQUE, so the table holds at most one row per path and repeated opens of one path cannot each have a row. Whether the time is the first or the most recent open of a file opened more than once was not established. On the tested device a row appeared when a file was opened from the app and was handled by one of Solid Explorer's own built-in viewers, the text editor and the image viewer. Whether a file opened into a different application is recorded here was not established, so the absence of a row is not evidence a file was never opened. The path is what the app wrote and is not resolved against the extraction, so a row shows the app recorded that path, not that the file is still there.",
        "paths": ('*/pl.solidexplorer2/databases/explorer.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
    "solid_explorer_bookmarks": {
        "name": "Solid Explorer Bookmarks",
        "description": "Bookmarked locations in Solid Explorer, with the stored hitcount",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Solid Explorer",
        "sample_data": {
            "emu_a15_oss_v14": "Solid Explorer 3.5.20 | 2 rows",
        },
        "notes": "One row per row of the bookmarks table in pl.solidexplorer2/databases/explorer.db. Name is the label shown in the app's drawer and Path is the location it points at. The table also has a file_id column that is not reported. It equalled Path on both rows of the emu_a15_oss images v14 to v17, which hold a byte-identical explorer.db, and that does not show the two are equal on a remote file system. hitcount (as stored) is the hitcount column unchanged. On the tested device a bookmark was added and its drawer entry was then tapped twice. Its hitcount read 0, then 1, then 2. The other bookmark was not tapped in that session and stayed at 0. Tapping a bookmark in the drawer is the only action tested, so whether other ways of reaching the location change hitcount was not established, and a 0 does not show the location was never visited. On the tested device (Solid Explorer 3.5.20) the Download bookmark was already in the table at the first read of the database, before the test session added or tapped any bookmark, and it stayed at 0. How that row came to exist was not recorded, so a row is not by itself evidence that a user created the bookmark. File System is the file_system column as stored. On emu_a15_oss v14 to v17 it read 1 on both rows and the only file_systems row had rowid 1. The schema declares no key between the two tables, so the link is not established. That one row is the local storage entry, so whether this column separates local from remote bookmarks was not exercised. Position is reported as stored.",
        "paths": ('*/pl.solidexplorer2/databases/explorer.db*',),
        "output_types": "standard",
        "artifact_icon": "bookmark",
    },
    "solid_explorer_searches": {
        "name": "Solid Explorer Searches",
        "description": "Rows of Solid Explorer's search_suggestions and suggestions tables",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Solid Explorer",
        "sample_data": {
            "emu_a15_oss_v14": "Solid Explorer 3.5.20 | 4 rows",
        },
        "notes": "One row per row of the search_suggestions and suggestions tables in pl.solidexplorer2/databases/explorer.db. Table says which of the two a row came from. Neither table carries a timestamp, so these terms cannot be placed in time from this store. Suggestion (as stored) is the suggestion column of either table. What the suggestions table stores there is not established, because that table was empty. The search_suggestions terms are worth reading literally. On the tested device the first term was entered into a newly opened search box. Before the second and the third, a Back key and a tap on the search icon were sent, and the next term was entered without clearing the box. Each of those two stored terms is the previous stored term with the new text appended. Before the fourth, delete key presses were sent to the box first, and the stored term equals the text entered, as does the first. The screen was not captured between those steps, so what the box held is inferred from the stored strings. That is what the app recorded and it is reported unchanged rather than split. Counter (as stored) is the counter column unchanged. It read 0 on every row of the tested device, where four terms were submitted and none of them incremented it past zero. Type (as stored) belongs to the suggestions table only and is blank for rows from search_suggestions. The suggestions table was empty on the tested device.",
        "paths": ('*/pl.solidexplorer2/databases/explorer.db*',),
        "output_types": "standard",
        "artifact_icon": "search",
    },
    "solid_explorer_connections": {
        "name": "Solid Explorer Connections",
        "description": "Rows of Solid Explorer's file_systems table",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Solid Explorer",
        "sample_data": {
            "emu_a15_oss_v14": "Solid Explorer 3.5.20 | 1 rows",
        },
        "notes": "One row per row of the file_systems table in pl.solidexplorer2/databases/explorer.db. The table has server, port, user, password and path columns. That suggests a remote connection would be stored here, which was not exercised: the emu_a15_oss images v14 to v17, which hold a byte-identical explorer.db, have no remote row. Password Stored reports only whether the password column holds a value. The password itself is not printed. The table also has password_mode and flags columns that are not reported. Both read 0 on those images. Connection Type (as stored) and Connection Mode (as stored) are the conn_type and conn_mode columns unchanged; no source for their values was found. Those images hold one row, and its Name and Package Name read as local storage. On that single row Server, User, Charset and Extra were empty, Password Stored read No, Port and both Connection columns read 0, and Path read a single slash. Package Name on that row read as a local storage identifier rather than an Android package. The rowid of this table is not shown. File System in the Bookmarks and Folder Display Settings artifacts read 1 on those images, the rowid of this one row, but the schema declares no key between the tables, so that link is not established.",
        "paths": ('*/pl.solidexplorer2/databases/explorer.db*',),
        "output_types": "standard",
        "artifact_icon": "server",
    },
    "solid_explorer_folders_viewed": {
        "name": "Solid Explorer Folder Display Settings",
        "description": "Folders Solid Explorer holds display settings for",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Solid Explorer",
        "sample_data": {
            "emu_a15_oss_v14": "Solid Explorer 3.5.20 | 4 rows",
        },
        "notes": "One row per row of the dirinfo table in pl.solidexplorer2/databases/explorer.db. The table holds per-folder display settings, so a row means the app kept settings for that folder rather than that someone deliberately configured it. A row is not written for every folder opened, which was tested rather than assumed: the bookmark for a folder was tapped twice in the drawer during the session that built the sample, hitcount rose each time, and that folder gained no row, while four other folders had rows throughout. So a row shows the app held settings for that folder, and the absence of one is not evidence the folder was never opened. No timestamp is stored either, so nothing here can be placed in time. Sort Mode (as stored), View Mode (as stored) and View Scale (as stored) are the sort_mode, view_mode and view_scale columns unchanged. Grouped is the grouped column, shown as Yes for a non-zero value and No otherwise. Hidden (as stored) is the dirinfo.hidden column without boolean conversion or an interpretation of what it controls. It read 0 on all four rows of the emu_a15_oss images v14 to v17, which hold a byte-identical explorer.db. What the column controls is not established. Original parser and recorded sample observations credited to @AlexisBrignoni, Claude. File System is the file_system column as stored. On those images it read 1 on all four rows and the only file_systems row had rowid 1. The schema declares no key between the two tables, so the link is not established.",
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
    headers = ('Name', 'Path', 'hitcount (as stored)', 'File System', 'Parent Path',
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
    headers = ('Suggestion (as stored)', 'Counter (as stored)', 'Type (as stored)', 'Table', 'Source File')
    return _rows(context, query,
                 lambda r: (r[0] or '', r[1], r[2] if r[2] is not None else '', r[3]),
                 headers)


@artifact_processor
def solid_explorer_connections(context):
    query = '''SELECT name, server, port, user, path, package_name, conn_type, conn_mode,
                      password, charset, extra
               FROM file_systems ORDER BY name'''
    headers = ('Name', 'Server', 'Port', 'User', 'Path', 'Package Name',
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
               'View Scale (as stored)', 'Grouped', 'Hidden (as stored)', 'Source File')
    return _rows(context, query,
                 lambda r: (r[0] or '', r[1], r[2], r[3], r[4],
                            'Yes' if r[5] else 'No', r[6]),
                 headers)
