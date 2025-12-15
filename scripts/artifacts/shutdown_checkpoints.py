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
    }
}

import datetime
from scripts.ilapfuncs import logfunc, artifact_processor

@artifact_processor
def shutdown_checkpoints(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    pattern = 'Shutdown request from '
    pattern2 = 'epoch='
    
    for file_found in files_found:
        file_found = str(file_found)
            
        with open(file_found, "r") as f:
            data = f.readlines()
            for line in data:
                if pattern in line:
                    
                    line = line.replace('\n','')
                    entry = line.split(" ")
                    request = entry[3]
                    
                    entry_epoch = line.split("epoch=")
                    epoch = int(entry_epoch[1].replace(')',''))
                    shutdown_timestamp = datetime.datetime.utcfromtimestamp(epoch/1000).strftime('%Y-%m-%d %H:%M:%S')
                    
                    data_list.append((shutdown_timestamp, request, line, file_found))
                else:
                    continue

    data_headers = (('Timestamp','datetime'),'Requestor','Entry','Source File')
    return data_headers, data_list, 'See source file(s) below:' 