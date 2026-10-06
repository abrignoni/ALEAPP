__artifacts_v2__ = {
    "get_nike_notifications": {
        "name": "NikeNotifications",
        "description": "Rows of the inbox table in the Nike Run Club ns_inbox.db database, with "
                       "the stored sender, timestamp, type, message, read and deleted values",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}, @AlexisBrignoni, Codex",
        "creation_date": "2023-03-18",
        "last_update_date": "2026-10-06",
        "requirements": "Python 3.7 or higher",
        "category": "Nike-Run",
        "notes": "Read (as stored) and Deleted (as stored) preserve the inbox values, "
                 "including NULL, zero and unknown codes; their app semantics are not "
                 "established. Only the first exact ns_inbox.db main database is read; "
                 "SQLite uses its adjacent sidecars. Notification Timestamp retains the "
                 "existing Unix-millisecond conversion. The registered UserB2 sample "
                 "recorded zero rows, so positive genuine coverage remains unavailable.",
        "paths": ('*/com.nike.plusgps/databases/ns_inbox.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "userb2_a13": "Android 13 | com.nike.plusgps vc 1717303105 | 0 rows",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_nike_notifications(context):
    files_found = context.get_files_found()

    data_headers = (('Notification Timestamp', 'datetime'), 'ID', 'Sender User ID',
                    'Sender App ID', 'Notification Type', 'Message',
                    'Read (as stored)', 'Deleted (as stored)')
    source_path = next((str(path) for path in files_found
                        if str(path).replace('\\', '/').rsplit('/', 1)[-1] == 'ns_inbox.db'), '')
    if not source_path:
        logfunc('Nike notifications: no exact ns_inbox.db main database found; sidecars skipped')
        return data_headers, [], ''
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        Select _id, sender_user_id, sender_app_id, notification_timestamp,
               notification_type, message, read, deleted
        from inbox
    ''')
    all_rows = cursor.fetchall()
    db.close()
    logfunc(f"Found {len(all_rows)} notifications")

    data_list = []
    for row in all_rows:
        timestamp = datetime.datetime.fromtimestamp(int(row[3]) / 1000, datetime.timezone.utc) if row[3] else ''
        data_list.append((timestamp, row[0], row[1], row[2], row[4], row[5], row[6], row[7]))

    return data_headers, data_list, source_path
