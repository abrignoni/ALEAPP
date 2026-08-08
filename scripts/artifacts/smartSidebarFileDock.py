"""
OxygenOS/ColorOS Smart Sidebar — File Dock (transfer dock)
ALEAPP module

Parses the hidden cache the Smart Sidebar keeps for every item the user adds
to its File Dock on OnePlus/Oppo/Realme devices, whether by drag and drop or
via the share sheet's "Save to File Dock":
    Download/.com_coloros_smartsidebar/transferdock/<Base64 folder>/<cached file>

Each Base64 folder name decodes to <uuid>|<uuid>|<epoch ms added>|<name tail>,
giving the exact time the item was added to the dock. The cached file is a full
copy of the added content and survives deletion of the original:
  - OPLUSDRAG_<source package>_<view>_<local time>.<ext> — media dragged out of
    an app, preserving content from ephemeral apps (e.g. Snapchat) with the
    source app and on-screen capture time embedded in the file name
  - transferdock_<epoch ms>.txt — text selections
  - link_file_<epoch ms>.link — links (JSON: link/title/subTitle/imgUrl)
  - any other name — files added from a file manager or the share sheet,
    keeping their original name

Also parses the app's private Room database (rooted/full file system extractions):
    data/com.coloros.smartsidebar/databases/smartSidebar.db (+ -wal)
transfer_dock_file_info holds one row per dock item with the original source
content:// URI, MIME type, size and timestamps; transfer_dock_deleted_file_info
retains removed items. The two UUIDs in each cached folder name are the row's
localFileId and groupUUId, so db rows and cached files cross-reference directly.
The main db is often empty with all rows resident in the un-checkpointed WAL.
"""

__artifacts_v2__ = {
    "get_smartSidebarFileDock": {
        "name": "Smart Sidebar File Dock",
        "description": (
            "Items the user added to the OxygenOS/ColorOS Smart Sidebar File "
            "Dock (OnePlus/Oppo/Realme) by drag and drop or via the share "
            "sheet's Save to File Dock. Each item is a cached copy stored "
            "under Download/.com_coloros_smartsidebar/transferdock/ in a "
            "Base64-named folder encoding the time it was added to the dock. "
            "Media dragged out of apps is saved as OPLUSDRAG_<source app>_"
            "<view>_<local time> files, preserving content from ephemeral apps "
            "(e.g. Snapchat) long after it is gone from the source app. Text "
            "selections and links are stored as transferdock_<ms>.txt and "
            "link_file_<ms>.link files; other files keep their original names."
        ),
        "author": "@akhil-dara",
        "creation_date": "2026-07-18",
        "last_update_date": "2026-07-18",
        "requirements": "none",
        "category": "Smart Sidebar",
        "notes": (
            "Folder name format: base64(<uuid>|<uuid>|<epoch ms added>|<last 20 "
            "chars of file name>). The capture time inside OPLUSDRAG file names "
            "is device local time. Items observed to persist for 2+ years."
        ),
        "paths": ('*/Download/.com_coloros_smartsidebar/transferdock/*/*',),
        "output_types": "standard",
        "artifact_icon": "sidebar",
    },
    "get_smartSidebarFileDockDb": {
        "name": "Smart Sidebar File Dock Db",
        "description": (
            "Item registry kept by the OxygenOS/ColorOS Smart Sidebar File Dock "
            "in its private Room database (smartSidebar.db). Each row records a "
            "dock item with its original source content:// URI, MIME type, size "
            "and timestamps; removed items are retained in a separate deleted-"
            "items table. Rows cross-reference the cached copies parsed by the "
            "Smart Sidebar File Dock artifact through the Local File ID and "
            "Group UUID encoded in each cached folder name."
        ),
        "author": "@akhil-dara",
        "creation_date": "2026-07-18",
        "last_update_date": "2026-07-18",
        "requirements": "none",
        "category": "Smart Sidebar",
        "notes": (
            "The main db file is often nearly empty with schema and rows "
            "resident in the un-checkpointed WAL, hence the db* search pattern. "
            "For text selections the db may hold only a preview of the text "
            "(isAll=false); the full text is in the cached transferdock file. "
            "fileType codes observed: 1=text, 2=image, 4=file, 6=link."
        ),
        "paths": ('*/com.coloros.smartsidebar/databases/smartSidebar.db*',),
        "output_types": "standard",
        "artifact_icon": "database",
    }
}

