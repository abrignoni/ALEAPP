__artifacts_v2__ = {
    'Life360_MemberCircles': {
        'name': 'Life360 Members and Circles',
        'description': 'Parses Life360 Members and Circles. created_at is read as Unix seconds and last_updated as Unix milliseconds; no source for those units is recorded here.',
        'author': '@AlexisBrignoni, Codex',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-10-05',
        'requirements': 'none',
        'category': 'Life360',
        'notes': 'Original parser by Heather Charpentier. Invalid or absent timestamps are left blank in converted date columns; the four stored values are retained in raw columns. The existing seconds/milliseconds interpretations remain unverified.',
        'paths': ('*/com.life360.android.safetymapd/databases/MembersEngineRoomDatabase*',),
        'output_types': 'standard',
        'artifact_icon': 'user',
        'sample_data': {
            'hc_pixel8pro_a16': 'Android 16 | com.life360.android.safetymapd vc 2897710 | 4 rows',
            'pixel7a_a14': 'Android 14 | com.life360.android.safetymapd vc 294540 | 3 rows',
        }
    }
}

from datetime import datetime, timezone
from scripts.ilapfuncs import (
    artifact_processor,
    null_absent_columns,
    get_file_path,
    get_sqlite_db_records,
    logfunc
)


def _timestamp(value, divisor=1):
    """Keep rows when a stored timestamp cannot be converted."""
    try:
        return datetime.fromtimestamp(int(value) / divisor, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


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
        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        for record in db_records:

            data_list.append((
                _timestamp(record[0]), _timestamp(record[1], 1000),
                _timestamp(record[10]), _timestamp(record[11], 1000),
                *record[2:10], record[12],
                record[0], record[1], record[10], record[11]
            ))

    except Exception as e:  # pylint: disable=broad-exception-caught
        logfunc(f'Error processing Life360 MemberCircles: {e}')

    data_headers = (
        ('Created Timestamp', 'datetime'), ('Updated Timestamp', 'datetime'),
        ('Circle Created Timestamp', 'datetime'), ('Circle Updated Timestamp', 'datetime'),
        'Member ID', 'First Name', 'Last Name', 'Email', 'Phone Number', 'Avatar', 'Admin',
        'Role', 'Circle Name', 'Raw Member Created At', 'Raw Member Last Updated',
        'Raw Circle Created At', 'Raw Circle Last Updated'
    )

    return data_headers, data_list, source_path
