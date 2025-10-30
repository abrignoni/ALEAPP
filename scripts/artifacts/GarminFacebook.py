# Get Information relative to user Facebook account from the XML file in shared_prefs and tries to use the access token to get the user's profile picture
# USES INTERNET CONNECTION
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher, ElementTree, json and datetime, http.client
import datetime
import http.client
import json
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline


# remove whitespace from xml first line
def remove_whitespace_from_xml_first_line(xml_file):
    with open(xml_file, 'r') as f:
        lines = f.readlines()
    # replace first line with <?xml version='1.0' encoding='utf-8' standalone='yes' ?>
    lines[0] = '<?xml version=\'1.0\' encoding=\'utf-8\' standalone=\'yes\' ?>\n'
    with open(xml_file, 'w') as f:
        f.writelines(lines)


def get_garminFB(files_found, report_folder, seeker, wrap_text):
    # Dictionary to store the user information
    user_info = {}
    token = ""
    user_id = 0
    # Attributes to be extracted from the xml file
    attribute = ["com.facebook.AccessTokenManager.CachedAccessToken", "com.facebook.ProfileManager.CachedProfile",
                 "anonymousAppDeviceGUID", "com.facebook.sdk.AutoInitEnabled"]

    logfunc("Processing data for Facebook XML")
    # Loop through the files found
    for file_found in files_found:
        file_found = str(file_found)
        logfunc("Processing file: " + file_found)
        # remove_whitespace_from_xml_first_line(file)
        tree = ET.parse(file_found)
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
            logfunc("Found Facebook XML")
            report = ArtifactHtmlReport('Facebook Data')
            report.start_artifact_report(report_folder, 'Facebook Data')
            report.add_script()
            data_headers = ('Name', 'Value')
            data_list = []
            for key, value in user_info.items():
                if key == "com.facebook.AccessTokenManager.CachedAccessToken":
                    access_token = json.loads(value)
                    for k, v in access_token.items():
                        #if v  is a timestamp
                        if k == "token":
                            token = v
                        elif k == "user_id":
                            user_id = v
                        if k == "last_refresh" or k == "data_access_expiration_time" or k == "expires_at":
                            #check if the timestamp is in milliseconds
                            if len(str(v)) == 13:
                                v = datetime.datetime.utcfromtimestamp(v / 1000.0)
                            else:
                                v = datetime.datetime.utcfromtimestamp(v)
                        data_list.append((k, v))
                elif key == "com.facebook.ProfileManager.CachedProfile":
                    profile = json.loads(value)
                    for k, v in profile.items():
                        data_list.append((k, v))
                else:
                    data_list.append((key, value))
            report.write_artifact_data_table(data_headers, data_list, file_found)

            # Create table with data from facebook api
            if token != "" and user_id != 0:
                logfunc("Getting Facebook data from API")
                conn = http.client.HTTPSConnection("graph.facebook.com")
                payload = ''
                headers = {}
                conn.request("GET",
                             "/" + str(user_id) + "?fields=id,name,email,picture,friends&access_token=" + token,
                             payload, headers)
                res = conn.getresponse()
                data = res.read()
                data = json.loads(data)
                data_headers = ('Name', 'Value')
                data_list = []
                for k, v in data.items():
                    if k == "picture":
                        # Get url from picture withouth the brackets
                        url = v["data"]["url"]
                        data_list.append(("picture", '<img src="'+url+'" alt="'+url+'" width="50" height="50">'))
                    elif k == "friends":
                        data_list.append(("friends", v["summary"]["total_count"]))
                    else:
                        data_list.append((k, v))
                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)

            report.end_artifact_report()
            tsvname = f'Garmin - Facebook'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = f'Garmin - Facebook'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc("No Garmin Facebook data found")


__artifacts__ = {
    "GarminFacebook USES INTERNET": (
        "Garmin-SharedPrefs",
        ('*/com.garmin.android.apps.connectmobile/shared_prefs/com.facebook*'),
        get_garminFB)
}
