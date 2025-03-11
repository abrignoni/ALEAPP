# kleinanzeigen.de App
# Author:  Bruno Fischer (@BrunoFischerGermany)
# Version: 1.0.0
# https://play.google.com/store/apps/details?id=com.ebay.kleinanzeigen
# kleinanzeigen.de App Version Tested: 15.16.0 from 2023-12-017
# kleinanzeigen.de App Version Tested: 15.23.0 from 2024-03-08
# kleinanzeigen.de App Version Tested: 15.26.0 from 2024-03-28
# kleinanzeigen.de App Version Tested: 15.27.0 from 2024-04-04
# Requirements:  xmltodict, json, datetime
#
#   Description: The kleinanzeigen.de app is one of the largest classified ad portals in Germany. There are probably messages between app users.
#

import xmltodict
import json
import datetime
import re

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_kleinanzeigenrecentsearchescache(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        #logfunc(f"{file_found}")
        if('RECENT_SEARCHES_CACHE' in file_found):
            logfunc("kleinanzeigen.de - recent searches cache found")
            with open(file_found, encoding='utf-8') as fd:
                json_data = json.load(fd)
                data = []
                number_search_terms = sum(1 for entry in json_data if 'searchTerm' in entry)
                for entry in json_data:
                    updated_at = datetime.datetime.utcfromtimestamp(entry['termSearchTimestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    data.append((entry['searchTerm'], entry['category']['localizedName'], updated_at))

                if(len(data)>0):
                    report = ArtifactHtmlReport('kleinanzeigen.de - recent search cache')
                    report.start_artifact_report(report_folder,'kleinanzeigen.de - recent search cache')
                    report.add_script()
                    data_headers = ('Search Term', 'Category', 'Search Timestamp')
                    data_list = []
                    for row in data:
                        data_list.append((row[0], row[1], row[2]))
                    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                    report.end_artifact_report()

                    tsvname = "kleinanzeigen.de - Recent Search Cache Data"
                    tsv(report_folder, data_headers, data_list,tsvname)

                else:
                    logfunc("No kleinanzeigen.de - Recent Search Cache data found")
def get_kleinanzeigennonresettablerecentsearchescache(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        #logfunc(f"{file_found}")
        if('NON_RESETTABLE_RECENT_SEARCHES_CACHE' in file_found):
            logfunc("kleinanzeigen.de - non resettable recent searches cache found")
            with open(file_found, encoding='utf-8') as fd:
                json_data = json.load(fd)
                data = []
                number_search_terms = sum(1 for entry in json_data if 'searchTerm' in entry)
                for entry in json_data:
                    updated_at = datetime.datetime.utcfromtimestamp(entry['termSearchTimestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    data.append((entry['searchTerm'], entry['category']['localizedName'], updated_at))

                if(len(data)>0):
                    report = ArtifactHtmlReport('kleinanzeigen.de - non resettable recent search cache')
                    report.start_artifact_report(report_folder,'kleinanzeigen.de - non resettable recent search cache')
                    report.add_script()
                    data_headers = ('Search Term', 'Category', 'Search Timestamp')
                    data_list = []
                    for row in data:
                        data_list.append((row[0], row[1], row[2]))
                    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                    report.end_artifact_report()

                    tsvname = "kleinanzeigen.de - resettable recent Search Cache Data"
                    tsv(report_folder, data_headers, data_list,tsvname)

                else:
                    logfunc("No kleinanzeigen.de - non resettable recent Search Cache data found")

def get_kleinanzeigenaccount(files_found, report_folder, seeker, wrap_text):
   for file_found in files_found:

       if('com.ebay.kleinanzeigen_preferences.xml' in file_found):
            keys_to_check = [
                'USERPROFILE_NAME_KEY',  # Account Profile Name
                'USERPROFILE_INITIALS',  # Account Profile Initials
                'LAST_EMAIL_USED',  # Account Last used Email Address
                'AUTH_USER_EMAIL',  # Account Authenticated User Email Address
                'AUTH_USER_ID', # Account User ID
                'USERPROFILE_PHONE_NUMBER_KEY',  # Account Phone Number'
                'USERPROFILE_ACCOUNT_TYPE_KEY',  # Account Type maybe PRIVATE
                'USERPROFILE_USER_SINCE_DATE_KEY',  # Account Since - Timestamp - ISO 8601 Format
                'USERPROFILE_LOCATION_LONGITUDE_KEY',  # Saved Location Longitude
                'USERPROFILE_LOCATION_LATITUDE_KEY'  # Saved Location Latitude
            ]
            logfunc("kleinanzeigen.de - Account data found")
            with open(file_found, encoding='utf-8') as fd:
                xml_dict = xmltodict.parse(fd.read())
                string_dict = xml_dict.get('map', {}).get('string', [])
                data = []
                for key in keys_to_check:
                    value = ""
                    for item in string_dict:
                        if item.get('@name') == key:
                            value = item.get('#text', '')
                            break
                    data.append(value)

                if(len(data)>0):
                    report = ArtifactHtmlReport('kleinanzeigen.de - account details')
                    report.start_artifact_report(report_folder,'kleinanzeigen.de - account details')
                    report.add_script()
                    data_headers = ('Account Profile Name', 'Account Profile Initials', 'Account Last Used Email Address', 'Account User Id',  'Account Authenticated Email Address', 'Account Phone Number', 'Account Type', 'Account Registered since', 'Saved Location Longitude', 'Saved Location Latitude')
                    data_list = []
                    data_list.append((data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9]))
                    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                    report.end_artifact_report()

                    tsvname = "kleinanzeigen.de - Account Data"
                    tsv(report_folder, data_headers, data_list,tsvname)

                else:
                    logfunc("No kleinanzeigen.de - Account data found")
def get_kleinanzeigenmessagebox(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)
        if(file_found.endswith('messageBoxDatabase.db')):
            logfunc('MessageBoxDatabase found')
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT 
            json_extract(conversations.counterParty, '$.name') AS "counterparty",
            json_extract(conversations.ad, '$.displayTitle') AS "ad title",
            json_extract(conversations.ad, '$.identifier') AS "ad number", 
            json_array_length(conversations.messages) AS count,
            datetime(conversations.sortByDate/1000,'unixepoch') AS "Last Message Time",
            messages,
            json_extract(conversations.counterParty, '$.identifier') AS "counterpartyidentifier"
            FROM `conversations` ORDER BY `sortByDate` DESC;
            ''')
            data = cursor.fetchall()
            usageentries = len(data)
            if usageentries > 0:
                # logfunc(str(data))
                report = ArtifactHtmlReport('kleinanzeigen.de - messagebox')
                report.start_artifact_report(report_folder, 'kleinanzeigen.de - messagebox')
                report.add_script()
                data_headers = ('counterparty', 'ad title', 'ad number', 'number of messages', 'last message time', '')
                data_list = []
                for row in data:
                    # CREATE SINGLE CHAT
                    singlereportname = f'kleinanzeigen.de - messagebox counterparty {row[0]} - ad-no. {row[2]}'
                    singlereport = ArtifactHtmlReport(singlereportname)
                    invalid_chars = '[^a-zA-Z0-9_.-]'

                    singlereportfilename = re.sub(invalid_chars, " ", singlereportname)
                    singlereportfilename = re.sub(r' +', " ", singlereportfilename)

                    singlereport.start_artifact_report(report_folder, singlereportfilename)
                    singlereport.add_script()
                    singlereport_list = []
                    message_data = json.loads(row[5])
                    body = ''
                    for message in message_data:
                        body += '<div class="chatline">\n'
                        if message['sender'] == "COUNTER_PARTY":
                            body += '<div class="chatname">'
                            body += row[0][0].upper()
                            body += '</div>'
                        if message['sender'] == "ME":
                            body += '<div class="chatme">'
                            direction = "outgoing"
                        elif message['sender'] == "COUNTER_PARTY":
                            body += '<div class="chatyou">'
                            direction = "incoming"
                        if len(message['text']) == 0:
                            body += 'message without text<br/>'
                        elif len(message['text']) > 0:
                            body += message['text'].replace("\n", "<br/>")
                        if "attachments" in message and len(message['attachments']) > 0:
                            body += 'This message has attachments.<br/>'
                            body += '<span style="font-size: small; font-style: italic;">'
                            for attachment in message["attachments"]:
                                zaehler = 0
                                if len(attachment['mimeType']) > 0:
                                    body += '<br/>'
                                    body += f'attachment-mimetype: {attachment["mimeType"]}'
                                    zaehler += 1
                                if len(attachment['url']) > 0:
                                    body += '<br/>'
                                    body += f'attachment-url: <a href="{attachment["url"]}" target=_blank>{attachment["url"]}</a>'
                                    zaehler += 1
                                if zaehler > 0:
                                    body += '<br/>'
                            body += '</span>'
                        if "warning" in message and message['warning'] and len(message['warning']['links']) > 0 and len(
                                message['warning']['message']) > 0:
                            warning = message["warning"]
                            body += '<br/><br/><div style="font-size: small; font-style: italic; font-family: monospace;color:red;">'
                            body += '<span style="text-decoration:underline;font-wight:bold;">automatic security message from the app provider shown in the app</span><br/>"'
                            for link_name, link_url in warning["links"].items():
                                body += warning["message"].replace(link_name, f'<a href="{link_url}" title="{link_url}" target=_blank>{link_name}</a>').replace("\n", "<br/>")
                            body += '"</div><br/>'
                        body += '</div>'
                        if message['sender'] == "ME":
                            body += '<p>'
                        elif message['sender'] == "COUNTER_PARTY":
                            body += '<p class="chatyou_date">'
                        body += message['sortByDate']
                        body += '<br/>message-state: '
                        body += message['state'].lower()
                        body += '</p>'
                        body += '</div>'
                        singlereport_list.append((row[0], row[1], message['text'], direction, message['state'].lower()))
                    button = ''
                    if row[3] > 1:
                        button = f'<a href="{singlereportfilename}.html" target="_self"  class="btn btn-primary" >Open Messages</a>'

                    singlereport.add_chat_window(f'counterparty: {row[0]} [identifier: {row[6]}]<br/> ad-title: <u>{row[1]}</u><br/>ad-no. {row[2]}<br/>{row[3]} messages', body)

                    singletsvname = f"kleinanzeigen.de - messages counterparty {row[0]} identifier - {row[6]}] ad-no {row[2]}"
                    singledata_headers = ('Counterparty', 'Counterparty-Identifier', 'Message-Text', 'Message-Direction', 'Message-State')
                    tsv(report_folder, singledata_headers, singlereport_list, singletsvname)

                    data_list.append((row[0], row[1], row[2], row[3], row[4], button))
                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()

                tsvname = "kleinanzeigen.de - messagebox"
                tsv(report_folder, data_headers, data_list, tsvname)

            else:
                logfunc('No messageBox data available')

__artifacts_v2__ = {
    "get_kleinanzeigenaccount": {
        "name": "kleinanzeigen.de App - Account Details",
        "description": "Extracts Account Details",
        "author": "@BrunoFischerGermany",
        "version": "0.1",
        "date": "2024-04-02",
        "requirements": "none",
        "category": "kleinanzeigen.de App",
        "notes": "",
        "paths": ('*/com.ebay.kleinanzeigen/shared_prefs/com.ebay.kleinanzeigen_preferences.xml'),
        "function": "get_kleinanzeigenaccount"
    },
    "get_kleinanzeigenrecentsearchescache": {
        "name": "kleinanzeigen.de - Recent Searches Cache",
        "description": "Extracts Recent Searches Cache",
        "author": "@BrunoFischerGermany",
        "version": "0.1",
        "date": "2024-04-02",
        "requirements": "none",
        "category": "kleinanzeigen.de App",
        "notes": "",
        "paths": ('*/com.ebay.kleinanzeigen/files/RECENT_SEARCHES_CACHE'),
        "function": "get_kleinanzeigenrecentsearchescache"
    },
    "get_kleinanzeigennonresettablerecentsearchescache": {
        "name": "kleinanzeigen.de - Non resettable Recent Searches Cache",
        "description": "Extracts Recent Searches Cache",
        "author": "@BrunoFischerGermany",
        "version": "0.1",
        "date": "2024-04-08",
        "requirements": "none",
        "category": "kleinanzeigen.de App",
        "notes": "",
        "paths": ('*/com.ebay.kleinanzeigen/files/NON_RESETTABLE_RECENT_SEARCHES_CACHE'),
        "function": "get_kleinanzeigennonresettablerecentsearchescache"
    },
    "get_kleinanzeigenmessagebox":  {
        "name": "kleinanzeigen.de - Messagebox",
        "description": "Extracts Messages from Database",
        "author": "@BrunoFischerGermany",
        "version": "0.1",
        "date": "2024-04-13",
        "requirements": "none",
        "category": "kleinanzeigen.de App",
        "notes": "",
        "paths": ('*com.ebay.kleinanzeigen/databases/messageBoxDatabase.db*'),
        "function": "get_kleinanzeigenmessagebox"
    }
}