import base64
import datetime
import json
import os
import re

from scripts.ilapfuncs import (artifact_processor, check_in_media, does_table_exist_in_db,
                               get_sqlite_db_records, logfunc)

OPLUSDRAG_PATTERN = re.compile(
    r'^OPLUSDRAG_(?P<package>.+)_(?P<view>[A-Za-z0-9$]+)_'
    r'(?P<local_time>\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_\d{2})\.\w+$')
TEXT_CLIP_PATTERN = re.compile(r'^transferdock_(\d{13})\.txt$')
LINK_PATTERN = re.compile(r'^link_file_(\d{13})\.link$')


def _ms_to_utc(value):
    '''Convert a millisecond Unix epoch value to a timezone-aware UTC datetime.

    Returns an empty string for missing or out-of-range values so callers can
    treat the result as a report cell directly.
    '''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _decode_dock_dirname(dirname):
    '''Decode a Base64 dock folder name into (local_file_id, group_uuid, added_utc).

    The folder name is base64 of "<localFileId>|<groupUUId>|<epoch ms added>|
    <last 20 chars of the cached file name>", stored without padding. Standard
    and URL-safe alphabets are both attempted. Returns ('', '', '') when the
    name does not decode to that layout; callers then fall back to timestamps
    embedded in the cached file name or the file modification time.
    '''
    padded = dirname + '=' * (-len(dirname) % 4)
    for altchars in (None, b'-_'):
        try:
            decoded = base64.b64decode(padded, altchars=altchars, validate=True).decode('utf-8')
        except (ValueError, UnicodeDecodeError):
            continue
        parts = decoded.split('|')
        if len(parts) == 4 and parts[2].isdigit():
            return parts[0], parts[1], _ms_to_utc(parts[2])
    return '', '', ''


def _parse_local_time(raw):
    '''Reformat an OPLUSDRAG capture time ("2026-06-28_19_06_00") for display.

    The value is device-local wall-clock time with no timezone information,
    so it is reported as a plain string rather than a typed datetime.
    '''
    try:
        parsed = datetime.datetime.strptime(raw, '%Y-%m-%d_%H_%M_%S')
    except ValueError:
        return raw
    return parsed.strftime('%Y-%m-%d %H:%M:%S')


def _read_text(file_found):
    '''Return the text content of a cached file, tolerating invalid UTF-8.'''
    with open(file_found, 'r', encoding='utf-8', errors='replace') as file:
        return file.read().strip()


@artifact_processor
def get_smartSidebarFileDock(context):
    '''Parse the cached dock items on shared storage (transferdock folder).'''
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source_path = ''
    seen_items = set()

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue

        file_name = os.path.basename(file_found)
        dock_dirname = os.path.basename(os.path.dirname(file_found))
        # The same item can surface through emulated-storage bind mounts
        # (/storage/emulated/0 and /data/media/0) — report it once.
        if (dock_dirname, file_name) in seen_items:
            continue
        seen_items.add((dock_dirname, file_name))

        source_path = os.path.dirname(os.path.dirname(file_found))
        # Parse each item in isolation: a single corrupt or unexpected cache
        # entry must not prevent the remaining items from being reported.
        try:
            data_list.append(_parse_dock_item(context, seeker, file_found, file_name, dock_dirname))
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logfunc(f'Smart Sidebar File Dock - could not parse {file_name}: {exc}')

    min_utc = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
    data_list.sort(key=lambda row: row[0] if isinstance(row[0], datetime.datetime) else min_utc)

    data_headers = (
        ('Added Timestamp', 'datetime'), 'Item Type', ('Media', 'media'), 'Content',
        'Source App', 'Source View', 'Capture Time (Device Local)', 'File Name',
        ('File Size', 'bytes'), 'Local File ID', 'Group UUID', 'Source Path')
    return data_headers, data_list, source_path


