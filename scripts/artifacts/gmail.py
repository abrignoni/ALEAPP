# gmailActive: Get gmail account information
# Author: Joshua James {joshua@dfirscience.org}
# Date: 2021-11-08
# Artifact version: 0.0.1
# Android version tested: 11
# Requirements: none

import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

class keyboard_event:
    def __init__(self, id, app, text, textbox_name, textbox_id, event_date, start_date='', end_date=''):
        self.id = id
        self.app = app
        self.text = text
        self.textbox_name = textbox_name
        self.textbox_id = textbox_id
        self.event_date = event_date
        self.start_date = start_date
        self.end_date = end_date

def get_gmailActive(files_found, report_folder, seeker, wrap_text):
    #logfunc("If you can read this, the module is working!")
    #logfunc(files_found)
    activeAccount = ''
    file_found = str(files_found[0])
    xmlTree = ET.parse(file_found)
    root = xmlTree.getroot()
    for child in root:
        if child.attrib['name'] == "active-account":
            logfunc("Active gmail account found: " + child.text)
            activeAccount = child.text

    if activeAccount != '':
        report = ArtifactHtmlReport('Gmail - Active')
        report.start_artifact_report(report_folder, 'Gmail - Active')
        report.add_script()
        data_headers = ('Active Gmail Address','') # final , needed for table formatting
        data_list = []
        data_list.append((activeAccount, ''))# We only expect one active account
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
            
        tsvname = f'Gmail - Active'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No active Gmail account found')

__artifacts__ = {
        "GmailActive": (
                "Gmail",
                ('*/com.google.android.gm/shared_prefs/Gmail.xml'),
                get_gmailActive)
}