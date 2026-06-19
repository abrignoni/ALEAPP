# pylint: disable=W0613
__artifacts_v2__ = {
    "get_presisted": {
        "name": "Garmin - Persistent",
        "description": "Get Information stored in the Garmin Persistent json file",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher, json and datetime",
        "category": "Garmin-Files",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/files/PersistedInstallation*',),
        "output_types": ['html', 'tsv', 'lava'],
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

from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_presisted(files_found, report_folder, seeker, wrap_text):
    # Dictionary to store the user information
    user_info = {}
    # Attributes to be extracted from the json file
    attribute = ["Fid", "AuthToken", "RefreshToken", "TokenCreationEpochInSecs", "ExpiresInSecs"]

    logfunc("Processing data for Garmin Presistent file")
    source_path = str(files_found[0])
    logfunc("Processing file: " + source_path)
    # Open JSON file
    with open(source_path, "r", encoding='utf-8') as f:
        data = json.load(f)
        # Get the user information
        for i in attribute:
            if i in data:
                if i == "TokenCreationEpochInSecs":
                    user_info[i] = str(data[i]) + " (" + str(datetime.datetime.fromtimestamp(data[i], datetime.timezone.utc).replace(tzinfo=None)) + ")"
                elif i == "ExpiresInSecs":
                    user_info[i] = str(data[i]) + " (" + str(datetime.datetime.fromtimestamp(data[i] + data["TokenCreationEpochInSecs"], datetime.timezone.utc).replace(tzinfo=None)) + ")"
                else:
                    user_info[i] = data[i]

    data_list = []
    for key, value in user_info.items():
        data_list.append((key, value))

    data_headers = ('Name', 'Value')
    return data_headers, data_list, source_path
