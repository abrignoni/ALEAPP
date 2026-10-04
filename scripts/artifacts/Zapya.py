__artifacts_v2__ = {
    "get_Zapya": {
        "name": "Zapya",
        "description": "Parses Zapya file transfer records (device, name, direction, timestamp, path and title) from the transfer20.db database.",
        "author": "@markmckinnon",
        "creation_date": "2020-03-21",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "File Transfer",
        "notes": ("direction is decoded from the transfer table 'direction' column. "
                  "direction = 1 is shown as Outgoing. No source or measurement for that reading "
                  "is recorded here, so it is this parser's label and not an established "
                  "meaning. Any other value is reported as stored.\nfromid is blank on every "
                  "row. toid "
                  "repeats the Device value when direction is 1 and is blank otherwise; the "
                  "other device recorded on the row is reported in the Device column regardless."),
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
        from_id = ''
        to_id = ''
        # Only direction = 1 is identified; any other value is reported as stored and
        # neither party is claimed.
        direction = {1: 'Outgoing'}.get(row[2], '' if row[2] is None else row[2])
        if direction == 'Outgoing':
            to_id = row[0]

        createtime = datetime.datetime.fromtimestamp(int(row[3]), datetime.timezone.utc) if row[3] else ''
        data_list.append((row[0], row[1], direction, from_id, to_id, createtime, row[4], row[5]))

    data_headers = ('Device', 'Name', 'direction', 'fromid', 'toid', ('createtime', 'datetime'), 'path', 'title')
    return data_headers, data_list, source_path
