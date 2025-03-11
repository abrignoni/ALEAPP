__artifacts_v2__ = {
    "urlUserprefs": {
        "name": "ULR User Prefs",
        "description": "ULR User Prefs",
        "author": "Alexis 'Brigs' Brignoni",
        "version": "1",
        "date": "2024/06/21",
        "requirements": "",
        "category": "App Semantic Locations",
        "notes": "Thanks to Josh Hickman for the research",
        "paths": (
            '*/com.google.android.gms/shared_prefs/ULR_USER_PREFS.xml'
        ),
        "function": "get_urluser"
    }
}
import json
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, timeline, kmlgen 

def get_urluser(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('ULR_USER_PREFS.xml'):
        
            data_list = []
            tree = ET.parse(file_found)
            root = tree.getroot()
            #print('Processed: '+filename)
            
            for child in root:
                jsondata = (child.attrib)
                name = (jsondata['name'])
                value = (jsondata.get('value',''))
                data_list.append((name,value))
        
                    
        
    if len(data_list) > 0:
        description = ''
        report = ArtifactHtmlReport('ULR User Preferences')
        report.start_artifact_report(report_folder, 'ULR User Preferences', description)
        report.add_script()
        data_headers = ('Name','Value')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
            
        tsvname = 'ULR User Preferences'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'ULR User Preferences'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No ULR User Preferences Data available')
                        
                
    