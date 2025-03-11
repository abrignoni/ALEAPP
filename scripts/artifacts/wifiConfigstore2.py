import os
import datetime
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, abxread, checkabx, logdevinfo

def get_wifiConfigstore(files_found, report_folder, seeker, wrap_text):
    data_list = []
    mini_data_list = []
    count = -1
    
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('WifiConfigStore.xml'):
            count = count + 1
            #check if file is abx
            if (checkabx(file_found)):
                multi_root = False
                tree = abxread(file_found, multi_root)
            else:
                tree = ET.parse(file_found)
            root = tree.getroot()
            
            for elem in root:
                #print(elem.tag)
                #print(elem.text)
                for a in elem:
                    #print(a.tag)
                    #print(a.text)
                    for b in a:
                        #print(b.tag)
                        tagg = b.tag
                        
                        for c in b:
                            combined = (c.attrib, c.text)
                            datafieldname = (c.attrib['name']) #field
                            datafieldvalue = (c.attrib.get('value', ''))
                            datafielddata= (c.text) 
                            
                            if datafieldname == 'ConfigKey':
                                configkey = f'{datafielddata}'
                                configkeyvalue = f'{datafieldvalue}'
                                configcombined = f'{configkey}'
                                
                            if datafieldname == 'SSID':
                                SSID = f'{datafielddata}'
                                SSIDvalue = f'{datafieldvalue}'
                                ssidcombined = f'{SSID}'
                                
                            if datafieldname == 'BSSID':
                                BSSID = f'{datafielddata}'
                                BSSIDvalue = f'{datafieldvalue}'
                                bssidcombined = f'{BSSID}'
                                
                            if datafieldname == 'PreSharedKey':
                                PreSharedKey = f'{datafielddata}'
                                PreSharedKeyvalue = f'{datafieldvalue}'
                                PreSharedKeycombined = f'{PreSharedKey}'
                                
                            if datafieldname == 'WEPKeys':
                                WEPKeys = f'{datafielddata}'
                                WEPKeysvalue = f'{datafieldvalue}'
                                WEPKeyscombined = f'{WEPKeys}'
                                
                            if datafieldname == 'HiddenSSID':
                                HiddenSSID = f'{datafielddata}'
                                HiddenSSIDvalue = f'{datafieldvalue}'
                                HiddenSSIDcombined = f'{HiddenSSID}'
                                
                            if datafieldname == 'RandomizedMacAddress':
                                RandomizedMacAddress = f'{datafielddata}'
                                RandomizedMacAddressvalue = f'{datafieldvalue}'
                                RandomizedMacAddresscombined = f'{RandomizedMacAddress}'
                                
                            if datafieldname == 'CreatorName':
                                CreatorName = f'{datafielddata}'
                                CreatorNamevalue = f'{datafieldvalue}'
                                CreatorNamecombined = f'{CreatorName}'
                                
                            if datafieldname == 'CreationTime':
                                CreationTime = f'{datafielddata}'
                                CreationTimevalue = f'{datafieldvalue}'
                                CreationTimecombined = f'{CreationTime}'
                                
                            if datafieldname == 'ConnectChoice':
                                ConnectChoice = f'{datafielddata}'
                                ConnectChoicevalue = f'{datafieldvalue}'
                                ConnectChoicecombined = f'{ConnectChoice}'
                                
                            if datafieldname == 'ConnectChoiceTimeStamp':
                                ConnectChoiceTimeStamp = f'{datafielddata}'
                                ConnectChoiceTimeStampvalue = f'{datafieldvalue}'
                                ConnectChoiceTimeStampcombined = f'{ConnectChoiceTimeStampvalue}'
                                if int(ConnectChoiceTimeStampcombined) > 1:
                                    ConnectChoiceTimeStampcombined = datetime.datetime.utcfromtimestamp(int(ConnectChoiceTimeStampvalue) / 1000)
                                    
                            if datafieldname == 'HasEverConnected':
                                HasEverConnected = f'{datafielddata}'
                                HasEverConnectedvalue = f'{datafieldvalue}'
                                HasEverConnectedcombined = f'{HasEverConnectedvalue}'
                                
                            if datafieldname == 'IpAssignment':
                                IpAssignment = f'{datafielddata}'
                                IpAssignmentvalue = f'{datafieldvalue}'
                                IpAssignmentcombined = f'{IpAssignment}'
                                
                            if datafieldname == 'ProxySettings':
                                ProxySettings = f'{datafielddata}'
                                ProxySettingsvalue = f'{datafieldvalue}'
                                ProxySettingscombined = f'{ProxySettings} - {ProxySettingsvalue}'
                                
                    data_list.append((configcombined,ssidcombined,bssidcombined,PreSharedKeycombined, WEPKeyscombined,HiddenSSIDcombined,RandomizedMacAddresscombined,CreatorNamecombined,CreationTimecombined,ConnectChoicecombined,ConnectChoiceTimeStampcombined,HasEverConnectedcombined,IpAssignmentcombined,ProxySettingscombined))                    
        
            if data_list:
                report = ArtifactHtmlReport(f'Wifi Configuration Store Details.xml - {count}')
                report.start_artifact_report(report_folder, f'Wifi Configuration Store Combined - {count}')
                report.add_script()
                data_headers = ['ConfigKey','SSID','BSSID','PreSharedKey','WEPKeys','HiddenSSID','RandomizedMacAddress','CreatorName','CreationTime','ConnectChoice','ConnectChoiceTimeStamp','HasEverConnected','IpAssignment','ProxySettings']
                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()
                
                tsvname = f'Wifi Configuration Store data - {count}'
                tsv(report_folder, data_headers, data_list, tsvname)
    
            else:
                logfunc(f'No Wifi Configuration Store {count} data available')
            
__artifacts__ = {
        "wifiConfigstore2": (
                "WiFi Profiles",
                ('*/misc/wifi/WifiConfigStore.xml', '*/misc**/apexdata/com.android.wifi/WifiConfigStore.xml'),
                get_wifiConfigstore)
}