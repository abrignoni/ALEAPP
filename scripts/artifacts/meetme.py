# pylint: disable=W0613,W0631
__artifacts_v2__ = {
    "get_meetmechats": {
        "name": "MeetMe Chats",
        "description": "Parses MeetMe Chat database",
        "author": "Matt Beers",
        "creation_date": "2024-12-27",
        "last_update_date": "2024-12-27",
        "requirements": "none",
        "category": "Chats",
        "notes": "",
        "paths": ('*/data/com.myyearbook.m/databases/chats.db*'),
        "output_types": "standard",
        "artifact_icon": "users",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_meetmechats(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('chats.db'):
            source_path = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            messages.sent_at,
            messages.thread_id,
            members.first_name,
            members.last_name,
            messages.sent_by,
            messages.body,
            messages.type,
            messages.local_path
            FROM
            messages
            LEFT JOIN
            members
            ON
            members.member_id = messages.sent_by
            ORDER BY
            messages.thread_id,
            messages.sent_at;
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
            db.close()

        else:
            continue

    data_headers = (
        ('Timestamp', 'datetime'),
        'Thread ID',
        'First Name',
        'Last Name',
        'Sent By',
        'Message Text',
        'Type',
        'Attachment Path',
    )
    return data_headers, data_list, source_path
