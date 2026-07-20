# pylint: disable=W0613
__artifacts_v2__ = {
    "get_cmh": {
        "name": "cmh",
        "description": "Parses the Samsung CMH media store (image dates, title, bucket, latitude, longitude, address and path) from cmh.db.",
        "author": "",
        "creation_date": "2020-03-05",
        "last_update_date": "2026-07-11",
        "requirements": "none",
        "category": "Samsung_CMH",
        "notes": "Queries the files table directly (media_type 1 = images), which matches the images view older CMH versions defined over it; newer CMH versions dropped that view.",
        "paths": ('*/cmh.db',),
        "output_types": "all",
        "artifact_icon": "file",
        "sample_data": {
            "galaxys10_a10": "Android 10 | com.samsung.cmh | 32 rows",
            "samsunga53_a14": "Android 14 | com.samsung.cmh | 2 rows",
            "samsungs20_a13": "Android 13 | com.samsung.cmh | 16 rows",
            "sharon_a14": "Android 14 | com.samsung.cmh | 1410 rows",
            "anne_a15": "Android 15 | com.samsung.cmh | 212 rows",
        },
    }
}

import datetime
import hashlib
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, does_table_exist_in_db


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


@artifact_processor
def get_cmh(files_found, report_folder, seeker, wrap_text):
    # Extractions can hold several cmh.db copies (e.g. one per user profile);
    # parse every distinct copy that carries the files table. The same
    # database can appear under aliased paths (data/data vs data/user/0,
    # tool mirror folders), so byte-identical copies are only parsed once.
    data_list = []
    sources = []
    seen_hashes = set()
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip mirror, it should be duplicate data

        with open(file_found, 'rb') as db_file:
            file_hash = hashlib.sha256(db_file.read()).hexdigest()
        if file_hash in seen_hashes:
            continue
        seen_hashes.add(file_hash)

        if not does_table_exist_in_db(file_found, 'files'):
            logfunc(f'No files table in {file_found} (unsupported CMH schema version?)')
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            # Older CMH versions defined an images view as exactly
            # "SELECT ... FROM files WHERE media_type=1"; newer versions
            # dropped the view, so query the files table directly.
            cursor.execute('''
                SELECT
                files.datetaken, files.date_added, files.date_modified, files.title,
                files.bucket_display_name, files.latitude, files.longitude,
                location_view.address_text, location_view.uri, files._data, files.isprivate
                FROM files
                left join location_view on location_view._id = files._id
                WHERE files.media_type = 1
            ''')
            all_rows = cursor.fetchall()
        except sqlite3.OperationalError as ex:
            logfunc(f'Unable to query {file_found} (unsupported CMH schema version?): {ex}')
            all_rows = []
        db.close()

        if all_rows:
            sources.append(file_found)
        for r in all_rows:
            data_list.append((_ms_to_utc(r[0]), _sec_to_utc(r[1]), _sec_to_utc(r[2]), r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]))

    source_path = ', '.join(sources) if sources else str(files_found[0])
    data_headers = (('Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), 'Title', 'Bucket Name', 'Latitude', 'Longitude', 'Address', 'URI', 'Data Location', 'Is Private')
    return data_headers, data_list, source_path
