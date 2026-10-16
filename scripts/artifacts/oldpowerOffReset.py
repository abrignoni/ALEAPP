__artifacts_v2__ = {
    "get_oldpowerOffReset": {
        "name": "oldpowerOffReset",
        "description": "Parses power-off and reset reasons (recorded time and reason) from the power_off_reset_reason log files.",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2023-03-14",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Power Events",
        "notes": "Each entry begins with a line holding a date and time as "
                 "yy/mm/dd hh:mm:ss with no time zone. The Timestamp (as "
                 "recorded) column shows that line as text, unconverted, and "
                 "the module assigns it no time zone. On galaxys10_a10, "
                 "samsungs20_a13 and sharon_a14 the same files also hold "
                 "lines that carry a UTC offset; each of the 26 reported "
                 "times was 0 to 22 seconds before the local time of the "
                 "next such line, where the offsets were +0200, -0500, "
                 "-0400 and -0600. On those images the recorded time is "
                 "therefore the device's local clock, not UTC. The module "
                 "does not read the offset lines. Reason is the text after "
                 "the first colon of the entry's reason line, up to any "
                 "second colon; every reason line on those three images "
                 "held one colon. When a caller line sits between the time "
                 "and the reason (3 of the 26 entries, all on "
                 "galaxys10_a10), the reason line after it is used.",
        "paths": ('*/log/power_off_reset_reason.txt', '*/log/power_off_reset_reason_backup.txt'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "battery",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 10 rows",
            "samsungs20_a13": "Android 13 | 6 rows",
            "sharon_a14": "Android 14 | 10 rows",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_oldpowerOffReset(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        source_path = os.path.dirname(file_found)
        filename = os.path.basename(file_found)

        with open(file_found, 'r', encoding='utf-8') as f:
            for line in f:
                if '/' in line and len(line) == 18:
                    # The line carries no time zone, so it is reported as
                    # recorded and not converted to an instant.
                    fecha = line.strip()

                    reason = next(f)
                    if reason.startswith('caller'):
                        reason = next(f)
                    reason = reason.split(':')[1].replace('\n', '')

                    data_list.append((fecha, reason, filename))

    data_headers = ('Timestamp (as recorded)', 'Reason', 'Filename')
    return data_headers, data_list, source_path
