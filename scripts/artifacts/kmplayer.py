__artifacts_v2__ = {
    "kmplayer_playback": {
        "name": "KMPlayer Playback History",
        "description": "Media KMPlayer opened, with the local URI or remote address of each and the time it was opened",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "KMPlayer",
        "sample_data": {
            "emu_a15_oss_v15": "KMPlayer 36.04.235 | 2 rows",
        },
        "notes": "One row per live entry of the Hive box "
                 "com.kmplayer/databases/db/hive_url_meta_box.hive. KMPlayer is written in "
                 "Flutter and keeps its state in Hive boxes rather than in SQLite. A Hive box is "
                 "a flat log of frames and a later frame for the same key supersedes an earlier "
                 "one, so only the surviving entries are reported; each frame carries its own "
                 "CRC32 and the reader stops at the first frame that fails it. "
                 "Hive stores a class as numbered fields and keeps the field names only in the "
                 "app's compiled Dart, so the numbers were mapped against playback created "
                 "deliberately on the tested device rather than read from any source. Two items "
                 "were played: a local video opened by content URI and a video fetched from an "
                 "http address, which is what lets the fields be told apart. "
                 "Opened is field 10, Unix milliseconds, reported as UTC; both rows matched the "
                 "wall clock of the play that produced them to the second. Address is field 3, "
                 "which held the full "
                 "content:// URI for the local play and the full http URL for the remote one, so "
                 "on the remote row it records an address the device contacted. Title is field 1, "
                 "which the app fills with the file name for a remote item and with the "
                 "MediaStore id for a local one, so it is not always a human title. Source (as "
                 "stored) is field 0; it read 0 on the local row and 1 on the remote row of the "
                 "tested image, which is one observation of each and not enough to state what the "
                 "field means, so it is reported as stored. "
                 "A row records that the app opened the item, not that anyone watched it, and "
                 "not how much was played. "
                 "Other stores in the same app that are not parsed here: hive_media_flag_box "
                 "holds a per-item playback flag block whose field meanings could not be "
                 "established from two entries; hive_setting_box, hive_home_group_box and "
                 "hive_quickbutton_box are app configuration and shipped menu layout; "
                 "hive_mylist_box, hive_queue_list_box, hive_media_bookmark_box and "
                 "hive_cloud_info_box were all zero bytes on the tested image and would carry "
                 "user lists, queues and bookmarks on a device that used those features. The app "
                 "also ships a VLC medialibrary SQLite at databases/db/database.dat; its Media, "
                 "File and Folder tables were empty here because the in-app library was never "
                 "scanned, and no existing module claims that path.",
        "paths": ('*/com.kmplayer/databases/db/hive_url_meta_box.hive',),
        "output_types": "standard",
        "artifact_icon": "film",
    },
}

import struct

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc
from scripts.artifacts.storagePathViews import unique_files
from scripts.artifacts.hiveReader import hive_entries

BOX_SUFFIX = 'com.kmplayer/databases/db/hive_url_meta_box.hive'

# Field numbers of an entry, mapped from playback created for the purpose. Hive keeps the
# names only in the app's compiled Dart, so these are named from observation.
ENTRY_SOURCE, ENTRY_TITLE, ENTRY_ADDRESS, ENTRY_OPENED = 0, 1, 3, 10


def _box_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(BOX_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value // 1000)
    except (OverflowError, OSError, ValueError):
        return ''


@artifact_processor
def kmplayer_playback(context):
    data_list = []
    sources = []
    for box_path in _box_files(context):
        try:
            entries, _ = hive_entries(box_path)
        except (OSError, ValueError, struct.error) as error:
            logfunc(f'KMPlayer: could not read {box_path}: {error}')
            continue
        seen = False
        for value in entries.values():
            if not isinstance(value, dict):
                continue
            seen = True
            data_list.append((
                _ms(value.get(ENTRY_OPENED)),
                value.get(ENTRY_ADDRESS) or '',
                value.get(ENTRY_TITLE) or '',
                value.get(ENTRY_SOURCE) if value.get(ENTRY_SOURCE) is not None else '',
                context.get_relative_path(box_path)))
        if seen and box_path not in sources:
            sources.append(box_path)

    data_list.sort(key=lambda row: row[0], reverse=True)
    data_headers = (
        ('Opened', 'datetime'), 'Address', 'Title', 'Source (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
