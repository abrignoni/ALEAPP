__artifacts_v2__ = {
    "get_persistentProp": {
        "name": "persistentProp",
        "description": "Parses persistent system properties and their set times (timestamp and event) from the persistent_properties file.",
        "author": "",
        "creation_date": "2021-08-18",
        "last_update_date": "2021-08-18",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "",
        "paths": ('*/property/persistent_properties',),
        "output_types": "standard",
        "artifact_icon": "info-circle",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "userb2_a13": "Android 13 | 0 rows",
        },
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_persistentProp(context):
    files_found = context.get_files_found()

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
