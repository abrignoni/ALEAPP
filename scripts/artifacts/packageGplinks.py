# pylint: disable=W0613
__artifacts_v2__ = {
    "get_packageGplinks": {
        "name": "packageGplinks",
        "description": "Parses installed package names and their possible Google Play Store links from the system packages.list.",
        "author": "",
        "creation_date": "2021-03-18",
        "last_update_date": "2021-03-18",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/system/packages.list',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "package",
        "html_columns": ['Possible Google Play Store Link'],
    }
}

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_packageGplinks(files_found, report_folder, seeker, wrap_text):

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if 'sbin' not in file_found:
            source_path = file_found

    data_list = []
    if source_path:
        with open(source_path, encoding='utf-8', errors='replace') as data:
            values = data.readlines()

        for x in values:
            bundleid = x.split(' ', 1)
            url = f'<a href="https://play.google.com/store/apps/details?id={bundleid[0]}" target="_blank"><font color="blue">https://play.google.com/store/apps/details?id={bundleid[0]}</font></a>'
            data_list.append((bundleid[0], url))

    data_headers = ('Bundle ID', 'Possible Google Play Store Link')
    return data_headers, data_list, source_path
