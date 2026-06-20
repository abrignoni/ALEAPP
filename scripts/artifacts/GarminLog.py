# pylint: disable=W0613
__artifacts_v2__ = {
    "get_log": {
        "name": "GarminLog",
        "description": "Get Information stored in the Garmin Log file",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/files/logs/app.log*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
    }
}

from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_log(files_found, report_folder, seeker, wrap_text):
    user_info = {}
    attribute = ["access_token", "expires_in", "refresh_token", "token_type", "id_token", "Authorization"]
    auth = False
    logfunc("Processing data for Garmin Logs")
    source_path = str(files_found[0])
    logfunc("Processing file: " + source_path)

    with open(source_path, "r", encoding='utf-8', errors='replace') as f:
        for line in f:
            for i in attribute:
                if i in line:
                    if i == "Authorization" and auth is False:
                        value = line.split(":")[1].strip().split(",")
                        for j in value:
                            j = j.split("=")
                            user_info[j[0].strip()] = j[1].strip()
                        auth = True
                    else:
                        value = line.split(":")[1].strip().replace('"', '').replace(',', '')
                        user_info[i] = value

    data_list = []
    for key, value in user_info.items():
        data_list.append((key, value))

    data_headers = ('Name', 'Value')
    return data_headers, data_list, source_path
