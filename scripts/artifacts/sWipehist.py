__artifacts_v2__ = {
    "get_sWipehist": {
        "name": "sWipehist",
        "description": "Records in the Samsung recovery history files that carry a --wipe_data or "
                       "--prompt_and_wipe_data argument and a reboot_reason line, with the record's "
                       "timestamp, reason, reboot reason, locale and requested time.",
        "author": "@abrignoni",
        "creation_date": "2021-08-15",
        "last_update_date": "2021-08-15",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "A row is written only when a line starting reboot_reason is reached after a "
                 "--wipe_data or --prompt_and_wipe_data line, so a record with neither argument "
                 "gives no row. A record that ends with the 'reboot reason:' spelling gives no "
                 "row, and the values read from it carry into the next record. Wipe reads Yes for "
                 "either argument and Prompt & Wipe reads Yes for --prompt_and_wipe_data. AOSP "
                 "documents --wipe_data as erasing user data and cache and --prompt_and_wipe_data "
                 "as prompting that data is corrupt and erasing it with consent. A row shows the "
                 "arguments recovery was started with and does not by itself show a wipe was "
                 "completed. Provider is not a stored field. It is a label this parser assigns "
                 "from text in the reason value: Samsung Find My Mobile for Fmm.RemoteWipeOut, "
                 "Google Find My Device for 'Find My Device wiping device remotely' and Local "
                 "Android UI for MasterClearConfirm, and blank otherwise. No source for that "
                 "mapping is given here. Timestamp and Request Timestamp are the header and "
                 "--requested_time text with slashes replaced by dashes; no time zone is stored "
                 "with them. Reference: AOSP, bootable/recovery/recovery.cpp at tag "
                 "android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/bootable/recovery/+/refs/tags/android-14.0.0_r1/recovery.cpp#83",
        "paths": ('*/efs/recovery/history', '*/data/log/recovery_history.log'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | 6 rows",
            "galaxys10_a10": "Android 10 | 4 rows",
            "samsunga53_a14": "Android 14 | 5 rows",
            "sharon_a14": "Android 14 | 4 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_sWipehist(context):
    files_found = context.get_files_found()

    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        if not (file_found.endswith('history') or file_found.endswith('recovery_history.log')):
            continue  # Skip all other files

        source_paths.append(file_found)
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
    return data_headers, data_list, '\n'.join(source_paths)
