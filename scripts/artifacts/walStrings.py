__artifacts_v2__ = {
    "get_walStrings": {
        "name": "walStrings",
        "description": "If  we only want ascii, use 'ascii_chars_re' below",
        "author": "",
        "creation_date": "2020-04-17",
        "last_update_date": "2020-04-17",
        "requirements": "none",
        "category": "SQLite Journaling",
        "notes": "",
        "paths": ('*/*-wal', '*/*-journal'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
        "html_columns": ['Report'],
    }
}

import os
import re
import string
from pathlib import Path

from scripts.ilapfuncs import artifact_processor

control_chars = ''.join(map(chr, range(0, 32))) + ''.join(map(chr, range(127, 160)))
not_control_char_re = re.compile(f'[^{control_chars}]' + '{4,}')
# If  we only want ascii, use 'ascii_chars_re' below
printable_chars_for_re = string.printable.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
ascii_chars_re = re.compile(f'[{printable_chars_for_re}]' + '{4,}')


@artifact_processor
def get_walStrings(context):
    files_found = context.get_files_found()
    report_folder = context.get_report_folder()
    x = 1
    data_list = []
    for file_found in files_found:
        if Path(file_found).stat().st_size == 0:
            continue

        journalName = os.path.basename(file_found)
        outputpath = os.path.join(report_folder, str(x) + '_' + journalName + '.txt')  # name of file in txt

        level2, level1 = os.path.split(outputpath)
        level2 = os.path.split(level2)[1]
        final = level2 + '/' + level1

        unique_items = set()  # For deduplication of strings found
        with open(outputpath, 'w', encoding='utf-8', errors='ignore') as g:
            with open(file_found, encoding='utf-8', errors="ignore") as f:
                data = f.read()
                for match in ascii_chars_re.finditer(data):  # Matches ONLY Ascii
                    if match.group() not in unique_items:
                        g.write(match.group())
                        g.write('\n')
                        unique_items.add(match.group())

        if unique_items:
            out = f'<a href="{final}" style = "color:blue" target="_blank">{journalName}</a>'
            data_list.append((out, context.get_relative_path(file_found)))
        else:
            try:
                os.remove(outputpath)  # delete empty file
            except OSError:
                pass
        x = x + 1

    data_headers = ('Report', 'Location')
    return data_headers, data_list, ''
