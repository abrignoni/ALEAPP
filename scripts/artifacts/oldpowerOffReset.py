# pylint: disable=W0613
__artifacts_v2__ = {
    "get_oldpowerOffReset": {
        "name": "oldpowerOffReset",
        "description": "Parses power-off and reset reasons (timestamp and reason) from the power_off_reset_reason log files.",
        "author": "",
        "creation_date": "2023-03-14",
        "last_update_date": "2023-03-14",
        "requirements": "none",
        "category": "Power Events",
        "notes": "",
        "paths": ('*/log/power_off_reset_reason.txt', '*/log/power_off_reset_reason_backup.txt'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "battery",
    }
}

import os
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_oldpowerOffReset(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        source_path = os.path.dirname(file_found)
        filename = os.path.basename(file_found)

        with open(file_found, 'r', encoding='utf-8') as f:
            for line in f:
                if '/' in line and len(line) == 18:
                    fecha = line.strip()
                    fecha = datetime.strptime(fecha, '%y/%m/%d %H:%M:%S').replace(tzinfo=timezone.utc)

                    reason = next(f)
                    reason = reason.split(':')[1].replace('\n', '')

                    data_list.append((fecha, reason, filename))

    data_headers = (('Timestamp', 'datetime'), 'Reason', 'Filename')
    return data_headers, data_list, source_path
