import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import filetype 
import magic
import shutil
from os.path import isfile, join, basename, dirname, getsize, abspath
from pathlib import Path
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_appLockerfishingnet(files_found, report_folder, seeker, wrap_text):
    
    def media(fileinreportfolder):
        mimetype = magic.from_file(fileinreportfolder, mime = True)
        if 'video' in mimetype:
            thumb = f'<video width="320" height="240" controls="controls"><source src="{fileinreportfolder}" type="video/mp4">Your browser does not support the video tag.</video>'
        elif 'image' in mimetype:
            thumb = f'<img src="{fileinreportfolder}"width="300"></img>'
        else:
            thumb = f'<a href="{fileinreportfolder}"> Link to {mimetype} </>'
        
        return thumb
    
    data_list = []
    
    ## Known constants
    standardKey = '526e7934384e693861506a59436e5549'
    standardIV = '526e7934384e693861506a59436e5549'
    
    
    
    for file_found in files_found:
        file_found = str(file_found)
        
        filesize = (getsize(file_found))
        
        if not isfile(file_found):
            continue
        filename = basename(file_found)
        if filename.startswith('~'):
            continue
        if filename.startswith('._'):
            continue
        
        if filesize > 0:
            mimetype = magic.from_file(file_found, mime = True)
            
            ext = filetype.guess(file_found)
            if ext is None:
                #decrypt & add extension
                #Ecryption algo
                cipher = AES.new(bytes.fromhex(standardKey), AES.MODE_CBC, bytes.fromhex(standardIV))
                try:
                    with open (file_found, 'rb') as target:
                        decryptedData = cipher.decrypt(target.read())
                        fileExtension = filetype.guess(decryptedData)
                        
                    with open (join(report_folder, basename(file_found)) , 'wb') as decryptedFile:
                        decryptedFile.write(decryptedData)
                        decryptedFile.close()
                    decrypted = 'True'
                except ValueError as e:
                    logfunc(f'Error on {file_found}: {e}')
                    shutil.copyfile(file_found, join(report_folder, basename(file_found)))
                    decrypted = 'False'
                
            else:
                #print(ext.extension)
                shutil.copyfile(file_found, join(report_folder, basename(file_found)))
                decrypted = 'Not encrypted'
        
            thumb = media(join(report_folder, basename(file_found)))
            filename = basename(file_found)
                       
            data_list.append((thumb, filename, decrypted, file_found))
                            
                        
        if data_list:
            report = ArtifactHtmlReport('Calculator Locker')
            report.start_artifact_report(report_folder, 'Calculator Locker')
            report.add_script()
            data_headers = ('Media', 'Filename', 'Decrypted?','Full Path')
            maindirectory = str(Path(file_found).parents[1])
            report.write_artifact_data_table(data_headers, data_list, maindirectory, html_no_escape=['Media'])
            report.end_artifact_report()
            
            tsvname = f'Calculator Locker data'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            
        else:
            logfunc('No Calculator Locker data available')