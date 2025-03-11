import os
import datetime
from pathlib import Path

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly, is_platform_windows, media_to_html, logfunc


def get_duckThumbs(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        filename = (Path(file_found).name)
        utctime = int(Path(file_found).stem)
        filepath = str(Path(file_found).parents[1])
        
        timestamp = (datetime.datetime.utcfromtimestamp(utctime/1000).strftime('%Y-%m-%d %H:%M:%S'))
                
        thumb = media_to_html(filename, files_found, report_folder)
        
        platform = is_platform_windows()
        if platform:
            thumb = thumb.replace('?', '')
            
        data_list.append((timestamp, thumb, filename, file_found))
    
    
    if data_list:
        description = 'DuckDuckGo Tab Thumbnails'
        report = ArtifactHtmlReport('DuckDuckGo Tab Thumbnails')
        report.start_artifact_report(report_folder, 'DuckDuckGo Tab Thumbnails', description)
        report.add_script()
        data_headers = ('Timestamp','Thumbnail','Filename','Location' )
        report.write_artifact_data_table(data_headers, data_list, filepath, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'DuckDuckGo Tab Thumbnails'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'DuckDuckGo Tab Thumbnails'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No DuckDuckGo Tab Thumbnails data available')
        
__artifacts__ = {
        "DuckThumbs'": (
                "DuckDuckGo",
                ('*/com.duckduckgo.mobile.android/cache/tabPreviews/*/*.jpg'),
                get_duckThumbs)
}