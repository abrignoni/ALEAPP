# Get User information from gcm_user_reference.xml file from Garmin Connect shared preferences
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher and ElementTree
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
                    user_info[i] = child.attrib["value"]
                else:
                    # Does the attribute have text?
                    if child.text:
                        user_info[i] = child.text

    if len(user_info) > 0:
        logfunc("Found Garmin User Profile XML")
        report = ArtifactHtmlReport('User Preferences')
        report.start_artifact_report(report_folder, 'User Preferences')
        report.add_script()
        data_headers = ('Name', 'Value')
        data_list = []
        for key, value in user_info.items():
            data_list.append((key, value))
        report.write_artifact_data_table(data_headers, data_list, file)
        report.end_artifact_report()
        tsvname = f'User'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'User'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc("No Garmin XML data found")


__artifacts__ = {
    "GarminUser": (
        "Garmin-SharedPrefs",
        ('*/com.garmin.android.apps.connectmobile/shared_prefs/gcm_user_preferences*'),
        get_garminUP)
}
