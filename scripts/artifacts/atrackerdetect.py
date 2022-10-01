import os
import datetime
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_atrackerdetect(files_found, report_folder, seeker, wrap_text):
    data_list=[]
    for file_found in files_found:
        file_found = str(file_found)
        
        tree = ET.parse(file_found)
        root = tree.getroot()
        
        for elem in root.iter():
            attribute = (elem.attrib)
            if attribute:
                data = attribute.get('name')
                if data.startswith('device'):
                    mac = data.split('_', 2)[1]
                    desc = data.split('_', 2)[2]
                    data_list.append((desc, mac, elem.text))
                else:
                    data_list.append((data, attribute.get('value'),''))
                                
        if data_list:
            report = ArtifactHtmlReport('Apple Tracker Detect Prefs')
            report.start_artifact_report(report_folder, 'Apple Tracker Detect Prefs')
            report.add_script()
            data_headers = ('Key', 'Value', 'Milliseconds from Last Boot Time')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Apple Tracker Detect Prefs'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('No Apple Tracker Detect Prefs data available')

__artifacts__ = {
        "atrackerdetect": (
                "AirTags",
                ('*/com.apple.trackerdetect/shared_prefs/com.apple.trackerdetect_preferences.xml'),
                get_atrackerdetect)
}