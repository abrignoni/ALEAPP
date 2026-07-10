# pylint: disable=W0613
__artifacts_v2__ = {
    "get_sRecoveryhist": {
        "name": "sRecoveryhist",
        "description": "Parses Samsung recovery history (timestamp, wipe events, reason, reboot reason and locale) from the efs recovery history file.",
        "author": "",
        "creation_date": "2021-08-15",
        "last_update_date": "2021-08-15",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "",
        "paths": ('*/efs/recovery/history',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 4 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_sRecoveryhist(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('history'):
            continue  # Skip all other files

        source_path = file_found
        timestamp = wipe = promptwipe = reason = rebootreason = locale = updateorg = updatepkg = reqtime = ''
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

    data_headers = ('Timestamp', 'Wipe', 'Prompt & Wipe', 'Reason', 'Reboot Reason', 'Locale', 'Request Timestamp', 'Update ORG', 'Update PKG')
    return data_headers, data_list, source_path
