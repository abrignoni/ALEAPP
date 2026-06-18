# pylint: disable=W0613,W1309,W1514
__artifacts_v2__ = {
    "get_presisted": {
        "name": "GarminPresistent",
        "description": "Get Information stored in the Garmin Persistent json file",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher, json and datetime",
        "category": "Garmin-Files",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/files/PersistedInstallation*',),
        "output_types": None,
        "artifact_icon": "activity",
    }
}

# Get Information stored in the Garmin Persistent json file
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher, json and datetime
import datetime
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv


def get_presisted(files_found, report_folder, seeker, wrap_text):
    # Dictionary to store the user information
    user_info = {}
    # Attributes to be extracted from the xml file
    attribute = ["Fid", "AuthToken", "RefreshToken", "TokenCreationEpochInSecs", "ExpiresInSecs"]

    logfunc("Processing data for Garmin Presistent file")
    file = str(files_found[0])
    logfunc("Processing file: " + file)
    #Open JSON file
    with open(file, "r") as f:
        data = json.load(f)
        #Get the user information
        for i in attribute:
            if i in data:
                if(i == "TokenCreationEpochInSecs"):
                    user_info[i] = str(data[i]) + " (" + str(datetime.datetime.utcfromtimestamp(data[i])) + ")"
                elif(i == "ExpiresInSecs"):
                    user_info[i] = str(data[i]) + " (" + str(datetime.datetime.utcfromtimestamp(data[i] + data["TokenCreationEpochInSecs"])) + ")"
                else:
                    user_info[i] = data[i]

    if len(user_info) > 0:
        logfunc("Found Garmin Presistent file")
        report = ArtifactHtmlReport('Persistent')
        report.start_artifact_report(report_folder, 'Persistent')
        report.add_script()
        data_headers = ('Name', 'Value')
        data_list = []
        for key, value in user_info.items():
            data_list.append((key, value))
        report.write_artifact_data_table(data_headers, data_list, file)
        report.end_artifact_report()
        tsvname = f'Garmin Log'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc("No Garmin Presistent data found")
