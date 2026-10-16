__artifacts_v2__ = {
    "get_Zapya": {
        "name": "Zapya",
        "description": "Reports Zapya transfer records with the stored direction and recorded device, name, timestamp, path and title from transfer20.db.",
        "author": "@markmckinnon, @AlexisBrignoni, Codex",
        "creation_date": "2020-03-21",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "File Transfer",
        "notes": ("Direction (as stored) preserves the transfer table direction value without "
                  "assigning a transfer direction. Recorded Device is the stored device field; "
                  "its sender or recipient role is not established. No source or measurement "
                  "for direction or device-role meanings is recorded here."),
        "paths": ('*/com.dewmobile.kuaiya.play/databases/transfer20.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_Zapya(context):
    files_found = context.get_files_found()

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT device, name, direction, createtime/1000, path, title FROM transfer
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        createtime = datetime.datetime.fromtimestamp(int(row[3]), datetime.timezone.utc) if row[3] else ''
        data_list.append((createtime, row[0], row[1], row[2], row[4], row[5]))

    data_headers = (('createtime', 'datetime'), 'Recorded Device', 'Name',
                    'Direction (as stored)', 'path', 'title')
    return data_headers, data_list, source_path
