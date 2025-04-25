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

def get_browserCachefirefox(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        filename = os.path.basename(file_found)
        
        modified_time = os.path.getmtime(file_found)
        utc_modified_date = datetime.datetime.utcfromtimestamp(modified_time)
        
        with open(file_found, 'rb') as file:
            data = file.read()
            
            ab = BytesIO(data)
            try:
                indexone = data.index(b'partitionKey=%28') + 16
                indextwo = data.index(b'necko') - 1
                urltoread = indextwo - indexone
                ab.read(indexone)
                url = ab.read(urltoread)
                url = (url.decode())
            except:
                url = ''
            
            mime = guess_mime(file_found)
            ext = guess_extension(file_found)
            
            sfilename = filename + '.' + ext if ext else filename
            spath = os.path.join(report_folder,sfilename)
            shutil.copy2(file_found, spath)
            
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
        report = ArtifactHtmlReport('Firefox Browser Cache')
        report.start_artifact_report(report_folder, f'Firefox  Browser Cache')
        report.add_script()
        data_headers = ('Timestamp Modified', 'Filename', 'Mime Type', 'Cached File', 'Source URL', 'Source')
        report.write_artifact_data_table(data_headers, data_list, note, html_no_escape=['Cached File'])
        report.end_artifact_report()
        
        tsvname = f'Firefox Browser Cache'
        tsv(report_folder, data_headers, data_list, tsvname)

            
__artifacts__ = {
        "browserCachefirefox": (
                "Browser Cache",
                ( '*/data/org.mozilla.firefox/cache/*/cache2/entries/**'),
                get_browserCachefirefox)
}
            