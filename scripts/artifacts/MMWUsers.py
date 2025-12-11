# Get Information related to the user from the Map My Walk app
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-25
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_map_users(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Map My Walk Users")
    files_found = [x for x in files_found if not x.endswith('-journal') and not x.endswith('_gear') and not x.endswith('_gear-journal')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    # Get information from the table device_sync_audit
    cursor = db.cursor()
    cursor.execute('''
        Select id, username, email, display_name, birthdate, gender, height, weight, timezone,  datetime("date_joined"/1000,'unixepoch'),  datetime("last_login"/1000,'unixepoch'), location_country, profile_image_medium
        from user_entity
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} entries in users")
        report = ArtifactHtmlReport('User')
        report.start_artifact_report(report_folder, 'Map-My-Walk User')
        report.add_script()
        data_headers = ('ID', 'Username', 'Email', 'Name', 'Birthdate', 'Gender', 'Height', 'Weight', 'Timezone', 'Date Joined', 'Last Login', 'Location Country', 'Profile Image URL')
        data_list = []
        for row in all_rows:
            height = row[6]
            height = round(height, 2)
            weight = row[7]
            weight = round(weight, 2)
            if row[12]:
                image = '<img src="'+row[12]+'" alt="'+row[10]+'" width="50" height="50">'
            else:
                image = 'N/A'

            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], height, weight, row[8], row[9], row[10], row[11], image))

        # Filter by date
        table_id = "MapUsers"
        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id, html_escape=False)
        report.end_artifact_report()

        tsvname = f'Map - User'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Map - User'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Map My Walk Users data available')

    db.close()


__artifacts__ = {
    "MapUsers": (
        "Map-My-Walk",
        ('*com.mapmywalk.android2/databases/mmdk_user*'),
        get_map_users)
}
