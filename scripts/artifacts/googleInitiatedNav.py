import blackboxprotobuf
from datetime import datetime, timezone
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, convert_utc_human_to_timezone, timeline

def get_googleInitiatedNav(files_found, report_folder, _seeker, _wrap_text):
    data_list = []
    for file_found in files_found:
        with open(file_found, 'rb') as f:
            data = f.read()

            pb = data[8:]
            values, _ = blackboxprotobuf.decode_message(pb)
        
        entries = values.get('1', [])
        if isinstance(entries, dict):
            entries = [entries]
        for entry in entries:
            timestamp = entry['2']
            timestamp = datetime.fromtimestamp(timestamp/1000000, tz=timezone.utc)
            timestamp = convert_utc_human_to_timezone(timestamp, 'UTC')
            intendeddest = entry['4']['1'].decode()
            data_list.append((timestamp, intendeddest))
                        
        if len(data_list) > 0:
            report = ArtifactHtmlReport('Google Initiated Navigation')
            report.start_artifact_report(report_folder, 'Google Initiated Navigation')
            report.add_script()
            data_headers = ('Timestamp', 'Initiated Navigation Destination')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = 'Google Initiated Navigation'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = 'Google Initiated Navigation'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No Google Initiated Navigation available')

__artifacts__ = {
        "googleInitiatedNav": (
                "GEO Location",
                ('*/com.google.android.apps.maps/files/new_recent_history_cache_navigated.cs','*/new_recent_history_cache_navigated.cs'),
                get_googleInitiatedNav)
}