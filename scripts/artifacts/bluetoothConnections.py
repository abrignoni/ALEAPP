import csv
import datetime
import os
import re
import scripts.artifacts.artGlobals 

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, logdevinfo, tsv, timeline, is_platform_windows

def get_bluetoothConnections(files_found, report_folder, seeker, wrap_text):
    data_list = []
    file_found = str(files_found[0])
    
    name_value = ''
    timestamp_value = ''
    linkkey_value = ''
    macaddrf = ''
    first_round = True
    
    with open(file_found, "r") as f:
        for line in f: 
            
            p = re.compile(r'(\[[0-9a-f]{2}(?::[0-9a-f]{2}){5}\])', re.IGNORECASE)
            macaddr = re.findall(p, line)
            if macaddr:
                try:
                    if first_round == True:
                        first_round = False
                    else:
                        data_list.append((timestamp_value, name_value, macaddrf, linkkey_value))
                        name_value = ''
                        timestamp_value = ''
                        linkkey_value = ''
                    macaddrf = macaddr[0].strip('[]')
                    macaddrf = macaddrf.upper()
                except:
                    pass
                
            splits = line.split(' = ')
                
            if splits[0] == 'Name':
                key = 'Name'
                name_value = splits[1].strip()
                
            if splits[0] == 'Timestamp':
                key = 'Timestamp'
                timestamp_value = splits[1].strip()
                timestamp_value = datetime.datetime.utcfromtimestamp(int(timestamp_value)).strftime('%Y-%m-%d %H:%M:%S')
                
            if splits[0] == 'LinkKey':
                key = 'LinkKey'
                linkkey_value = splits[1].strip()
    
    data_list.append((timestamp_value, name_value, macaddrf, linkkey_value))
        
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Bluetooth Connections')
        report.start_artifact_report(report_folder, f'Bluetooth Connections')
        report.add_script()
        data_headers = ('Last Connected Timestamp','Device Name','MAC Address','Link Key')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Bluetooth Connections'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Bluetooth Connections'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc(f'No Bluetooth Connections data available')
   
    data_list = []
    with open(file_found, "r") as f:
        for line in f: 
            
            p = re.compile(r'(\[[0-9a-f]{2}(?::[0-9a-f]{2}){5}\])', re.IGNORECASE)
            macaddr = re.findall(p, line)
            if macaddr:
                break
            if '=' in line:
                splits = line.split(' = ')
                data_list.append((splits[0], splits[1].strip()))
                
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Bluetooth Adapter Information')
        report.start_artifact_report(report_folder, f'Bluetooth Adapter Information')
        report.add_script()
        data_headers = ('Key','Value')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Bluetooth Adapter Information'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc(f'No Bluetooth Adapter Information data available')

__artifacts__ = {
        "Bluetooth Connections": (
                "Bluetooth Connections",
                ('*/misc/bluedroid/bt_config.conf'),
                get_bluetoothConnections)
}