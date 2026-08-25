__artifacts_v2__ = {
    "microsoft_onedrive": {
        "name": "Microsoft OneDrive",
        "description": "Parses Microsoft OneDrive metadata and previews cached stream media",
        "author": "@stark4n6, Matt Beers, Anthony Reince",
        "creation_date": "2025-04-17",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Cloud Storage",
        "notes": "Timestamps <= 0 are blanked. Storage path is resolved by recursively walking parent RID references. Cached streams are resolved via seeker.",
        "paths": (
            '*/com.microsoft.skydrive/files/QTMetadata.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "cloud",
    }
}

import mimetypes
import os

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_embedded_media,
    convert_unix_ts_to_utc,
    does_column_exist_in_db,
    logfunc,
    open_sqlite_db_readonly,
)

from scripts.artifacts.storagePathViews import unique_files

def _safe_convert_ts(ts):
    """Converts unix millisecond timestamps to UTC, blanking <= 0 or invalid values."""
    if not ts:
        return ''
    try:
        ts_val = int(ts)
        if ts_val <= 0:
            return ''
        return convert_unix_ts_to_utc(ts_val)
    except (ValueError, TypeError, OverflowError):
        return ''


def _find_cached_file(seeker, stream_path):
    """Locate the cached stream file in the extraction by matching its path tail."""
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
    """Return (media_ref, info_text) for a cached stream file. Images are checked in as media."""
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


def _resolve_storage_path(resource_id, parent_map, name_map, visited=None):
    """Recursively resolves the folder hierarchy using resourceId -> parentRid lookups."""
    if visited is None:
        visited = set()
    if not resource_id or resource_id in visited:
        return ""
    visited.add(resource_id)

    name = name_map.get(resource_id, str(resource_id))
    parent_id = parent_map.get(resource_id)

    if parent_id and parent_id in name_map:
        parent_path = _resolve_storage_path(parent_id, parent_map, name_map, visited)
        return f"{parent_path}\\{name}" if parent_path else name
    return name


@artifact_processor
def microsoft_onedrive(context):
    files_found = unique_files(context)
    seeker = context.get_seeker()
    data_list = []
    sources = []

    for file_found in files_found:
        file_path = str(file_found)
        if not file_path.endswith("QTMetadata.db"):
            continue

        sources.append(file_path)
        source_name = str(context.get_relative_path(file_found))

        hash_column = 'items.sha1Hash'
        if not does_column_exist_in_db(file_path, 'items', 'sha1Hash'):
            hash_column = 'NULL'
            logfunc(f'No items.sha1Hash column in {file_path}; hash values unavailable')

        query = f'''
        SELECT
            items.itemDate,
            items.creationDate,
            items.modifiedDateOnClient,
            CASE items.itemType
                WHEN 1 then 'File'
                WHEN 3 then 'Image'
                WHEN 32 then 'Folder'
                ELSE items.itemType
            end,
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

        db = open_sqlite_db_readonly(file_path)
        cursor = db.cursor()
        cursor.execute(query)
        db_records = cursor.fetchall()

        if not db_records:
            logfunc(f"No OneDrive records found in {file_path}")
            db.close()
            continue

        name_map = {}
        parent_map = {}

        # Pass 1: Build comprehensive parent/name mappings independent of sort order
        for row in db_records:
            resource_id = row[12]
            parent_rid = row[13]
            display_name = row[4] if row[4] else (row[9] if row[9] else str(resource_id or ''))

            if resource_id:
                name_map[resource_id] = display_name
                parent_map[resource_id] = parent_rid

        # Pass 2: Resolve full path recursively and preview streams
        for row in db_records:
            resource_id = row[12]
            extension = row[5] or ''
            stream_path = row[11]

            folder_string = _resolve_storage_path(resource_id, parent_map, name_map) if resource_id else (row[4] or '')

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
                _safe_convert_ts(row[0]),
                _safe_convert_ts(row[1]),
                _safe_convert_ts(row[2]),
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
                row[13],
                source_name
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
        'Parent Resource ID',
        'Source File'
    )

    return data_headers, data_list, ", ".join(sources) if sources else ""