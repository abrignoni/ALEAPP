# pylint: disable=W0702,W0718
__artifacts_v2__ = {
    "get_torrentinfo": {
        "name": "torrentinfo",
        "description": "Parses torrent file metadata (file, info hash and data) from .torrent files.",
        "author": "",
        "creation_date": "2023-03-26",
        "last_update_date": "2023-03-26",
        "requirements": "none",
        "category": "BitTorrent",
        "notes": "",
        "paths": ('*/*.torrent',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "download",
        "html_columns": ['Data'],
    }
}

import bencoding
import hashlib
import datetime
import textwrap

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.html_safe import esc


def timestampcalc(timevalue):
    timestamp = (datetime.datetime.fromtimestamp(int(timevalue), datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp


@artifact_processor
def get_torrentinfo(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        try:
            with open(file_found, 'rb') as f:
                decodedDict = bencoding.bdecode(f.read())

            aggregate = ''
            try:
                infoh= hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest()
                infohash = infoh
            except:
                infohash = ''

            for key, value in decodedDict.items():
                if key.decode() == 'info':
                    for x, y in value.items():
                        if x == b'pieces':
                            pass
                        elif key.decode() == 'info':
                            for itemkey, itemvalue in value.items():
                                if itemkey.decode() == 'files':
                                    for y in itemvalue:
                                        if len(y[b'path']) == 1:
                                            file = (y[b'path'][0].decode())
                                            aggregate = aggregate + f'Files: {esc(file)} <br>'
                        else:
                            aggregate = aggregate + f'{esc(x.decode())}: {esc(y.decode())} <br>'

                elif key.decode() == 'pieces':
                    pass
                elif key.decode() == 'creation date':
                    aggregate = aggregate + f'{key.decode()}: {timestampcalc(value)} <br>'
                else:
                    aggregate = aggregate + f'{esc(key.decode())}: {esc(value.decode())} <br>' #add if value is binary decode

            data_list.append((textwrap.fill(file_found.strip(), width=25),infohash,aggregate))
        except Exception as e: logfunc(str(e))

    data_headers = ('File', 'InfoHash', 'Data')
    return data_headers, data_list, source_path
