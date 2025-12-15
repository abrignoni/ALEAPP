import os
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_sWipehist(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('history'):
            name = 'History'
        if file_found.endswith('recovery_history.log'):
            name = 'Recovery History Log'
        
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
                    reason = line.split('=', 1)
                    reason = reason[1]
                    if 'Fmm.RemoteWipeOut' in reason:
                        provider = 'Samsung Find My Mobile'
                    elif 'Find My Device wiping device remotely' in reason:
                        provider = 'Google Find My Device'
                    elif 'MasterClearConfirm' in reason:
                        provider = 'Local Android UI'
                    else:
                        provider = ''
                if line.startswith('reboot_reason'):
                    rebootreason = line.split('=')
                    rebootreason = rebootreason[1]
                    
                    if wipe == 'Yes':
                        
                        data_list.append((timestamp, wipe, promptwipe, reason, provider, rebootreason, locale, reqtime))
                        timestamp = wipe = promptwipe = reason = rebootreason = locale = updateorg = updatepkg = reqtime = ''
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
                        
        if data_list:
            report = ArtifactHtmlReport(f'Samsung Wipe {name}')
            report.start_artifact_report(report_folder, f'Samsung Wipe {name}')
            report.add_script()
            data_headers = ('Timestamp', 'Wipe', 'Prompt & Wipe', 'Reason', 'Provider', 'Reboot Reason', 'Locale', 'Request Timestamp')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Samsung Wipe {name}'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Samsung Wipe {name}'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc(f'No Samsung Wipe History data available')

__artifacts__ = {
        "sWipehist": (
                "Wipe & Setup",
                ('*/efs/recovery/history', '*/data/log/recovery_history.log'),
                get_sWipehist)
}