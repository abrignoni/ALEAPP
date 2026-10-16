__artifacts_v2__ = {
    "get_persistentProp": {
        "name": "Persistent Properties - Matched Text Observations",
        "description": "Reports text lines selected by the existing reboot-like prefix rules in "
                       "persistent_properties. The last comma field is converted using the existing "
                       "Unix-seconds rule when representable; raw text and conversion status are retained.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2021-08-18",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "These are matched replacement-decoded text observations, not proof of a reboot, "
                 "wipe, event completion or ownership. The existing three independent selectors and "
                 "Unix-seconds assumption are retained. Other properties and binary/protobuf store "
                 "formats are not decoded. Matched Text is stripped UTF-8 replacement-decoded text, "
                 "not reversible original bytes. Input Line Ordinal follows text-loader iteration, "
                 "not chronology. Invalid or unrepresentable timestamps retain a blank date and "
                 "their raw text. Source paths include actual contributors only; Source File is "
                 "added only when rows combine distinct evidence-relative origins.",
        "paths": ('*/property/persistent_properties',),
        "output_types": "standard",
        "artifact_icon": "info-circle",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "userb2_a13": "Android 13 | 0 rows",
        },
    }
}

import datetime
import json

from scripts.ilapfuncs import artifact_processor, logfunc


def _matched_observation(raw, description, clean, ordinal, relative, branch):
    try:
        timestamp = datetime.datetime.fromtimestamp(int(raw), datetime.timezone.utc)
        status = 'Converted by existing Unix-seconds rule'
    except (ValueError, OverflowError, OSError) as error:
        timestamp = ''
        status = f'Not converted ({type(error).__name__})'
        source = json.dumps(relative[:240], ensure_ascii=True)
        if len(relative) > 240:
            source += ' [truncated]'
        logfunc(f'Persistent properties: timestamp not converted at {source}; input line ordinal {ordinal}; branch {branch} ({type(error).__name__})')
    return timestamp, raw, description, status, ordinal, clean


@artifact_processor
def get_persistentProp(context):
    files_found = context.get_files_found()

    data_list = []
    contributors = []
    origins = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('persistent_properties'):
            continue  # Skip all other files

        relative = context.get_relative_path(file_found)
        first_row = len(data_list)
        with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
            for ordinal, line in enumerate(f, 1):
                clean = line.strip()
                if clean.startswith('persist.sys.boot.reason.historyDreboot'):
                    parts = clean.split(',')
                    description = parts[0]
                    data_list.append(_matched_observation(parts[-1], description, clean, ordinal, relative, 'history'))

                if clean.startswith('reboot,factory_reset,'):
                    parts = clean.split(',')
                    description = parts[0] + ' ' + parts[1]
                    data_list.append(_matched_observation(parts[-1], description, clean, ordinal, relative, 'factory-reset'))

                if clean.startswith('reboot'):
                    parts = clean.split(',')
                    if len(parts) == 2:
                        description = parts[0]
                        data_list.append(_matched_observation(parts[-1], description, clean, ordinal, relative, 'reboot'))

        count = len(data_list) - first_row
        origins.extend([relative] * count)
        if count and relative not in contributors:
            contributors.append(relative)

    data_headers = (('Timestamp', 'datetime'), 'Raw Timestamp Text', 'Event',
                    'Timestamp Conversion Status', 'Input Line Ordinal',
                    'Matched Text (replacement decoded)')
    if len(contributors) > 1:
        data_headers += ('Source File',)
        data_list = [row + (origin,) for row, origin in zip(data_list, origins)]
    return data_headers, data_list, '\n'.join(contributors)
