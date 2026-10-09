__artifacts_v2__ = {
    "get_sWipehist": {
        "name": "sWipehist",
        "description": "Records in the Samsung recovery history files that carry a --wipe_data or "
                       "--prompt_and_wipe_data argument, with the record's timestamp, reason, reboot "
                       "reason, locale and requested time as stored.",
        "author": "@abrignoni",
        "creation_date": "2021-08-15",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "A record starts at a line beginning with a plus sign and runs to the next such "
                 "line or the end of the file. One row is written for each record that holds a "
                 "line starting --wipe_data or --prompt_and_wipe_data; a record with neither "
                 "argument gives no row. The --wipe_data and --prompt_and_wipe_data columns read "
                 "Yes when the record holds that argument and are blank otherwise. AOSP documents "
                 "--wipe_data as erasing user data and cache and --prompt_and_wipe_data as "
                 "prompting that data is corrupt and erasing it with consent. A row shows the "
                 "arguments recovery was started with and does not by itself show a wipe was "
                 "completed. Reason is the text of the --reason argument as stored; this parser "
                 "adds no label naming what requested the wipe. Reboot Reason is read from a "
                 "line starting reboot_reason= or 'reboot reason:' and is blank when the record "
                 "has neither. Timestamp and Request Timestamp are the header and "
                 "--requested_time text with slashes replaced by dashes; no time zone is stored "
                 "with them. Both matched files are read. A record whose lines are the same in "
                 "a second file is reported once, and a record repeated inside one file is "
                 "reported as often as that file holds it. On anne_a15, galaxys10_a10 and "
                 "sharon_a14 the two files gave the same wipe records, so each is reported once "
                 "(measured 2026-10-09). Reference: AOSP, "
                 "bootable/recovery/recovery.cpp at tag android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/bootable/recovery/+/refs/tags/android-14.0.0_r1/recovery.cpp#83",
        "paths": ('*/efs/recovery/history', '*/data/log/recovery_history.log'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | 3 rows",
            "galaxys10_a10": "Android 10 | 2 rows",
            "samsunga53_a14": "Android 14 | 5 rows",
            "sharon_a14": "Android 14 | 2 rows",
        },
    }
}

from collections import Counter

from scripts.ilapfuncs import artifact_processor


def _record_row(lines):
    """One report row from a record's lines, or None when it holds no wipe argument."""
    timestamp = wipe = promptwipe = reason = rebootreason = locale = reqtime = ''
    for line in lines:
        if line.startswith('+') and not timestamp:
            if '|' in line:
                parts = line.split('|')
                timestamp = parts[1].strip().replace('/', '-') if len(parts) > 1 else ''
            elif ':' in line:
                timestamp = line.split(':', 1)[1].strip().replace(']', '').replace('/', '-')
        elif line.startswith('--wipe_data'):
            wipe = 'Yes'
        elif line.startswith('--prompt_and_wipe_data'):
            promptwipe = 'Yes'
        elif line.startswith('--reason') and '=' in line:
            reason = line.split('=', 1)[1]
        elif line.startswith('reboot_reason') and '=' in line:
            rebootreason = line.split('=', 1)[1]
        elif line.startswith('reboot reason') and ':' in line:
            rebootreason = line.split(':', 1)[1]
        elif line.startswith('--locale') and '=' in line:
            locale = line.split('=', 1)[1]
        elif line.startswith('--requested_time') and '=' in line:
            reqtime = line.split('=', 1)[1].replace('/', '-')
    if not wipe and not promptwipe:
        return None
    return (timestamp, wipe, promptwipe, reason, rebootreason, locale, reqtime)


@artifact_processor
def get_sWipehist(context):
    data_list = []
    source_paths = []
    emitted = Counter()
    seen_files = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not (file_found.endswith('history') or file_found.endswith('recovery_history.log')):
            continue  # Skip all other files
        if file_found in seen_files:
            continue
        seen_files.add(file_found)

        records = []
        with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.startswith('+') or not records:
                    records.append([])
                records[-1].append(line)

        source_paths.append(file_found)
        in_file = Counter()
        for lines in records:
            row = _record_row(lines)
            if row is None:
                continue
            key = ''.join(lines)
            in_file[key] += 1
            # A record another file already gave is not repeated; a record this
            # file holds more often than any earlier file is.
            if in_file[key] > emitted[key]:
                emitted[key] = in_file[key]
                data_list.append(row)

    data_headers = ('Timestamp', '--wipe_data', '--prompt_and_wipe_data', 'Reason',
                    'Reboot Reason', 'Locale', 'Request Timestamp')
    return data_headers, data_list, '\n'.join(source_paths)
