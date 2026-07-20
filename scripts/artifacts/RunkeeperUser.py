# pylint: disable=W1309
__artifacts_v2__ = {
    "get_run_user": {
        "name": "RunkeeperUser",
        "description": "Get User information from the xml file com.fitnesskeeper.runkeeper.pro_preferences.xml in the Runkeeper app related to the user",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-03-25",
        "last_update_date": "2023-03-25",
        "requirements": "Python 3.7 or higher and ElementTree",
        "category": "Runkeeper",
        "notes": "",
        "paths": ('*/com.fitnesskeeper.runkeeper.pro/shared_prefs/com.fitnesskeeper.runkeeper.pro_preferences*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    }
}

# Get User information from the xml file com.fitnesskeeper.runkeeper.pro_preferences.xml in the Runkeeper app related to the user
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-25
# Version: 1.0
# Requirements: Python 3.7 or higher and ElementTree
import datetime
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc


# The source XML's first line may carry leading whitespace that makes ElementTree
# choke on the declaration. Normalize it in memory only; the evidence file on disk
# is never modified.
def _read_xml_with_fixed_first_line(xml_file):
    with open(xml_file, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = text.splitlines()
    if lines:
        lines[0] = "<?xml version='1.0' encoding='utf-8' standalone='yes' ?>"
    return "\n".join(lines)


def _ms_to_utc(value):
    return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _s_to_utc(value):
    return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


@artifact_processor
def get_run_user(context):
    files_found = context.get_files_found()
    # Dictionary to store the user information
    user_info = {}
    # Attributes to be extracted from the xml file
    attribute = ["id", "creationTime", "lastActive", "fitbitAuth", "garminAuth", "googleFitnessAuth", "lastWeightSyncTime", "profilePictureUrl",
                 "server_locale", "name", "gender", "birthday", "height", "userWeight", "profilePrivacy", "lifetimeTotalDistance",
                 "email_preference", 'asicsId']

    data_headers = ('Name', 'Value')
    data_list = []
    source_path = ''

    logfunc("Processing data for Runkeeper User Profile XML")
    source_path = str(files_found[0])
    logfunc("Processing file: " + source_path)

    # File is not well formatted; fix the malformed first line in memory only.
    xml_text = _read_xml_with_fixed_first_line(source_path)
    root = ET.fromstring(xml_text)
    for child in root:
        for i in attribute:
            if child.attrib["name"] == i:
                # Does the attribute have a value?
                if "value" in child.attrib:
                    if i in ("lastActive", "lastWeightSyncTime", "birthday"):
                        user_info[i] = _ms_to_utc(child.attrib["value"])
                    elif i == "creationTime":
                        user_info[i] = _s_to_utc(child.attrib["value"])
                    else:
                        user_info[i] = child.attrib["value"]
                else:
                    # Does the attribute have text?
                    if child.text:
                        if i == "profilePictureUrl":
                            user_info[i] = '<img src="' + child.text + '" alt="' + child.text + '" width="50" height="50">'
                        else:
                            user_info[i] = child.text

    if len(user_info) > 0:
        logfunc("Found Runkeeper User Profile XML")
        for key, value in user_info.items():
            data_list.append((key, value))
    else:
        logfunc("No Runkeeper XML data found")

    return data_headers, data_list, source_path
