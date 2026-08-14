__artifacts_v2__ = {
    "get_errp": {
        "name": "Errp",
        "description": "Parses power on/off, reboot and shutdown events (timestamp, event, code and details) from the system users eRR.p file.",
        "author": "@abrignoni",
        "creation_date": "2021-08-15",
        "last_update_date": "2026-08-14",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "The file moved to a data subfolder: current devices store it at "
                 "system/users/service/data/eRR.p (both the registered Android 10-16 corpora and "
                 "reporter-supplied Android 15 and 16 samples use that path), while the earlier "
                 "system/users/service/eRR.p is kept for older images. Each line is "
                 "'timestamp | event | code | details'; the timestamp carries the device's UTC "
                 "offset and is also converted to UTC.",
        "paths": ('*/system/users/service/eRR.p',
                  '*/system/users/service/data/eRR.p'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 24 rows",
            "cookbook_a11": "Android 11 | 50 rows",
            "samsungs20_a13": "Android 13 | 35 rows",
            "s20fe_a13": "Android 13 | 52 rows",
            "sharon_a13": "Android 13 | 44 rows",
            "samsunga53_a14": "Android 14 | 18 rows",
            "sharon_a14": "Android 14 | 175 rows",
            "anne_a15": "Android 15 | 61 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, convert_local_to_utc


@artifact_processor
def get_errp(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('eRR.p'):
            continue  # Skip all other files

        source_path = file_found
        with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                # The file opens with a binary LOGM header, and on some devices its
                # NUL padding is prepended to the first record with no newline, so
                # strip NUL bytes before looking for the timestamp.
                line = line.replace('\x00', '').strip()
                if line.startswith('LOGM') or line == '':
                    continue

                parts = line.split('|')
                timestamp = parts[0].strip()
                try:
                    timestamp_utc = str(convert_local_to_utc(timestamp))
                except (ValueError, TypeError):
                    # A line whose timestamp will not parse must not lose the whole
                    # file; keep the row with the value as stored and no UTC form.
                    timestamp_utc = ''
                event = parts[1].strip() if len(parts) >= 2 else ''
                code = parts[2].strip() if len(parts) >= 3 else ''
                details = parts[3].strip() if len(parts) >= 4 else ''
                data_list.append((timestamp_utc, timestamp, event, code, details))

    data_headers = ('Timestamp', 'Timestamp (Local)', 'Event', 'Code', 'Details')
    return data_headers, data_list, source_path
