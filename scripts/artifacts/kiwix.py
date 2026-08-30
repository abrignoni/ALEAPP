__artifacts_v2__ = {
    "kiwix_reading_history": {
        "name": "Kiwix - Reading History",
        "description": "Parses the offline article reading history recorded by the Kiwix Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Kiwix",
        "notes": "One row per entry in the HistoryRoomEntity table of databases/KiwixRoom.db. Kiwix "
                 "reads offline content packaged as ZIM files, so each row records that an article was "
                 "opened inside one of those files, with the article title and its in content URL, "
                 "the name of the ZIM the article came from, and the path to that ZIM on the device. "
                 "Timestamp is Unix milliseconds and was UTC on the tested device (16:13 UTC matched "
                 "the device's 12:13 local clock), so it is reported as UTC; the app also stores a "
                 "human date string which is carried in the Date Text column as stored. The ZIM path "
                 "shows which downloaded content library the article was read from. The stored favicon "
                 "for each entry is a base64 image and is not reported. Two related stores in the same "
                 "database are not parsed here: RecentSearchRoomEntity is covered by the Searches "
                 "artifact, and NotesRoomEntity holds notes written against articles, which was "
                 "empty on the tested device. The database runs in WAL mode and held its rows in the "
                 "-wal sidecar on the tested device, so the sidecar is in the paths and is required.",
        "paths": ('*/org.kiwix.kiwixmobile*/databases/KiwixRoom.db*',),
        "output_types": "standard",
        "artifact_icon": "book",
        "sample_data": {
            "emu_a15_oss_v1": "Android 15 | org.kiwix.kiwixmobile.standalone vc 6231767 | 1 rows",
        },
    },
    "kiwix_searches": {
        "name": "Kiwix - Searches",
        "description": "Parses the in-content search terms recorded by the Kiwix Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Kiwix",
        "notes": "One row per entry in the RecentSearchRoomEntity table of databases/KiwixRoom.db. Each "
                 "row is a term searched inside a ZIM's content, with the ZIM id it was run against and "
                 "the resulting article URL where stored. This table does not carry a timestamp. It was "
                 "empty on the tested device, so this artifact is code present and exercised against no "
                 "rows here. The data lives in the KiwixRoom.db WAL sidecar on the tested device.",
        "paths": ('*/org.kiwix.kiwixmobile*/databases/KiwixRoom.db*',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "emu_a15_oss_v1": "Android 15 | org.kiwix.kiwixmobile.standalone vc 6231767 | 0 rows; in-content search table present and empty, confirmed by reading it",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/KiwixRoom.db'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


@artifact_processor
def kiwix_reading_history(context):
    query = '''SELECT timeStamp, historyTitle, historyUrl, zimName, zimReaderSource,
                      dateString, zimId
               FROM HistoryRoomEntity ORDER BY timeStamp DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', r[2] or '', r[3] or '', r[4] or '',
                              r[5] or '', r[6] or '', context.get_relative_path(db_path)))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (('Timestamp', 'datetime'), 'Title', 'Content URL', 'ZIM Name',
                    'ZIM Path', 'Date Text', 'ZIM ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def kiwix_searches(context):
    query = 'SELECT searchTerm, zimId, url FROM RecentSearchRoomEntity ORDER BY searchTerm'
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            data_list.append((r[0] or '', r[1] or '', r[2] or '',
                              context.get_relative_path(db_path)))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = ('Search Term', 'ZIM ID', 'Content URL', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
