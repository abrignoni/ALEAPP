__artifacts_v2__ = {
    "alex_device_info": {
        "name": "ALEX Info",
        "description": "Reads device informations \
            from a PRFS backup created by ALEX.",
        "author": "@C_Peter",
        "creation_date": "2025-10-17",
        "last_update_date": "2025-10-17",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": ('*/device_info_alex.json'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "terminal"
    }
}

import json
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, device_info


@artifact_processor
def alex_device_info(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "device_info_alex.json")
    data_list = []
    
    try:
        with open(source_path, encoding='utf-8') as info_file:
            info_data = json.load(info_file)
            info_data.pop(0)
            for pair in info_data:
                for key, value in pair.items():
                    if value != "-":
                        device_info("ADB Live (ALEX)", key, value)
                        data_list.append((key, value))
    except (OSError, UnicodeDecodeError):
        pass

    data_headers = ('Key', 'Value')

    return data_headers, data_list, source_path