def _parse_dock_item(context, seeker, file_found, file_name, dock_dirname):
    '''Build one report row for a cached dock item.

    Classifies the item by its file name (OPLUSDRAG app drag, text selection,
    shared link, or a file added with its original name), extracts content for
    text and link items, and checks binary items into the media system for
    thumbnails.
    '''
    item_id, secondary_id, added_utc = _decode_dock_dirname(dock_dirname)
    file_size = os.path.getsize(file_found)

    item_type = 'File'
    source_app = source_view = capture_local_time = content = ''
    media = ''
    name_ms_match = None

    drag_match = OPLUSDRAG_PATTERN.match(file_name)
    link_match = LINK_PATTERN.match(file_name)
    text_match = TEXT_CLIP_PATTERN.match(file_name)
    if drag_match:
        item_type = 'Media dragged from app'
        source_app = drag_match.group('package')
        source_view = drag_match.group('view')
        capture_local_time = _parse_local_time(drag_match.group('local_time'))
    elif link_match:
        item_type = 'Shared link'
        name_ms_match = link_match
        raw = _read_text(file_found)
        try:
            link_data = json.loads(raw)
        except ValueError:
            link_data = {}
        if not isinstance(link_data, dict):
            link_data = {}
        content = str(link_data.get('link') or '') or raw
        title = ' '.join(str(value) for value in
                         (link_data.get('title'), link_data.get('subTitle')) if value)
        if title:
            content = f'{title} — {content}'
    elif text_match:
        item_type = 'Text selection'
        name_ms_match = text_match

    # Any .txt item carries its text as the evidence - including files dragged
    # from a file manager that kept an original .txt name.
    if not content and file_name.lower().endswith('.txt'):
        content = _read_text(file_found)

    if not added_utc and name_ms_match:
        added_utc = _ms_to_utc(name_ms_match.group(1))

    # Items without textual content are checked into the media system so the
    # cached copy itself is surfaced (image/video thumbnail or file link).
    # Extracted zip archives carry no file dates, so the added-to-dock time
    # and the on-disk modification time are supplied explicitly.
    if not content and not link_match:
        file_info = seeker.file_infos.get(file_found)
        modified = file_info.modification_date if file_info and file_info.modification_date \
            else int(os.path.getmtime(file_found))
        created = int(added_utc.timestamp()) if added_utc else None
        media = check_in_media(file_found, name=file_name,
                               force_creation_date=created,
                               force_modification_date=modified) or ''

    # Last resort for undecodable folder names: the file modification time,
    # which extraction restores from the archive. A zero mtime is treated as
    # unknown rather than reported as 1970-01-01.
    if not added_utc:
        mtime = os.path.getmtime(file_found)
        added_utc = _ms_to_utc(mtime * 1000) if mtime > 0 else ''

    return (added_utc, item_type, media, content, source_app, source_view,
            capture_local_time, file_name, file_size, item_id, secondary_id,
            context.get_relative_path(file_found))


# fileType codes observed on test devices; unknown codes are reported raw.
FILE_TYPE_LABELS = {1: 'Text selection', 2: 'Image', 4: 'File', 6: 'Shared link'}

# The deleted-items table has the same columns as the live table except
# localPath, which is substituted so both queries yield identical row shapes.
DOCK_DB_COLUMNS = ('createTime, updateTime, fileType, mimeType, fileContent, fileName, '
                   'fileOName, linkSource, fileSize, md5, status, {local_path}, '
                   'localFileId, groupUUId, mediaStoreUri, userId')
