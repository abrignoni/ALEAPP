__artifacts_v2__ = {
    "adb_hosts": {
        "name": "ADB Hosts",
        "description": "Authentication keys used in the Android Debug Bridge (ADB) protocol \
            to secure communication between a device and a computer.",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-11-21",
        "last_update_date": "2025-03-15",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": ('*/misc/adb/adb_keys'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "terminal"
    }
}


from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_txt_file_content, device_info


@artifact_processor
def adb_hosts(files_found, report_folder, seeker, wrap_text):
    source_path = get_file_path(files_found, "adb_keys")
    data_list = []
    
    file = get_txt_file_content(source_path)
    for line in file:
        try:
            adb_host = line.split(" ")[1].rstrip('\n')
            if 'unknown' not in adb_host:
                device_info("ADB Hosts", "Hosts", adb_host, source_path)
            data_list.append(adb_host.split('@', 1))
        except:
            pass
    
    data_headers = ('Username', 'Hostname')

    return data_headers, data_list, source_path