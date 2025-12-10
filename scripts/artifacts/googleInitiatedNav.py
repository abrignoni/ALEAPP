import blackboxprotobuf
from datetime import *
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, convert_utc_human_to_timezone, kmlgen, timeline

def get_googleInitiatedNav(files_found, report_folder, seeker, wrap_text):
    data_list = []
    
    for file_found in files_found:
        with open(file_found, 'rb') as f:
            data = f.read()

        arreglo = data
        pb = arreglo[8:]

        try:
            values, types = blackboxprotobuf.decode_message(pb)
        except Exception as e:
            logfunc(f"Failed to decode protobuf: {e}")
            continue

        # Perbaikan utama → cek values['1']
        if '1' not in values:
            logfunc('Key "1" missing in protobuf decoded data')
            continue

        entry = values['1']

        # Case A: entry adalah dict
        if isinstance(entry, dict):
            try:
                timestamp_raw = entry.get('2', None)
                if timestamp_raw is None:
                    raise KeyError("timestamp (key '2') missing")

                timestamp = datetime.fromtimestamp(timestamp_raw/1_000_000, tz=timezone.utc)
                timestamp = convert_utc_human_to_timezone(timestamp, 'UTC')

                intendeddest_raw = entry.get('4', {}).get('1', b'')
                intendeddest = intendeddest_raw.decode() if isinstance(intendeddest_raw, bytes) else str(intendeddest_raw)

                data_list.append((timestamp, intendeddest))
            except Exception as e:
                logfunc(f"Error parsing dict entry: {e}")

        # Case B: entry adalah list
        elif isinstance(entry, list):
            for item in entry:
                try:
                    timestamp_raw = item.get('2', None)
                    if timestamp_raw is None:
                        continue

                    timestamp = datetime.fromtimestamp(timestamp_raw/1_000_000, tz=timezone.utc)
                    timestamp = convert_utc_human_to_timezone(timestamp, 'UTC')

                    intendeddest_raw = item.get('4', {}).get('1', b'')
                    intendeddest = intendeddest_raw.decode() if isinstance(intendeddest_raw, bytes) else str(intendeddest_raw)

                    data_list.append((timestamp, intendeddest))
                except Exception as e:
                    logfunc(f"Error parsing list item: {e}")

        else:
            logfunc('Unexpected protobuf format: values["1"] is neither dict nor list')
            continue

    # Output
    if data_list:
        report = ArtifactHtmlReport('Google Initiated Navigation')
        report.start_artifact_report(report_folder, 'Google Initiated Navigation')
        report.add_script()
        data_headers = ('Timestamp', 'Initiated Navigation Destination')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsv(report_folder, data_headers, data_list, 'Google Initiated Navigation')
        timeline(report_folder, 'Google Initiated Navigation', data_list, data_headers)

    else:
        logfunc('No Google Initiated Navigation available')


__artifacts__ = {
        "googleInitiatedNav": (
                "GEO Location",
                ('*/com.google.android.apps.maps/files/new_recent_history_cache_navigated.cs','*/new_recent_history_cache_navigated.cs'),
                get_googleInitiatedNav)
}