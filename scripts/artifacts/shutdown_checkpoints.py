__artifacts_v2__ = {
    "shutdown_checkpoints": {
        "name": "Shutdown Checkpoints",
        "description": "Parses powering off and reset events",
        "author": "@stark4n6",
        "creation_date": "2022-01-22",
        "last_update_date": "2025-08-09",
        "requirements": "none",
        "category": "Power Events",
        "notes": "",
        "paths": ('*/system/shutdown-checkpoints/checkpoints-*'),
        "output_types": "standard",
        "artifact_icon": "power",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | 61 rows",
            "kevin_pocox7_a15": "Android 15 | 31 rows",
            "pixel7a_a14": "Android 14 | 41 rows",
        },
    }
}

import datetime
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def shutdown_checkpoints(context):
    files_found = context.get_files_found()
    data_list = []
    pattern = 'Shutdown request from '

    for file_found in files_found:
        file_found = str(file_found)
            
        with open(file_found, "r", encoding="utf-8") as f:
            data = f.readlines()
            for line in data:
                if pattern in line:
                    
                    line = line.replace('\n','')
                    entry = line.split(" ")
                    request = entry[3]
                    
                    entry_epoch = line.split("epoch=")
                    epoch = int(entry_epoch[1].replace(')',''))
                    shutdown_timestamp = datetime.datetime.utcfromtimestamp(epoch/1000).strftime('%Y-%m-%d %H:%M:%S')
                    
                    data_list.append((shutdown_timestamp, request, line, context.get_relative_path(file_found)))
                else:
                    continue

    data_headers = (('Timestamp','datetime'),'Requestor','Entry','Source File')
    return data_headers, data_list, 'See source file(s) below:' 