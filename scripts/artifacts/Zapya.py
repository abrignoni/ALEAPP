# pylint: disable=W0613
__artifacts_v2__ = {
    "get_Zapya": {
        "name": "Zapya",
        "description": "Parses Zapya file transfer records (device, name, direction, timestamp, path and title) from the transfer20.db database.",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "File Transfer",
        "notes": "",
        "paths": ('*/com.dewmobile.kuaiya.play/databases/transfer20.db*',),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_Zapya(files_found, report_folder, seeker, wrap_text):

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
        from_id = ''
        to_id = ''
        if row[2] == 1:
            direction = 'Outgoing'
            to_id = row[0]
        else:
            direction = 'Incoming'
            from_id = row[0]

        createtime = datetime.datetime.fromtimestamp(int(row[3]), datetime.timezone.utc) if row[3] else ''
        data_list.append((row[0], row[1], direction, from_id, to_id, createtime, row[4], row[5]))

    data_headers = ('Device', 'Name', 'direction', 'fromid', 'toid', ('createtime', 'datetime'), 'path', 'title')
    return data_headers, data_list, source_path
