__artifacts_v2__ = {
    "get_puma_users": {
        "name": "PumaUsers",
        "description": "Parses the users table of the Puma Trac database.",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}, @AlexisBrignoni, Codex",
        "creation_date": "2023-03-25",
        "last_update_date": "2026-10-06",
        "requirements": "Python 3.7 or higher",
        "category": "Puma-Trac",
        "notes": "Date of Birth is read as Unix milliseconds. Workout Duration (as stored) "
                 "retains preferences_workoutDuration, including zero and NULL. Workout "
                 "Duration / 60 (unit unverified) preserves the existing division and N/A "
                 "fallback; its unit is not established. An empty profile image URL is "
                 "shown as N/A. Only the first database file found is read.",
        "paths": ('*com.pumapumatrac/databases/pumatrac-db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "html_columns": ['Profile Image URL'],
    }
}

import datetime

_EPOCH_UTC = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

from scripts.html_safe import esc
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_puma_users(context):
    files_found = context.get_files_found()

    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm')
                   and not str(x).endswith('journal')]
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
        # Added to the epoch rather than passed to fromtimestamp: a date of birth can
        # predate 1970, where that function raises gmtime() errors on some platforms.
        dob = _EPOCH_UTC + datetime.timedelta(milliseconds=int(row[4])) if row[4] else ''
        work_time = row[16] / 60 if row[16] else 'N/A'
        # The avatar URL is remote, so an <img> here would make opening the report
        # fetch it and disclose the examination to the service. Report the URL as
        # escaped text instead; the evidence is preserved, nothing is fetched.
        image = esc(row[10]) if row[10] else 'N/A'
        data_list.append((row[0], row[1], row[2], row[3], dob, row[5], row[6], row[7], row[8], row[9], image, row[11], row[12], row[13], row[14], row[15], row[16], work_time))

    data_headers = (('Date of Birth', 'datetime'), 'ID', 'Email', 'Name', 'Gender', 'Weight', 'Height', 'Country', 'Location', 'Interests', 'Profile Image URL', 'Total Score', 'Following Count', 'Followers Count', 'Goal', 'Workout Time of Day', 'Workout Duration (as stored)', 'Workout Duration / 60 (unit unverified)')
    data_list = [(row[4],) + row[:4] + row[5:] for row in data_list]
    return data_headers, data_list, source_path
