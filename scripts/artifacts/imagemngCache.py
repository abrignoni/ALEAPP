import datetime
from os.path import isfile, isdir, join, basename, dirname, getsize, abspath, getmtime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, media_to_html, timeline

def get_imagemngCache(files_found, report_folder, seeker, wrap_text):
    data_list = []
    
    for file_found in files_found:
        if isdir(file_found):
            continue
        #else:
        filename = basename(file_found)
        thumb = media_to_html(filename, files_found, report_folder)
        last_modified_date = datetime.datetime.utcfromtimestamp(getmtime(file_found))
        data_list.append((last_modified_date, thumb, filename, file_found))
    
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Image Manager Cache')
        report.start_artifact_report(report_folder, f'Image Manager Cache')
        report.add_script()
        data_headers = ('Timestamp Last Modified', 'Media', 'Filename', 'Source File')
        report.write_artifact_data_table(data_headers, data_list, 'See paths in report', html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Image Manager Cache'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Image Manager Cache'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc(f'No Image Manager Cache files available')

__artifacts__ = {
        "ImagemngCache": (
                "Image Manager Cache",
                ('*/cache/image_manager_disk_cache/*.*','*/*.cnt'),
                get_imagemngCache)
}