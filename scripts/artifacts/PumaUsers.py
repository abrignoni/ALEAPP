# Get Information related to the users table in the Puma Trac database
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-25
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_puma_users(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Puma Users")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    # Get information from the table device_sync_audit
    cursor = db.cursor()
    cursor.execute('''
        Select id, email, name, sex, datetime("dateOfBirth"/1000,'unixepoch'), weight, height, country, location, interestsIds, profileImageUrl, totalScore, followingCount, followersCount, goal_id, preferences_workoutTimeOfDay, preferences_workoutDuration
        from users
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} entries in users")
        report = ArtifactHtmlReport('User')
        report.start_artifact_report(report_folder, 'Puma User')
        report.add_script()
        data_headers = ('ID', 'Email', 'Name', 'Gender', 'Date of Birth', 'Weight', 'Height', 'Country', 'Location', 'Interests', 'Profile Image URL', 'Total Score', 'Following Count', 'Followers Count', 'Goal', 'Workout Time of Day', 'Workout Duration')
        data_list = []
        for row in all_rows:
            work_time = row[16]
            if work_time:
                # convert to minutes
                work_time = work_time / 60
            else:
                work_time = 'N/A'
            if row[10]:
                image = '<img src="'+row[10]+'" alt="'+row[10]+'" width="50" height="50">'
            else:
                image = 'N/A'

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], image, row[11], row[12], row[13], row[14], row[15], work_time))

        # Filter by date
        table_id = "PumaUsers"
        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id, html_escape=False)
        report.end_artifact_report()

        tsvname = f'Puma - User'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Puma - User'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Puma Users data available')

    db.close()


__artifacts__ = {
    "PumaUsers": (
        "Puma-Trac",
        ('*com.pumapumatrac/databases/pumatrac-db*'),
        get_puma_users)
}
