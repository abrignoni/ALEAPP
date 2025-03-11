import os
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_sRecoveryhist(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('history'):
            continue # Skip all other files
        
        data_list = []
        
        timestamp = wipe = promptwipe = reason = rebootreason = locale = updateorg = updatepkg = reqtime = ''
        with open(file_found, 'r') as f:
            for line in f:
                #print(line)
                if line.startswith('+'):
                    if '|' in line:
                        timestamp = line.split('|')
                        timestamp = timestamp[1].strip()
                        timestamp = timestamp.replace('/', '-')
                    else:
                        timestamp = line.split(':',1)
                        timestamp = timestamp[1].strip()
                        timestamp = timestamp.replace(']', '')
                        timestamp = timestamp.replace('/', '-')
                if line.startswith('--wipe_data'):
                    wipe = 'Yes'
                if line.startswith('--reason'):
                    reason = line.split('=')
                    reason = reason[1]
                if line.startswith('reboot_reason'):
                    rebootreason = line.split('=')
                    rebootreason = rebootreason[1]
                if line.startswith('reboot reason'):
                    rebootreason = line.split(':', 1)
                    rebootreason = rebootreason[1]
                if line.startswith('--locale'):
                    locale = line.split('=')
                    locale = locale[1]
                if line.startswith('--requested_time'):
                    reqtime = line.split('=')
                    reqtime = reqtime[1].replace('/', '-')
                if line.startswith('--update_org_package'):
                    updateorg = line.split('=')
                    updateorg = updateorg[1]
                if line.startswith('--update_package'):
                    updatepkg = line.split('=')
                    updatepkg = updatepkg[1]
                if line.startswith('--prompt_and_wipe_data'):
                    promptwipe = 'Yes'
                    wipe = 'Yes'
                if line.startswith('-\n'):
                    data_list.append((timestamp, wipe, promptwipe, reason, rebootreason, locale, reqtime, updateorg, updatepkg))
                    timestamp = wipe = promptwipe = reason = rebootreason = locale = updateorg = updatepkg = reqtime = ''
                    
        if data_list:
            report = ArtifactHtmlReport('Samsung Recovery History')
            report.start_artifact_report(report_folder, 'Samsung Recovery History')
            report.add_script()
            data_headers = ('Timestamp', 'Wipe', 'Promtp & Wipe', 'Reason', 'Reboot Reason', 'Locale', 'Request Timestamp', 'Update ORG', 'Update PKG')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Samsung Recovery History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Samsung Recovery History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Samsung Recovery History data available')

__artifacts__ = {
        "sRecoveryhist": (
                "Wipe & Setup",
                ('*/efs/recovery/history'),
                get_sRecoveryhist)
}