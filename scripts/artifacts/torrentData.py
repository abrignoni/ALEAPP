# pylint: disable=W0613,W0702
__artifacts_v2__ = {
    "get_TorrentData": {
        "name": "TorrentData",
        "description": "",
        "author": "",
        "creation_date": "2023-09-15",
        "last_update_date": "2023-09-15",
        "requirements": "none",
        "category": "Torrent Data",
        "notes": "",
        "paths": ('*/*.torrent',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "download",
        "html_columns": ['Path'],
    }
}

import hashlib
import bencoding

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_TorrentData(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.torrent'):
            continue

        source_path = file_found
        with open(file_found, 'rb') as f:
            encoded_data = f.read()

        decodedDict = bencoding.bdecode(encoded_data)
        info_hash = hashlib.sha1(bencoding.bencode(decodedDict[b"info"])).hexdigest().upper()

        torrentname = aggf = ''
        for key, value in decodedDict.items():
            if key == b'info':
                for ikey, ivalue in value.items():
                    if ikey == b'name':
                        torrentname = ivalue.decode()
                    if ikey == b'files':
                        aggf = '<table>'
                        for files in ivalue:
                            dirr = filen = ''
                            for iikey, iivalue in files.items():
                                if iikey == b'path':
                                    if len(iivalue) > 1:
                                        try:
                                            dirr = iivalue[0].decode()
                                            filen = iivalue[1].decode()
                                        except:
                                            dirr = iivalue[0]
                                            filen = iivalue[1]
                                    else:
                                        dirr = ''
                                        try:
                                            filen = iivalue[0].decode()
                                        except:
                                            filen = iivalue[0]
                            aggf = aggf + f'<tr><td>{dirr}</td><td>{filen}</td></tr>'
                        aggf = aggf + '</table>'

        data_list.append((torrentname, info_hash, aggf))

    data_headers = ('Torrent Name', 'Info Hash', 'Path')
    return data_headers, data_list, source_path
