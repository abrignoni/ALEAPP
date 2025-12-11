__artifacts_v2__ = {
    "last_boot_time": {
        "name": "Last Boot Time",
        "description": "Parses the last boot timestamp of the device",
        "author": "@stark4n6",
        "creation_date": "2022-01-05",
        "last_update_date": "2025-08-09",
        "requirements": "none",
        "category": "Power Events",
        "notes": "",
        "paths": ('*/misc/bootstat/last_boot_time_utc'),
        "output_types": "standard",
        "artifact_icon": "power",
    }
}

import os
import time
from scripts.ilapfuncs import logfunc, logdevinfo, artifact_processor

@artifact_processor
def last_boot_time(files_found, report_folder, seeker, wrap_text):

    data_list = []

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('last_boot_time_utc'):
            continue # Skip all other files
        
        file_name = 'last_boot_time_utc'
        modTimesinceEpoc = os.path.getmtime(file_found)

        last_boot_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(modTimesinceEpoc))
                     
        logdevinfo(f"<b>Last Boot Timestamp: </b>{last_boot_time}")
        data_list.append((last_boot_time, file_name))

    data_headers = (('Timestamp','datetime'), 'File Name')
    return data_headers, data_list, file_found