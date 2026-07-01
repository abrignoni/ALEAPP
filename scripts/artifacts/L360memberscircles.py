__artifacts_v2__ = {
    'Life360_MemberCircles': {
        'name': 'Life360 Members and Circles',
        'description': 'Parses Life360 Members and Circles',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-06-10',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/MembersEngineRoomDatabase*',),
        'output_types': 'standard',
        'artifact_icon': 'user'
    }
}

from datetime import datetime, timezone
from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    logfunc
)

@artifact_processor
def Life360_MemberCircles(context):

    data_list = []

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'MembersEngineRoomDatabase')

    query = '''
    SELECT 
        members.created_at AS "Created Timestamp",
        members.last_updated AS "Last Updated Timestamp",
        members.id AS "Member ID", 
        members.first_name AS "First Name",
        members.last_name AS "Last Name", 
        members.login_email AS "Email",
        members.login_phone AS "Phone Number", 
        members.avatar AS "Avatar",
        members.is_admin AS "Admin", 
        members.role AS "Role",
        circles.created_at AS "Circle Created Timestamp",
        circles.last_updated AS "Circle Last Updated Timestamp",
        circles.name  AS "Circle Name"
    FROM members 
    LEFT JOIN circles
    ON members.circle_id = circles.id
    '''

    try:
        db_records = get_sqlite_db_records(source_path, query)

        logfunc(f'Life360_MemberCircles: Records found = {len(db_records)}')

        for record in db_records:

            created_timestamp = datetime.fromtimestamp(int(record[0]), tz=timezone.utc)
            updated_timestamp = datetime.fromtimestamp(int(record[1]) / 1000, tz=timezone.utc)
            second_created_timestamp = datetime.fromtimestamp(int(record[10]), tz=timezone.utc)
            second_updated_timestamp = datetime.fromtimestamp(int(record[11]) / 1000, tz=timezone.utc)

            data_list.append((created_timestamp, updated_timestamp, record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9], second_created_timestamp,second_updated_timestamp, record[12]))

    except Exception as e:
        logfunc(f'Error processing Life360 MemberCircles: {e}')

    data_headers = (('Created Timestamp', 'datetime'), ('Updated Timestamp', 'datetime'), 'Member ID', 'First Name', 'Last Name', 'Email', 'Phone Number', 'Avatar', 'Admin', 'Role', ('Circle Created Timestamp', 'datetime'), ('Circle Updated Timestamp', 'datetime'), 'Circle Name')

    return data_headers, data_list, source_path