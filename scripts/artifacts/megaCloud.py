__artifacts_v2__ = {
    "mega_cloud_files": {
        "name": "MEGA - Cloud Files",
        "description": 'Files, folders and root nodes in the MEGA node cache, with the folder '
                       'path rebuilt from the stored parent links',
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-12",
        "last_update_date": "2026-09-12",
        "requirements": "none",
        "category": "Mega",
        "notes": 'Read from the nodes table of megaclient_statecache<version>_<account>.db in '
                 'the MEGA app\'s own directory, the local node cache the MEGA SDK keeps for a '
                 'signed in account. The nodes table appears from cache version 13: the SDK\'s '
                 'LAST_DB_VERSION_WITHOUT_NOD is 12 '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/db.cpp#L137), '
                 'and the version 12 store on pixel3_a12 holds only the statecache blob '
                 'table, whose rows DbTable::put writes through PaddedCBC::encrypt '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/db.cpp#L68), '
                 'and it produces no rows here. Cache versions 14 and 15 were read across the '
                 'tested images. The name column is the value Node::displayname returns '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/db/sqlite.cpp#L1619), '
                 'so it is the decrypted file or folder name rather than ciphertext. '
                 'displayname returns the literal CRYPTO_ERROR when a node carries no name '
                 'attribute '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/node.cpp#L1013); '
                 'that was the case on 9 rows across the tested images, and all 9 of them are '
                 'the root, vault and rubbish nodes, which have no name attribute of their '
                 'own. Item Type is the SDK\'s nodetype_t '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/mega/types.h#L421), '
                 'Share Type decodes the ShareType_t bits the SDK writes from getShareType '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/mega/types.h#L434), '
                 'Label is nodelabel_t '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/mega/types.h#L456), '
                 'and In Rubbish, Is Version and Marked Sensitive are the three bits of '
                 'Node::Flags '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/mega/node.h#L474). '
                 'Values outside those vocabularies are reported as stored. Folder Path is '
                 'built by walking each node\'s parenthandle to the root. The root, vault and '
                 'rubbish nodes carry no name of their own, so a path starts at the first '
                 'named folder below them; 3 rows per image have no path on that basis. '
                 'Created and Modified are the ctime and mtime columns, which the SDK binds '
                 'from the node\'s own ctime and mtime; the SDK documents both as seconds '
                 'since the epoch '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/megaapi.h#L1333 '
                 'and '
                 'https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/megaapi.h#L1342). '
                 'Where the store has no size column the size is taken from the counter blob, '
                 'which NodeCounter::serialize writes as files, folders, storage, versions '
                 'and version storage '
                 '(https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/node.cpp#L4018); '
                 'Files in Folder, Folders in Folder and Folder Size come from that same blob '
                 'on folder rows. The store can carry its whole schema in the write-ahead '
                 'log. On pixel7a_a14 the main database file holds 0 tables when the log is '
                 'ignored and 2 when it is applied, and all 7 rows this artifact reports for '
                 'that image come from the log, so a path pattern that does not stage the '
                 'sidecars reports the app as holding nothing. The app directory is present '
                 'under more than one Android storage view. On pixel3_a12 the 3 views hold '
                 '150 cache entries between them for 50 distinct files, and the Cached Media '
                 'artifact reports 50 rows there, so the duplicate views collapse rather than '
                 'multiplying. Measured on the tested images: Share Type was LINK on 4 rows '
                 'and NO_SHARES on the rest, Favourite was Yes on 0 rows, none of the three '
                 'flag columns was Yes on any row, and Description and Tags were empty on '
                 'every row. Cached Copy is the file MEGA kept on the device for that node, '
                 'matched on the handle in the cache file name; 19 of the 33 reported rows '
                 'carried one, and Cache Holding the Copy names which cache it came from. '
                 'Account Handle and Node Cache Version hold one value per image because each '
                 'tested image held one account\'s cache at one version, and Share Value (as '
                 'stored) is the integer behind Share Type.',
        "paths": ('*/mega.privacy.android.app/megaclient_statecache*.db*',
                  '*/mega.privacy.android.app/cache/thumbnailsMEGA/*',
                  '*/mega.privacy.android.app/cache/previewsMEGA/*',
                  '*/mega.privacy.android.app/cache/tempMEGA/*'),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            'galaxys10_a10': 'Android 10 | mega.privacy.android.app | 0 rows',
            'hc_pixel8pro_a16': 'Android 16 | mega.privacy.android.app | 13 rows',
            'hc_pixel8pro_a17': 'Android 17 | mega.privacy.android.app | 13 rows',
            'pixel3_a12': 'Android 12 | mega.privacy.android.app | 0 rows',
            'pixel7a_a14': 'Android 14 | mega.privacy.android.app | 7 rows',
            'samsunga53_a14': 'Android 14 | mega.privacy.android.app | 0 rows',
        },
    },
    "mega_cached_media": {
        "name": "MEGA - Cached Media",
        "description": 'Files in MEGA\'s thumbnail, preview and temporary caches, with the '
                       'node handle read from the file name',
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-12",
        "last_update_date": "2026-09-12",
        "requirements": "none",
        "category": "Mega",
        "notes": 'One row per file staged from MEGA\'s thumbnailsMEGA, previewsMEGA and '
                 'tempMEGA caches. All three name the file after the node handle, with or '
                 'without an extension; a name that is not an 8 character handle is reported '
                 'with an empty Handle rather than guessed at, which was the case for 1 of '
                 'the 112 rows across the tested images. The rows break down as '
                 'thumbnailsMEGA 60, previewsMEGA 35, tempMEGA 17. 55 resolved to a node in '
                 'the same extraction\'s node cache. The rest did not, and on pixel3_a12 that '
                 'is every row, because that image\'s node cache is at a version with no nodes '
                 'table. Handle in the Node Cache therefore holds one value on every row of a '
                 'given image on the tested set, and Name in the Node Cache is blank on every '
                 'row of pixel3_a12 for the same reason. Size on Disk is the size of the '
                 'staged file, not a size the store recorded.',
        "paths": ('*/mega.privacy.android.app/megaclient_statecache*.db*',
                  '*/mega.privacy.android.app/cache/thumbnailsMEGA/*',
                  '*/mega.privacy.android.app/cache/previewsMEGA/*',
                  '*/mega.privacy.android.app/cache/tempMEGA/*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            'galaxys10_a10': 'Android 10 | mega.privacy.android.app | 0 rows',
            'hc_pixel8pro_a16': 'Android 16 | mega.privacy.android.app | 24 rows',
            'hc_pixel8pro_a17': 'Android 17 | mega.privacy.android.app | 24 rows',
            'pixel3_a12': 'Android 12 | mega.privacy.android.app | 50 rows',
            'pixel7a_a14': 'Android 14 | mega.privacy.android.app | 14 rows',
            'samsunga53_a14': 'Android 14 | mega.privacy.android.app | 0 rows',
        },
    },
}

