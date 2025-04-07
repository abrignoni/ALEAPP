import datetime
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_shutdown_checkpoints(files_found, report_folder, seeker, wrap_text, time_offset):
    
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

        num_entries = len(data_list)
    if num_entries > 0:
        report = ArtifactHtmlReport('Shutdown Checkpoints')
        report.start_artifact_report(report_folder, 'Shutdown Checkpoints')
        report.add_script()
        data_headers = ('Timestamp','Requestor','Entry','Source File')

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Shutdown Checkpoints'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Shutdown Checkpoints'
        timeline(report_folder, tlactivity, data_list, data_headers)           
        
    else:
        logfunc('No Shutdown Checkpoints data available')

__artifacts__ = {
        "shutdown_checkpoints": (
                "Power Events",
                ('*/system/shutdown-checkpoints/checkpoints-*'),
                get_shutdown_checkpoints)
}