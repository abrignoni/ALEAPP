# pylint: disable=W0631
__artifacts_v2__ = {
    "factory_reset": {
        "name": "Factory Reset",
        "description": "Reports the factory_reset bootstat record; AOSP stores the event value in the file's modification time.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2022-01-05",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "Extraction and acquisition handling can disturb file timestamps, so validate the value against other sources. Reference: AOSP bootstat, 'boot_event_record_store.cpp (event values are stored in the file mtime attribute)', https://android.googlesource.com/platform/system/core/+/refs/heads/main/bootstat/boot_event_record_store.cpp",
        "paths": ('*/misc/bootstat/factory_reset'),
        "output_types": "standard",
        "artifact_icon": "loader",
        "sample_data": {
            "anne_a15": "Android 15 | 1 row",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel7a_a14": "Android 14 | 1 row",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "userb2_a13": "Android 13 | 1 row",
        },
    }
}

import os
import time

from scripts.ilapfuncs import artifact_processor, logdevinfo

@artifact_processor
def factory_reset(context):
    files_found = context.get_files_found()

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
