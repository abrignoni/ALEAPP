# Android Samsung Notes App (com.samsung.android.app.notes)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Tested Version: 4.4.30.91


__artifacts_v2__ = {
  
    "snotes": {
        "name": "Samsung Notes",
        "description": "Samsung Notes",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2026-01-17",
        "last_update_date": "2026-01-17",
        "requirements": "os",
        "category": "Notes",
        "notes": "",
        "output_types": ["standard"],
        "html_columns": ["Media"],
        "paths": (  '*/com.samsung.android.app.notes/databases/sdoc.db*',
                    '*/user/*/com.samsung.android.app.notes/SDocData/*/media/*'),
        "artifact_icon": "edit"
    }

}

import os
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, media_to_html

@artifact_processor
def snotes(files_found, report_folder, _seeker, _wrap_text):

    main_db = ''
    medias = []

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('sdoc.db'):
            main_db = file_found

        if 'media' in os.path.dirname(file_found):
            if not file_found.endswith('dat') and not file_found.endswith('spi'):
                medias.append(file_found)

    query = ('''
        SELECT
        sd.createdAt,
        sd.lastModifiedAt,
        sd.title,
        sd.content,
        sd.isDeleted ,
        sd.recycle_bin_time_moved,
        sd.firstOpendAt,
        sd.secondOpenedAt,
        sd.lastOpenedAt,
        sd.filePath
        FROM sdoc sd
    ''')

    data_list = []

    db_records = get_sqlite_db_records(main_db, query)

    for row in db_records:
        created = convert_unix_ts_to_utc(int(row[0])/1000)
        last_modified = convert_unix_ts_to_utc(int(row[1])/1000)
        title = row[2]
        content = row[3].decode('utf-8')
        is_deleted = row[4]
        deleted = convert_unix_ts_to_utc(int(row[5])/1000)
        first_opened = convert_unix_ts_to_utc(int(row[6])/1000)
        second_opened = convert_unix_ts_to_utc(int(row[7])/1000)
        last_opened = convert_unix_ts_to_utc(int(row[8])/1000)
        file_path = row[9]

        media = []
        for media_path in medias:
            if os.path.basename(file_path) in media_path:
                media.append(media_to_html(os.path.basename(media_path), medias, report_folder))

        data_list.append(( created, last_modified, title, content, is_deleted, deleted, first_opened, second_opened, last_opened, media))

    data_headers = ('Creation Time' , 'Last Modification TIme', 'Title', 'Text Content', 'Deleted?', 'Deletion Time', 'First Opened Time', 'Second Opened Time', 'Last Opened Time', 'Media')

    return data_headers, data_list, files_found[0]