import base64
import os
import re
import struct

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    does_column_exist_in_db,
    does_table_exist_in_db,
    get_sqlite_db_records,
    logfunc,
)
from scripts.artifacts.storagePathViews import unique_files

# Node types, from the SDK's nodetype_t.
# https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/include/mega/types.h
_NODE_TYPES = {-5: 'TYPE_NESTED_MOUNT', -4: 'TYPE_SYMLINK', -3: 'TYPE_DONOTSYNC',
               -2: 'TYPE_SPECIAL', -1: 'TYPE_UNKNOWN', 0: 'FILENODE', 1: 'FOLDERNODE',
               2: 'ROOTNODE', 3: 'VAULTNODE', 4: 'RUBBISHNODE'}

# Share bits, from ShareType_t in the same header. The column holds getShareType(), which
# sets IN_SHARES for a node shared in, OUT_SHARES for one shared with a named user,
# PENDING_OUTSHARES for an invitation not yet accepted and LINK for a public link.
_SHARE_BITS = ((0x01, 'IN_SHARES'), (0x02, 'OUT_SHARES'),
               (0x04, 'PENDING_OUTSHARES'), (0x08, 'LINK'))

# Colour labels, from the SDK's nodelabel_t in the same header.
_LABELS = {0: 'LBL_UNKNOWN', 1: 'LBL_RED', 2: 'LBL_ORANGE', 3: 'LBL_YELLOW',
           4: 'LBL_GREEN', 5: 'LBL_BLUE', 6: 'LBL_PURPLE', 7: 'LBL_GREY'}

# Bit positions of the node flags bitset, from Node::Flags in the SDK's node.h.
_FLAG_IS_VERSION = 0
_FLAG_IS_IN_RUBBISH = 1
_FLAG_IS_MARKED_SENSITIVE = 2

