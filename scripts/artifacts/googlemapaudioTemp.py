from re import fullmatch
from datetime import datetime
from pathlib import Path
from os.path import getsize
import os


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, media_to_html

def get_googlemapaudioTemp(files_found, report_folder, seeker, wrap_text):

    data_list = []
    
    for file_found in files_found:

        name = Path(file_found).name
        modified_time = os.path.getmtime(file_found)
        file_size = getsize(file_found)
        has_data = file_size > 0

        if  os.path.isdir(file_found) is False:
            
            if has_data :
                
                # Timestamp
                utc_modified_date = datetime.utcfromtimestamp(modified_time)
                
                # Audio
                audio = media_to_html(file_found, files_found, report_folder)
                
                # Size
                file_size_kb = f"{round(file_size / 1024, 2)} kb"
    
                # Artefacts
                data_list.append((utc_modified_date,audio,name,file_size))


    if len(data_list) > 0:

        source_dir = str(Path(file_found).parent)

        report = ArtifactHtmlReport('Google Maps Temp Voice Guidance')
        report.start_artifact_report(report_folder, 'Google Maps Temp Voice Guidance')
        report.add_script()
        data_headers = ('Timestamp Modified', 'Audio', 'Name', 'File Size')
        report.write_artifact_data_table(data_headers, data_list, source_dir, html_escape=False)
        report.end_artifact_report()
            
        tsvname = f'Google Maps Temp Voice Guidance'
        tsv(report_folder, data_headers, data_list, tsvname, source_dir)
            
    else:
        logfunc('No Google Maps Temp Voice Guidance found')
            
__artifacts__ = {
        "GooglemapaudioT": (
                "Google Maps Temp Voice Guidance",
                ('*/com.google.android.apps.maps/app_tts-temp/**'),
                get_googlemapaudioTemp)
}