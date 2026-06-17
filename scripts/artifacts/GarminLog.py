__artifacts_v2__ = {
    "get_log": {
        "name": "GarminLog",
        "description": "Get Information stored in the Garmin Log file",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher",
        "category": "Garmin-Files",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/files/logs/app.log*',),
        "output_types": None,
        "artifact_icon": "activity",
    }
}

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv


def get_log(files_found, report_folder, seeker, wrap_text):
    # Dictionary to store the user information
    user_info = {}
    # Attributes to be extracted from the xml file
    attribute = ["access_token", "expires_in", "refresh_token", "token_type", "id_token", "Authorization"]
    auth = False
    logfunc("Processing data for Garmin Logs")
    file = str(files_found[0])
    logfunc("Processing file: " + file)
    #Open text file
    with open(file, "r") as f:
        # Read the file line by line
        for line in f:
            # Get the user information
            for i in attribute:
                if i in line:
                    if i == "Authorization" and auth == False:
                        value = line.split(":")[1].strip()
                        # Split by ,
                        value = value.split(",")
                        # Get different values
                        for j in value:
                            # Split by =
                            j = j.split("=")
                            user_info[j[0].strip()] = j[1].strip()
                        auth = True
                    else:
                        # Get value from line after :
                        value = line.split(":")[1].strip()
                        # Remove "
                        value = value.replace('"', '')
                        # Remove ,
                        value = value.replace(',', '')
                        # Add to dictionary
                        user_info[i] = value

    if len(user_info) > 0:
        logfunc("Found Garmin Log file")
        report = ArtifactHtmlReport('Log')
        report.start_artifact_report(report_folder, 'Log')
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
        logfunc("No Garmin Log data found")

