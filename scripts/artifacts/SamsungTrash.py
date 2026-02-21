__artifacts_v2__ = {
    "samsungTrash": {
        "name": "Samsung Trash",
        "description": "Parses Samsung trash records from com.samsung.android.providers.trash",
        "author": "Kalinko",
        "version": "0.1",
        "creation_date": "2026-02-21",
        "last_update_date": "2026-02-21",
        "requirements": "inspect, pathlib",
        "category": "Trash",
        "notes": "More info on: https://bebinary4n6.blogspot.com/2026/02/samsung-trash-provider-app-traces-of.html",
        "paths": (
            "*/com.samsung.android.providers.trash/databases/trash.db*",
            "*/data/media/*/Android/.Trash/*",
            "*/storage/*/Android/.Trash/*",
        ),
        "output_types": "standard",
        "artifact_icon": "trash-2",
    }
}

import inspect
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, get_sqlite_db_records


@artifact_processor
def samsungTrash(files_found, report_folder, seeker, _wrap_text):
    artifact_info = inspect.stack()[0]

    query = """
        SELECT
            _id [File ID],
            _data [Trash File Path],
            original_path [Original File Path],
            title [File Titel],
            _display_name [File Name],
            _size [File Size],
            mime_type [MIME Type],
            delete_package_name [App Context],
            user_id [User ID],
            date_deleted [Deletion Timestamp],
            date_expires [Expiration Timestamp],
            extra [Extra Info JSON]
        FROM trashes
    """

    data_list = []
    source_path = "See Source DB column"
    media_files = [str(path) for path in files_found if "/.Trash/" in str(path)]

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith("trash.db"):
            continue

        db_records = get_sqlite_db_records(file_found, query)

        # Get the media file path to show the media in the results table
        for row in db_records:
            trash_file_path = row[1]
            media_item = ""

            suffix = trash_file_path.split("/Android/.Trash/", 1)[1]
            matched_media_path = ""
            for media_path in media_files:
                if media_path.endswith(suffix):
                    matched_media_path = media_path
                    break

            if matched_media_path:
                media_item = check_in_media(
                    artifact_info, report_folder, seeker, files_found + [matched_media_path], matched_media_path, Path(matched_media_path).name
                )

            data_list.append((
                convert_unix_ts_to_utc(int(row[9]) / 1000),  # date_deleted
                convert_unix_ts_to_utc(int(row[10]) / 1000),  # date_expires
                media_item, # the media if it was foun in the data
                row[0],   # file id
                row[1],   # file path
                row[2],   # original file path
                row[3],   # title
                row[4],   # file name
                row[5],   # file size
                row[6],   # mime_type
                row[7],   # package context of deletion
                row[8],   # user_id of deletion
                row[11],  # extra with JSON oinside - addtional info not parsed atm.
                file_found
            ))

    data_headers = (
        ("Date Deleted UTC", "datetime"),
        ("Date Expires UTC", "datetime"),
        ("Media", "media"),
        "Internal ID",
        "Current Trash Path",
        "Original Path",
        "Title (No Extension)",
        "Display Name (File Name)",
        "Size (Bytes)",
        "MIME Type",
        "Delete Package Name",
        "User ID",
        "Extra",
        "Source DB",
    )

    return data_headers, data_list, source_path
