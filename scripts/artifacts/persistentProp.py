import os
import datetime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_persistentProp(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('persistent_properties'):
            continue # Skip all other files
        
        data_list = []
        with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                clean = line.strip()
                if clean.startswith('persist.sys.boot.reason.historyDreboot'):
                    parts = clean.split(',')
                    utctimestamp = (datetime.datetime.utcfromtimestamp(int(parts[-1])).strftime('%Y-%m-%d %H:%M:%S'))
                    description = parts[0]
                    data_list.append((utctimestamp, description))
                    
                if clean.startswith('reboot,factory_reset,'):
                    parts = clean.split(',')
                    utctimestamp = (datetime.datetime.utcfromtimestamp(int(parts[-1])).strftime('%Y-%m-%d %H:%M:%S'))
                    description = parts[0] + ' ' + parts[1]
                    data_list.append((utctimestamp, description))
                    
                if clean.startswith('reboot'):
                    parts = clean.split(',')
                    if len(parts) == 2:
                        utctimestamp = (datetime.datetime.utcfromtimestamp(int(parts[-1])).strftime('%Y-%m-%d %H:%M:%S'))
                        description = parts[0]
                        data_list.append((utctimestamp, description))
                            
        if data_list:
            report = ArtifactHtmlReport('Persistent Properties')
            report.start_artifact_report(report_folder, 'Persistent Properties')
            report.add_script()
            data_headers = ('Timestamp', 'Event')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Persistent Properties'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Persistent Properties'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Persistent Properties data available')
            
__artifacts__ = {
        "persistentProp": (
                "Wipe & Setup",
                ('*/property/persistent_properties'),
                get_persistentProp)
}