DOCK_DB_LIVE_QUERY = ('SELECT ' + DOCK_DB_COLUMNS.format(local_path='localPath') +
                      ' FROM transfer_dock_file_info')
DOCK_DB_DELETED_QUERY = ('SELECT ' + DOCK_DB_COLUMNS.format(local_path="'' AS localPath") +
                         ' FROM transfer_dock_deleted_file_info')


def _dock_db_content(file_type, file_content, link_source):
    '''Extract displayable content from a database row.

    Text rows (fileType 1) store JSON {"content", "duration", "isAll"} in
    fileContent - isAll false means the db holds only a preview of the text.
    Link rows store JSON {"link", "title", "subTitle", "imgUrl"} in
    linkSource. Returns (content, content_complete) report cells; malformed
    JSON is returned as-is rather than discarded.
    '''
    if file_type == 1 and file_content:
        try:
            parsed = json.loads(file_content)
        except ValueError:
            parsed = None
        if not isinstance(parsed, dict):
            return file_content, ''
        complete = parsed.get('isAll')
        return str(parsed.get('content') or ''), \
            '' if complete is None else ('Yes' if complete else 'No (preview)')
    if link_source:
        try:
            parsed = json.loads(link_source)
        except ValueError:
            parsed = None
        if not isinstance(parsed, dict):
            return link_source, ''
        link = str(parsed.get('link') or '')
        title = ' '.join(str(value) for value in
                         (parsed.get('title'), parsed.get('subTitle')) if value)
        return (f'{title} — {link}' if title else link), ''
    return '', ''


@artifact_processor
def get_smartSidebarFileDockDb(context):
    '''Parse the dock item registry in the app's private Room database.

    The search pattern co-extracts -wal and -shm sidecars: on test devices
    the main db was a near-empty stub with schema and rows resident in the
    un-checkpointed WAL, which SQLite reads through the standard read-only
    open as long as the -wal file is present. Only the main db file is opened
    here; the sidecars are skipped by name.
    '''
    files_found = context.get_files_found()
    data_list = []
    source_paths = []
    seen_records = set()

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('smartSidebar.db'):
            continue
        source_paths.append(file_found)

        records = [row + ('Active',) for row in
                   get_sqlite_db_records(file_found, DOCK_DB_LIVE_QUERY)]
        if does_table_exist_in_db(file_found, 'transfer_dock_deleted_file_info'):
            records += [row + ('Deleted',) for row in
                        get_sqlite_db_records(file_found, DOCK_DB_DELETED_QUERY)]

        for row in records:
            (create_ms, update_ms, file_type, mime_type, file_content, file_name,
             original_source, link_source, file_size, md5, status, local_path,
             local_file_id, group_uuid, media_store_uri, user_id, record) = row
            # The same db can surface through /data/data, /data/user/0 and
            # data_mirror bind mounts — report each record once.
            key = (record, local_file_id, group_uuid, create_ms)
            if key in seen_records:
                continue
            seen_records.add(key)

            content, content_complete = _dock_db_content(file_type, file_content, link_source)
            item_type = FILE_TYPE_LABELS.get(file_type, f'Type {file_type}')
            data_list.append((
                _ms_to_utc(create_ms), _ms_to_utc(update_ms), record, item_type, content,
                content_complete, file_name, original_source, mime_type, file_size, md5,
                status, local_path, local_file_id, group_uuid, media_store_uri, user_id))

    min_utc = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
    data_list.sort(key=lambda row: row[0] if isinstance(row[0], datetime.datetime) else min_utc)

    data_headers = (
        ('Created Timestamp', 'datetime'), ('Updated Timestamp', 'datetime'), 'Record',
        'Item Type', 'Content', 'Content Complete', 'File Name', 'Original Source',
        'MIME Type', ('File Size', 'bytes'), 'MD5', 'Status', 'Cached Path',
        'Local File ID', 'Group UUID', 'MediaStore URI', 'User ID')
    return data_headers, data_list, '\n'.join(source_paths)
