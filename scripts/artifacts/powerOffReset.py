__artifacts_v2__ = {
    "powerOffReset": {
        "name": "Power Off Reset",
        "description": "Parses powering off and reset events",
        "author": "@stark4n6",
        "creation_date": "2021-10-12",
        "last_update_date": "2025-08-09",
        "requirements": "none",
        "category": "Power Events",
        "notes": "",
        "paths": ('*/log/power_off_reset_reason.txt','*/log/power_off_reset_reason_backup.txt'),
        "output_types": "standard",
        "artifact_icon": "power",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 9 rows",
            "samsungs20_a13": "Android 13 | 8 rows",
            "sharon_a14": "Android 14 | 10 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor

@artifact_processor
def powerOffReset(context):
    files_found = context.get_files_found()
    data_list = []
    pattern = 'REASON:'
    
    for file_found in files_found:
        file_found = str(file_found)
            
        with open(file_found, "r", encoding="utf-8") as f:
            data = f.readlines()
            for line in data:
                if pattern in line:
                    entry = [x.strip() for x in line.split("|")]
            
                    time_split = entry[0].split()
                    
                    timestamp = time_split[1]+' '+time_split[2]
                    
                    timezone_split = []
                    
                    for index in range(0, len(timestamp), 19):
                        timezone_split.append(timestamp[index : index + 19])                    
                    
                    timestamp1 = timezone_split[0]
                    timezone = timezone_split[1] 
                    
                    action = entry[1]
                    reason_split = entry[3].split(": ")
                    reason = reason_split[1]
                    
                    data_list.append((timestamp1,timezone,action,reason, context.get_relative_path(file_found)))
                else:
                    continue

    data_headers = (('Timestamp (Local)','datetime'),'Timezone Offset','Action','Reason','Source File')
    return data_headers, data_list, 'See source file(s) below:'