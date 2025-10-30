__artifacts_v2__ = {
    "usagestatsVersion": {
        "name": "OS Version",
        "description": "Extracts OS Version from Usagestats",
        "author": "@AlexisBrignoni",
        "creation_date": "2021-04-15",
        "last_update_date": "2025-03-07",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": ('*/system/usagestats/*/version', '*/system_ce/*/usagestats/version'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bar-chart-2"
    }
}


import scripts.artifacts.artGlobals
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_txt_file_content, \
    logfunc, device_info


@artifact_processor
def usagestatsVersion(files_found, report_folder, seeker, wrap_text):
    source_path = get_file_path(files_found, "version")
    data_list = []

    text_file = get_txt_file_content(source_path)
    for line in text_file:
        splits = line.strip().split(';')
        totalvalues = len(splits)
        if totalvalues >= 3:
            device_info("Usagestats", "Android version", splits[0])
            logfunc(f"Android version {str(splits[0])}")
            scripts.artifacts.artGlobals.versionf = splits[0]
            data_list.append(('Android Version', splits[0]))
            
            device_info("Usagestats", "Codename", splits[1])
            data_list.append(('Codename', splits[1]))
            
            device_info("Usagestats", "Build version", splits[2])
            data_list.append(('Build version', splits[2]))

        if totalvalues == 5:
            device_info("Usagestats", "Country Specific Code", splits[3])
            data_list.append(('Country Specific Code', splits[3]))            

    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, source_path
