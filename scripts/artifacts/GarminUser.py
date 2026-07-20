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
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 23 rows",
        },
    }
}

# Get User information from gcm_user_reference.xml file from Garmin Connect shared preferences
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher and ElementTree
import re
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


INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_xml(file_found):
    """Parse XML, recovering from invalid tokens / unescaped ampersands; empty element if unparseable."""
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


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
    root = _parse_xml(source_path)
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
