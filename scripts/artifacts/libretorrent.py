# pylint: disable=W0613
__artifacts_v2__ = {
    "get_libretorrent": {
        "name": "Libretorrent",
        "description": "Parses torrents added in LibreTorrent/BitLord (timestamp, name, download path, magnet, paused state and visibility) from libretorrent.db.",
        "author": "",
        "creation_date": "2023-09-12",
        "last_update_date": "2023-09-12",
        "requirements": "none",
        "category": "Libre Torrent",
        "notes": "",
        "paths": ('*/data/com.houseoflife.bitlord/databases/libretorrent.db*', '*/libretorrent.db*'),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_libretorrent(files_found, report_folder, seeker, wrap_text):

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
