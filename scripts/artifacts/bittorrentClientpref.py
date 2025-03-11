import os
import datetime
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, abxread, checkabx, logdevinfo
    
def timestampcalc(timevalue):
    timestamp = (datetime.datetime.utcfromtimestamp(int(timevalue)/1000).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp

def get_bittorrentClientpref(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
            
        #check if file is abx
        if (checkabx(file_found)):
            multi_root = False
            tree = abxread(file_found, multi_root)
        else:
            tree = ET.parse(file_found)
        
        root = tree.getroot()
    
        for elem in root:
            key = elem.attrib['name']
            value = elem.attrib.get('value')
            text = elem.text
            if key == 'BornOn':
                value = timestampcalc(value)
            data_list.append((key, value, text))
                    
    if data_list:
        report = ArtifactHtmlReport('Bittorent Client Preferences')
        report.start_artifact_report(report_folder, 'Bittorent Client Preferences')
        report.add_script()
        data_headers = ('Key', 'Value', 'Text')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Bittorent Client Preferences'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Bittorent Client Preferences data available')
        
__artifacts__ = {
        "BitTorrent Prefs": (
                "BitTorrent",
                ('*/com.bittorrent.client/shared_prefs/com.bittorrent.client_preferences.xml'),
                get_bittorrentClientpref)
}