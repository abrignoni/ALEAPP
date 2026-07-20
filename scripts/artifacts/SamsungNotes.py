__artifacts_v2__ = {
  
    "snotes": {
        "name": "Samsung Notes",
        "description": "Samsung Notes",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2026-01-17",
        "last_update_date": "2026-01-17",
        "requirements": "os",
        "category": "Notes",
        "notes": "",
        "output_types": ["standard"],
        "paths": (  '*/com.samsung.android.app.notes/databases/sdoc.db*',
                    '*/user/*/com.samsung.android.app.notes/SDocData/*/media/*'),
        "artifact_icon": "edit",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.app.notes vc 443081000 | 2 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.app.notes vc 442923000 | 7 rows",
            "sharon_a14": "Android 14 | com.samsung.android.app.notes vc 441305000 | 1 row",
        }
    }

}

# Android Samsung Notes App (com.samsung.android.app.notes)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Tested Version: 4.4.30.91
import os
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, check_in_media

@artifact_processor
def snotes(files_found, _report_folder, _seeker, _wrap_text):

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

        # Require an actual file so a matched directory is never passed to
        # check_in_media (which returns None for a directory), and only keep truthy
        # refs so no None lands in the media list -- a None serialized to null in
        # the json.dumps'd media cell crashes the LAVA viewer on hover.
        media_refs = []
        for media_path in medias:
            if os.path.isfile(media_path) and os.path.basename(file_path) in media_path:
                ref = check_in_media(media_path, os.path.basename(media_path))
                if ref:
                    media_refs.append(ref)
        if len(media_refs) == 1:
            media = media_refs[0]
        elif media_refs:
            media = media_refs
        else:
            media = ''

        data_list.append((  created,
                            last_modified,
                            title,
                            content,
                            is_deleted,
                            deleted,
                            first_opened,
                            second_opened,
                            last_opened,
                            media)
                        )

    data_headers = (
                        ('Creation Time', 'datetime'),
                        ('Last Modification Time', 'datetime'),
                        'Title',
                        'Text Content',
                        'Deleted?',
                        ('Deletion Time', 'datetime'),
                        ('First Opened Time', 'datetime'),
                        ('Second Opened Time', 'datetime'),
                        ('Last Opened Time', 'datetime'),
                        ('Media', 'media')
                    )

    return data_headers, data_list, files_found[0]