# The account's own user handle is the tail of the node cache file name.
_STATECACHE = re.compile(
    r'megaclient_statecache(\d+)_(?!status_|transfers_|prefs)([A-Za-z0-9_-]+)\.db$')
_CACHE_DIRS = ('thumbnailsMEGA', 'previewsMEGA', 'tempMEGA')
# A node handle prints as 8 base64 characters and a user handle as 11.
_HANDLE = re.compile(r'^[A-Za-z0-9_-]{8}$')


def _handle_to_base64(handle):
    """MEGA prints a node handle as the URL-safe base64 of its low six bytes, which is the
    form used for the media cache file names and for the handles the app stores elsewhere."""
    if handle is None:
        return ''
    return base64.urlsafe_b64encode(
        (int(handle) & ((1 << 48) - 1)).to_bytes(6, 'little')).decode().rstrip('=')


def _counter(blob):
    """NodeCounter::serialize writes files, folders, storage, versions and version storage.
    https://github.com/meganz/sdk/blob/b93cc672b92eb61fefe84a21719657c13a9b11c0/src/node.cpp"""
    if not isinstance(blob, (bytes, bytearray)) or len(blob) != 28:
        return None
    files, folders, storage, versions, version_storage = struct.unpack('<IIqIq', blob)
    return {'files': files, 'folders': folders, 'storage': storage,
            'versions': versions, 'version_storage': version_storage}


def _share_type(value):
    if value is None:
        return ''
    value = int(value)
    names = [name for bit, name in _SHARE_BITS if value & bit]
    if names:
        return '|'.join(names)
    return 'NO_SHARES' if value == 0 else str(value)


def _flag(flags, bit):
    if flags is None:
        return ''
    return 'Yes' if int(flags) >> bit & 1 else 'No'


def _stored(value, names):
    if value is None:
        return ''
    name = names.get(value)
    return name if name else str(value)


def _sort_files(files_found):
    """Split the staged files into the node caches and the media cache."""
    node_dbs, media = [], []
    for file_found in files_found:
        path = str(file_found)
        if os.path.isdir(path):
            continue
        normalised = path.replace('\\', '/')
        if _STATECACHE.search(normalised):
            node_dbs.append(path)
        elif any('/%s/' % name in normalised for name in _CACHE_DIRS):
            media.append(path)
    return node_dbs, media


def _media_entries(media_files):
    """List every staged cache file as (cache name, handle, path). All three caches name the
    file after the handle, with or without an extension; a name that is not a handle is
    reported with an empty handle rather than guessed at."""
    entries = []
    for path in media_files:
        parts = path.replace('\\', '/').split('/')
        for name in _CACHE_DIRS:
            if name not in parts:
                continue
            rest = parts[parts.index(name) + 1:]
            if len(rest) != 1:
                continue
            stem = rest[0].split('.', 1)[0]
            entries.append((name, stem if _HANDLE.match(stem) else '', path))
    return entries


def _media_index(media_files):
    """Map (cache name, handle) to one staged file."""
    index = {}
    for name, handle, path in _media_entries(media_files):
        if handle:
            index.setdefault((name, handle), path)
    return index


def _pick_media(index, handle):
    """Prefer the largest cache the app kept, then the preview, then the thumbnail."""
    for name in ('tempMEGA', 'previewsMEGA', 'thumbnailsMEGA'):
        path = index.get((name, handle))
        if path:
            return path, name
    return '', ''


def _node_rows(path):
    """Read one node cache, resolving the columns that differ between releases."""
    if not does_table_exist_in_db(path, 'nodes'):
        return []
    present = {name: does_column_exist_in_db(path, 'nodes', name)
               for name in ('size', 'mtime', 'label', 'description', 'tags', 'share', 'fav',
                            'flags', 'counter', 'ctime')}
    columns = ['nodehandle', 'parenthandle', 'name', 'type']
    columns += [name if present[name] else 'NULL AS %s' % name
                for name in ('size', 'ctime', 'mtime', 'share', 'fav', 'flags',
                             'label', 'description', 'tags', 'counter')]
    return list(get_sqlite_db_records(path, 'SELECT %s FROM nodes' % ', '.join(columns)))


