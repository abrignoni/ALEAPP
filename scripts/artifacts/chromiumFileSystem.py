__artifacts_v2__ = {
    "chromiumFileSystemSites": {
        "name": "Chromium File System API - Sites",
        "description": "Sites listed in the Origins database of a Chromium profile's File System folder, the "
                       "store Chromium keeps for its File System APIs (webkitRequestFileSystem and the "
                       "Origin Private File System).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-29",
        "last_update_date": "2026-10-29",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the Origins database in a Chromium profile's File System folder (any "
                 "<package>/app_*/Default/File System). Format and meanings come from Chromium at commit "
                 "3a50e012e4c9b8a410a4e2b12bf577e69ee8f755 (tag 130.0.6723.58). The folder is read with "
                 "the vendored ccl_leveldb, and only the newest version of each key is used: LevelDB "
                 "orders the versions of a key by sequence number "
                 "(https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). "
                 "The storage views one extraction can hold for an app data directory (data/data, "
                 "data/user/0, data_mirror) are read once; a second Android user's folder is read as its "
                 "own. Known data (Chrome 124.0.6367.219 on an Android 15 emulator, profile "
                 "app_chrome/Default): a page that wrote a file through webkitRequestFileSystem and a "
                 "page that wrote one through the Origin Private File System "
                 "(navigator.storage.getDirectory) both stored them in this folder, under one site "
                 "folder. After clearing only browsing history for the last hour, the site's History rows "
                 "were gone and its Origins record, folder names, file names and file contents were "
                 "unchanged; Chrome rewrote the Origin Private File System file between the two "
                 "snapshots, so that file's data path and its folder's stored time changed. After "
                 "clearing cookies and site data for the last hour, the site folder was removed and the "
                 "newest version of its Origins key was a deletion. Other Chrome versions and WebView "
                 "apps were not tested this way. The Origins database keys each site as "
                 "ORIGIN:<identifier> and stores the name of the numbered folder that holds its files "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/sandbox_origin_database.cc#L32-L33, "
                 "https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/sandbox_origin_database.cc#L253-L258). "
                 "Site Key is the identifier as stored; Site is the origin it encodes, scheme_host_port "
                 "with port 0 for the scheme's default port "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/common/database/database_identifier.cc#L101-L104, "
                 "https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/common/database/database_identifier.cc#L203-L204), "
                 "split at the first and last underscore as Chromium does "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/common/database/database_identifier.cc#L126-L137). "
                 "State is Deleted when the newest version of the key is a deletion; Chromium deletes the "
                 "key when the site's stored data is removed "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/sandbox_origin_database.cc#L276-L277, "
                 "https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/obfuscated_file_util.cc#L1016-L1021), "
                 "and the deleted key still names the site; Folder and Saved Entries are blank on it and "
                 "Folder Present is No. Folder is the stored folder name, Folder Present says whether "
                 "that folder is in the extraction, and Saved Entries counts the folders and files its "
                 "Paths databases list, not counting the root folder (see Chromium File System API - "
                 "Files). Only a site's first-party default storage is kept in this folder "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/obfuscated_file_util.cc#L926-L930). "
                 "Storage a site holds while embedded in another site, or in a named bucket, is kept "
                 "under WebStorage/<bucket>/FileSystem and is not read; on the tested images, 28 such "
                 "Paths databases on 5 images (anne_a15, cookbook_a11, kevin_pocox7_a15, russell_a14, "
                 "sharon_a14) each belonged to a storage key naming two sites in WebStorage/QuotaManager, "
                 "and none held a record. A row records that a site opened a sandboxed file system in "
                 "that profile; it need not have saved a file, and on the tested images 30 of the 31 live "
                 "rows had no saved entries. It does not establish when or who used the browser, and the "
                 "database stores no time. On the tested images: 33 rows on 16 of 22 images, 30 live with "
                 "their folder present, 1 live whose folder was not in the extraction (pixel3_a12) and 2 "
                 "deleted (adams_ss135dl_a13); Browser was Chrome on 28 rows, "
                 "com.sec.android.app.sbrowser on 2, Edge on 1, com.duckduckgo.mobile.android on 1 and an "
                 "app's WebView (com.xingin.xhs) on 1. Browser and Profile Folder held one value on every "
                 "row of 13 of the 16 images with rows, and the other 3 held two profiles; State held "
                 "Live and Folder Present held Yes on every row of every image but adams_ss135dl_a13 and "
                 "pixel3_a12; Saved Entries held 0 on every live row but one on pixel3_a12, which held 1. "
                 "In known data Site held one value, the test site, on every row.",
        "paths": ('*/Default/File System/*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 2 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 1 row",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 1 row",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
            "hickman_a13": "Android 13 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | 3 rows",
            "pixel3_a11": "Android 11 | 2 rows",
            "pixel3_a12": "Android 12 | 3 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 4 rows",
            "russell_pixel6a_a13": "Android 13 | 3 rows",
            "s20fe_a13": "Android 13 | 1 row",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 2 rows",
            "userb2_a13": "Android 13 | 1 row",
        },
    },
    "chromiumFileSystemEntries": {
        "name": "Chromium File System API - Files",
        "description": "Folders and files websites saved through Chromium's File System APIs, rebuilt from "
                       "the Paths database of each site folder, with the saved file shown as media.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-29",
        "last_update_date": "2026-10-29",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the Paths database in each site folder's type folder in a Chromium profile's File "
                 "System folder (any <package>/app_*/Default/File System/<folder>/t, p or s, the "
                 "temporary, persistent and syncable types: "
                 "https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/sandbox_file_system_backend_delegate.cc#L52-L54). "
                 "Format and meanings come from Chromium at commit "
                 "3a50e012e4c9b8a410a4e2b12bf577e69ee8f755 (tag 130.0.6723.58). The folder is read with "
                 "the vendored ccl_leveldb, and only the newest version of each key is used: LevelDB "
                 "orders the versions of a key by sequence number "
                 "(https://github.com/google/leveldb/blob/bb74ef739973a70ca9f0d90788a1da89b788c0ad/db/dbformat.cc#L47-L63). "
                 "The storage views one extraction can hold for an app data directory (data/data, "
                 "data/user/0, data_mirror) are read once; a second Android user's folder is read as its "
                 "own. Known data (Chrome 124.0.6367.219 on an Android 15 emulator, profile "
                 "app_chrome/Default): a page that wrote a file through webkitRequestFileSystem and a "
                 "page that wrote one through the Origin Private File System "
                 "(navigator.storage.getDirectory) both stored them in this folder, under one site "
                 "folder. After clearing only browsing history for the last hour, the site's History rows "
                 "were gone and its Origins record, folder names, file names and file contents were "
                 "unchanged; Chrome rewrote the Origin Private File System file between the two "
                 "snapshots, so that file's data path and its folder's stored time changed. After "
                 "clearing cookies and site data for the last hour, the site folder was removed and the "
                 "newest version of its Origins key was a deletion. Other Chrome versions and WebView "
                 "apps were not tested this way. Each entry is stored under its numeric id as a record of "
                 "parent id, data path, name and time "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/sandbox_directory_database.cc#L38-L49), "
                 "and its name under CHILD_OF:<parent id>:<name> "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/sandbox_directory_database.cc#L70-L73). "
                 "Path is rebuilt from the parent ids, / being the root folder; an entry with an empty "
                 "data path is a folder "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/sandbox_directory_database.h#L50). "
                 "File is the saved file at Data Path in the type folder, shown as media with its type "
                 "sniffed from its content, and Size its size in bytes; both are blank when that file is "
                 "not in the extraction. A row with State Deleted comes from a CHILD_OF key whose newest "
                 "version is a deletion: it gives the name and parent folder of a name that was removed "
                 "from that folder, because the entry was deleted, renamed or moved, and nothing else; "
                 "Entry Type, File, Size and Data Path are blank on it. Folder Last Changed is the stored "
                 "time of a folder entry, microseconds since 1601-01-01 UTC rounded down to the second "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/sandbox_directory_database.cc#L38-L49): "
                 "Chromium sets it when the folder is made "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/obfuscated_file_util.cc#L450) "
                 "and again when an entry inside it is created, copied, moved or removed or the folder is "
                 "touched "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/obfuscated_file_util.cc#L103-L106, "
                 "https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/obfuscated_file_util.cc#L539-L541). "
                 "Chromium reports the stored time only for folders and takes a file's time from its data "
                 "file "
                 "(https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/obfuscated_file_util.cc#L1144-L1156, "
                 "https://github.com/chromium/chromium/blob/3a50e012e4c9b8a410a4e2b12bf577e69ee8f755/storage/browser/file_system/sandbox_directory_database.h#L54-L56), "
                 "so the column is blank on file rows; in the known data both files stored a time of 0. "
                 "Site is the live Origins key whose folder this is, blank when none names it; Storage "
                 "Type names the type folder. In the known data the two file rows showed the exact text "
                 "written, the folder times matched the test's clock to the second, and one Deleted row "
                 "named a file with .crswap appended that Chrome created and removed during the Origin "
                 "Private File System write. On the tested images: 2 rows, both on pixel3_a12: its root "
                 "folder and one folder below it, both Live and Temporary, so File, Size and Data Path "
                 "are blank on both and Storage Type held Temporary on every row. In known data Site held "
                 "one value, the test site, on every row; Browser and Profile Folder held one value on "
                 "every row of the one image with rows.",
        "paths": ('*/Default/File System/*',),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hickman_a13": "Android 13 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import datetime
import os
import struct

from scripts.artifacts.chrome import get_browser_name
from scripts.artifacts.storagePathViews import unique_files
from scripts.ccl import ccl_leveldb
from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc

_FS = 'File System'
_ORIGIN_PREFIX = 'ORIGIN:'
_CHILD_PREFIX = 'CHILD_OF:'
# SandboxFileSystemBackendDelegate type folders (see the notes).
_TYPES = {'t': 'Temporary', 'p': 'Persistent', 's': 'Syncable'}
_READ_ERRORS = (OSError, ValueError, KeyError, IndexError, EOFError, struct.error)


def _roots(context):
    """Distinct <profile>/File System folders among the files found, storage views collapsed."""
    roots = []
    for found in unique_files(context):
        found = str(found)
        normal = found.replace('\\', '/')
        marker = f'/Default/{_FS}/'
        at = normal.find(marker)
        if at < 0:
            continue
        root = found[:at + len(marker) - 1]
        if root not in roots:
            roots.append(root)
    return roots


def _newest(folder, label, context):
    """{key: (state, value)} for the newest version of every key in a LevelDB folder."""
    newest = {}
    try:
        database = ccl_leveldb.RawLevelDb(folder)
        try:
            for record in database.iterate_records_raw():
                key = bytes(record.user_key).decode('utf-8', 'replace')
                held = newest.get(key)
                if held is None or record.seq > held[0]:
                    newest[key] = (record.seq, record.state, bytes(record.value or b''))
        finally:
            database.close()
    except _READ_ERRORS as ex:
        logfunc(f'{label}: could not read {context.get_relative_path(folder)}: {ex}')
        return None
    return {key: (state, value) for key, (_seq, state, value) in newest.items()}


def _site(identifier):
    """The origin a DatabaseIdentifier string names: scheme_host_port, port 0 the default."""
    if identifier == 'file__0':
        return 'file:///'
    first, last = identifier.find('_'), identifier.rfind('_')
    if first <= 0 or last == first or last == len(identifier) - 1:
        return ''
    scheme, host, port = identifier[:first], identifier[first + 1:last], identifier[last + 1:]
    return f'{scheme}://{host}' if port == '0' else f'{scheme}://{host}:{port}'


def _file_info(value):
    """(parent id, data path, name, time) from a Paths record's pickled FileInfo."""
    size, = struct.unpack_from('<I', value, 0)
    if size + 4 > len(value):
        raise ValueError('pickle shorter than its header')
    offset = 4
    parent, = struct.unpack_from('<q', value, offset)
    offset += 8
    strings = []
    for _ in range(2):
        length, = struct.unpack_from('<i', value, offset)
        offset += 4
        if length < 0 or offset + length > len(value):
            raise ValueError('string runs past the pickle')
        strings.append(value[offset:offset + length].decode('utf-8', 'replace'))
        offset += (length + 3) // 4 * 4
    internal, = struct.unpack_from('<q', value, offset)
    return parent, strings[0], strings[1], internal


def _chromium_time(internal):
    if not internal or internal <= 0:
        return ''
    try:
        return datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(microseconds=internal)
    except OverflowError:
        return ''


def _origins(root, context, label):
    """[(site key, state, folder)] from <root>/Origins, newest version of each ORIGIN key."""
    folder = os.path.join(root, 'Origins')
    if not os.path.isdir(folder):
        return []
    records = _newest(folder, label, context)
    if records is None:
        return []
    out = []
    for key, (state, value) in sorted(records.items()):
        if not key.startswith(_ORIGIN_PREFIX):
            continue
        deleted = state == ccl_leveldb.KeyState.Deleted
        out.append((key[len(_ORIGIN_PREFIX):], 'Deleted' if deleted else 'Live',
                    '' if deleted else value.decode('utf-8', 'replace')))
    return out


def _path_stores(root):
    """[(site folder, type letter, Paths folder)] under a File System folder."""
    stores = []
    for site_folder in sorted(os.listdir(root)):
        for letter in sorted(_TYPES):
            paths = os.path.join(root, site_folder, letter, 'Paths')
            if os.path.isdir(paths):
                stores.append((site_folder, letter, paths))
    return stores


def _full_path(entry_id, entries):
    names, seen = [], set()
    while entry_id and entry_id in entries and entry_id not in seen:
        seen.add(entry_id)
        parent, _data, name, _time = entries[entry_id]
        names.append(name)
        entry_id = parent
    if entry_id and entry_id not in entries:
        names.append('<unresolved>')
    return '/' + '/'.join(reversed(names))


def _entries(paths_folder, context, label):
    """(live entries {id: info}, deleted [(parent id, name)]) from a Paths store."""
    records = _newest(paths_folder, label, context)
    if records is None:
        return {}, []
    live, deleted = {}, []
    for key, (state, value) in records.items():
        if key.isdigit() and state == ccl_leveldb.KeyState.Live:
            try:
                live[int(key)] = _file_info(value)
            except _READ_ERRORS as ex:
                logfunc(f'{label}: entry {key} in {context.get_relative_path(paths_folder)} did not decode: {ex}')
        elif key.startswith(_CHILD_PREFIX) and state == ccl_leveldb.KeyState.Deleted:
            parent, _sep, name = key[len(_CHILD_PREFIX):].partition(':')
            if parent.isdigit():
                deleted.append((int(parent), name))
    return live, deleted


@artifact_processor
def chromiumFileSystemSites(context):
    label = 'Chromium File System API - Sites'
    data_list = []
    sources = []
    for root in _roots(context):
        relative = context.get_relative_path(root)
        origins = _origins(root, context, label)
        if origins:
            sources.append(os.path.join(root, 'Origins'))
        live_counts = {}
        for site_folder, _letter, paths in _path_stores(root):
            live, _deleted = _entries(paths, context, label)
            live_counts[site_folder] = live_counts.get(site_folder, 0) + sum(1 for entry_id in live if entry_id)
        for key, state, folder in origins:
            present = os.path.isdir(os.path.join(root, folder)) if folder else False
            data_list.append((state, _site(key), key, folder, 'Yes' if present else 'No',
                              live_counts.get(folder, 0) if folder else '',
                              get_browser_name(root + '/x'), relative))
    data_headers = ('State', 'Site', 'Site Key (as stored)', 'Folder', 'Folder Present', 'Saved Entries',
                    'Browser', 'Profile Folder')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chromiumFileSystemEntries(context):
    label = 'Chromium File System API - Files'
    data_list = []
    sources = []
    for root in _roots(context):
        relative = context.get_relative_path(root)
        sites = {folder: key for key, state, folder in _origins(root, context, label) if state == 'Live'}
        browser = get_browser_name(root + '/x')
        for site_folder, letter, paths in _path_stores(root):
            live, deleted = _entries(paths, context, label)
            if not live and not deleted:
                continue
            sources.append(paths)
            key = sites.get(site_folder, '')
            site = _site(key) if key else ''
            type_folder = os.path.join(root, site_folder, letter)
            for entry_id in sorted(live):
                _parent, data_path, name, internal = live[entry_id]
                is_folder = data_path == ''
                media, size = '', ''
                if not is_folder:
                    stored = os.path.join(type_folder, *data_path.split('/'))
                    if os.path.isfile(stored):
                        size = os.path.getsize(stored)
                        media = check_in_media(stored, name) or ''
                data_list.append((_chromium_time(internal) if is_folder else '', site,
                                  _full_path(entry_id, live) if entry_id else '/',
                                  'Folder' if is_folder else 'File', 'Live', media, size, data_path,
                                  _TYPES[letter], browser, relative))
            for parent, name in deleted:
                parent_path = _full_path(parent, live) if parent else ''
                data_list.append(('', site, f'{parent_path}/{name}' if parent_path != '/' else f'/{name}',
                                  '', 'Deleted', '', '', '', _TYPES[letter], browser, relative))
    data_headers = (('Folder Last Changed', 'datetime'), 'Site', 'Path', 'Entry Type', 'State', ('File', 'media'),
                    'Size', 'Data Path (as stored)', 'Storage Type', 'Browser', 'Profile Folder')
    return data_headers, data_list, '\n'.join(sources)
