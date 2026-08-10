__artifacts_v2__ = {
    "get_nike_notifications": {
        "name": "NikeNotifications",
        "description": "Get Information relative to the notifications stored in the database of the Nike Run Club Mobile application",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-03-18",
        "last_update_date": "2023-03-18",
        "requirements": "Python 3.7 or higher",
        "category": "Nike-Run",
        "notes": "",
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

    files_found = [x for x in files_found if not str(x).endswith('-journal')]
    source_path = str(files_found[0])
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
        read = 'No' if row[6] == 0 else 'Yes'
        deleted = 'No' if row[7] == 0 else 'Yes'
        data_list.append((row[0], row[1], row[2], timestamp, row[4], row[5], read, deleted))

    data_headers = ('ID', 'Sender User ID', 'Sender App ID', ('Notification Timestamp', 'datetime'), 'Notification Type', 'Message', 'Read', 'Deleted')
    return data_headers, data_list, source_path
