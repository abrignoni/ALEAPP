__artifacts_v2__ = {
    "powerOffReset": {
        "name": "Power Off Reset",
        "description": "Parses the REASON lines of Samsung's power_off_reset_reason.txt and its backup.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2021-10-12",
        "last_update_date": "2025-08-09",
        "requirements": "none",
        "category": "Power Events",
        "notes": "Only lines containing REASON: are reported. Timestamp "
                 "(Local) is the device local time as written in the log, and "
                 "Timezone Offset is the offset the same log line carries. No "
                 "conversion to UTC is made. The column is typed as a "
                 "datetime, so a viewer that assumes UTC shows the local "
                 "reading as if it were UTC.",
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
    source_paths = set()
    pattern = 'REASON:'

    for file_found in files_found:
        file_found = str(file_found)
        source_paths.add(file_found)

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
    return data_headers, data_list, '\n'.join(sorted(source_paths))