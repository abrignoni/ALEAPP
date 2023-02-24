# Get JSON information from the Garmin GCM database
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher and json module
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_garmin_json(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin JSON")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm') and not x.endswith('journal')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    cursor = db.cursor()
    cursor.execute('''
    SELECT  
    _id, 
    datetime("saved_timestamp"/1000, 'unixepoch'),
    concept_name,
    cached_val
    from json
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} JSON entries")
        report = ArtifactHtmlReport('JSON')
        report.start_artifact_report(report_folder, 'JSON')
        report.add_script()
        data_headers = ('_id', 'saved_timestamp', 'concept_id', 'json')
        data_list = []

        for row in all_rows:
            jsonData = row[3]
            # convert to json
            jsonData = jsonData.replace('\"', '"')
            jsonData = jsonData.replace('"{', '{')
            jsonData = jsonData.replace('}"', '}')
            jsonData = json.loads(jsonData)
            jsonData = json.dumps(jsonData, indent=4, sort_keys=True)
            # replace " with &quot; to avoid breaking the html
            jsonData = jsonData.replace('"', '&quot;')
            data_list.append((row[0], row[1], row[2], '<button class="btn btn-light btn-sm" onclick="changeJSONHidden(this)" value="'+jsonData+'">View</button>'))

        table_id = "garmin_json"
        report.filter_by_date(table_id, 1)
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False, table_id=table_id)

        # Insert pretty JSON into the report
        i = 0
        for row in all_rows:
            jsonData = row[3]
            #convert to json
            jsonData = jsonData.replace('\"', '"')
            jsonData = jsonData.replace('"{', '{')
            jsonData = jsonData.replace('}"', '}')
            jsonData = json.loads(jsonData)
            jsonData = json.dumps(jsonData, indent=4, sort_keys=True)
            if i == 0:
                report.add_json_to_artifact("Response", jsonData, False, row[0], True)
            i += 1

        report.end_artifact_report()

        tsvname = f'Garmin - JSON'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Garmin - JSON'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Garmin JSON data available')

    db.close()


__artifacts__ = {
    "GarminJson": (
        "Garmin-GCM",
        ('*/com.garmin.android.apps.connectmobile/databases/gcm_cache*'),
        get_garmin_json)
}
