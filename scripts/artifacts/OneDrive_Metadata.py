# pylint: disable=W0613
__artifacts_v2__ = {
    "get_onedrive": {
        "name": "OneDrive Metadata",
        "description": "Parses the QTMetadata.db from OneDrive",
        "author": "Matt Beers and Anthony Reince",
        "creation_date": "2025-04-17",
        "last_update_date": "2025-04-17",
        "requirements": "none",
        "category": "Cloud Storage",
        "notes": "Inline base64 image previews replaced with checked-in media; cached image streams are "
                 "shown in the Preview (media) column, other types are summarised in Preview Info.",
        "paths": ('*/com.microsoft.skydrive/files/QTMetadata.db*'),
        "output_types": "standard",
        "artifact_icon": "cloud",
        "sample_data": {
            "anne_a15": "Android 15 | com.microsoft.skydrive vc 2027390102 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.microsoft.skydrive vc 2026998332 | 0 rows",
            "samsunga53_a14": "Android 14 | com.microsoft.skydrive vc 2027440202 | 0 rows",
            "samsungs20_a13": "Android 13 | com.microsoft.skydrive | 0 rows",
            "sharon_a14": "Android 14 | com.microsoft.skydrive vc 2027110002 | 0 rows",
        },
    }
}

import datetime
import os
import mimetypes

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_embedded_media


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _find_cached_file(seeker, stream_path):
    """Locate the cached stream file in the extraction by matching its path tail."""
    stream_path_norm = os.path.normpath(stream_path).lower().lstrip(os.sep)
    stream_path_tail = os.path.join(*stream_path_norm.split(os.sep)[-6:]).replace('\\', '/')
    for match in seeker.search(f'*{os.path.basename(stream_path)}'):
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
        ref = check_in_embedded_media(str(found_file), data, name=os.path.basename(str(found_file)),
                                      force_type=guessed_mime, force_extension=ext) or ''
        return ref, 'Image' if ref else f'image ({len(data)} bytes)'
    if guessed_mime and guessed_mime.startswith('text'):
        return '', data.decode('utf-8', errors='ignore')[:300]
    if guessed_mime:
        return '', f'{guessed_mime} ({len(data)} bytes)'
    return '', f'Unknown file type ({len(data)} bytes)'


@artifact_processor
def get_onedrive(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source = ''

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('QTMetadata.db'):
            source = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            cursor.execute('''
            SELECT
                items.itemDate,
                items._id,
                items.extension,
                items.name,
                items.ownerName,
                items.sha1Hash,
                stream_cache.parentID,
                stream_cache.stream_location
            FROM
                items
            LEFT JOIN
                stream_cache
            ON items._id = stream_cache.parentID
            ORDER BY items.itemDate ASC;
            ''')

            for row in cursor.fetchall():
                item_date = _ms_to_utc(row[0])
                item_id = row[1]
                extension = row[2] or ''
                name = row[3]
                owner = row[4]
                sha1 = row[5]
                parent_id = row[6]
                stream_path = row[7]

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

                data_list.append((item_date, item_id, extension, name, owner, sha1, parent_id,
                                  stream_path, preview_ref, preview_info))
            db.close()

    data_headers = (
        ('Item Date', 'datetime'), 'ID', 'Extension', 'File or Folder Name', 'Owner Name',
        'Sha1 Hash', 'Parent ID', 'Stream Location', ('Preview', 'media'), 'Preview Info')

    return data_headers, data_list, source