def _paths_for(nodes):
    """Rebuild each node's folder path by walking its parent links. The three root nodes carry
    no name attribute of their own, so the path starts below them."""
    resolved = {}

    def walk(handle, seen):
        if handle in resolved:
            return resolved[handle]
        node = nodes.get(handle)
        if node is None or handle in seen:
            return None
        seen.add(handle)
        parent = (walk(node['parent'], seen) or '') if node['parent'] in nodes else ''
        if node['type'] in (2, 3, 4):
            value = ''
        elif parent:
            value = '%s/%s' % (parent, node['name'])
        else:
            value = node['name']
        resolved[handle] = value
        return value

    for handle in nodes:
        walk(handle, set())
    return resolved


@artifact_processor
def mega_cloud_files(context):
    node_dbs, media_files = _sort_files(unique_files(context))
    index = _media_index(media_files)
    data_list = []
    sources = []
    seen = set()

    for path in sorted(node_dbs):
        match = _STATECACHE.search(path.replace('\\', '/'))
        version, account = match.group(1), match.group(2)
        rows = _node_rows(path)
        if not rows:
            continue
        sources.append(path)
        nodes = {}
        for row in rows:
            nodes[row[0]] = {'parent': row[1], 'name': row[2] or '', 'type': row[3]}
        folders = _paths_for(nodes)
        for row in rows:
            key = (account, row[0])
            if key in seen:
                continue
            seen.add(key)
            handle = _handle_to_base64(row[0])
            counter = _counter(row[13])
            size = row[4]
            if size is None and counter and row[3] == 0:
                size = counter['storage']
            media_path, cache = _pick_media(index, handle)
            media_ref = check_in_media(media_path, row[2] or handle) if media_path else ''
            data_list.append((
                convert_unix_ts_to_utc(row[5]) if row[5] else '',
                convert_unix_ts_to_utc(row[6]) if row[6] else '',
                folders.get(row[0], ''),
                row[2] or '',
                _stored(row[3], _NODE_TYPES),
                size,
                counter['files'] if counter and row[3] == 1 else '',
                counter['folders'] if counter and row[3] == 1 else '',
                counter['storage'] if counter and row[3] == 1 else '',
                _flag(row[9], _FLAG_IS_IN_RUBBISH),
                _flag(row[9], _FLAG_IS_VERSION),
                _flag(row[9], _FLAG_IS_MARKED_SENSITIVE),
                'Yes' if row[8] else 'No',
                _share_type(row[7]),
                _stored(row[10], _LABELS),
                row[11] or '',
                row[12] or '',
                row[7],
                handle,
                _handle_to_base64(row[1]) if row[1] not in (None, -1) else '',
                account,
                version,
                media_ref,
                cache,
                context.get_relative_path(path)))

    data_headers = (
        ('Created', 'datetime'), ('Modified', 'datetime'), 'Folder Path', 'Name', 'Item Type',
        'Size', 'Files in Folder', 'Folders in Folder', 'Folder Size', 'In Rubbish',
        'Is Version', 'Marked Sensitive', 'Favourite', 'Share Type', 'Label (as stored)',
        'Description', 'Tags', 'Share Value (as stored)', 'Node Handle', 'Parent Handle',
        'Account Handle', 'Node Cache Version', ('Cached Copy', 'media'),
        'Cache Holding the Copy', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def mega_cached_media(context):
    node_dbs, media_files = _sort_files(unique_files(context))
    names = {}
    sources = []

    for path in sorted(node_dbs):
        rows = _node_rows(path)
        if not rows:
            continue
        sources.append(path)
        for row in rows:
            names[_handle_to_base64(row[0])] = row[2] or ''

    data_list = []
    for cache, handle, path in sorted(_media_entries(media_files)):
        try:
            size = os.path.getsize(path)
        except OSError as error:
            logfunc('MEGA cached media could not be sized: %s' % type(error).__name__)
            size = ''
        on_disk = os.path.basename(path.replace('\\', '/'))
        in_cloud = names.get(handle, '') if handle else ''
        data_list.append((
            cache,
            handle,
            'Yes' if handle and handle in names else 'No',
            in_cloud,
            on_disk,
            size,
            check_in_media(path, in_cloud or on_disk),
            context.get_relative_path(path)))
        sources.append(os.path.dirname(path.replace('\\', '/')))

    data_headers = (
        'Cache', 'Handle', 'Handle in the Node Cache', 'Name in the Node Cache',
        'Name on Disk', 'Size on Disk', ('File', 'media'), 'Source File')
    return data_headers, data_list, '\n'.join(sorted(set(sources)))
