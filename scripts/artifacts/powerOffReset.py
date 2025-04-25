import datetime
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_powerOffReset(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    pattern = 'REASON:'
    
    for file_found in files_found:
        file_found = str(file_found)
            
        with open(file_found, "r") as f:
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
                    
                    data_list.append((timestamp1,timezone,action,reason))
                else:
                    continue

        num_entries = len(data_list)
    if num_entries > 0:
        report = ArtifactHtmlReport('Power Off Reset')
        report.start_artifact_report(report_folder, 'Power Off Reset')
        report.add_script()
        data_headers = ('Timestamp (Local)','Timezone Offset','Action','Reason')

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Power Off Reset'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Power Off Reset'
        timeline(report_folder, tlactivity, data_list, data_headers)           
        
    else:
        logfunc('No Power Off Reset data available')

__artifacts__ = {
        "powerOffReset": (
                "Power Events",
                ('*/log/power_off_reset_reason.txt','*/log/power_off_reset_reason_backup.txt'),
                get_powerOffReset)
}