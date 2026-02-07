__artifacts_v2__ = {
    "alex_live_appops": {
        "name": "App Ops",
        "description": "Reads App Ops Data \
            from a PRFS backup created by ALEX.",
        "author": "@C_Peter",
        "creation_date": "2026-01-30",
        "last_update_date": "2026-01-30",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/app_ops.json'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "package"
    }
}

import json
import datetime
from scripts.ilapfuncs import artifact_processor, \
    get_file_path

# App Ops
@artifact_processor
def alex_live_appops(files_found, _report_folder, _seeker, _wrap_text):
    source_path = get_file_path(files_found, "app_ops.json")
    data_list = []
    
    try:
        with open(source_path, "r", encoding="utf-8") as app_ops_file:
            app_ops_data = json.load(app_ops_file)
        for package, permissions in app_ops_data.items():
            for permission, value in permissions.items():
                state = None
                allowtime = None
                rejecttime = None
                if isinstance(value, str):
                    if value == "ignore":
                        continue
                    state = value
                elif isinstance(value, list):
                    state = value[0]
                    if state == "ignore":
                        continue
                    for entry in value[1:]:
                        if not isinstance(entry, dict):
                            continue
                        if "time" in entry:
                            try:
                                if isinstance(entry["time"], int):
                                    atime = entry["time"]
                                else:
                                    atime = int(entry["time"].split()[0])
                                allowtime = datetime.datetime.fromtimestamp(atime, tz=datetime.timezone.utc)
                            except ValueError:
                                pass
                        if "rejectTime" in entry:
                            try:
                                if isinstance(entry["rejectTime"], int):
                                    rtime = entry["rejectTime"]
                                else:
                                    rtime = int(entry["rejectTime"].split()[0])
                                rejecttime = datetime.datetime.fromtimestamp(rtime, tz=datetime.timezone.utc)
                            except ValueError:
                                pass
                data_list.append((allowtime, rejecttime, package, permission, state))  
    except (OSError, UnicodeDecodeError):
        pass

    data_headers = (('Access Timestamp', 'datetime'), ('Reject Timestamp', 'datetime'), 'Package Name', 'Permission', 'Value')

    return data_headers, data_list, source_path

