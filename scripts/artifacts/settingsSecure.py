import glob
import json
import os
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_settingsSecure(files_found, report_folder, seeker):

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

def process_ssecure(folder, uid, report_folder):
    
    tree = ET.parse(folder)
    root = tree.getroot()
    data_list = []
    for setting in root.findall('setting'):
        nme = setting.get('name')
        val = setting.get('value')
        if nme == 'bluetooth_name':
            data_list.append((nme, val))
        elif nme == 'mock_location':
            data_list.append((nme, val))
        elif nme == 'android_id':
            data_list.append((nme, val))
        elif nme == 'bluetooth_address':
            data_list.append((nme, val))
     
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Settings Secure')
        report.start_artifact_report(report_folder, f'Settings_Secure_{uid}')
        report.add_script()
        data_headers = ('Name', 'Value')
        report.write_artifact_data_table(data_headers, data_list, folder)
        report.end_artifact_report()
    else:
        logfunc('No Settings Secure data available')
        
    