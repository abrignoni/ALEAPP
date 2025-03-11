from re import fullmatch
from datetime import datetime
from pathlib import Path
from os.path import getsize


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, media_to_html

def convertGeo(s):
    length = len(s)
    if length > 6:
        return (s[0 : length-6] + "." + s[length-6 : length])
    else:
        return (s)

def get_googlemapaudio(files_found, report_folder, seeker, wrap_text):

    files_found = list(filter(lambda x: "sbin" not in x, files_found))

    data_headers = ("Timestamp", "Filename", "Audio", "Size")
    audio_info = []
    source_dir = ""

    pattern = r"-?\d+_\d+"

    for file_found in files_found:

        name = Path(file_found).name

        match = fullmatch(pattern, name)
        file_size = getsize(file_found)
        has_data = file_size > 0

        if match and has_data:

            # Timestamp
            timestamp = Path(file_found).name.split("_")[1]
            timestamp_datetime = datetime.utcfromtimestamp(int(timestamp) / 1000)
            timestamp_str = timestamp_datetime.isoformat(timespec="seconds", sep=" ")
            
            # Audio
            audio = media_to_html(name, files_found, report_folder)
            
            # Size
            file_size_kb = f"{round(file_size / 1024, 2)} kb"

            # Artefacts
            info = (timestamp_str, name, audio, file_size_kb)
            audio_info.append(info)


    if audio_info:

        source_dir = str(Path(files_found[0]).parent)

        report = ArtifactHtmlReport('Google Maps Voice Guidance')
        report.start_artifact_report(report_folder, 'Google Maps Voice Guidance')
        report.add_script()

        report.write_artifact_data_table(data_headers, audio_info, source_dir, html_escape=False)
        report.end_artifact_report()
            
        tsvname = f'Google Map Audio'
        tsv(report_folder, data_headers, audio_info, tsvname, source_dir)
            
    else:
        logfunc('No Google Audio Locations found')
            
__artifacts__ = {
        "Googlemapaudio": (
                "Google Maps Voice Guidance",
                ('*/com.google.android.apps.maps/app_tts-cache/*_*'),
                get_googlemapaudio)
}