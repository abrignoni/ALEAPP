__artifacts_v2__ = {
    "linkbox_uploads": {
        "name": "Linkbox - Uploads",
        "description": "Rows from the upload table of the app's per-account upload database, "
                       "each a file sent from the device to the service, with the path it was "
                       "read from, its size and its MD5",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Linkbox",
        "notes": "com.linkbox.plus.android sends files from the device to a cloud service. The "
                 "store is databases/upload_<account id>.db, one per account, and the account "
                 "id in that file name is reported in its own column; on the corpus below it "
                 "also appeared inside the service side path the same row records, which is why "
                 "it is read as an account id. Local Path is where the file was read from on the "
                 "device, so a row records a file leaving a known location, and on the corpus "
                 "below those locations included the camera folder and the media folders of "
                 "other applications. MD5 is the value the app stored for the file, so a row can "
                 "be matched to a file elsewhere without the file itself being present here. "
                 "create_time, update_time and real_time are Unix milliseconds. Status was 5 on "
                 "every row below and Error Code and Error Message were empty, so no failed "
                 "upload is represented; no source for the status code list was located and it "
                 "is reported as stored. Use Mobile Data held 0 on every row below, so none of "
                 "these transfers was recorded as having used the mobile network, and the column "
                 "is kept because another value would say one had. The table also carries "
                 "per-upload access key"
                 "key and session token columns, whose stored times equal the row's own create "
                 "time and so are scoped to that single upload; they are credential material "
                 "that adds nothing to what the other columns already show, and they are "
                 "deliberately not reported. The same database holds table_upload_part, which "
                 "records the byte range and tag of each transfer chunk and held one part per "
                 "upload covering the whole file, so it adds nothing per row and is not "
                 "reported. Two corpora below carry this application and their upload databases "
                 "are byte identical, so they are one dataset rather than two independent "
                 "observations.",
        "paths": ('*/com.linkbox.plus.android/databases/upload_*.db*',),
        "output_types": "standard",
        "artifact_icon": "upload-cloud",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.linkbox.plus.android | 10 rows",
            "hc_pixel8pro_a17": "Android 17 | com.linkbox.plus.android | 10 rows",
        },
    },
}

import os
import re

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records

SIDECARS = ('-wal', '-shm', '-journal')

# databases/upload_<account id>.db
UPLOAD_DB = re.compile(r'^upload_(.+)\.db$')


def _upload_databases(context):
    """(path, account id) for each per-account upload database."""
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or file_found.endswith(SIDECARS):
            continue
        match = UPLOAD_DB.match(os.path.basename(file_found))
        if match:
            found.append((file_found, match.group(1)))
    return found


@artifact_processor
def linkbox_uploads(context):
    data_list = []
    source_paths = []

    for db_path, account in _upload_databases(context):
        rows = list(get_sqlite_db_records(db_path, '''
            SELECT create_time, update_time, real_time, file_name, file_uri, file_size, md5,
                   parent_path, bucket, server, pool_path, item_id, upload_id, etag, status,
                   error_code, error_msg, use_mobile_data, task_id
            FROM table_upload_data ORDER BY create_time
        '''))
        source_paths.append(context.get_relative_path(db_path))
        for row in rows:
            (created, updated, real_time, name, uri, size, md5, parent, bucket, server,
             pool, item_id, upload_id, etag, status, error_code, error_msg,
             mobile, task_id) = row
            data_list.append((
                convert_unix_ts_to_utc(created / 1000) if created else '',
                convert_unix_ts_to_utc(updated / 1000) if updated else '',
                name or '',
                uri or '',
                size if size is not None else '',
                md5 or '',
                account,
                parent or '',
                bucket or '',
                server or '',
                pool or '',
                item_id or '',
                upload_id or '',
                etag or '',
                status if status is not None else '',
                error_code if error_code is not None else '',
                error_msg or '',
                mobile if mobile is not None else '',
                convert_unix_ts_to_utc(real_time / 1000) if real_time else '',
                task_id or '',
            ))

    data_headers = (
        ('Create Time', 'datetime'),
        ('Update Time', 'datetime'),
        'File Name',
        'Local Path',
        'Size',
        'MD5',
        'Account ID',
        'Destination Folder',
        'Bucket',
        'Server',
        'Service Path',
        'Item ID',
        'Upload ID',
        'ETag',
        'Status (as stored)',
        'Error Code',
        'Error Message',
        'Use Mobile Data',
        ('Real Time', 'datetime'),
        'Task ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)
