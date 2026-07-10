# pylint: disable=W0613
__artifacts_v2__ = {
    "get_keepNotes": {
        "name": "Google Keep Notes",
        "description": "Parses Google Keep Notes",
        "author": "Heather Charpentier",
        "creation_date": "2024-12-02",
        "last_update_date": "2024-12-02",
        "requirements": "none",
        "category": "Google Keep Notes",
        "notes": "",
        "paths": ('*/data/com.google.android.keep/databases/keep.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.keep vc 220663535 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.keep vc 220627544 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.keep vc 220548335 | 2 rows",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_keepNotes(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)

        if filename.endswith('keep.db'):
            source_path = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
                datetime(tree_entity.time_created/1000, 'unixepoch') AS "Time Created",
                datetime(tree_entity.time_last_updated/1000, 'unixepoch') AS "Time Last Updated",
                datetime(tree_entity.user_edited_timestamp/1000, 'unixepoch') AS "User Edited Timestamp",
                tree_entity.title AS Title,
                text_search_note_content_content.c0text AS "Text",
                tree_entity.last_modifier_email AS "Last Modifier Email"
            FROM text_search_note_content_content
            INNER JOIN tree_entity ON text_search_note_content_content.docid = tree_entity._id
            ''')

            all_rows = cursor.fetchall()
            for row in all_rows:
                data_list.append((convert_human_ts_to_utc(row[0]), convert_human_ts_to_utc(row[1]), convert_human_ts_to_utc(row[2]), row[3], row[4], row[5]))
            db.close()

    data_headers = (
        ('Time Created', 'datetime'),
        ('Time Last Updated', 'datetime'),
        ('User Edited Timestamp', 'datetime'),
        'Title',
        'Text',
        'Last Modifier Email',
    )
    return data_headers, data_list, source_path
