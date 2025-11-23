import datetime
import email
import os
import struct
import gzip
import shutil
from io import BytesIO

from scripts.filetype import guess_mime, guess_extension
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, media_to_html, is_platform_windows

def get_browserCachechrome(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('_0'):
        
            filename = os.path.basename(file_found)
            
            modified_time = os.path.getmtime(file_found)
            utc_modified_date = datetime.datetime.utcfromtimestamp(modified_time)
            
            with open(file_found, 'rb') as file:
                data = file.read()
                ab = BytesIO(data)
                
                try:
                    eofloc = data.index(b'\xD8\x41\x0D\x97\x45\x6F\xFA\xF4')
                except ValueError:
                    logfunc(f'Skipping {file_found}: Expected byte pattern not found')
                    continue
                
                header = ab.read(8)
                version = ab.read(4)
                lenghturl = ab.read(4)
                lenghturl = (struct.unpack_from("<i",lenghturl)[0])
                dismiss = ab.read(8)
                
                headerlenght = lenghturl + 8 + 4 + 4 + 8
                
                url = ab.read(lenghturl)
                url = (url.decode())
                filedata = ab.read(eofloc - headerlenght)
                
                mime = guess_mime(filedata)
                ext = guess_extension(filedata)
                
                sfilename = filename + '.' + ext if ext else filename
                spath = os.path.join(report_folder,sfilename)
                
                with open(f'{spath}', 'wb') as d:
                    d.write(filedata)
                
                if ext == 'x-gzip':
                    try:
                        with gzip.open(f'{spath}', 'rb') as f_in:
                            file_content = f_in.read()
                                
                            mime = guess_mime(file_content)
                            extin = guess_extension(file_content)
                            #logfunc(f'Gzip mime: {mime} for {spath}')    
                            sfilename = filename + '.' + extin if extin else filename
                            spath = os.path.join(report_folder,sfilename)
                            
                        with open(f'{spath}', 'wb') as f_out:
                            f_out.write(file_content)

                    except Exception as e: logfunc(str(e))
                
                filetosearch = []
                filetosearch.append(spath)
                
                media = media_to_html(sfilename, filetosearch, report_folder)
                if is_platform_windows:
                    media = media.replace('/?','',1)

                data_list.append((utc_modified_date, filename, mime, media, url, file_found))
        
    if len(data_list) > 0:
        note = 'Source location in extraction found in the report for each item.'
        report = ArtifactHtmlReport('Chrome Browser Cache')
        report.start_artifact_report(report_folder, f'Chrome Browser Cache')
        report.add_script()
        data_headers = ('Timestamp Modified', 'Filename', 'Mime Type', 'Cached File', 'Source URL', 'Source')
        report.write_artifact_data_table(data_headers, data_list, note, html_no_escape=['Cached File'])
        report.end_artifact_report()
        
        tsvname = f'Chrome Browser Cache'
        tsv(report_folder, data_headers, data_list, tsvname)
    
__artifacts__ = {
        "browserCachechrome": (
                "Browser Cache",
                ( '*/data/com.android.chrome/cache/Cache/*_0'),
                get_browserCachechrome)
}
            
