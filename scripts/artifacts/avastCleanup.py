__artifacts_v2__ = {
    "avast_cleanup_app_storage": {
        "name": "Avast Cleanup App Storage and Data Usage",
        "description": "Per-app storage size and data usage recorded by an Avast Cleanup scan",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Avast Cleanup",
        "sample_data": {
            "emu_a15_oss2_v3": "Avast Cleanup 26.16.1 | 23 rows",
        },
        "notes": "One row per package, built from com.avast.android.cleaner/databases/AppDb.db by "
                 "joining AppDataUsageItem to AppGrowingSizeItem on packageName. On the tested "
                 "image each table held 23 rows over 23 distinct packages with no package repeated "
                 "in either, and the two package sets were identical, so the join returned 23 rows "
                 "and dropped nothing.\n"
                 "**The two tables are not joined on their date columns.** Each row carries its own "
                 "write time, and on the tested image the two times differed on every one of the 23 "
                 "packages, by between 3,413,949 and 3,414,360 milliseconds, so the two tables were "
                 "written in separate passes about 57 minutes apart and a join on date would have "
                 "matched nothing.\n"
                 "Data Usage (bytes) and App Size (bytes) are reported as stored and the app's unit "
                 "for them was not sourced. App Name is looked up from the CachedApp table in the "
                 "separate databases/cleaner store of the same container, so a second Android "
                 "user's copy of that cache cannot name this user's packages. It held 6 "
                 "packages covering 5 of the 23, so "
                 "the column is blank on the other 18.\n"
                 "Recorded and Size Recorded are Unix milliseconds reported as UTC. A row is "
                 "evidence the scan measured that package at that moment, not evidence of activity "
                 "by a person.\n"
                 "**Avast Cleanup and CCleaner ship databases with identical file names**, so every "
                 "path pattern here is anchored on the com.avast.android.cleaner directory and the "
                 "code checks for that segment again before reading. The two apps' schemas "
                 "differ, which is why this is a separate module rather than a widening of the "
                 "CCleaner one: the photo table alone differs in four column names (dateTaken, "
                 "cvScore, classifiedAsBad and similarityAnalysisDone here against date, score, "
                 "isBad and wasAnalyzedForDuplicates there), and the duplicate-photo tables have "
                 "different names and different designs.\n"
                 "**Most of this app's content exists only in the write-ahead log**, so every path "
                 "pattern here ends in * to take the -wal sidecar along with the database. Measured "
                 "on this image by reading each store with and without its log: without it the "
                 "cleaner, PhotoAnalyzerDb.db and VideoOptimizerDb.db files report no tables at "
                 "all, and AppDb.db reports its tables but one AppDataUsageItem row short, 22 "
                 "against 23.",
        "paths": ('*/com.avast.android.cleaner/databases/AppDb.db*',
                  '*/com.avast.android.cleaner/databases/cleaner*'),
        "output_types": "standard",
        "artifact_icon": "hard-drive",
    },
    "avast_cleanup_photo_analysis": {
        "name": "Avast Cleanup Photo Analysis",
        "description": "Images on the device that Avast Cleanup's photo analyzer indexed and scored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Avast Cleanup",
        "sample_data": {
            "emu_a15_oss2_v3": "Avast Cleanup 26.16.1 | 15 rows",
        },
        "notes": "One row per row of MediaDbItem in "
                 "com.avast.android.cleaner/databases/PhotoAnalyzerDb.db, which is the analyzer's "
                 "own index of images it found on shared storage. Path is the app's recorded "
                 "absolute path on the device and Media Store Id is Android's own media "
                 "identifier for the same file. On the tested image all 15 rows carried a distinct "
                 "path and a distinct media id.\n"
                 "Photo Taken is the dateTaken column, Unix milliseconds reported as UTC. The "
                 "column stores -1 where the app recorded no date and that is reported as blank, "
                 "which was the case on 9 of the 15 rows.\n"
                 "Dark Score, Blurry Score, Colour Score and Quality Score are the app's own "
                 "scores, reported as stored with no scale sourced. Marked Bad is the app's "
                 "classifiedAsBad flag and was set on 1 of the 15 rows. Faces Detected is the "
                 "app's own facesCount and read 0 on every row, so the column is populated and its "
                 "non-zero behaviour was not exercised here. Orientation, Is HDR and Invalid read 0 "
                 "on every row too, for the same reason.\n"
                 "The image file itself is not rendered here: the path is what the store records, "
                 "and the file is reported by the artifacts that read shared storage.\n"
                 "A row is evidence the analyzer indexed the file, not evidence a person viewed "
                 "it, and a path the analyzer never recorded is not evidence the image was never "
                 "on the device.",
        "paths": ('*/com.avast.android.cleaner/databases/PhotoAnalyzerDb.db*',),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "avast_cleanup_duplicate_photos": {
        "name": "Avast Cleanup Duplicate Photo Sets",
        "description": "Images Avast Cleanup grouped together as duplicates of one another",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Avast Cleanup",
        "sample_data": {
            "emu_a15_oss2_v3": "Avast Cleanup 26.16.1 | 0 rows",
        },
        "notes": "One row per image per set, from the DuplicatesSetMember table in "
                 "com.avast.android.cleaner/databases/PhotoAnalyzerDb.db. Set is the app's setId "
                 "and every image sharing one is a member of that set.\n"
                 "**The link to the photo analysis artifact is one the store declares**: the "
                 "table's own primary key is the path and it carries a foreign key on that path to "
                 "MediaDbItem, so a member row names the analyzed image rather than being matched "
                 "to it on size or time. That is read from the table's own CREATE statement in the "
                 "tested image.\n"
                 "**The table held no rows on the tested image**, so this artifact is present and "
                 "unexercised there. Its columns come from the schema, not from observed values.\n"
                 "Grouping is the app's own judgement and the basis for it was not sourced, so a "
                 "row records that Avast Cleanup considered the images duplicates, not that they "
                 "are byte-identical. Detected is Unix milliseconds reported as UTC.\n"
                 "This table is not the one CCleaner uses. CCleaner keeps a DuplicatesSet table "
                 "whose members are a JSON map, so the two apps are read by separate code.",
        "paths": ('*/com.avast.android.cleaner/databases/PhotoAnalyzerDb.db*',),
        "output_types": "standard",
        "artifact_icon": "copy",
    },
    "avast_cleanup_video_analysis": {
        "name": "Avast Cleanup Video Analysis",
        "description": "Videos on the device that Avast Cleanup's optimizer inspected, with codec detail",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Avast Cleanup",
        "sample_data": {
            "emu_a15_oss2_v3": "Avast Cleanup 26.16.1 | 4 rows",
        },
        "notes": "One row per row of VideoOptimizerMediaItem in "
                 "com.avast.android.cleaner/databases/VideoOptimizerDb.db. Path is the app's "
                 "recorded absolute path; the table's own primary key is that path, and the tested "
                 "image held 4 rows over 4 distinct paths.\n"
                 "Last Modified and Analyzed are Unix milliseconds reported as UTC. Last Modified "
                 "is the file's own time as the app read it and Analyzed is when the app inspected "
                 "it.\n"
                 "Duration, dimensions, rotation, frame rate, codecs and bitrates are reported as "
                 "stored. The three clips placed on this device deliberately were compared against "
                 "the files themselves with ffprobe: the recorded duration (6,000, 15,000 and "
                 "30,000 ms), dimensions (640 by 360 on all three), frame rate (15, 25 and 25) and "
                 "size matched exactly, and the one clip carrying no audio track is the one whose "
                 "Audio Codec is blank.\n"
                 "**Video Bitrate (kbps) is the whole file's rate, not the video stream's.** On "
                 "all four rows of this image it equals the file size in bits divided by the "
                 "duration, to the kilobit: 43, 82, 839 and 332.\n"
                 "Is HDR, Has DRM and Invalid read 0 on every row, and Video Codec read video/avc on "
                 "every row, so none of those four is exercised on more than one value here.\n"
                 "**The scan reaches files another app wrote.** The fourth row of the tested image "
                 "is a video saved out of a different app into the device camera folder, which is "
                 "worth knowing because it means this table can record a file whose own app keeps "
                 "no record of it.\n"
                 "A row is evidence the optimizer inspected the file, not evidence a person played "
                 "it.",
        "paths": ('*/com.avast.android.cleaner/databases/VideoOptimizerDb.db*',),
        "output_types": "standard",
        "artifact_icon": "film",
    },
    "avast_cleanup_cleaning_history": {
        "name": "Avast Cleanup Cleaning History",
        "description": "Cleaning operations Avast Cleanup recorded, with the bytes each reported removing",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Avast Cleanup",
        "sample_data": {
            "emu_a15_oss2_v3": "Avast Cleanup 26.16.1 | 1 rows",
        },
        "notes": "One row per row of the CleanedItem table in "
                 "com.avast.android.cleaner/databases/cleaner.\n"
                 "**Cleaned is written when the cleaning finishes, not when it is asked for.** "
                 "Measured once on the tested device by starting a Quick Clean and reading the "
                 "table afterwards: the recorded time was 20.5 seconds after the tap that "
                 "started the clean. One observation, so the gap on a larger clean was not "
                 "established.\n"
                 "Cleaned is Unix milliseconds reported as UTC. Cleaning Type, Category Id and "
                 "Group Item are reported as stored; no lookup table for the numeric category was "
                 "found in the store, so the integer would be printed rather than named. The "
                 "tested image held 1 row, of type QUICK_CLEAN, with Category Id and Group Item "
                 "both empty, so a row is not necessarily categorised.\n"
                 "Bytes Cleaned is the app's own cleanedValueInBytes. **A row records that the app "
                 "reported removing that many bytes; it does not identify which files were "
                 "removed, and the store retains no list of them.**\n"
                 "The store's IgnoredItem, TransferredItem and cloudqueue tables held no rows on "
                 "the tested image and are a checked absence, as are AppNotificationItem in AppDb.db "
                 "and every table of BatteryAnalysisDb.db and purchase_database.\n"
                 "The app's directory-scanner.db is not parsed. Its AloneDir, AppLeftOver, JunkDir, "
                 "UsefulCacheDir and ExcludedDir tables are the vendor's own definitions of what "
                 "counts as junk rather than anything found on the device: on the tested image "
                 "AppLeftOver carried rows naming com.avast.cleanup.test.app1 and Test1, and JunkDir "
                 "entries carried regular expressions such as junk/[.{8}]. The app's own config.xml "
                 "preferences are not parsed either: every value in it is an opaque base64 blob "
                 "rather than readable text, and no key for them was looked for.",
        "paths": ('*/com.avast.android.cleaner/databases/cleaner*',),
        "output_types": "standard",
        "artifact_icon": "trash-2",
    },
}

import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import canonical_path, unique_files

PACKAGE = '/com.avast.android.cleaner/'
APP_DB = 'databases/AppDb.db'
CLEANER_DB = 'databases/cleaner'
PHOTO_DB = 'databases/PhotoAnalyzerDb.db'
VIDEO_DB = 'databases/VideoOptimizerDb.db'


def _files(context, suffix):
    """Storage-view collapsed files under this app's own directory whose path ends in suffix.

    CCleaner ships databases with these exact file names, so the package segment is checked
    here as well as in the artifact's paths: a widened pattern must not make this module read
    the other app's store. Directories are excluded because a pattern ending in * can match
    one and open() would raise on it.
    """
    out = []
    for found in unique_files(context):
        path = str(found).replace('\\', '/')
        if PACKAGE in path and path.endswith(suffix) and not os.path.isdir(found):
            out.append(found)
    return out


def _ms(value):
    """Unix milliseconds to UTC. Blank for absent values and for the app's -1 sentinel."""
    if value in (None, '', 0):
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value / 1000)
    except (OverflowError, OSError, ValueError):
        return ''


