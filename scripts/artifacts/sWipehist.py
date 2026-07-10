# pylint: disable=W0613
__artifacts_v2__ = {
    "get_sWipehist": {
        "name": "sWipehist",
        "description": "Parses Samsung wipe and recovery events (timestamp, wipe events, reason, provider and reboot reason) from the recovery history files.",
        "author": "",
        "creation_date": "2021-08-15",
        "last_update_date": "2021-08-15",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "",
        "paths": ('*/efs/recovery/history', '*/data/log/recovery_history.log'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
    }
}

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_sWipehist(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not (file_found.endswith('history') or file_found.endswith('recovery_history.log')):
            continue  # Skip all other files

        source_path = file_found
        timestamp = wipe = promptwipe = reason = provider = rebootreason = locale = updateorg = updatepkg = reqtime = ''
        with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.startswith('+'):
                    if '|' in line:
                        timestamp = line.split('|')
                        timestamp = timestamp[1].strip()
                        timestamp = timestamp.replace('/', '-')
                    else:
                        timestamp = line.split(':', 1)
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
                        timestamp = wipe = promptwipe = reason = provider = rebootreason = locale = updateorg = updatepkg = reqtime = ''
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

    data_headers = ('Timestamp', 'Wipe', 'Prompt & Wipe', 'Reason', 'Provider', 'Reboot Reason', 'Locale', 'Request Timestamp')
    return data_headers, data_list, source_path
