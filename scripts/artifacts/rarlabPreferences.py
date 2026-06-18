# pylint: disable=W0611,W0613,W1309
__artifacts_v2__ = {
    "get_rarlabPreferences": {
        "name": "rarlabPreferences",
        "description": "",
        "author": "",
        "creation_date": "2023-03-29",
        "last_update_date": "2023-03-29",
        "requirements": "none",
        "category": "RAR Lab Prefs",
        "notes": "",
        "paths": ('*/com.rarlab.rar_preferences.xml',),
        "output_types": None,
        "artifact_icon": "settings",
        "function": "get_rarlabPreferences",
    }
}

import os
import datetime
import json

import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, abxread, checkabx, logdevinfo

def get_rarlabPreferences(files_found, report_folder, seeker, wrap_text):
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('com.rarlab.rar_preferences.xml'):
            
            #check if file is abx
            if (checkabx(file_found)):
                multi_root = False
                tree = abxread(file_found, multi_root)
            else:
                tree = ET.parse(file_found)
            root = tree.getroot()
            
            for elem in root.iter():
                name = elem.attrib.get('name')
                value = elem.attrib.get('value')
                text = elem.text 
                if name is not None:
                    if name == 'ArcHistory' or name == 'ExtrPathHistory' :
                        items = json.loads(text)
                        agg = ''
                        for x in items:
                            agg = agg + f'{x}<br>'
                        data_list.append((name,agg,value))
                    else:
                        data_list.append((name,text,value))
                        
                    
        if data_list:
            report = ArtifactHtmlReport(f'RAR Lab Preferences')
            report.start_artifact_report(report_folder, f'RAR Lab Preferences')
            report.add_script()
            data_headers = ('Key','Text','Value')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Text'])
            report.end_artifact_report()
            
            tsvname = f'RAR Lab Preferences'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc(f'No RAR Lab Preferences data available')
            
