__artifacts_v2__ = {
    "kiwix_reading_history": {
        "name": "Kiwix - Reading History",
        "description": "Parses the offline article reading history recorded by the Kiwix Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Kiwix",
        "notes": "One row per entry in the HistoryRoomEntity table of databases/KiwixRoom.db. "
                 "Each row carries the article title and its in content URL, the name of the ZIM "
                 "file the entry names, and the zimReaderSource value as stored (the zimFilePath "
                 "field of the same table is not read). In the app's source at commit "
                 "b11715c7d9b3a5b5c055f50627ec5cfc5129df2a (kiwix/kiwix-android, "
                 "core/src/main/java/org/kiwix/kiwixmobile/core/reader/ZimReaderSource.kt line "
                 "116, toDatabase) the value written is a file's canonical path or, where there is "
                 "no file, the URI as a string; whether the build on the tested device wrote it "
                 "the same way was not established. "
                 "Timestamp is Unix milliseconds and was UTC on the tested device (16:13 UTC "
                 "matched the device's 12:13 local clock), so it is reported as UTC; the app "
                 "also stores a human date string which is carried in the Date Text column as "
                 "stored. "
                 "The stored favicon for each entry is a base64 image and is not reported. Two "
                 "related stores in the same database are not parsed here: "
                 "RecentSearchRoomEntity is covered by the Searches artifact, and "
                 "NotesRoomEntity was empty on the tested device and is not parsed. The database "
                 "runs in WAL mode and held its rows in the "
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
                 "row carries the searchTerm, zimId and url fields of the app's "
                 "RecentSearchRoomEntity (kiwix/kiwix-android, "
                 "core/src/main/java/org/kiwix/kiwixmobile/core/dao/entities/RecentSearchRoomEntity.kt "
                 "at commit ba5da43c89a1a627a28e13a37d570aaf8ab3cda6, lines 24 to 29). What the "
                 "url field holds was not measured. This table does not carry a timestamp. It was "
                 "empty on the tested device, so this artifact is code present and exercised against no "
                 "rows here. On the tested device the database's content sat in the KiwixRoom.db "
                 "-wal sidecar, so the sidecar is in the paths.",
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
