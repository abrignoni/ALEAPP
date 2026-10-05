__artifacts_v2__ = {
    "bashHistory": {
        "name": "Bash History",
        "description": "Parses distinct matched .bash_history file. Entry Order is the line number within its source; repeated command lines are retained. Android storage aliases of one history are collapsed.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2020-10-11",
        "last_update_date": "2026-10-05",
        "requirements": "none",
        "category": "Bash History",
        "notes": "Original parser: Kevin Pagano (@stark4n6). Source File identifies each history.",
        "paths": ('*/.bash_history'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "terminal",
        "sample_data": {"emu_a15_oss_v17": "Android 15 | 15 rows"},
    }
}

from scripts.ilapfuncs import artifact_processor
from scripts.artifacts.storagePathViews import unique_files

@artifact_processor
def bashHistory(context):
    data_list = []
    source_paths = []
    for file_found in unique_files(context):
        source_paths.append(context.get_relative_path(file_found))
        with open(file_found, 'r', encoding='utf-8-sig') as history:
            for counter, row in enumerate(history, 1):
                data_list.append((counter, row, context.get_relative_path(file_found)))

    data_headers = ('Entry Order', 'Command', 'Source File')
    return data_headers, data_list, '\n'.join(source_paths)
