__artifacts_v2__ = {
    "get_walStrings": {
        "name": "walStrings",
        "description": "ASCII strings of four or more characters read from files whose names end in -wal or -journal",
        "author": "@abrignoni",
        "creation_date": "2020-04-17",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "SQLite Journaling",
        "notes": "One row per file that yielded at least one string; the Report column links to a "
                 "text file listing them. A string is a run of four or more printable ASCII "
                 "characters, white space included. Each distinct string is listed once per file, "
                 "in the order first seen. The file is read as bytes, so every string is a run of "
                 "bytes that are adjacent in the file. Text in other encodings (for example UTF-16) "
                 "and characters outside ASCII are not extracted. Zero-byte "
                 "files are skipped. The file is not checked to be a SQLite file, and a string is "
                 "not tied to a table, row or state of the database.",
        "paths": ('*/*-wal', '*/*-journal'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 720 rows",
            "samsunga53_a14": "Android 14 | 657 rows",
            "anne_a15": "Android 15 | 861 rows",
            "hc_pixel8pro_a16": "Android 16 | 526 rows",
            "kevin_pocox7_a15": "Android 15 | 520 rows",
            "pixel7a_a14": "Android 14 | 511 rows",
            "samsungs20_a13": "Android 13 | 799 rows",
            "sharon_a14": "Android 14 | 899 rows",
            "russell_pixel6a_a13": "Android 13 | 456 rows",
            "userb2_a13": "Android 13 | 265 rows",
        },
        "html_columns": ['Report'],
    }
}

import os
import re
import string
from pathlib import Path

from scripts.html_safe import safe_local_link
from scripts.ilapfuncs import artifact_processor
from scripts.artifacts.storagePathViews import unique_files

control_chars = ''.join(map(chr, range(0, 32))) + ''.join(map(chr, range(127, 160)))
not_control_char_re = re.compile(f'[^{control_chars}]' + '{4,}')
# If  we only want ascii, use 'ascii_chars_re' below
printable_chars_for_re = string.printable.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
ascii_chars_re = re.compile(f'[{printable_chars_for_re}]' + '{4,}')
# The same character class over bytes, so a run is matched in the file's own
# bytes and can only hold bytes that are adjacent in the file.
ascii_bytes_re = re.compile(('[' + re.escape(string.printable) + ']{4,}').encode('ascii'))


@artifact_processor
def get_walStrings(context):
    files_found = unique_files(context)
    report_folder = context.get_report_folder()
    x = 1
    data_list = []
    source_paths = set()
    for file_found in files_found:
        # The seeker can list files it could not extract (e.g. zero-byte
        # archive members), so the path may not exist on disk.
        path = Path(file_found)
        if not path.is_file() or path.stat().st_size == 0:
            continue

        journalName = os.path.basename(file_found)
        outputpath = os.path.join(report_folder, str(x) + '_' + journalName + '.txt')  # name of file in txt

        level2, level1 = os.path.split(outputpath)
        level2 = os.path.split(level2)[1]
        final = level2 + '/' + level1

        unique_items = set()  # For deduplication of strings found
        with open(outputpath, 'w', encoding='utf-8', errors='ignore') as g:
            with open(file_found, 'rb') as f:
                data = f.read()
                for match in ascii_bytes_re.finditer(data):  # Matches ONLY Ascii
                    found = match.group().decode('ascii')
                    if found not in unique_items:
                        g.write(found)
                        g.write('\n')
                        unique_items.add(found)

        if unique_items:
            # Report-relative link to the strings file written beside the report.
            # safe_local_link() escapes the label and refuses any target that would
            # leave the report folder.
            out = safe_local_link(final, journalName)
            source_paths.add(str(file_found))
            data_list.append((out, context.get_relative_path(file_found)))
        else:
            try:
                os.remove(outputpath)  # delete empty file
            except OSError:
                pass
        x = x + 1

    data_headers = ('Report', 'Location')
    return data_headers, data_list, '\n'.join(sorted(source_paths))
