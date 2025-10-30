import struct
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline

def get_wifiHotspot(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        ssid = ''
        security_type = ''
        passphrase = ''

        if file_found.endswith('.conf'):
            with open(file_found, 'rb') as f:
                data = f.read()
                ssid_len = data[5]
                ssid = data[6 : 6 + ssid_len].decode('utf8', 'ignore')

                data_len = len(data)
                start_pos = -1
                while data[start_pos] != 0 and (-start_pos < data_len):
                    start_pos -= 1
                passphrase = data[start_pos + 2:].decode('utf8', 'ignore')
        else:
            tree = ET.parse(file_found)
            for node in tree.iter('SoftAp'):
                for elem in node.iter():
                    if not elem.tag==node.tag:
                        #print(elem.attrib)
                        data = elem.attrib
                        name = data.get('name', '')
                        if name == 'SSID' or name == 'WifiSsid':
                            ssid = elem.text
                        elif name == 'SecurityType':
                            security_type = data.get('value', '')
                        elif name == 'Passphrase':
                            passphrase = elem.text
        if ssid:
            data_list.append((ssid, passphrase, security_type))

    if data_list:
        report = ArtifactHtmlReport('Wi-Fi Hotspot')
        report.start_artifact_report(report_folder, 'Wi-Fi Hotspot')
        report.add_script()
        data_headers = ('SSID', 'Passphrase', 'SecurityType')
        report.write_artifact_data_table(data_headers, data_list, ", ".join(files_found))
        report.end_artifact_report()
        
        tsvname = f'wifi hotspot'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Wi-Fi Hotspot data available')

__artifacts__ = {
        "wifiHotspot": (
                "WiFi Profiles",
                ('*/misc/wifi/softap.conf', '*/misc**/apexdata/com.android.wifi/WifiConfigStoreSoftAp.xml'),
                get_wifiHotspot)
}