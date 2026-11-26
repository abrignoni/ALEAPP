__artifacts_v2__ = {
    "get_errp": {
        "name": "Errp",
        "description": "Parses the records of the eRR.p file under system/users/service or its data subfolder. Each record is split on the pipe character into timestamp, event, code and details. NUL bytes and surrounding whitespace are removed, bytes that are not valid UTF-8 are replaced, and text after a fourth pipe is not reported.",
        "author": "@abrignoni",
        "creation_date": "2021-08-15",
        "last_update_date": "2026-11-24",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Two paths are read. The eight registered images listed in sample_data (Android "
                 "10 to 15) all hold the file at system/users/service/data/eRR.p. The path "
                 "system/users/service/eRR.p is also read. Each record line is split on the pipe character, and the first four fields are reported by position as Timestamp, Event, Code and Details. No line on the images run held more than four. What each field means is not established from the code that writes "
                 "the file. Across those eight images, 411 of 459 record lines have four fields "
                 "and 48 have three, with no Details field. Event is blank on 58 lines and Code "
                 "on 217. A missing field is reported blank. All 459 timestamps in those images "
                 "carry a UTC offset; the value is shown in Timestamp (Local) and converted to "
                 "UTC in Timestamp. A line whose timestamp "
                 "cannot be read in that form keeps its row with Timestamp blank. When both paths are present their rows are reported together, no column names the file, and the source path lists both. No tested image held both paths, so this was run only on a constructed pair of files.",
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
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('eRR.p'):
            continue  # Skip all other files

        source_paths.append(file_found)
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
                    timestamp_utc = convert_local_to_utc(timestamp)
                except (ValueError, TypeError):
                    # A line whose timestamp will not parse must not lose the whole
                    # file; keep the row with the value as stored and no UTC form.
                    timestamp_utc = ''
                event = parts[1].strip() if len(parts) >= 2 else ''
                code = parts[2].strip() if len(parts) >= 3 else ''
                details = parts[3].strip() if len(parts) >= 4 else ''
                data_list.append((timestamp_utc, timestamp, event, code, details))

    data_headers = (('Timestamp', 'datetime'), 'Timestamp (Local)', 'Event', 'Code', 'Details')
    return data_headers, data_list, '\n'.join(source_paths)
