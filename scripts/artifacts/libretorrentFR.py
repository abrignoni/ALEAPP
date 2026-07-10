# pylint: disable=W0613
__artifacts_v2__ = {
    "get_libretorrentFR": {
        "name": "LibretorrentFR",
        "description": "Parses torrent fast-resume data (info hash, name, save path, bytes downloaded and uploaded) from the LibreTorrent libretorrent.db.",
        "author": "",
        "creation_date": "2023-09-15",
        "last_update_date": "2023-09-15",
        "requirements": "none",
        "category": "Libre Torrent",
        "notes": "",
        "paths": ('*/data/com.houseoflife.bitlord/databases/libretorrent.db*', '*/libretorrent.db*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "download",
        "html_columns": ['Length - Path', 'Key - Value'],
    }
}

import bencoding

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_libretorrentFR(files_found, report_folder, seeker, wrap_text):

    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('libretorrent.db'):
            source_path = file_found
            break

    data_list = []
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        cursor.execute('SELECT * from FastResume')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            torrentihash = row[0]
            encoded_data = row[1]
            decodedDict = bencoding.bdecode(encoded_data)

            torrentname = spath = iname = tdown = tup = aggf = agg = ''
            for key, value in decodedDict.items():
                if key == b'info':
                    for ikey, ivalue in value.items():
                        if ikey == b'name':
                            torrentname = ivalue.decode()
                        if ikey == b'files':
                            for files in ivalue:
                                lenghtf = pathf = ''
                                for iikey, iivalue in files.items():
                                    if iikey == b'length':
                                        lenghtf = iivalue
                                    if iikey == b'path':
                                        pathf = iivalue[0].decode()
                                aggf = aggf + f'Lenght: {lenghtf} Path: {pathf} <br>'
                elif key == b'save_path':
                    spath = value.decode()
                elif key == b'name':
                    iname = value.decode()
                elif key == b'total_downloaded':
                    tdown = value
                elif key == b'total_uploaded':
                    tup = value
                elif key in (b'trackers', b'pieces', b'peers', b'banned_peers', b'banned_peers6',
                             b'peers6', b'mapped_files', b'piece_priority', b'file_priority',
                             b'info-hash', b'info-hash2'):
                    pass
                else:
                    if isinstance(value, int):
                        pass
                    elif isinstance(value, list):
                        value = str(value)
                    else:
                        value = value.decode()
                    agg = agg + f'{key.decode()}: {value} <br>'

            data_list.append((torrentihash, torrentname, spath, iname, tdown, tup, aggf, agg))

    data_headers = ('Torrent InfoHash', 'Torrent Name', 'Save Path', 'Name', 'Total Downloaded', 'Total Uploaded', 'Length - Path', 'Key - Value')
    return data_headers, data_list, source_path
