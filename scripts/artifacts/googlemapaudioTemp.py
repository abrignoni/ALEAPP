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
        file_found = str(file_found)

        # Skip folder
        if os.path.isdir(file_found):
            continue
        
        # Optional: skip file tanpa ekstensi audio 
        # (Maps biasanya menghasilkan .wav)
        if not file_found.lower().endswith(('.wav', '.mp3', '.ogg')):
            continue

        try:
            modified_time = os.path.getmtime(file_found)
        except FileNotFoundError:
            # File gagal di-copy oleh ALEAPP, skip
            logfunc(f"Skipped missing file: {file_found}")
            continue

        file_size = getsize(file_found)
        if file_size == 0:
            continue

        # Timestamp
        utc_modified_date = datetime.utcfromtimestamp(modified_time)

        # Audio HTML embed
        audio = media_to_html(file_found, files_found, report_folder)

        name = Path(file_found).name

        data_list.append((utc_modified_date, audio, name, file_size))

    if data_list:
        source_dir = str(Path(file_found).parent)

        report = ArtifactHtmlReport('Google Maps Temp Voice Guidance')
        report.start_artifact_report(report_folder, 'Google Maps Temp Voice Guidance')
        report.add_script()
        data_headers = ('Timestamp Modified', 'Audio', 'Name', 'File Size')
        report.write_artifact_data_table(data_headers, data_list, source_dir, html_escape=False)
        report.end_artifact_report()

        tsv(report_folder, data_headers, data_list, 'Google Maps Temp Voice Guidance', source_dir)

    else:
        logfunc('No Google Maps Temp Voice Guidance found')
            
__artifacts__ = {
        "GooglemapaudioT": (
                "Google Maps Temp Voice Guidance",
                ('*/com.google.android.apps.maps/app_tts-temp/**'),
                get_googlemapaudioTemp)
}