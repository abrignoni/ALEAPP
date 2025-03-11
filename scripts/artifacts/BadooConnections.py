# Get Information related to possible connections (messages, views etc) of the user with other users from the Badoo app (com.badoo.mobile)
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-05-03
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_badoo_conn(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Badoo Conections")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    cursor = db.cursor()
    cursor.execute('''
        Select id, name, gender, origin, datetime("sort_timestamp"/1000,'unixepoch'), avatar_url, display_message
        from connection
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} entries in connection")
        report = ArtifactHtmlReport('Chat')
        report.start_artifact_report(report_folder, 'Badoo Connections')
        report.add_script()
        data_headers = ('ID', 'Name', 'Gender', 'Origin', 'Sort Timestamp', 'Avatar URL', 'Display Message')
        data_list = []

        for row in all_rows:
            id = row[0]
            name = row[1]
            gender = row[2]
            origin = row[3]
            sort_timestamp = row[4]
            avatar_url = '<img src="' + row[5] + '" width="100" height="100">'
            display_message = row[6]
            data_list.append((id, name, gender, origin, sort_timestamp, avatar_url, display_message))
        # Filter by date
        table_id = "BadooConnection"
        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=table_id, html_escape=False)
        report.end_artifact_report()

        tsvname = f'Badoo - Connections'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Badoo - Connections'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Badoo Connection data available')

    db.close()


__artifacts__ = {
    "BadooConnections": (
        "Badoo",
        ('*com.badoo.mobile/databases/CombinedConnectionsDatabase*'),
        get_badoo_conn)
}
