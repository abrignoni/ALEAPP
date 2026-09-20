# pylint: disable=W0718
__artifacts_v2__ = {
    "get_emulatedSmeta": {
        "name": "Emulated Storage Metadata - Downloads",
        "description": "Parses media store metadata (downloads)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "Reads each com.google.android.providers.media.module external.db found, including a second Android user's, and takes one copy where one user's database appears under more than one of the data/data, data/user/N and data_mirror paths. A copy under data/misc_ce/N/rollback/, where installd's snapshotAppData copies an app's credential encrypted data, is also read as a separate database: on hc_pixel8pro_a16 every path in the copy is also in the live database, while on pixel3_a12 the copy's files table lists 31 paths that the live database's files table does not. Reference: AOSP, 'InstalldNativeService::snapshotAppData', https://android.googlesource.com/platform/frameworks/native/+/2827a4a16b0340ecd07c2d5a6c89991799b362bb/cmds/installd/InstalldNativeService.cpp#1676 The Source DB Path column names the database each row came from, and the report's 'located at' line lists every database read, including any that returned no rows. MediaStore records DATE_ADDED and DATE_MODIFIED in seconds since epoch and DATE_TAKEN in milliseconds, and this parser decodes them that way. Reference: AOSP, 'MediaStore.MediaColumns', https://developer.android.com/reference/android/provider/MediaStore.MediaColumns",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.providers.media.module | 0 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.media | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.providers.media.module | 24 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.providers.media.module | 30 rows",
            "pixel7a_a14": "Android 14 | com.google.android.providers.media.module | 74 rows",
            "samsunga53_a14": "Android 14 | com.google.android.providers.media.module | 1 row",
            "samsungs20_a13": "Android 13 | com.google.android.providers.media.module | 6 rows",
            "sharon_a14": "Android 14 | com.google.android.providers.media.module | 122 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.providers.media.module | 1 row",
            "userb2_a13": "Android 13 | com.google.android.providers.media.module | 2 rows",
            "emu_a15_oss2_v3": "Android 15 | com.google.android.providers.media.module | 3 rows",
            "pixel3_a12": "Android 12 | com.google.android.providers.media.module | 53 rows",
            "russell_a14": "Android 14 | com.google.android.providers.media.module | 4 rows",
        },
    },
    "get_emulatedSmeta_images": {
        "name": "Emulated Storage Metadata - Images",
        "description": "Parses media store metadata (images)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "Reads each com.google.android.providers.media.module external.db found, including a second Android user's, and takes one copy where one user's database appears under more than one of the data/data, data/user/N and data_mirror paths. A copy under data/misc_ce/N/rollback/, where installd's snapshotAppData copies an app's credential encrypted data, is also read as a separate database: on hc_pixel8pro_a16 every path in the copy is also in the live database, while on pixel3_a12 the copy's files table lists 31 paths that the live database's files table does not. Reference: AOSP, 'InstalldNativeService::snapshotAppData', https://android.googlesource.com/platform/frameworks/native/+/2827a4a16b0340ecd07c2d5a6c89991799b362bb/cmds/installd/InstalldNativeService.cpp#1676 The Source DB Path column names the database each row came from, and the report's 'located at' line lists every database read, including any that returned no rows. MediaStore records ORIENTATION as a rotation in degrees, so 0 and 180 are reported as Horizontal and 90 and 270 as Vertical; any other value, including NULL, is passed through unchanged. DATE_ADDED and DATE_MODIFIED are seconds since epoch and DATE_TAKEN is milliseconds, and this parser decodes them that way. Reference: AOSP, 'MediaStore.MediaColumns.ORIENTATION', https://developer.android.com/reference/android/provider/MediaStore.MediaColumns#ORIENTATION",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.providers.media.module | 212 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.media | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.providers.media.module | 38 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.providers.media.module | 330 rows",
            "pixel7a_a14": "Android 14 | com.google.android.providers.media.module | 193 rows",
            "samsunga53_a14": "Android 14 | com.google.android.providers.media.module | 2 rows",
            "samsungs20_a13": "Android 13 | com.google.android.providers.media.module | 16 rows",
            "sharon_a14": "Android 14 | com.google.android.providers.media.module | 1410 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.providers.media.module | 96 rows",
            "userb2_a13": "Android 13 | com.google.android.providers.media.module | 4 rows",
            "emu_a15_oss2_v3": "Android 15 | com.google.android.providers.media.module | 15 rows",
            "pixel3_a12": "Android 12 | com.google.android.providers.media.module | 143 rows",
            "russell_a14": "Android 14 | com.google.android.providers.media.module | 622 rows",
        },
    },
    "get_emulatedSmeta_files": {
        "name": "Emulated Storage Metadata - Files",
        "description": "Parses media store metadata (files)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "Reads each com.google.android.providers.media.module external.db found, including a second Android user's, and takes one copy where one user's database appears under more than one of the data/data, data/user/N and data_mirror paths. A copy under data/misc_ce/N/rollback/, where installd's snapshotAppData copies an app's credential encrypted data, is also read as a separate database: on hc_pixel8pro_a16 every path in the copy is also in the live database, while on pixel3_a12 the copy's files table lists 31 paths that the live database's files table does not. Reference: AOSP, 'InstalldNativeService::snapshotAppData', https://android.googlesource.com/platform/frameworks/native/+/2827a4a16b0340ecd07c2d5a6c89991799b362bb/cmds/installd/InstalldNativeService.cpp#1676 The Source DB Path column names the database each row came from, and the report's 'located at' line lists every database read, including any that returned no rows. MediaStore records ORIENTATION as a rotation in degrees, so 0 and 180 are reported as Horizontal and 90 and 270 as Vertical; any other value, including NULL, is passed through unchanged. DATE_ADDED and DATE_MODIFIED are seconds since epoch and DATE_TAKEN is milliseconds, and this parser decodes them that way. Reference: AOSP, 'MediaStore.MediaColumns.ORIENTATION', https://developer.android.com/reference/android/provider/MediaStore.MediaColumns#ORIENTATION",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.providers.media.module | 369 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.media | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.providers.media.module | 420 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.providers.media.module | 660 rows",
            "pixel7a_a14": "Android 14 | com.google.android.providers.media.module | 364 rows",
            "samsunga53_a14": "Android 14 | com.google.android.providers.media.module | 26 rows",
            "samsungs20_a13": "Android 13 | com.google.android.providers.media.module | 153 rows",
            "sharon_a14": "Android 14 | com.google.android.providers.media.module | 1938 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.providers.media.module | 226 rows",
            "userb2_a13": "Android 13 | com.google.android.providers.media.module | 26 rows",
            "emu_a15_oss2_v3": "Android 15 | com.google.android.providers.media.module | 197 rows",
            "pixel3_a12": "Android 12 | com.google.android.providers.media.module | 461 rows",
            "russell_a14": "Android 14 | com.google.android.providers.media.module | 1015 rows",
        },
    },
    "get_emulatedSmeta_videos": {
        "name": "Emulated Storage Metadata - Videos",
        "description": "Parses media store metadata (videos)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "Reads each com.google.android.providers.media.module external.db found, including a second Android user's, and takes one copy where one user's database appears under more than one of the data/data, data/user/N and data_mirror paths. A copy under data/misc_ce/N/rollback/, where installd's snapshotAppData copies an app's credential encrypted data, is also read as a separate database: on hc_pixel8pro_a16 every path in the copy is also in the live database, while on pixel3_a12 the copy's files table lists 31 paths that the live database's files table does not. Reference: AOSP, 'InstalldNativeService::snapshotAppData', https://android.googlesource.com/platform/frameworks/native/+/2827a4a16b0340ecd07c2d5a6c89991799b362bb/cmds/installd/InstalldNativeService.cpp#1676 The Source DB Path column names the database each row came from, and the report's 'located at' line lists every database read, including any that returned no rows. MediaStore records ORIENTATION as a rotation in degrees, so 0 and 180 are reported as Horizontal and 90 and 270 as Vertical; any other value, including NULL, is passed through unchanged. DATE_ADDED and DATE_MODIFIED are seconds since epoch and DATE_TAKEN is milliseconds, and this parser decodes them that way. Reference: AOSP, 'MediaStore.MediaColumns.ORIENTATION', https://developer.android.com/reference/android/provider/MediaStore.MediaColumns#ORIENTATION",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "video",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.providers.media.module | 11 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.media | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.providers.media.module | 6 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.providers.media.module | 90 rows",
            "pixel7a_a14": "Android 14 | com.google.android.providers.media.module | 9 rows",
            "samsunga53_a14": "Android 14 | com.google.android.providers.media.module | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.providers.media.module | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.providers.media.module | 29 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.providers.media.module | 6 rows",
            "userb2_a13": "Android 13 | com.google.android.providers.media.module | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | com.google.android.providers.media.module | 5 rows",
            "pixel3_a12": "Android 12 | com.google.android.providers.media.module | 5 rows",
            "russell_a14": "Android 14 | com.google.android.providers.media.module | 56 rows",
        },
    },
    "get_emulatedSmeta_audio": {
        "name": "Emulated Storage Metadata - Audio",
        "description": "Parses media store metadata (audio)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "Reads each com.google.android.providers.media.module external.db found, including a second Android user's, and takes one copy where one user's database appears under more than one of the data/data, data/user/N and data_mirror paths. A copy under data/misc_ce/N/rollback/, where installd's snapshotAppData copies an app's credential encrypted data, is also read as a separate database: on hc_pixel8pro_a16 every path in the copy is also in the live database, while on pixel3_a12 the copy's files table lists 31 paths that the live database's files table does not. Reference: AOSP, 'InstalldNativeService::snapshotAppData', https://android.googlesource.com/platform/frameworks/native/+/2827a4a16b0340ecd07c2d5a6c89991799b362bb/cmds/installd/InstalldNativeService.cpp#1676 The Source DB Path column names the database each row came from, and the report's 'located at' line lists every database read, including any that returned no rows. MediaStore records DATE_ADDED and DATE_MODIFIED in seconds since epoch and DATE_TAKEN in milliseconds, and this parser decodes them that way. Reference: AOSP, 'MediaStore.MediaColumns', https://developer.android.com/reference/android/provider/MediaStore.MediaColumns",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.providers.media.module | 2 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.media | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.providers.media.module | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.providers.media.module | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.providers.media.module | 14 rows",
            "samsunga53_a14": "Android 14 | com.google.android.providers.media.module | 1 row",
            "samsungs20_a13": "Android 13 | com.google.android.providers.media.module | 1 row",
            "sharon_a14": "Android 14 | com.google.android.providers.media.module | 2 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.providers.media.module | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.providers.media.module | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | com.google.android.providers.media.module | 8 rows",
            "pixel3_a12": "Android 12 | com.google.android.providers.media.module | 3 rows",
            "russell_a14": "Android 14 | com.google.android.providers.media.module | 0 rows",
        },
    },
    "get_emulatedSmeta_files_legacy": {
        "name": "Emulated Storage Metadata - Files (Legacy)",
        "description": "Parses media store metadata (files, older schema)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "Reads each com.android.providers.media external.db found and takes one copy where one user's database appears under more than one of the data/data, data/user/N and data_mirror paths. The Source DB Path column names the database each row came from, and the report's 'located at' line lists every database read, including any that returned no rows. MediaStore records ORIENTATION as a rotation in degrees, so 0 and 180 are reported as Horizontal and 90 and 270 as Vertical; any other value, including NULL, is passed through unchanged. DATE_ADDED and DATE_MODIFIED are seconds since epoch and DATE_TAKEN is milliseconds, and this parser decodes them that way. Reference: AOSP, 'MediaStore.MediaColumns.ORIENTATION', https://developer.android.com/reference/android/provider/MediaStore.MediaColumns#ORIENTATION",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.providers.media.module | 0 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.media | 64 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.providers.media.module | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.providers.media.module | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.providers.media.module | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.providers.media.module | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.providers.media.module | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.providers.media.module | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.providers.media.module | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.providers.media.module | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | com.google.android.providers.media.module | 0 rows",
            "pixel3_a12": "Android 12 | com.google.android.providers.media.module | 0 rows",
            "russell_a14": "Android 14 | com.google.android.providers.media.module | 0 rows",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import unique_files

# MediaStore stores ORIENTATION as a rotation in degrees; unexpected values stay raw
ORIENTATION = ("case orientation when 0 then 'Horizontal' when 180 then 'Horizontal' "
               "when 90 then 'Vertical' when 270 then 'Vertical' else orientation end")
YESNO = "case {0} when 0 then '' when 1 then 'Yes' end"


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _keytime(date_added, date_modified):
    return _sec_to_utc(date_added if date_added else date_modified)


def _external_dbs(context, media_module):
    '''Every distinct external.db for the given provider.

    unique_files collapses the storage-view copies of one user's database and keeps
    different users apart, because canonical_path keeps the Android user id in its key.
    '''
    dbs = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.endswith('external.db'):
            continue
        if media_module != ('media.module' in file_found):
            continue
        dbs.append(file_found)
    return dbs


def _run(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except Exception as e:
        logfunc(str(e))
        rows = []
    db.close()
    return rows


@artifact_processor
def get_emulatedSmeta(context):
    data_list = []
    source_paths = []
    for source_path in _external_dbs(context, True):
        source_paths.append(source_path)
        source_db = context.get_relative_path(source_path)
        for r in _run(source_path, f'''
            SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size,
            owner_package_name, bucket_display_name, referer_uri, download_uri, relative_path,
            {YESNO.format('is_download')}, {YESNO.format('is_favorite')}, {YESNO.format('is_trashed')}, xmp
            FROM downloads
        '''):
            xmp = str(r[15])[2:-1] if isinstance(r[15], bytes) else r[15]
            data_list.append((_keytime(r[0], r[1]), _sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                              r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], xmp, source_db))
    data_headers = (('Key Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Date Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Owner Package Name', 'Bucket Display Name', 'Referer URI', 'Download URI',
                    'Relative Path', 'Is Downloaded?', 'Is Favorited?', 'Is Trashed?', 'XMP', 'Source DB Path')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_emulatedSmeta_images(context):
    data_list = []
    source_paths = []
    for source_path in _external_dbs(context, True):
        source_paths.append(source_path)
        source_db = context.get_relative_path(source_path)
        for r in _run(source_path, f'''
            SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size, latitude, longitude,
            {ORIENTATION}, owner_package_name, bucket_display_name, relative_path,
            {YESNO.format('is_download')}, {YESNO.format('is_favorite')}, {YESNO.format('is_trashed')}
            FROM images
        '''):
            data_list.append((_keytime(r[0], r[1]), _sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                              r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], source_db))
    data_headers = (('Key Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Date Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Latitude', 'Longitude', 'Orientation', 'Owner Package Name',
                    'Bucket Display Name', 'Relative Path', 'Is Downloaded?', 'Is Favorited?', 'Is Trashed?', 'Source DB Path')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_emulatedSmeta_files(context):
    data_list = []
    source_paths = []
    for source_path in _external_dbs(context, True):
        source_paths.append(source_path)
        source_db = context.get_relative_path(source_path)
        for r in _run(source_path, f'''
            SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size, latitude, longitude,
            {ORIENTATION}, owner_package_name, bucket_display_name, referer_uri, download_uri, relative_path,
            {YESNO.format('is_download')}, {YESNO.format('is_favorite')}, {YESNO.format('is_trashed')}
            FROM files
        '''):
            data_list.append((_keytime(r[0], r[1]), _sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                              r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16], r[17], source_db))
    data_headers = (('Key Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Date Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Latitude', 'Longitude', 'Orientation', 'Owner Package Name',
                    'Bucket Display Name', 'Referer URI', 'Download URI', 'Relative Path', 'Is Downloaded?', 'Is Favorited?', 'Is Trashed?', 'Source DB Path')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_emulatedSmeta_videos(context):
    data_list = []
    source_paths = []
    for source_path in _external_dbs(context, True):
        source_paths.append(source_path)
        source_db = context.get_relative_path(source_path)
        for r in _run(source_path, f'''
            SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size, latitude, longitude,
            {ORIENTATION}, owner_package_name, bucket_display_name, relative_path,
            {YESNO.format('is_download')}, {YESNO.format('is_favorite')}, {YESNO.format('is_trashed')}
            FROM video
        '''):
            data_list.append((_keytime(r[0], r[1]), _sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                              r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], source_db))
    data_headers = (('Key Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Date Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Latitude', 'Longitude', 'Orientation', 'Owner Package Name',
                    'Bucket Display Name', 'Relative Path', 'Is Downloaded?', 'Is Favorited?', 'Is Trashed?', 'Source DB Path')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_emulatedSmeta_audio(context):
    data_list = []
    source_paths = []
    for source_path in _external_dbs(context, True):
        source_paths.append(source_path)
        source_db = context.get_relative_path(source_path)
        for r in _run(source_path, f'''
            SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size,
            owner_package_name, bucket_display_name, relative_path,
            {YESNO.format('is_download')}, {YESNO.format('is_favorite')}, {YESNO.format('is_trashed')}
            FROM audio
        '''):
            data_list.append((_keytime(r[0], r[1]), _sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                              r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], source_db))
    data_headers = (('Key Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Date Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Owner Package Name', 'Bucket Display Name', 'Relative Path',
                    'Is Downloaded?', 'Is Favorited?', 'Is Trashed?', 'Source DB Path')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_emulatedSmeta_files_legacy(context):
    data_list = []
    source_paths = []
    for source_path in _external_dbs(context, False):
        source_paths.append(source_path)
        source_db = context.get_relative_path(source_path)
        for r in _run(source_path, f'''
            SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size, latitude, longitude,
            {ORIENTATION}, bucket_display_name, width, height, _id
            FROM files
        '''):
            data_list.append((_sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                              r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], source_db))
    data_headers = (('Timestamp Added', 'datetime'), ('Timestamp Modified', 'datetime'), ('Timestamp Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Latitude', 'Longitude', 'Orientation', 'Bucket Display Name',
                    'Width', 'Height', 'ID', 'Source DB Path')
    return data_headers, data_list, '\n'.join(source_paths)
