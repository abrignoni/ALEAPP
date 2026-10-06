__artifacts_v2__ = {
    "alex_device_info": {
        "name": "ALEX Info",
        "description": "Reads the key and value pairs of device_info_alex.json from a PRFS backup created by ALEX. Key and value pairs are reported as stored, including the first object and literal hyphens.",
        "author": "@C_Peter, @AlexisBrignoni, Codex",
        "creation_date": "2025-10-17",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Device Information",
        "notes": "The first object is preserved as source content without assigning it a header "
                 "or device-attribute meaning. Device information is still populated only "
                 "from non-first objects whose values are not literal hyphens. Values are "
                 "not flattened or coerced; malformed roots and non-object entries are logged.",
        "paths": ('*/device_info_alex.json'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "terminal"
    }
}

import json
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, device_info, logfunc


@artifact_processor
def alex_device_info(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "device_info_alex.json")
    data_list = []
    
    try:
        with open(source_path, encoding='utf-8') as info_file:
            info_data = json.load(info_file)
            if not isinstance(info_data, list):
                logfunc(f'ALEX Info: unsupported JSON root in {context.get_relative_path(source_path)}; expected a list')
                return ('Key', 'Value'), data_list, source_path
            for index, pair in enumerate(info_data):
                if not isinstance(pair, dict):
                    logfunc(f'ALEX Info: skipping non-object entry {index} in {context.get_relative_path(source_path)}')
                    continue
                for key, value in pair.items():
                    data_list.append((key, value))
                    if index > 0 and value != "-":
                        device_info("ADB Live (ALEX)", key, value)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        logfunc(f'ALEX Info: cannot read {context.get_relative_path(source_path)}: {error}')

    data_headers = ('Key', 'Value')

    return data_headers, data_list, source_path