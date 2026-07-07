__artifacts_v2__ = {
    "get_bittorrentDlhist": {
        "name": "bittorrentDlhist",
        "description": "",
        "author": "",
        "creation_date": "2023-03-26",
        "last_update_date": "2023-03-26",
        "requirements": "none",
        "category": "BitTorrent",
        "notes": "",
        "paths": ('*/dlhistory*.config.bak', '*/dlhistory*.config'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "download",
    }
}

import bencoding
import datetime
import textwrap

from scripts.ilapfuncs import artifact_processor


def timestampcalc(timevalue):
    timestamp = datetime.datetime.fromtimestamp(int(timevalue)/1000, datetime.timezone.utc)
    return timestamp


@artifact_processor
def get_bittorrentDlhist(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        with open(file_found, 'rb') as f:
            decodedDict = bencoding.bdecode(f.read())

        for key, value in decodedDict.items():
            if key.decode() == 'records':
                for x in value:
                    time = timestampcalc(x[b'a'])
                    filename = x[b'n'].decode()
                    filepath = x[b's'].decode()
                data_list.append((time,filename,filepath,textwrap.fill(context.get_relative_path(file_found).strip(), width=25)))

    data_headers = (
        ('Record Timestamp', 'datetime'),
        'Filename',
        'Download File Path',
        'Source File',
    )
    return data_headers, data_list, context.get_relative_path(source_path)
