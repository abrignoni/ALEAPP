import sys
import shutil
import os
import xml.etree.ElementTree as ET
import base64
import scripts.filetype as filetype
import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pathlib import Path
from os.path import isfile, join, basename, dirname, getsize, abspath
from pathlib import Path
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, media_to_html

def get_playgroundVault(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    
    for file_found in files_found:
        file_found = str(file_found)
        
        #filesize = (getsize(file_found))
        
        if not isfile(file_found):
            continue
        filename = basename(file_found)
        if filename.startswith('._'):
            continue
        if filename.startswith('crypto.KEY_256.xml'):
            tree = ET.parse(file_found)
            root = tree.getroot()
            key = base64.b64decode(root.findall('./string[@name="cipher_key"]')[0].text)
            logfunc(f'Encryption key found: {key}')
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if not isfile(file_found):
            continue
        filename = basename(file_found)
        if filename.startswith('._'):
            continue
        if filename.startswith('crypto.KEY_256.xml'):
            continue
        
        with open (file_found, 'rb') as openFile:
            #print('Atttempting to decrypt...')
            fullFile = openFile.read()
            ### IV is after the first 2 bytes
            IV = fullFile[2:14]
            ### Following IV encrypted data minus the GCM validation (16 bytes) at the end
            encryptedData = fullFile[14:-16]
            ### New encryption algo
            cipher = AES.new((key), AES.MODE_GCM, (IV))
            ### Decrypt the data
            decryptedData = cipher.decrypt((encryptedData))
            ### Determine the correct file extension
            fileExtension = filetype.guess(decryptedData)
            ### Open the new output file for writing
            
            with open (join(report_folder, basename(file_found)) , 'wb') as decryptedFile:
                decryptedFile.write(decryptedData)
                decryptedFile.close()
                
                tolink = []
                pathdec = join(report_folder, basename(file_found))
                tolink.append(pathdec)
                thumb = media_to_html(pathdec, tolink, report_folder)
                filename = basename(file_found)
                
                if 'EIF' in filename:
                    utctime = filename.split('EIF')
                    enctimestamp = datetime.datetime.utcfromtimestamp(int(utctime[1]) / 1000)
                elif 'EVF' in filename:
                    utctime = filename.split('EVF')
                    enctimestamp = datetime.datetime.utcfromtimestamp(int(utctime[1]) / 1000)
                else:
                    enctimestamp = ''
                    
                data_list.append((thumb, filename, enctimestamp, file_found))
    
        if data_list:
            report = ArtifactHtmlReport('Playground Vault')
            report.start_artifact_report(report_folder, 'Playground Vault')
            report.add_script()
            data_headers = ('Media', 'Filename', 'Encrypted On Timestamp', 'Full Path')
            maindirectory = str(Path(file_found).parents[1])
            report.write_artifact_data_table(data_headers, data_list, maindirectory, html_no_escape=['Media'])
            report.end_artifact_report()
            
            tsvname = f'Playground Vault'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            
        else:
            logfunc('No Playground Vault data available')

__artifacts__ = {
        "playgroundVault": (
                "Encrypting Media Apps",
                ('*/playground.develop.applocker/shared_prefs/crypto.KEY_256.xml','*/applocker/vault/*'),
                get_playgroundVault)
}