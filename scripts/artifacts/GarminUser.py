# pylint: disable=W0613
__artifacts_v2__ = {
    "get_garminUP": {
        "name": "Garmin - User Preferences",
        "description": "Get User information from gcm_user_reference.xml file from Garmin Connect shared preferences",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher and ElementTree",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/shared_prefs/gcm_user_preferences*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    }
}

# Get User information from gcm_user_reference.xml file from Garmin Connect shared preferences
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher and ElementTree
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc


# remove whitespace from xml first line
def remove_whitespace_from_xml_first_line(xml_file):
    with open(xml_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # replace first line with <?xml version='1.0' encoding='utf-8' standalone='yes' ?>
    lines[0] = '<?xml version=\'1.0\' encoding=\'utf-8\' standalone=\'yes\' ?>\n'
    with open(xml_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)


@artifact_processor
def get_garminUP(files_found, report_folder, seeker, wrap_text):
    # Dictionary to store the user information
    user_info = {}
    # Attributes to be extracted from the xml file
    attribute = ["keyUserHasCurrentPregnancy", "userSleepStartTime", "keyUserTimezone", "transactionKey", "userHeight",
                 "key_primary_activity_tracker_id", "userLocation", "keyUserCyclingVO2Max", "keyUserLocale", "userGarminGUID",
                 "keyRegisteredRealTimeHeartRateDeviceId", "key_ghs_ecg_enabled", "key_user_location_country_code",
                 "keyPulseOxSleepCardSupported", "userIconURL", "userSleepStopTime", "userSettingsUserID", "userLevel", "keyUserRunningVO2Max",
                 "userWeightStr", "userActivityLevel", "userHandednessCapability", "userName", "userDateOfBirthString", "keyNewsfeedLastViewedTimeGMT",
                 "userPoints", "userGender"]

    logfunc("Processing data for Garmin User Profile XML")
    source_path = str(files_found[0])
    logfunc("Processing file: " + source_path)
    # File is not well formatted, remove first element from first line
    remove_whitespace_from_xml_first_line(source_path)
    tree = ET.parse(source_path)
    root = tree.getroot()
    for child in root:
        for i in attribute:
            if child.attrib["name"] == i:
                # Does the attribute have a value?
                if "value" in child.attrib:
                    user_info[i] = child.attrib["value"]
                else:
                    # Does the attribute have text?
                    if child.text:
                        user_info[i] = child.text

    data_list = []
    for key, value in user_info.items():
        data_list.append((key, value))

    data_headers = ('Name', 'Value')
    return data_headers, data_list, source_path
