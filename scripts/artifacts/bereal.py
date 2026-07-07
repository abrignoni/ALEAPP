__artifacts_v2__ = {
    "berealAndroidCache": {
        "name": "BeReal Android - Cache",
        "description": "Parses BeReal Android cached JSON artifacts",
        "author": "@Gear-I",
        "creation_date": "2026-07-06",
        "last_update_date": "2026-07-06",
        "requirements": "none",
        "category": "BeReal",
        "notes": "Initial Android BeReal artifact parser",
        "paths": (
            "*/data/data/com.bereal.ft/cache/*",
            "*/data/user/0/com.bereal.ft/cache/*",
            "*/data/data/com.bereal.ft/files/*",
            "*/data/user/0/com.bereal.ft/files/*",
            "*/Android/data/com.bereal.ft/*",
        ),
        "output_types": ["lava", "html", "tsv"],
        "artifact_icon": "camera"
    }
}
# Parse BeReal Android cached artifacts.


import json
import os
from pathlib import Path

from scripts.ilapfuncs import artifact_processor


def get_json_data(file_path):
    if not os.path.isfile(file_path):
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        return {}

    except UnicodeDecodeError:
        return {}

    except OSError as ex:
        logfunc(f"Error reading BeReal file {file_path}: {ex}")
        return {}


@artifact_processor
def berealAndroidCache(context):
    data_headers = (
        "File Name",
        "Key",
        "Value",
        "Source Path"
    )

    data_list = []

    for file_found in context.get_files_found():
        json_data = get_json_data(file_found)

        if not json_data:
            continue

        file_name = Path(file_found).name

        if isinstance(json_data, dict):
            for key, value in json_data.items():
                data_list.append((
                    file_name,
                    key,
                    str(value),
                    file_found
                ))

        elif isinstance(json_data, list):
            for index, value in enumerate(json_data):
                data_list.append((
                    file_name,
                    f"[{index}]",
                    str(value),
                    file_found
                ))

    return data_headers, data_list, "See Source Path"