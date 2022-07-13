import os
import shutil

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_vlcThumbs(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        data_file_real_path = file_found
        shutil.copy2(data_file_real_path, report_folder)
        data_file_name = os.path.basename(data_file_real_path)
        thumb = f'<img src="{report_folder}/{data_file_name}"></img>'
        
        data_list.append((data_file_name, thumb))
    
    path_to_files = os.path.dirname(data_file_real_path)
    
    description = 'VLC Thumbnails'
    report = ArtifactHtmlReport('VLC Thumbnails')
    report.start_artifact_report(report_folder, 'VLC Thumbnails', description)
    report.add_script()
    data_headers = ('Filename', 'Thumbnail' )
    report.write_artifact_data_table(data_headers, data_list, path_to_files, html_escape=False)
    report.end_artifact_report()
    
    tsvname = 'VLC Thumbnails'
    tsv(report_folder, data_headers, data_list, tsvname)
        


        
        