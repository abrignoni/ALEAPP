__artifacts_v2__ = {
    "get_keepNotes": {
        "name": "Google Keep Notes",
        "description": "Parses Google Keep Notes",
        "author": "Heather Charpentier",
        "creation_date": "2024-12-02",
        "last_update_date": "2026-08-10",
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
            "russell_pixel6a_a13": "Android 13 | com.google.android.keep vc 220522207 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.keep vc 220589177 | 0 rows",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, does_table_exist_in_db, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_keepNotes(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)

        if filename.endswith('keep.db'):
            source_path = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            if does_table_exist_in_db(file_found, 'text_search_note_content_content'):
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
            else:
                # Older keep.db generations have no FTS shadow table; note text
                # lives in list_item instead. Fallback from community PR #638,
                # exercised against the contributor's database only, not a
                # registered corpus image.
                cursor.execute('''
                SELECT
                    datetime(tree_entity.time_created/1000, 'unixepoch') AS "Time Created",
                    datetime(tree_entity.time_last_updated/1000, 'unixepoch') AS "Time Last Updated",
                    datetime(tree_entity.user_edited_timestamp/1000, 'unixepoch') AS "User Edited Timestamp",
                    tree_entity.title AS Title,
                    list_item.text AS "Text",
                    tree_entity.last_modifier_email AS "Last Modifier Email"
                FROM tree_entity
                LEFT JOIN list_item ON tree_entity._id = list_item._id
                WHERE tree_entity.title IS NOT NULL OR list_item.text IS NOT NULL
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
