__artifacts_v2__ = {
    "bashHistory": {
        "name": "Bash History",
        "description": "Parses the bash history entries",
        "author": "@stark4n6",
        "creation_date": "2020-10-11",
        "last_update_date": "2025-08-09",
        "requirements": "none",
        "category": "Bash History",
        "notes": "",
        "paths": ('*/.bash_history'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "terminal",
    }
}

from scripts.ilapfuncs import artifact_processor

@artifact_processor
def bashHistory(context):
    files_found = context.get_files_found()
    data_list = []
    file_found = str(files_found[0])
    counter = 1
    with open(file_found, 'r', encoding='utf-8-sig') as csvfile:
        for row in csvfile:
            data_list.append((counter, row))
            counter += 1

    data_headers = ('Entry Order', 'Command')
    return data_headers, data_list, file_found    