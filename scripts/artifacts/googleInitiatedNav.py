import blackboxprotobuf
from datetime import *
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, convert_utc_human_to_timezone, kmlgen, timeline

def get_googleInitiatedNav(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        with open(file_found, 'rb') as f:
            data = f.read()
            
            arreglo = (data)
            pb = arreglo[8:]
            values, types = blackboxprotobuf.decode_message(pb)
        
        if isinstance(values, dict):
            timestamp = values['1']['2']
            timestamp = datetime.fromtimestamp(timestamp/1000000, tz=timezone.utc)
            timestamp = convert_utc_human_to_timezone(timestamp, 'UTC')
            intendeddest = values['1']['4']['1'].decode()
            
            data_list.append((timestamp, intendeddest))
        else:
            for data in values['1']:
                timestamp = data['2']
                timestamp = datetime.fromtimestamp(timestamp/1000000, tz=timezone.utc)
                timestamp = convert_utc_human_to_timezone(timestamp, 'UTC')
                intendeddest = data['4']['1'].decode()
                
                data_list.append((timestamp, intendeddest))
                        
        if len(data_list) > 0:
            report = ArtifactHtmlReport('Google Initiated Navigation')
            report.start_artifact_report(report_folder, f'Google Initiated Navigation')
            report.add_script()
            data_headers = ('Timestamp', 'Initiated Navigation Destination')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Google Initiated Navigation'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Google Initiated Navigation'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc(f'No Google Initiated Navigation available')

__artifacts__ = {
        "googleInitiatedNav": (
                "GEO Location",
                ('*/com.google.android.apps.maps/files/new_recent_history_cache_navigated.cs','*/new_recent_history_cache_navigated.cs'),
                get_googleInitiatedNav)
}