# pylint: disable=W0718
__artifacts_v2__ = {
    "get_TorrentData": {
        "name": "TorrentData",
        "description": "Parses the torrent name, the info hash (SHA-1 of the bencoded info "
                       "dictionary, computed by this parser) and, for multi-file torrents, the "
                       "folder and file name of each listed file from .torrent files.",
        "author": "@abrignoni",
        "creation_date": "2023-09-15",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Torrent Data",
        "notes": "One row per .torrent file read. In the Path column each listed file is one "
                 "line: the folder is every component of the file's path list except the last, "
                 "joined with '/', and the file name is the last component. The info hash is "
                 "computed after decoding and re-encoding the info dictionary; that the "
                 "re-encoded bytes equal the bytes in the file was not established. Source File "
                 "names the .torrent file each row was read from. A file that does not decode "
                 "as bencoding, or that has no info dictionary, is named in the run log and "
                 "produces no row.",
        "paths": ('*/*.torrent',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "download",
        "html_columns": ['Path'],
    }
}

import hashlib
import os
import bencoding

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.html_safe import esc


def _text(value):
    """Bytes as UTF-8 text (undecodable bytes shown as escapes); anything else as str."""
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='backslashreplace')
    return str(value)


@artifact_processor
def get_TorrentData(context):
    files_found = context.get_files_found()

    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.torrent') or os.path.isdir(file_found):
            continue

        relative = context.get_relative_path(file_found)
        try:
            with open(file_found, 'rb') as f:
                decoded = bencoding.bdecode(f.read())
            info = decoded[b'info']
            info_hash = hashlib.sha1(bencoding.bencode(info)).hexdigest().upper()
            torrentname = _text(info[b'name']) if b'name' in info else ''
            aggf = ''
            if b'files' in info:
                aggf = '<table>'
                for entry in info[b'files']:
                    parts = entry.get(b'path', [])
                    if not isinstance(parts, (list, tuple)):
                        parts = [parts]
                    parts = [_text(part) for part in parts]
                    dirr = '/'.join(parts[:-1])
                    filen = parts[-1] if parts else ''
                    aggf = aggf + f'<tr><td>{esc(dirr)}</td><td>{esc(filen)}</td></tr>'
                aggf = aggf + '</table>'
        except Exception as ex:
            logfunc(f'TorrentData: could not read {relative}: {ex}')
            continue

        if file_found not in sources:
            sources.append(file_found)
        data_list.append((torrentname, info_hash, aggf, relative))

    data_headers = ('Torrent Name', 'Info Hash', 'Path', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
