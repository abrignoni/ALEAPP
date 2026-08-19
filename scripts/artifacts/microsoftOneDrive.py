__artifacts_v2__ = {
    "microsoft_onedrive": {
        "name": "Microsoft OneDrive",
        "description": "Parses Microsoft OneDrive metadata and previews cached stream media",
        "author": "@stark4n6, Matt Beers, Anthony Reince",
        "creation_date": "2025-04-17",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Cloud Storage",
        "notes": "",
        "paths": (
            '*/com.microsoft.skydrive/files/QTMetadata.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "cloud",
    }
}

import os
import mimetypes
from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    open_sqlite_db_readonly,
    convert_unix_ts_to_utc,
    logfunc,
    check_in_embedded_media,
    does_column_exist_in_db
)


def _find_cached_file(seeker, stream_path):
    """Locate the cached stream file in the extraction by matching its path tail[cite: 2]."""
    if not seeker or not stream_path:
        return None
    stream_path_norm = os.path.normpath(stream_path).lower().lstrip(os.sep)
    stream_path_tail = os.path.join(*stream_path_norm.split(os.sep)[-6:]).replace('\\', '/')
    filename = os.path.basename(stream_path)
    if not filename:
        return None

    for match in seeker.search(f'*{filename}'):
        match_path_norm = os.path.normpath(str(match)).lower().replace('\\', '/')
        if stream_path_tail in match_path_norm:
            return match
    return None


def _build_preview(found_file, extension):
    """Return (media_ref, info_text) for a cached stream file. Images are checked in as media[cite: 2]."""
    ext = (extension or '').lower().lstrip('.')
    guessed_mime = mimetypes.types_map.get(f'.{ext}') if ext else None
    try:
        with open(found_file, 'rb') as f:
            data = f.read()
    except OSError as e:
        return '', f'Error reading file: {e}'

    if guessed_mime and guessed_mime.startswith('image'):
        ref = check_in_embedded_media(
            str(found_file),
            data,
            name=os.path.basename(str(found_file)),
            force_type=guessed_mime,
            force_extension=ext
        ) or ''
        return ref, 'Image' if ref else f'image ({len(data)} bytes)'
    if guessed_mime and guessed_mime.startswith('text'):
        return '', data.decode('utf-8', errors='ignore')[:300]
    if guessed_mime:
        return '', f'{guessed_mime} ({len(data)} bytes)'
    return '', f'Cached binary ({len(data)} bytes)'


@artifact_processor
def microsoft_onedrive(context):
    source_path = get_file_path(context.get_files_found(), "QTMetadata.db")
    if not source_path:
        logfunc("No QTMetadata.db found")
        return

    seeker = context.get_seeker()
    data_list = []
    id_to_path = {None: ""}

    hash_column = 'items.sha1Hash'
    if not does_column_exist_in_db(source_path, 'items', 'sha1Hash'):
        hash_column = 'NULL'
        logfunc(f'No items.sha1Hash column in {source_path}; hash values unavailable[cite: 2]')

    query = f'''
    SELECT
        items.itemDate,
        items.creationDate,
        items.modifiedDateOnClient,
        CASE items.itemType
            WHEN '1' THEN 'Document'
            WHEN '3' THEN 'Image'
            WHEN '32' THEN 'Folder'
            ELSE items.itemType
        END AS "itemType",
        COALESCE(items.name, '') || COALESCE(items.extension, ''),
        items.extension,
        items.ownerName,
        items.size,
        {hash_column},
        items.resourceIdAlias,
        items._id,
        stream_cache.stream_location,
        items.resourceId,
        items.parentRid
    FROM items
    LEFT JOIN stream_cache ON items._id = stream_cache.parentId
    WHERE items.resourceId NOT IN ('search', 'Mru', 'SharedBy', 'SharedWithMe')
       OR items.resourceId IS NULL
    ORDER BY items.itemDate ASC
    '''

    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute(query)
    db_records = cursor.fetchall()

    if not db_records:
        logfunc("No OneDrive records found in QTMetadata.db")
        db.close()
        return

    # First pass: Build resourceId to display name mapping
    for row in db_records:
        name_to_use = row[4] if row[4] else (row[9] if row[9] else str(row[12]))
        resource_id = row[12]
        if resource_id:
            id_to_path[resource_id] = name_to_use

    # Second pass: Build storage path strings and resolve cached stream media
    for row in db_records:
        name_to_use = row[4] if row[4] else (row[9] if row[9] else str(row[12]))
        resource_id = row[12]
        parent_rid = row[13]
        extension = row[5] or ''
        stream_path = row[11]

        if parent_rid in id_to_path and id_to_path[parent_rid]:
            parent_path = id_to_path[parent_rid]
            folder_string = f"{parent_path}\\{name_to_use}"
            if resource_id:
                id_to_path[resource_id] = folder_string
        else:
            folder_string = name_to_use
            if resource_id:
                id_to_path[resource_id] = name_to_use

        preview_ref = ''
        preview_info = ''
        if stream_path:
            found_file = _find_cached_file(seeker, stream_path)
            if found_file:
                preview_ref, preview_info = _build_preview(found_file, extension)
            else:
                preview_info = 'File not found in extraction'
        else:
            preview_info = 'No stream path provided'

        data_list.append((
            convert_unix_ts_to_utc(row[0]),
            convert_unix_ts_to_utc(row[1]),
            convert_unix_ts_to_utc(row[2]),
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            folder_string,
            row[10],
            stream_path,
            preview_ref,
            preview_info,
            row[12],
            row[13]
        ))

    db.close()

    data_headers = (
        ('Item Date', 'datetime'),
        ('Creation Date', 'datetime'),
        ('Modified Date on Client', 'datetime'),
        'Item Type',
        'Item Name',
        'Item Extension',
        'Owner Name',
        'Size',
        'SHA1 Hash',
        'Storage Path',
        'Item ID',
        'Stream Cache Local Path',
        ('Preview', 'media'),
        'Preview Info',
        'Resource ID',
        'Parent Resource ID'
    )

    return data_headers, data_list, source_path