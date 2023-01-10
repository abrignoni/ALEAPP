import os
import datetime
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, abxread, checkabx, logdevinfo

def get_wifiConfigstore(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('WifiConfigStore.xml'):
            
            #check if file is abx
            if (checkabx(file_found)):
                multi_root = False
                tree = abxread(file_found, multi_root)
            else:
                tree = ET.parse(file_found)
            root = tree.getroot()
            
            for elem in root.iter():
                if elem.attrib.get('name') is not None:
                    if elem.text is not None:
                        data_list.append((elem.attrib.get('name'), elem.text ))
                    elif elem.attrib.get('value')is not None:
                        data_list.append((elem.attrib.get('name'), elem.attrib.get('value') ))
                        
                    if (elem.attrib.get('name')) == 'RandomizedMacAddress':
                        logdevinfo(f'Randomized MAC Address: {elem.text}')
                        
                    if (elem.attrib.get('name')) == 'wifi_sta_factory_mac_address':
                        logdevinfo(f'WIFI Factory MAC Address: {elem.text}')
                        
                    if (elem.attrib.get('name')) == 'DefaultGwMacAddress':
                        logdevinfo(f'Default Gw MAC Address: {elem.text}')
                        
                    if (elem.attrib.get('name')) == 'ConfigKey':
                        splitted = elem.text.split('"')
                        logdevinfo(f'Config Key: {splitted[1]}')
                        logdevinfo(f'Protocol: {splitted[2]}')
                        
                    if (elem.attrib.get('name')) == 'SSID':
                        splitted = elem.text.split('"')
                        logdevinfo(f'SSID: {splitted[1]}')
                        
                    if (elem.attrib.get('name')) == 'PreSharedKey':
                        try:
                            splitted = elem.text.split('"')
                            logdevinfo(f'Pre-Shared Key ASCII: {splitted[1]}')
                        except:
                            logdevinfo(f'Pre-Shared Key 64 hex digits raw PSK: {elem.text}')
                    
                    if (elem.attrib.get('name')) == 'LastConnectedTime':
                        timestamp = datetime.datetime.fromtimestamp(int(elem.attrib.get("value"))/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
                        logdevinfo(f'WIFI Last Connected Time: {timestamp}')
                    
        if data_list:
            report = ArtifactHtmlReport('Wifi Configuration Store.xml')
            report.start_artifact_report(report_folder, 'Wifi Configuration Store')
            report.add_script()
            data_headers = ('Key', 'Value')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Wifi Configuration Store data'
            tsv(report_folder, data_headers, data_list, tsvname)

        else:
            logfunc('No Wifi Configuration Store data available')
            
__artifacts__ = {
        "wifiConfigstore": (
                "WiFi Profiles",
                ('*/misc/wifi/WifiConfigStore.xml', '*/misc**/apexdata/com.android.wifi/WifiConfigStore.xml'),
                get_wifiConfigstore)
}