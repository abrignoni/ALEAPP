# pylint: disable=W0613
__artifacts_v2__ = {
    "get_bittorrentClientpref": {
        "name": "BitTorrent Prefs",
        "description": "",
        "author": "",
        "creation_date": "2023-03-26",
        "last_update_date": "2023-03-26",
        "requirements": "none",
        "category": "BitTorrent",
        "notes": "",
        "paths": ('*/com.bittorrent.client/shared_prefs/com.bittorrent.client_preferences.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "download",
    }
}

import datetime
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, abxread, checkabx


def timestampcalc(timevalue):
    timestamp = (datetime.datetime.fromtimestamp(int(timevalue)/1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp


@artifact_processor
def get_bittorrentClientpref(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        # check if file is abx
        if (checkabx(file_found)):
            multi_root = False
            tree = abxread(file_found, multi_root)
        else:
            tree = ET.parse(file_found)

        root = tree.getroot()

        for elem in root:
            key = elem.attrib['name']
            value = elem.attrib.get('value')
            text = elem.text
            if key == 'BornOn':
                value = timestampcalc(value)
            data_list.append((key, value, text))

    data_headers = ('Key', 'Value', 'Text')
    return data_headers, data_list, source_path
