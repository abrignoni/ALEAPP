__artifacts_v2__ = {
    "get_log": {
        "name": "Garmin - Matching Log Lines",
        "description": "Reports matching lines from Garmin Connect app.log inputs, with line numbers and evidence sources. Case-sensitive matches use access_token, expires_in, refresh_token, token_type, id_token and Authorization; rows are log-line evidence, not decoded credentials.",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}, @AlexisBrignoni, Codex",
        "creation_date": "2023-02-24",
        "last_update_date": "2026-10-05",
        "requirements": "Python 3.7 or higher",
        "category": "Garmin",
        "notes": "One row represents one LF-delimited source line containing any listed attribute; "
                 "all matched attributes are listed without splitting values or inferring a timestamp. "
                 "Repeated lines and later Authorization records remain separate. Line terminators "
                 "are retained in Log Line and Raw Line Bytes (hex). UTF-8 display escapes invalid "
                 "bytes with backslash notation; the hex column preserves the exact original bytes "
                 "and distinguishes invalid bytes from literal escape text. Text Decoding identifies "
                 "this condition. Canonical storage aliases use a preferred evidence path; rotations, "
                 "other Android users and distinct evidence roots remain separate. Read failures are "
                 "logged by evidence source and other logs continue. No timestamp, credential validity "
                 "or account/event meaning is inferred. The registered pixel7a sample contains a log "
                 "but no matching lines; positive real matching-line coverage remains unavailable.",
        "paths": ('*/com.garmin.android.apps.connectmobile/files/logs/app.log*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "activity",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 0 rows",
        },
    }
}

from pathlib import Path

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

ATTRIBUTES = ('access_token', 'expires_in', 'refresh_token', 'token_type', 'id_token',
              'Authorization')


@artifact_processor
def get_log(context):
    data_list = []
    source_paths = []
    files = sorted(unique_files(context), key=context.get_relative_path)
    for file_found in files:
        file_found = str(file_found)
        if not Path(file_found).name.startswith('app.log'):
            continue
        relative = context.get_relative_path(file_found)
        try:
            with open(file_found, 'rb') as stream:
                source_paths.append(file_found)
                for line_number, raw_line in enumerate(stream, 1):
                    matched = [name for name in ATTRIBUTES if name.encode('ascii') in raw_line]
                    if not matched:
                        continue
                    try:
                        line = raw_line.decode('utf-8')
                        decoding = 'UTF-8'
                    except UnicodeDecodeError:
                        line = raw_line.decode('utf-8', errors='backslashreplace')
                        decoding = 'Invalid UTF-8 bytes escaped; original bytes in hex'
                    data_list.append((line_number, ', '.join(matched), line, raw_line.hex(),
                                      decoding, relative))
        except OSError as error:
            logfunc(f'Garmin log read error for {relative}: {error.strerror or type(error).__name__}')
    data_headers = ('Line Number', 'Matched Attributes', 'Log Line (as stored)',
                    'Raw Line Bytes (hex)', 'Text Decoding', 'Source File')
    return data_headers, data_list, '\n'.join(source_paths)
