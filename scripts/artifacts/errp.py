# pylint: disable=W0613
__artifacts_v2__ = {
    "get_errp": {
        "name": "Errp",
        "description": "",
        "author": "",
        "creation_date": "2021-08-15",
        "last_update_date": "2021-08-15",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "",
        "paths": ('*/system/users/service/eRR.p',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
    }
}

from scripts.ilapfuncs import artifact_processor, convert_local_to_utc


@artifact_processor
def get_errp(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('eRR.p'):
            continue  # Skip all other files

        source_path = file_found
        with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if line.startswith('LOGM') or line == '':
                    continue

                parts = line.split('|')
                timestamp = parts[0].strip()
                timestamp_utc = str(convert_local_to_utc(timestamp))
                event = parts[1].strip() if len(parts) >= 2 else ''
                code = parts[2].strip() if len(parts) >= 3 else ''
                details = parts[3].strip() if len(parts) >= 4 else ''
                data_list.append((timestamp_utc, timestamp, event, code, details))

    data_headers = ('Timestamp', 'Timestamp (Local)', 'Event', 'Code', 'Details')
    return data_headers, data_list, source_path
