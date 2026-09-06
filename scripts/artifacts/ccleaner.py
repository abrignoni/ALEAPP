__artifacts_v2__ = {
    "ccleaner_app_storage": {
        "name": "CCleaner App Storage and Data Usage",
        "description": "Per-app storage size and data usage recorded by a CCleaner scan",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "CCleaner",
        "sample_data": {
            "emu_a15_oss_v17": "CCleaner 26.12.2 | 95 rows",
        },
        "notes": "One row per package, built from com.piriform.ccleaner/databases/AppDb.db by "
                 "joining TABLE AppDataUsageItem to AppGrowingSizeItem on packageName. On the "
                 "tested image each table held 95 rows over 95 distinct packages with no package "
                 "repeated in either, and the two package sets were identical, so the join "
                 "returned 95 rows and dropped nothing. The two tables are NOT joined on their "
                 "date columns: each row carries its own write time and the values differ by "
                 "milliseconds, so a join on date matched only 42 of 95. Data Usage (bytes) and "
                 "App Size (bytes) are reported as stored and the app's unit for them was not "
                 "sourced. App Name is looked up from the CachedApp table in the separate "
                 "databases/cleaner store, which held 78 packages covering 77 of the 95, so the "
                 "column is blank on the remaining 18. Recorded and Size Recorded are Unix "
                 "milliseconds rendered as UTC. A row is evidence the scan measured that package "
                 "at that moment, not evidence of activity by a person.",
        "paths": ('*/com.piriform.ccleaner/databases/AppDb.db*',
                  '*/com.piriform.ccleaner/databases/cleaner*'),
        "output_types": "standard",
        "artifact_icon": "hard-drive",
    },
    "ccleaner_photo_analysis": {
        "name": "CCleaner Photo Analysis",
        "description": "Images on the device that CCleaner's photo analyzer indexed and scored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "CCleaner",
        "sample_data": {
            "emu_a15_oss_v17": "CCleaner 26.12.2 | 17 rows",
        },
        "notes": "One row per row of MediaDbItem in "
                 "com.piriform.ccleaner/databases/PhotoAnalyzerDb.db, which is the analyzer's own "
                 "index of images it found on shared storage. Path is the app's recorded absolute "
                 "path on the device. Photo Date is Unix milliseconds rendered as UTC; the column "
                 "stores -1 when the app recorded no date and that is reported as blank, which was "
                 "the case on 11 of the 17 rows of the tested image. Faces Detected is the app's "
                 "own facesCount and held 0 on every row of that image, so the column is populated "
                 "but its non-zero behaviour was not exercised here. Dark Score, Blurry Score and "
                 "Quality Score are the app's own scores, reported as stored with no scale "
                 "sourced. Marked Bad is the app's isBad flag and was 1 on 2 rows. A row is "
                 "evidence the analyzer indexed the file, not evidence a person viewed it, and an "
                 "absent path is not evidence the image was never on the device.",
        "paths": ('*/com.piriform.ccleaner/databases/PhotoAnalyzerDb.db*',),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "ccleaner_duplicate_photos": {
        "name": "CCleaner Duplicate Photo Sets",
        "description": "Images CCleaner grouped together as duplicates of one another",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "CCleaner",
        "sample_data": {
            "emu_a15_oss_v17": "CCleaner 26.12.2 | 9 rows",
        },
        "notes": "One row per image per set, expanded from the DuplicatesSet table in "
                 "com.piriform.ccleaner/databases/PhotoAnalyzerDb.db. The photos column is JSON "
                 "mapping a media id to a path, and those ids are MediaDbItem ids: every id in "
                 "both sets of the tested image resolved to a row in MediaDbItem, so the link "
                 "between this artifact and the photo analysis artifact is one the store recorded "
                 "rather than a match on name or size. Set Detected is Unix milliseconds rendered "
                 "as UTC. The tested image held 2 sets of 3 and 6 images. Grouping is the app's "
                 "own judgement and the basis for it was not sourced, so a row records that "
                 "CCleaner considered the images duplicates, not that they are byte-identical.",
        "paths": ('*/com.piriform.ccleaner/databases/PhotoAnalyzerDb.db*',),
        "output_types": "standard",
        "artifact_icon": "copy",
    },
    "ccleaner_video_analysis": {
        "name": "CCleaner Video Analysis",
        "description": "Videos on the device that CCleaner's optimizer inspected, with codec detail",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "CCleaner",
        "sample_data": {
            "emu_a15_oss_v17": "CCleaner 26.12.2 | 3 rows",
        },
        "notes": "One row per row of VideoOptimizerMediaItem in "
                 "com.piriform.ccleaner/databases/VideoOptimizerDb.db. Path is the app's recorded "
                 "absolute path. Last Modified and Analyzed are Unix milliseconds rendered as UTC; "
                 "Last Modified is the file's own time as the app read it and Analyzed is when the "
                 "app inspected it. Duration, dimensions, rotation, frame rate, codecs and "
                 "bitrates are reported as stored. Has DRM and Is HDR are the app's own flags. The "
                 "tested image held 3 rows, all of them files placed on the device deliberately, "
                 "and the recorded duration, dimensions and codec matched those files. A row is "
                 "evidence the optimizer inspected the file, not evidence a person played it.",
        "paths": ('*/com.piriform.ccleaner/databases/VideoOptimizerDb.db*',),
        "output_types": "standard",
        "artifact_icon": "film",
    },
    "ccleaner_cleaning_history": {
        "name": "CCleaner Cleaning History",
        "description": "Cleaning operations CCleaner recorded, with the bytes each reported removing",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "CCleaner",
        "sample_data": {
            "emu_a15_oss_v17": "CCleaner 26.12.2 | 2 rows",
        },
        "notes": "One row per row of the CleanedItem table in "
                 "com.piriform.ccleaner/databases/cleaner. Cleaned is Unix milliseconds rendered "
                 "as UTC. Cleaning Type, Category Id and Group Item are reported as stored; no "
                 "lookup table for the numeric category was found in the store, so the integer is "
                 "printed rather than named. The tested image held 2 rows written at the same "
                 "millisecond, both of type QUICK_CLEAN, one naming IntentAppsCacheItem and one "
                 "with Category Id and Group Item empty, so a single cleaning run can write more "
                 "than one row and not every row is categorised. Bytes Cleaned is the app's own "
                 "cleanedValueInBytes. A row records that the app reported removing that many "
                 "bytes; it does not identify which files were removed, and the store retains no "
                 "list of them.",
        "paths": ('*/com.piriform.ccleaner/databases/cleaner*',),
        "output_types": "standard",
        "artifact_icon": "trash-2",
    },
}

import json
import os

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, \
    get_sqlite_db_records, logfunc
from scripts.artifacts.storagePathViews import unique_files

APP_DB = 'databases/AppDb.db'
CLEANER_DB = 'databases/cleaner'
PHOTO_DB = 'databases/PhotoAnalyzerDb.db'
VIDEO_DB = 'databases/VideoOptimizerDb.db'


def _files(context, suffix):
    """Storage-view collapsed files whose path ends in suffix, directories excluded."""
    out = []
    for found in unique_files(context):
        path = str(found).replace('\\', '/')
        if path.endswith(suffix) and not os.path.isdir(found):
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


def _app_titles(context):
    """packageName to title from the cleaner store's CachedApp name cache."""
    titles = {}
    for db_path in _files(context, CLEANER_DB):
        for row in get_sqlite_db_records(db_path, 'SELECT packageName, title FROM CachedApp'):
            if row[0]:
                titles[row[0]] = row[1] or ''
    return titles


@artifact_processor
def ccleaner_app_storage(context):
    titles = _app_titles(context)
    query = '''SELECT u.packageName, u.dataUsage, u.date, g.appSize, g.date
               FROM AppDataUsageItem u
               JOIN AppGrowingSizeItem g ON g.packageName = u.packageName
               ORDER BY g.appSize DESC'''
    data_list = []
    sources = []
    for db_path in _files(context, APP_DB):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[2]), _ms(r[4]), r[0] or '', titles.get(r[0], ''),
                              r[1], r[3], context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Recorded', 'datetime'), ('Size Recorded', 'datetime'), 'Package', 'App Name',
        'Data Usage (bytes)', 'App Size (bytes)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ccleaner_photo_analysis(context):
    query = '''SELECT date, path, width, height, orientation, facesCount, dark, blurry,
                      score, isBad, wasAnalyzedForDuplicates
               FROM MediaDbItem ORDER BY date DESC, path'''
    data_list = []
    sources = []
    for db_path in _files(context, PHOTO_DB):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', r[2], r[3], r[4], r[5], r[6], r[7],
                              r[8], r[9], r[10], context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Photo Date', 'datetime'), 'Path', 'Width', 'Height', 'Orientation',
        'Faces Detected', 'Dark Score', 'Blurry Score', 'Quality Score', 'Marked Bad',
        'Analyzed For Duplicates', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ccleaner_duplicate_photos(context):
    data_list = []
    sources = []
    for db_path in _files(context, PHOTO_DB):
        records = get_sqlite_db_records(db_path, 'SELECT id, time, photos FROM DuplicatesSet')
        seen = False
        for set_id, when, payload in records:
            try:
                members = json.loads(payload or '{}')
            except ValueError as error:
                logfunc(f'CCleaner: duplicate set {set_id} did not parse as JSON: {error}')
                continue
            if not isinstance(members, dict):
                continue
            for media_id, path in sorted(members.items(), key=lambda kv: str(kv[0])):
                seen = True
                data_list.append((_ms(when), set_id, media_id, path or '',
                                  context.get_relative_path(db_path)))
        if seen and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Set Detected', 'datetime'), 'Set', 'Media Id', 'Path', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ccleaner_video_analysis(context):
    query = '''SELECT analyzedAt, lastModifiedTime, path, sizeBytes, durationMs, width,
                      height, rotation, frameRate, videoCodecMime, videoBitrateKbps,
                      audioCodecMime, audioBitrateKbps, isHdr, hasDrm
               FROM VideoOptimizerMediaItem ORDER BY analyzedAt DESC, path'''
    data_list = []
    sources = []
    for db_path in _files(context, VIDEO_DB):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), _ms(r[1]), r[2] or '', r[3], r[4], r[5], r[6],
                              r[7], r[8], r[9] or '', r[10], r[11] or '', r[12], r[13],
                              r[14], context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Analyzed', 'datetime'), ('Last Modified', 'datetime'), 'Path', 'Size (bytes)',
        'Duration (ms)', 'Width', 'Height', 'Rotation', 'Frame Rate', 'Video Codec',
        'Video Bitrate (kbps)', 'Audio Codec', 'Audio Bitrate (kbps)', 'Is HDR',
        'Has DRM', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def ccleaner_cleaning_history(context):
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
