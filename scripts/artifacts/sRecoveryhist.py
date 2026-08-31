__artifacts_v2__ = {
    "get_sRecoveryhist": {
        "name": "sRecoveryhist",
        "description": "Parses Samsung recovery history (timestamp, firmware build, wipe events, reason, reboot reason and locale) from the efs recovery history file.",
        "author": "@abrignoni",
        "creation_date": "2021-08-15",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "Each record begins with a '+ [tag | timestamp | build]' header. Older devices end "
                 "each record with a lone '-' line; newer devices write no separator and the next "
                 "'+' header ends the previous record. Both layouts are read. Timestamps are stored "
                 "in the device's local time. A record with --wipe_data or --prompt_and_wipe_data is "
                 "a factory reset; records with --carry_out=open_fota are firmware (FOTA) updates.",
        "paths": ('*/efs/recovery/history',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 4 rows",
            "anne_a15": "Android 15 | 9 rows",
            "sharon_a14": "Android 14 | 13 rows",
            "samsunga53_a14": "Android 14 | 50 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor


_EMPTY = {
    'timestamp': '', 'tag': '', 'build': '', 'wipe': '', 'promptwipe': '',
    'reason': '', 'rebootreason': '', 'locale': '', 'carryout': '',
    'reqtime': '', 'updateorg': '', 'updatepkg': '',
}


def _record_row(rec, rel_path):
    return (
        rec['timestamp'], rec['reqtime'], rec['build'], rec['tag'],
        rec['wipe'], rec['promptwipe'], rec['reason'], rec['rebootreason'],
        rec['locale'], rec['carryout'], rec['updateorg'], rec['updatepkg'],
        rel_path)


def _parse_header(line):
    """A '+ [tag | 2022/01/24 14:11:57 | BUILD]' header into (tag, timestamp, build)."""
    inner = line.lstrip('+').strip().strip('[]')
    if '|' in inner:
        parts = [p.strip() for p in inner.split('|')]
        tag = parts[0]
        timestamp = parts[1].replace('/', '-') if len(parts) > 1 else ''
        build = parts[2] if len(parts) > 2 else ''
        return tag, timestamp, build
    # Fallback for an older header shape without pipes: '+ ... : timestamp'
    if ':' in inner:
        timestamp = inner.split(':', 1)[1].strip().replace('/', '-')
        return '', timestamp, ''
    return '', inner, ''


@artifact_processor
def get_sRecoveryhist(context):
    data_headers = (
        'Timestamp', 'Request Timestamp', 'Build', 'Entry Tag (as stored)',
        'Wipe', 'Prompt & Wipe', 'Reason', 'Reboot Reason', 'Locale',
        'Carry Out', 'Update ORG', 'Update PKG', 'Source File')
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith('history'):
            continue  # Skip all other files

        rel_path = context.get_relative_path(file_found)
        record = None
        rows_before = len(data_list)

        with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.rstrip('\n')
                if line.startswith('+'):
                    if record is not None:
                        data_list.append(_record_row(record, rel_path))
                    record = dict(_EMPTY)
                    record['tag'], record['timestamp'], record['build'] = _parse_header(line)
                    continue
                if record is None:
                    continue  # content before the first header
                if line.startswith('--wipe_data'):
                    record['wipe'] = 'Yes'
                elif line.startswith('--prompt_and_wipe_data'):
                    record['promptwipe'] = 'Yes'
                    record['wipe'] = 'Yes'
                elif line.startswith('--reason'):
                    record['reason'] = line.split('=', 1)[1] if '=' in line else ''
                elif line.startswith('--locale'):
                    record['locale'] = line.split('=', 1)[1] if '=' in line else ''
                elif line.startswith('--carry_out'):
                    record['carryout'] = line.split('=', 1)[1] if '=' in line else ''
                elif line.startswith('--requested_time'):
                    record['reqtime'] = line.split('=', 1)[1].replace('/', '-') if '=' in line else ''
                elif line.startswith('--update_org_package'):
                    record['updateorg'] = line.split('=', 1)[1] if '=' in line else ''
                elif line.startswith('--update_package'):
                    record['updatepkg'] = line.split('=', 1)[1] if '=' in line else ''
                elif line.startswith('reboot_reason'):
                    record['rebootreason'] = line.split('=', 1)[1] if '=' in line else ''
                elif line.startswith('reboot reason'):
                    record['rebootreason'] = line.split(':', 1)[1].strip() if ':' in line else ''
            if record is not None:
                data_list.append(_record_row(record, rel_path))  # last record has no trailing header

        if len(data_list) > rows_before:
            sources.append(rel_path)

    return data_headers, data_list, ', '.join(dict.fromkeys(sources))
