__artifacts_v2__ = {
    "powerOffReset": {
        "name": "Power Off Reset",
        "description": "Parses the REASON lines of Samsung's power_off_reset_reason.txt and its backup.",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Codex",
        "creation_date": "2021-10-12",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Power Events",
        "notes": "Only lines containing REASON: are reported. Timestamp "
                 "(Local) is the date and time as written in the log line and "
                 "Timezone Offset is the offset written directly after it on "
                 "the same line; both are reported as text, as stored. "
                 "Timestamp is computed by this module: the written time "
                 "minus the written offset, read in the usual numeric zone "
                 "sense where -0500 means five hours behind UTC. It is blank "
                 "when the written time and offset do not parse. On the three "
                 "listed images all 27 REASON lines carried a time and an "
                 "offset in the form YYYY-MM-DD HH:MM:SS followed by a sign "
                 "and four digits, and the offsets seen were +0200, -0400, "
                 "-0500 and -0600. No source for the log format was found and "
                 "the computed Timestamp was not compared with an independent "
                 "UTC record of the same events.",
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

from datetime import datetime, timezone

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
                    timezone_offset = timezone_split[1] 
                    
                    action = entry[1]
                    reason_split = entry[3].split(": ")
                    reason = reason_split[1]
                    
                    try:
                        timestamp_utc = datetime.strptime(
                            timestamp, '%Y-%m-%d %H:%M:%S%z').astimezone(timezone.utc)
                    except ValueError:
                        timestamp_utc = ''

                    data_list.append((timestamp_utc,timestamp1,timezone_offset,action,reason, context.get_relative_path(file_found)))
                else:
                    continue

    data_headers = (('Timestamp','datetime'),'Timestamp (Local)','Timezone Offset','Action','Reason','Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))