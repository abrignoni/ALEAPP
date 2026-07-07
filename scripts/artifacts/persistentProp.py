# pylint: disable=W0613
__artifacts_v2__ = {
    "get_persistentProp": {
        "name": "persistentProp",
        "description": "",
        "author": "",
        "creation_date": "2021-08-18",
        "last_update_date": "2021-08-18",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "",
        "paths": ('*/property/persistent_properties',),
        "output_types": "standard",
        "artifact_icon": "info-circle",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_persistentProp(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('persistent_properties'):
            continue  # Skip all other files

        source_path = file_found
        with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                clean = line.strip()
                if clean.startswith('persist.sys.boot.reason.historyDreboot'):
                    parts = clean.split(',')
                    utctimestamp = datetime.datetime.fromtimestamp(int(parts[-1]), datetime.timezone.utc)
                    description = parts[0]
                    data_list.append((utctimestamp, description))

                if clean.startswith('reboot,factory_reset,'):
                    parts = clean.split(',')
                    utctimestamp = datetime.datetime.fromtimestamp(int(parts[-1]), datetime.timezone.utc)
                    description = parts[0] + ' ' + parts[1]
                    data_list.append((utctimestamp, description))

                if clean.startswith('reboot'):
                    parts = clean.split(',')
                    if len(parts) == 2:
                        utctimestamp = datetime.datetime.fromtimestamp(int(parts[-1]), datetime.timezone.utc)
                        description = parts[0]
                        data_list.append((utctimestamp, description))

    data_headers = (('Timestamp', 'datetime'), 'Event')
    return data_headers, data_list, source_path
