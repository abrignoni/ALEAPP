import os
import datetime
from PIL import Image

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_torThumbs(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        data_file_real_path = file_found
        modifiedtime = os.path.getmtime(file_found)
        modifiedtime = (datetime.datetime.fromtimestamp(int(modifiedtime)).strftime('%Y-%m-%d %H:%M:%S'))
        
        filename = os.path.basename(file_found)
        location = os.path.dirname(file_found)
        newfilename = filename + '.png'
        savepath = os.path.join(report_folder, newfilename)
        
        img = Image.open(file_found) 
        img.save(savepath,'png')
        
        thumb = f'<img src="{report_folder}/{newfilename}"width="300"></img>'
        
        data_list.append((modifiedtime, thumb, filename, location))
    
    path_to_files = os.path.dirname(filename)
    
    if data_list:
        description = 'TOR Thumbnails'
        report = ArtifactHtmlReport('TOR Thumbnails')
        report.start_artifact_report(report_folder, 'TOR Thumbnails', description)
        report.add_script()
        data_headers = ('Modified Time','Thumbnail','Filename','Location' )
        report.write_artifact_data_table(data_headers, data_list, path_to_files, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'TOR Thumbnails'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'TOR Thumbnails'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No TOR Thumbnails data available')
        

        
        