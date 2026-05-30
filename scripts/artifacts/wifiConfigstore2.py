import datetime
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, abxread, checkabx

def get_wifiConfigstore(files_found, report_folder, _seeker, _wrap_text):
    data_list = []
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
                    configcombined = ssidcombined = bssidcombined = ''
                    PreSharedKeycombined = WEPKeyscombined = HiddenSSIDcombined = ''
                    RandomizedMacAddresscombined = CreatorNamecombined = CreationTimecombined = ''
                    ConnectChoicecombined = ConnectChoiceTimeStampcombined = ''
                    HasEverConnectedcombined = IpAssignmentcombined = ProxySettingscombined = ''
                    for b in a:
                        for c in b:
                            datafieldname = c.attrib.get('name')
                            if datafieldname is None:
                                continue
                            datafieldvalue = c.attrib.get('value', '')
                            datafielddata = c.text

                            if datafieldname == 'ConfigKey':
                                configcombined = datafielddata or ''

                            elif datafieldname == 'SSID':
                                ssidcombined = datafielddata or ''

                            elif datafieldname == 'BSSID':
                                bssidcombined = datafielddata or ''

                            elif datafieldname == 'PreSharedKey':
                                PreSharedKeycombined = datafielddata or ''

                            elif datafieldname == 'WEPKeys':
                                WEPKeyscombined = datafielddata or ''

                            elif datafieldname == 'HiddenSSID':
                                HiddenSSIDcombined = datafieldvalue or ''

                            elif datafieldname == 'RandomizedMacAddress':
                                RandomizedMacAddresscombined = datafielddata or ''

                            elif datafieldname == 'CreatorName':
                                CreatorNamecombined = datafielddata or ''

                            elif datafieldname == 'CreationTime':
                                CreationTimecombined = datafielddata or ''

                            elif datafieldname == 'ConnectChoice':
                                ConnectChoicecombined = datafielddata or ''

                            elif datafieldname == 'ConnectChoiceTimeStamp':
                                ConnectChoiceTimeStampcombined = datafieldvalue
                                if int(ConnectChoiceTimeStampcombined) > 1:
                                    ConnectChoiceTimeStampcombined = datetime.datetime.utcfromtimestamp(int(datafieldvalue) / 1000)

                            elif datafieldname == 'HasEverConnected':
                                HasEverConnectedcombined = datafieldvalue or ''

                            elif datafieldname == 'IpAssignment':
                                IpAssignmentcombined = datafielddata or ''

                            elif datafieldname == 'ProxySettings':
                                ProxySettingscombined = f'{datafielddata} - {datafieldvalue}'
                                
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