# pylint: disable=W0613
__artifacts_v2__ = {
    "get_skout_messages": {
        "name": "Skout Messages",
        "description": "Parses Skout messages (timestamp, user, message, type, picture and gift URLs and thread) from the Skout database.",
        "author": "",
        "creation_date": "2021-05-10",
        "last_update_date": "2021-05-10",
        "requirements": "none",
        "category": "Skout",
        "notes": "",
        "paths": ('*/com.skout.android/databases/skoutDatabase*',),
        "output_types": "standard",
        "artifact_icon": "message",
    },
    "get_skout_users": {
        "name": "Skout Users",
        "description": "Parses Skout users (last message timestamp, user name, picture URL and user ID) from the Skout database.",
        "author": "",
        "creation_date": "2021-05-10",
        "last_update_date": "2021-05-10",
        "requirements": "none",
        "category": "Skout",
        "notes": "",
        "paths": ('*/com.skout.android/databases/skoutDatabase*',),
        "output_types": "standard",
        "artifact_icon": "users",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_skout_messages(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('skoutDatabase'):
            source_path = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            strftime('%Y-%m-%d %H:%M:%S.', "timestamp"/1000, 'unixepoch') || ("timestamp"%1000) AS MessageTime,

            ifnull(skoutUsersTable.userName,'(local user)') AS SkoutUser,

            skoutMessagesTable.message,
            skoutMessagesTable.type,
            skoutMessagesTable.pictureUrl,
            skoutMessagesTable.giftUrl,
            skoutMessagesTable.chatId AS ThreadID

            FROM skoutMessagesTable
                LEFT JOIN skoutUsersTable ON skoutMessagesTable.fromUserID = skoutUsersTable.userId

                ORDER BY skoutMessagesTable.chatId,
                skoutMessagesTable.timestamp
            ''')

            all_rows = cursor.fetchall()
            for row in all_rows:
                data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],row[4],row[5],row[6]))

            db.close()

    data_headers = (
        ('Timestamp', 'datetime'),
        'User',
        'Message',
        'Type',
        'Picture URL',
        'Gift URL',
        'Thread ID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def get_skout_users(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('skoutDatabase'):
            source_path = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            strftime('%Y-%m-%d %H:%M:%S.', "lastMessageTimestamp"/1000, 'unixepoch') || ("lastMessageTimestamp"%1000) AS LastMessageTime,
            skoutUsersTable.userName,
            skoutUsersTable.picUrl,
            skoutUsersTable.userId AS UserID
            FROM skoutUsersTable
            ORDER BY skoutUsersTable.lastMessageTimestamp
            ''')

            all_rows = cursor.fetchall()
            for row in all_rows:
                data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3]))

            db.close()

    data_headers = (
        ('Last Message Timestamp', 'datetime'),
        'User',
        'Picture URL',
        'User ID',
    )
    return data_headers, data_list, source_path
