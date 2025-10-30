import glob
import json
import os
import re
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, logdevinfo, is_platform_windows, abxread, checkabx

def get_settingsSecure(files_found, report_folder, seeker, wrap_text):

    slash = '\\' if is_platform_windows() else '/' 
    # Filter for path xxx/yyy/system_ce/0
    for file_found in files_found:
        file_found = str(file_found)
        parts = file_found.split(slash)
        uid = parts[-2]
        try:
            uid_int = int(uid)
            # Skip sbin/.magisk/mirror/data/system_de/0 , it should be duplicate data??
            if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
                continue
            process_ssecure(file_found, uid, report_folder)
        except ValueError:
                pass # uid was not a number

def process_ssecure(file_path, uid, report_folder):
     
    if (checkabx(file_path)):
        multi_root = True
        tree = abxread(file_path, multi_root)
        root = tree.getroot()
    else:
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError: # Fix for android 11 invalid XML file (no root element present)
            with open(file_path) as f:
                xml = f.read()
                root = ET.fromstring(re.sub(r"(<\?xml[^>]+\?>)", r"\1<root>", xml) + "</root>")
    
    data_list = []
    for setting in root.iter('setting'):
        nme = setting.get('name')
        val = setting.get('value')
        if nme == 'bluetooth_name':
            data_list.append((nme, val))
            logdevinfo(f"<b>Bluetooth name: </b>{val}")
        elif nme == 'mock_location':
            data_list.append((nme, val))
        elif nme == 'android_id':
            data_list.append((nme, val))
        elif nme == 'bluetooth_address':
            data_list.append((nme, val))
            logdevinfo(f"<b>Bluetooth address: </b>{val}")
     
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Settings Secure')
        report.start_artifact_report(report_folder, f'Settings_Secure_{uid}')
        report.add_script()
        data_headers = ('Name', 'Value')
        report.write_artifact_data_table(data_headers, data_list, file_path)
        report.end_artifact_report()
        
        tsvname = f'settings secure'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Settings Secure data available')
        
__artifacts__ = {
        "settingsSecure": (
                "Device Info",
                ('*/system/users/*/settings_secure.xml'),
                get_settingsSecure)
}