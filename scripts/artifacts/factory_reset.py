__artifacts_v2__ = {
    "factory_reset": {
        "name": "Factory Reset",
        "description": "Timestamp of when a factory reset occurred",
        "author": "Kevin Pagano",
        "creation_date": "2022-01-05",
        "last_updated_date": "2025-09-09",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "",
        "paths": ('*/misc/bootstat/factory_reset'),
        "output_types": "standard",
        "artifact_icon": "loader",
    }
}

import os
import time

from scripts.ilapfuncs import artifact_processor, logdevinfo

@artifact_processor
def factory_reset(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('factory_reset'):
            continue # Skip all other files
        
        data_list = []
        file_name = 'factory_reset'
        
        modTimesinceEpoc = os.path.getmtime(file_found)

        reset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(modTimesinceEpoc))
                     
        logdevinfo(f"<b>Factory Reset Timestamp: </b>{reset_time}")
        data_list.append((reset_time, file_name))
    
    data_headers = ('Timestamp', 'File Name')
    return data_headers, data_list, file_found