__artifacts_v2__ = {
    "get_puma_users": {
        "name": "PumaUsers",
        "description": "Get Information related to the users table in the Puma Trac database",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-03-25",
        "last_update_date": "2023-03-25",
        "requirements": "Python 3.7 or higher",
        "category": "Puma-Trac",
        "notes": "",
        "paths": ('*com.pumapumatrac/databases/pumatrac-db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "html_columns": ['Profile Image URL'],
    }
}

import datetime

from scripts.html_safe import esc
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_puma_users(context):
    files_found = context.get_files_found()

    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        Select id, email, name, sex, dateOfBirth, weight, height, country, location, interestsIds,
               profileImageUrl, totalScore, followingCount, followersCount, goal_id,
               preferences_workoutTimeOfDay, preferences_workoutDuration
        from users
    ''')
    all_rows = cursor.fetchall()
    db.close()
    logfunc(f"Found {len(all_rows)} entries in users")

    data_list = []
    for row in all_rows:
        dob = datetime.datetime.fromtimestamp(int(row[4]) / 1000, datetime.timezone.utc) if row[4] else ''
        work_time = row[16] / 60 if row[16] else 'N/A'
        image = '<img src="' + esc(row[10]) + '" alt="' + esc(row[10]) + '" width="50" height="50">' if row[10] else 'N/A'
        data_list.append((row[0], row[1], row[2], row[3], dob, row[5], row[6], row[7], row[8], row[9], image, row[11], row[12], row[13], row[14], row[15], work_time))

    data_headers = ('ID', 'Email', 'Name', 'Gender', ('Date of Birth', 'datetime'), 'Weight', 'Height', 'Country', 'Location', 'Interests', 'Profile Image URL', 'Total Score', 'Following Count', 'Followers Count', 'Goal', 'Workout Time of Day', 'Workout Duration')
    return data_headers, data_list, source_path
