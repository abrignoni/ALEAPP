# Get User information from the xml file com.fitnesskeeper.runkeeper.pro_preferences.xml in the Runkeeper app related to the user
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-25
# Version: 1.0
# Requirements: Python 3.7 or higher and ElementTree
import datetime
import xml.etree.ElementTree as ET


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline


# remove whitespace from xml first line
def remove_whitespace_from_xml_first_line(xml_file):
    with open(xml_file, 'r') as f:
        lines = f.readlines()
    #replace first line with <?xml version='1.0' encoding='utf-8' standalone='yes' ?>
    lines[0] = '<?xml version=\'1.0\' encoding=\'utf-8\' standalone=\'yes\' ?>\n'
    with open(xml_file, 'w') as f:
        f.writelines(lines)


def get_run_user(files_found, report_folder, seeker, wrap_text):
    # Dictionary to store the user information
    user_info = {}
    # Attributes to be extracted from the xml file
    attribute = ["id", "creationTime", "lastActive", "fitbitAuth", "garminAuth", "googleFitnessAuth", "lastWeightSyncTime", "profilePictureUrl",
                 "server_locale", "name", "gender", "birthday", "height", "userWeight", "profilePrivacy", "lifetimeTotalDistance",
                 "email_preference", 'asicsId']

    logfunc("Processing data for Garmin User Profile XML")
    file = str(files_found[0])
    logfunc("Processing file: " + file)
    # File is not well formatted, remove first element from first line
    remove_whitespace_from_xml_first_line(file)
    tree = ET.parse(file)
    root = tree.getroot()
    for child in root:
        for i in attribute:
            if child.attrib["name"] == i:
                # Does the attribute have a value?
                if "value" in child.attrib:
                    if i == "lastActive" or i == "lastWeightSyncTime" or i == "birthday":
                        time = child.attrib["value"]
                        time = int(time)
                        user_info[i] = datetime.datetime.utcfromtimestamp(time / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    elif i == "creationTime":
                        time = child.attrib["value"]
                        time = int(time)
                        user_info[i] = datetime.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        user_info[i] = child.attrib["value"]
                else:
                    # Does the attribute have text?
                    if child.text:
                        if i == "profilePictureUrl":
                            user_info[i] = '<img src="'+child.text+'" alt="'+child.text+'" width="50" height="50">'
                        else:
                            user_info[i] = child.text

    if len(user_info) > 0:
        logfunc("Found Runkeeper User Profile XML")
        report = ArtifactHtmlReport('User')
        report.start_artifact_report(report_folder, 'Runkeeper User')
        report.add_script()
        data_headers = ('Name', 'Value')
        data_list = []
        for key, value in user_info.items():
            data_list.append((key, value))
        report.write_artifact_data_table(data_headers, data_list, file, html_escape=False)
        report.end_artifact_report()
        tsvname = f'User'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'User'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc("No Runkeeper XML data found")


__artifacts__ = {
    "RunkeeperUser": (
        "Runkeeper",
        ('*/com.fitnesskeeper.runkeeper.pro/shared_prefs/com.fitnesskeeper.runkeeper.pro_preferences*'),
        get_run_user)
}
