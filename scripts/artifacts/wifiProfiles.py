import os
import xml.etree.ElementTree as ET
import textwrap
import datetime
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_wifiProfiles(files_found, report_folder, seeker, wrap_text):

    #Create sqlite databases
    db = sqlite3.connect(os.path.join(report_folder, 'WiFiConfig.db'))
    cursor = db.cursor()

    #Create table WiFiConfig.

    cursor.execute('''
        CREATE TABLE wifi(ConfigKey TEXT, SSID TEXT, PreSharedKey TEXT, WEPKeys TEXT, DefaultGwMacAddress TEXT, semCreationTime INTEGER,
        semUpdateTime INTEGER, LastConnectedTime INTEGER, CaptivePortal TEXT, LoginUrl TEXT, IpAssignment TEXT, Identity TEXT, Password TEXT)
    ''')

    db.commit()

    #slash = '\\' if is_platform_windows() else '/' 
    hit = 0
    Identity = ''
    Password = ''
    PreSharedKey = ''
    WEPKeys = ''
    Password = ''
    LoginUrl = ''
    SecurityMode = '' 
    SSID = ''
    PreSharedKey = ''
    WEPKeys = ''
    DefaultGwMacAddress = '' 
    semCreationTimeUTC = '' 
    semUpdateTimeUTC = '' 
    LastConnectedTimeUTC = '' 
    CaptivePortal = '' 
    LoginUrl = ''
    IpAssignment = ''
    SecurityMode = '' 
    semCreationTime = '' 
    semUpdateTime = '' 
    LastConnectedTime = ''
    
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        tree = ET.parse(file_found)

        for node in tree.iter('Network'):
            for elem in node.iter():
                if not elem.tag==node.tag:
                    #print(elem.attrib)
                    data = elem.attrib
                    for key, value in data.items():
                        if value == 'ConfigKey':
                            cut = elem.text.split('"')
                            SecurityMode = (cut[2]) 
                            hit = 1

                        if value == 'SSID':
                            SSID = elem.text
                            SSID = SSID.strip('"')
                            hit = 1

                        if value == 'PreSharedKey':
                            PreSharedKey = elem.text
                            hit = 1

                        if value == 'WEPKeys':
                            WEPKeys = elem.text
                            hit = 1

                        if value == 'DefaultGwMacAddress':
                            DefaultGwMacAddress = elem.text
                            hit = 1
                        

                        if value == 'semCreationTime':
                            semCreationTime = elem.attrib['value']
                            semCreationTimeUTC = elem.attrib['value']

                            if int(semCreationTime) > 0:
                                semCreationTime = datetime.datetime.utcfromtimestamp(int(semCreationTime) / 1000)
                            hit = 1
                        

                        if value == 'semUpdateTime':
                            semUpdateTime = elem.attrib['value']
                            semUpdateTimeUTC = elem.attrib['value']
                            if int(semUpdateTime) > 0:
                                semUpdateTime = datetime.datetime.utcfromtimestamp(int(semUpdateTime) / 1000)
                            hit = 1
                        

                        if value == 'LastConnectedTime':
                            LastConnectedTime = elem.attrib['value']
                            LastConnectedTimeUTC = elem.attrib['value']
                            if int(LastConnectedTime) > 0:
                                LastConnectedTime = datetime.datetime.utcfromtimestamp(int(LastConnectedTime) / 1000)
                            hit = 1
                        

                        if value == 'CaptivePortal':
                            CaptivePortal = elem.attrib['value']
                            hit = 1
                        

                        if value == 'LoginUrl':
                            LoginUrl = elem.text
                            hit = 1
                        

                        if value == 'IpAssignment':
                            IpAssignment = elem.text 
                            hit = 1
                        
                        if value == 'Identity':
                            Identity = elem.text  
                            hit = 1

                        if value == 'Password':
                            Password = elem.text  
                            hit = 1
                        #data_list.append((SecurityMode, SSID, PreSharedKey, WEPKeys, DefaultGwMacAddress, semCreationTime, semUpdateTime, LastConnectedTime, CaptivePortal, LoginUrl, IpAssignment))
            if hit == 1:           
                if PreSharedKey == None:
                    PreSharedKey = ''
                if WEPKeys == None:
                    WEPKeys = ''
                if Password == None:
                    Password = ''
                if LoginUrl == None:
                    LoginUrl = ''
                
                cursor = db.cursor()
                datainsert = (SecurityMode, SSID, PreSharedKey, WEPKeys, Password, Identity, DefaultGwMacAddress, semCreationTimeUTC, semUpdateTimeUTC, LastConnectedTimeUTC, CaptivePortal, LoginUrl, IpAssignment)
                cursor.execute('INSERT INTO wifi (ConfigKey, SSID, PreSharedKey, WEPKeys, Password, Identity, DefaultGwMacAddress, semCreationTime, '
                'semUpdateTime , LastConnectedTime , CaptivePortal , LoginUrl , IpAssignment ) '
                'VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
                db.commit()

                if wrap_text:
                    data_list.append((SecurityMode, SSID, PreSharedKey, WEPKeys, Password, Identity, DefaultGwMacAddress, semCreationTime, semUpdateTime, LastConnectedTime, CaptivePortal, (textwrap.fill(LoginUrl, width=10)), IpAssignment, file_found))
                else:
                    data_list.append((SecurityMode, SSID, PreSharedKey, WEPKeys, Password, Identity, DefaultGwMacAddress, semCreationTime, semUpdateTime, LastConnectedTime, CaptivePortal, LoginUrl, IpAssignment, file_found))
                
                #data_list.append(datainsert)
                Identity = ''
                Password = ''
    db.close()

    if hit == 1:
        report = ArtifactHtmlReport('Wi-Fi Profiles')
        report.start_artifact_report(report_folder, 'Wi-Fi Profiles')
        report.add_script()
        data_headers = ('SecurityMode', 'SSID', 'PreSharedKey', 'WEPKeys', 'Password', 'Identity', 'DefaultGwMacAddress', 'semCreationTime', 'semUpdateTime', 'LastConnectedTime', 'CaptivePortal', 'LoginUrl', 'IpAssignment', 'Path')
        report.write_artifact_data_table(data_headers, data_list, ", ".join(files_found))
        report.end_artifact_report()
        
        tsvname = f'wifi profiles'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Wi-Fi Profiles data available')

__artifacts__ = {
        "wifiProfiles": (
                "WiFi Profiles",
                ('*/misc/wifi/WifiConfigStore.xml', '*/misc**/apexdata/com.android.wifi/WifiConfigStore.xml'),
                get_wifiProfiles)
}