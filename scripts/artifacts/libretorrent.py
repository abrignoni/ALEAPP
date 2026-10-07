__artifacts_v2__ = {
    "get_libretorrent": {
        "name": "Torrent Table (libretorrent.db)",
        "description": "Rows from the Torrent table of the first selected libretorrent.db, including stored name, path, magnet and state fields.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-09-12",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Torrent Data",
        "notes": "Selection uses the filename and expected table, not verified app provenance. "
                 "The filename does not establish which app wrote the database, and a row does "
                 "not establish a completed download or user action. Only the first exact main "
                 "is read. Timestamp uses the existing dateAdded millisecond conversion. "
                 "No cache lifecycle or writing-app ownership is inferred.",
        "paths": ('*/libretorrent.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_libretorrent(context):
    files_found = context.get_files_found()

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('libretorrent.db'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('''
            SELECT id, name, downloadPath, dateAdded, error, manuallyPaused, magnet, downloadingMetadata, visibility
            FROM Torrent
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(row[3] / 1000, datetime.timezone.utc) if row[3] else ''
            data_list.append((timestamp, row[0], row[1], row[2], row[4], row[5], row[6], row[7], row[8]))

    data_headers = (('Timestamp', 'datetime'), 'ID', 'Name', 'Download Path', 'Error', 'Manually Paused', 'Magnet', 'Downloading Metadata', 'Visibility')
    return data_headers, data_list, source_path
