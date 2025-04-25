import os
import datetime
from pathlib import Path

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly, is_platform_windows, media_to_html, logfunc


def get_vlcthumbsADB(files_found, report_folder, seeker, wrap_text):
    data_list_t = []
    data_list_m = []
    for file_found in files_found:
        file_found = str(file_found)
        
        
        filename = (Path(file_found).name)
        filepath = str(Path(file_found).parents[1])
        
        modifiedtime = os.path.getmtime(file_found)
        modifiedtime = (datetime.datetime.utcfromtimestamp(int(modifiedtime)).strftime('%Y-%m-%d %H:%M:%S'))
        
        thumb = media_to_html(filename, files_found, report_folder)
        
        platform = is_platform_windows()
        if platform:
            thumb = thumb.replace('?', '')
        
        if "thumbnails" in file_found:
            data_list_t.append((modifiedtime, thumb, filename, file_found))
        else:
            data_list_m.append((modifiedtime, thumb, filename, file_found))
    
    if data_list_t:
        description = 'VLC Thumbnails'
        report = ArtifactHtmlReport('VLC Thumbnails')
        report.start_artifact_report(report_folder, 'VLC Thumbnails', description)
        report.add_script()
        data_headers = ('Modified Timestamp','Thumbnail','Filename','Location' )
        report.write_artifact_data_table(data_headers, data_list_t, filepath, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'VLC Thumbnails'
        tsv(report_folder, data_headers, data_list_t, tsvname)
        
        tlactivity = f'VLC Thumbnails'
        timeline(report_folder, tlactivity, data_list_t, data_headers)
    else:
        logfunc('VLC Thumbnails data available')
    
    if data_list_m:
        description = 'VLC Media Lib'
        report = ArtifactHtmlReport('VLC Media Lib')
        report.start_artifact_report(report_folder, 'VLC Media Lib', description)
        report.add_script()
        data_headers = ('Modified Timestamp','Thumbnail','Filename','Location')
        report.write_artifact_data_table(data_headers, data_list_m, filepath, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'VLC Media Lib'
        tsv(report_folder, data_headers, data_list_m, tsvname)
        
        tlactivity = f'VLC Media Lib'
        timeline(report_folder, tlactivity, data_list_m, data_headers)
    else:
        logfunc('VLC Media Lib data available')
        
__artifacts__ = {
        "VLC Thumbs ADB": (
                "VLC thumbs",
                ('*/org.videolan.vlc/ef/medialib/*.*','*/org.videolan.vlc/ef/medialib/thumbnails/*.*'),
                get_vlcthumbsADB)
}