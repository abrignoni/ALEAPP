# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_emulatedSmeta": {
        "name": "Emulated Storage Metadata - Downloads",
        "description": "Parses media store metadata (downloads)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2020-10-19",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "download",
    },
    "get_emulatedSmeta_images": {
        "name": "Emulated Storage Metadata - Images",
        "description": "Parses media store metadata (images)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2020-10-19",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "get_emulatedSmeta_files": {
        "name": "Emulated Storage Metadata - Files",
        "description": "Parses media store metadata (files)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2020-10-19",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "file",
    },
    "get_emulatedSmeta_videos": {
        "name": "Emulated Storage Metadata - Videos",
        "description": "Parses media store metadata (videos)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2020-10-19",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "video",
    },
    "get_emulatedSmeta_audio": {
        "name": "Emulated Storage Metadata - Audio",
        "description": "Parses media store metadata (audio)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2020-10-19",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "music",
    },
    "get_emulatedSmeta_files_legacy": {
        "name": "Emulated Storage Metadata - Files (Legacy)",
        "description": "Parses media store metadata (files, older schema)",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-10-19",
        "last_update_date": "2020-10-19",
        "requirements": "none",
        "category": "Emulated Storage Metadata",
        "notes": "",
        "paths": ('*/com.google.android.providers.media.module/databases/external.db*', '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "file",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

ORIENTATION = "case orientation when 0 then 'Horizontal' else 'Vertical' end"
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


def _external_db(files_found, media_module):
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('external.db'):
            continue
        if media_module == ('media.module' in file_found):
            return file_found
    return ''


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
def get_emulatedSmeta(files_found, report_folder, seeker, wrap_text):
    source_path = _external_db(files_found, True)
    rows = _run(source_path, f'''
        SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size,
        owner_package_name, bucket_display_name, referer_uri, download_uri, relative_path,
        {YESNO.format('is_download')}, {YESNO.format('is_favorite')}, {YESNO.format('is_trashed')}, xmp
        FROM downloads
    ''')
    data_list = []
    for r in rows:
        xmp = str(r[15])[2:-1] if isinstance(r[15], bytes) else r[15]
        data_list.append((_keytime(r[0], r[1]), _sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                          r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], xmp))
    data_headers = (('Key Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Date Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Owner Package Name', 'Bucket Display Name', 'Referer URI', 'Download URI',
                    'Relative Path', 'Is Downloaded?', 'Is Favorited?', 'Is Trashed?', 'XMP')
    return data_headers, data_list, source_path


@artifact_processor
def get_emulatedSmeta_images(files_found, report_folder, seeker, wrap_text):
    source_path = _external_db(files_found, True)
    rows = _run(source_path, f'''
        SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size, latitude, longitude,
        {ORIENTATION}, owner_package_name, bucket_display_name, relative_path,
        {YESNO.format('is_download')}, {YESNO.format('is_favorite')}, {YESNO.format('is_trashed')}
        FROM images
    ''')
    data_list = [(_keytime(r[0], r[1]), _sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                  r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15]) for r in rows]
    data_headers = (('Key Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Date Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Latitude', 'Longitude', 'Orientation', 'Owner Package Name',
                    'Bucket Display Name', 'Relative Path', 'Is Downloaded?', 'Is Favorited?', 'Is Trashed?')
    return data_headers, data_list, source_path


@artifact_processor
def get_emulatedSmeta_files(files_found, report_folder, seeker, wrap_text):
    source_path = _external_db(files_found, True)
    rows = _run(source_path, f'''
        SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size, latitude, longitude,
        {ORIENTATION}, owner_package_name, bucket_display_name, referer_uri, download_uri, relative_path,
        {YESNO.format('is_download')}, {YESNO.format('is_favorite')}, {YESNO.format('is_trashed')}
        FROM files
    ''')
    data_list = [(_keytime(r[0], r[1]), _sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                  r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16], r[17]) for r in rows]
    data_headers = (('Key Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Date Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Latitude', 'Longitude', 'Orientation', 'Owner Package Name',
                    'Bucket Display Name', 'Referer URI', 'Download URI', 'Relative Path', 'Is Downloaded?', 'Is Favorited?', 'Is Trashed?')
    return data_headers, data_list, source_path


@artifact_processor
def get_emulatedSmeta_videos(files_found, report_folder, seeker, wrap_text):
    source_path = _external_db(files_found, True)
    rows = _run(source_path, f'''
        SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size, latitude, longitude,
        {ORIENTATION}, owner_package_name, bucket_display_name, relative_path,
        {YESNO.format('is_download')}, {YESNO.format('is_favorite')}, {YESNO.format('is_trashed')}
        FROM video
    ''')
    data_list = [(_keytime(r[0], r[1]), _sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                  r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15]) for r in rows]
    data_headers = (('Key Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Date Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Latitude', 'Longitude', 'Orientation', 'Owner Package Name',
                    'Bucket Display Name', 'Relative Path', 'Is Downloaded?', 'Is Favorited?', 'Is Trashed?')
    return data_headers, data_list, source_path


@artifact_processor
def get_emulatedSmeta_audio(files_found, report_folder, seeker, wrap_text):
    source_path = _external_db(files_found, True)
    rows = _run(source_path, f'''
        SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size,
        owner_package_name, bucket_display_name, relative_path,
        {YESNO.format('is_download')}, {YESNO.format('is_favorite')}, {YESNO.format('is_trashed')}
        FROM audio
    ''')
    data_list = [(_keytime(r[0], r[1]), _sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                  r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12]) for r in rows]
    data_headers = (('Key Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Date Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Owner Package Name', 'Bucket Display Name', 'Relative Path',
                    'Is Downloaded?', 'Is Favorited?', 'Is Trashed?')
    return data_headers, data_list, source_path


@artifact_processor
def get_emulatedSmeta_files_legacy(files_found, report_folder, seeker, wrap_text):
    source_path = _external_db(files_found, False)
    rows = _run(source_path, f'''
        SELECT date_added, date_modified, datetaken, _data, title, _display_name, _size, latitude, longitude,
        {ORIENTATION}, bucket_display_name, width, height, _id
        FROM files
    ''')
    data_list = [(_sec_to_utc(r[0]), _sec_to_utc(r[1]), _ms_to_utc(r[2]),
                  r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13]) for r in rows]
    data_headers = (('Timestamp Added', 'datetime'), ('Timestamp Modified', 'datetime'), ('Timestamp Taken', 'datetime'),
                    'Path', 'Title', 'Display Name', 'Size', 'Latitude', 'Longitude', 'Orientation', 'Bucket Display Name',
                    'Width', 'Height', 'ID')
    return data_headers, data_list, source_path
