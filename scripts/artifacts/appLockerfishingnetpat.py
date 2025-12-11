import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_appLockerfishingnetpat(files_found, report_folder, seeker, wrap_text):
    
    standardKey = '526e7934384e693861506a59436e5549'
    standardIV = '526e7934384e693861506a59436e5549'
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        tree = ET.parse(file_found)
        root = tree.getroot()
        encryptedPattern = root.findall('./string[@name="85B064D26810275C89F1F2CC15E20B442E98874398F16F6717BBD5D34920E3F8"]')[0].text
        cipher = AES.new(bytes.fromhex(standardKey), AES.MODE_CBC, bytes.fromhex(standardIV))
        decryptedPattern = unpad(cipher.decrypt(bytes.fromhex(encryptedPattern)), AES.block_size)
            
                       
        data_list.append((encryptedPattern, decryptedPattern))
                            
                        
        if data_list:
            report = ArtifactHtmlReport('Calculator Locker Pattern')
            report.start_artifact_report(report_folder, 'Calculator Locker Pattern')
            report.add_script()
            data_headers = ('Encrypted Pattern', 'Decrypted Pattern')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Media'])
            report.end_artifact_report()
            
            tsvname = f'Calculator Locker Pattern data'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            
        else:
            logfunc('No Calculator Locker Pattern data available')
            
__artifacts__ = {
        "App Locker Pat": (
                "Encrypting Media Apps",
                ('*/com.hld.anzenbokusufake/shared_prefs/share_privacy_safe.xml'),
                get_appLockerfishingnetpat)
}