def _tenant(context, path):
    """The storage class and Android user of the container a file sits in, else ''.

    A name read from one container is only ever attached to rows from the same one, so a
    second Android user's copy of the cache cannot name the first user's packages.
    """
    key, _ = canonical_path(context.get_relative_path(path))
    parts = str(key).split('\x00')
    return parts[1] if len(parts) == 3 else ''


def _app_titles(context):
    """(container, packageName) to title from the cleaner store's CachedApp name cache."""
    titles = {}
    for db_path in _files(context, CLEANER_DB):
        tenant = _tenant(context, db_path)
        for row in get_sqlite_db_records(db_path, 'SELECT packageName, title FROM CachedApp'):
            if row[0]:
                titles[(tenant, row[0])] = row[1] or ''
    return titles


@artifact_processor
def avast_cleanup_app_storage(context):
    titles = _app_titles(context)
    query = '''SELECT u.packageName, u.dataUsage, u.date, g.appSize, g.date
               FROM AppDataUsageItem u
               JOIN AppGrowingSizeItem g ON g.packageName = u.packageName
               ORDER BY g.appSize DESC'''
    data_list = []
    sources = []
    for db_path in _files(context, APP_DB):
        tenant = _tenant(context, db_path)
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[2]), _ms(r[4]), r[0] or '',
                              titles.get((tenant, r[0]), ''),
                              r[1], r[3], context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Recorded', 'datetime'), ('Size Recorded', 'datetime'), 'Package', 'App Name',
        'Data Usage (bytes)', 'App Size (bytes)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def avast_cleanup_photo_analysis(context):
    query = '''SELECT dateTaken, path, mediaStoreId, scannedSizeInBytes, width, height,
                      orientation, facesCount, dark, blurry, color, cvScore,
                      classifiedAsBad, isHdr, invalid
               FROM MediaDbItem ORDER BY dateTaken DESC, path'''
    data_list = []
    sources = []
    for db_path in _files(context, PHOTO_DB):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', r[2], r[3], r[4], r[5], r[6], r[7],
                              r[8], r[9], r[10], r[11], r[12], r[13], r[14],
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Photo Taken', 'datetime'), 'Path', 'Media Store Id', 'Scanned Size (bytes)',
        'Width', 'Height', 'Orientation', 'Faces Detected', 'Dark Score', 'Blurry Score',
        'Colour Score', 'Quality Score', 'Marked Bad', 'Is HDR', 'Invalid', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def avast_cleanup_duplicate_photos(context):
    query = 'SELECT time, setId, path FROM DuplicatesSetMember ORDER BY setId, path'
    data_list = []
    sources = []
    for db_path in _files(context, PHOTO_DB):
        records = get_sqlite_db_records(db_path, query)
        for when, set_id, path in records:
            data_list.append((_ms(when), set_id, path or '',
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (('Detected', 'datetime'), 'Set', 'Path', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def avast_cleanup_video_analysis(context):
    query = '''SELECT analyzedAt, lastModifiedTime, path, sizeBytes, durationMs, width,
                      height, rotation, frameRate, videoCodecMime, videoBitrateKbps,
                      audioCodecMime, audioBitrateKbps, isHdr, hasDrm, invalid
               FROM VideoOptimizerMediaItem ORDER BY analyzedAt DESC, path'''
    data_list = []
    sources = []
    for db_path in _files(context, VIDEO_DB):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), _ms(r[1]), r[2] or '', r[3], r[4], r[5], r[6],
                              r[7], r[8], r[9] or '', r[10], r[11] or '', r[12], r[13],
                              r[14], r[15], context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Analyzed', 'datetime'), ('Last Modified', 'datetime'), 'Path', 'Size (bytes)',
        'Duration (ms)', 'Width', 'Height', 'Rotation', 'Frame Rate', 'Video Codec',
        'Video Bitrate (kbps)', 'Audio Codec', 'Audio Bitrate (kbps)', 'Is HDR',
        'Has DRM', 'Invalid', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def avast_cleanup_cleaning_history(context):
    query = '''SELECT timestamp, cleaningType, categoryId, groupItemId, cleanedValueInBytes
               FROM CleanedItem ORDER BY timestamp DESC'''
    data_list = []
    sources = []
    for db_path in _files(context, CLEANER_DB):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', '' if r[2] is None else r[2],
                              r[3] or '', r[4], context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Cleaned', 'datetime'), 'Cleaning Type', 'Category Id', 'Group Item',
        'Bytes Cleaned', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
