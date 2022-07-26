import os
import time

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, media_to_html, timeline

def triage_text(file_found):
    output = ''
    with open(file_found,'r' ,encoding="utf8", errors="backslashreplace") as file:
        counter = 0
        for f in file:
            counter = counter + 1
            if counter == 8:
                output = output + (f[20:])
            elif counter > 8:
                output = output + (f)
        
        if not output:
            counter = 0
            file.seek(0)
            for f in file:
                counter = counter + 1
                if counter == 7:
                    output = output + (f[91:])
                elif counter > 7:
                    output = output + (f)
    
    return str(output.rstrip())

def get_clipBoard(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        if file_found.endswith('.DS_Store'):
            pass
        else:
            if os.path.isfile(file_found):
                dirname = os.path.dirname(file_found)
                matching = [s for s in files_found if dirname in s]
                if len(matching) > 1:
                    if file_found.endswith('clip'):
                        pass
                    else:
                        thumb = media_to_html(file_found, files_found, report_folder)
                        path = file_found
                        modtime = os.path.getmtime(file_found)
                        modtime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(modtime))
                        data_list.append((thumb, modtime, path))
                else:
                    #print('Outside of Matching')
                    path = file_found
                    textdata = triage_text(file_found)
                    modtime = os.path.getmtime(file_found)
                    modtime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(modtime))
                    data_list.append((textdata, modtime, path))
            
            
    
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Clipboard Data')
        report.start_artifact_report(report_folder, f'Clipboard Data')
        report.add_script()
        data_headers = ('Data', 'Modified Time', 'Path')
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Clipboard Data'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Clipboard Data'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc(f'No Clipboard Data available')

__artifacts__ = {
        "ClipBoard": (
                "Clipboard",
                ('*/data/*clipboard/*/*'),
                get_clipBoard)
}