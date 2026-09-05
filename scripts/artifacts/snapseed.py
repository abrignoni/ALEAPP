__artifacts_v2__ = {
    "snapseed_images": {
        "name": "Snapseed Images",
        "description": "Images opened in Snapseed, with the edit state the app recorded for each",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Snapseed",
        "sample_data": {
            "emu_a15_oss_v13": "Snapseed 4.1.6.975983225 | 6 rows",
        },
        "notes": "One row per row of the image_metadata table in "
                 "com.niksoftware.snapseed/databases/image_edit_local_db, left joined to the "
                 "image_edits row that carries the same id, which is the link the database itself "
                 "records. The store is a Room database in write ahead log mode and the log is "
                 "load bearing: on the tested device the database file read without its log held "
                 "nothing at all in the four data tables, only the two bookkeeping ones, while the "
                 "same file read with its log held every image, so the -wal sidecar is matched by "
                 "the path pattern and must be carried with the database. "
                 "Import Time, Last Activity Time, Edit Saved Time and Capture Time are Unix "
                 "milliseconds and are reported as UTC. Import Time is when the image was first "
                 "registered in the app and Capture Time is what the app recorded for the "
                 "photograph itself; Capture Time is blank where the app stored zero. "
                 "A row is written when an image is opened in the editor, before any adjustment "
                 "is made. On the tested device opening an image and leaving without editing "
                 "produced a row with an empty edit list, so a row is evidence the image was "
                 "opened in Snapseed, not that it was altered. "
                 "Width and Height are the dimensions of the current edit state rather than of "
                 "the source file, so they are where a crop shows: the tested device carried two "
                 "rows for one 640x480 source photograph, the unedited row reading 640x480 and "
                 "the row holding a square crop reading 480x480. "
                 "Original URI and MediaStore ID name the image the row currently stands for, and "
                 "Latest Edited URI names the MediaStore item the app wrote when an edit was "
                 "saved or exported. Read those three alongside Edited Promoted To Original, "
                 "because the app rewrites them, and the rewrite was exercised on the device "
                 "rather than inferred. A throwaway photograph was opened, adjusted, saved, and "
                 "its source file then deleted from shared storage and dropped from MediaStore. "
                 "Reopening the app left both the row and the app's own copy of the picture in "
                 "place, and changed the row: Original URI and MediaStore ID moved off the "
                 "deleted source and onto the app's own saved output, Edited Promoted To Original "
                 "went from 0 to 1, Latest Edited URI was cleared, and the stored edit list was "
                 "emptied, so Edit Steps fell from 1 to 0. "
                 "Three things follow. A row whose Edited Promoted To Original reads 1 names the "
                 "app's own output in Original URI, not the photograph the edit was made on. A "
                 "blank Latest Edited URI is not evidence that nothing was ever saved. And a zero "
                 "in Edit Steps is not evidence that no edit was ever made, because the list is "
                 "discarded when that promotion happens. "
                 "SHA-1 Hash is a content hash the store can carry for an image. Measured on the "
                 "tested device, the stored value equalled the SHA-1 of the bytes of the file it "
                 "names, so an examiner can match a file to this record by hashing it. It was "
                 "populated on one row, the row the app created for a file it had itself exported "
                 "and then read back. "
                 "Edit Steps counts the repeated top level entries of the editListData protobuf. "
                 "On the tested device one adjustment produced one entry and one crop produced "
                 "one more, while applying a bundled Look added two, because that Look's own "
                 "asset inside the application package is itself a two entry stack. A single "
                 "action can therefore contribute more than one step, so the number bounds the "
                 "work done on an image rather than counting the taps that produced it. It is "
                 "blank where the image has no image_edits row at all. The individual steps are "
                 "not decoded: the field numbers that identify each tool carry no names in the "
                 "store, so reporting them as tool names would be guesswork. "
                 "Camera Capture, Trashed, Favorite and Raw are the app's own flags for an image "
                 "taken with the in-app camera, an image sent to the app's trash, an image marked "
                 "as a favourite, and a raw file. Each read the same value on every row of the "
                 "tested device, which had none of those states; they are reported because each "
                 "one separates images on a device where they do occur. Unreachable Since is "
                 "reported as stored. It had no value on any row, the row whose source file was "
                 "deleted in the test above included, so whatever does set it, a source becoming "
                 "unreachable through deletion did not. "
                 "The store holds six tables and the other four are not reported. collages and "
                 "collage_images would carry a collage and the images combined into it, and are "
                 "the ones worth having; both were empty here and could not be filled, because "
                 "the tested build surfaces no way to reach the feature. Its strings and its "
                 "table definitions are in the application package, the gallery filter offers "
                 "only All, Camera and Edits, and the selection menu offers only copy style, "
                 "paste style, remove and share, so nothing here is exercised against them and "
                 "no code is shipped for them. A device whose Snapseed does expose collages "
                 "would be the sample that closes that gap. android_metadata and "
                 "room_master_table are SQLite and Room bookkeeping and carry no user data. "
                 "Location metadata is worth reading with care here. Snapseed's manifest requests "
                 "ACCESS_MEDIA_LOCATION and the permission was not granted on the tested device, "
                 "so Android handed the app image bytes with the GPS EXIF tags overwritten with "
                 "zeroes in place. The source photograph on shared storage still carried its "
                 "coordinates while the app's own copy and the file it exported both carried "
                 "zeroed tags of the same length. Absence of coordinates in a Snapseed copy or "
                 "export is therefore not evidence that the photograph had none.",
        "paths": ('*/com.niksoftware.snapseed/databases/image_edit_local_db*',),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "snapseed_cached_images": {
        "name": "Snapseed Cached Images",
        "description": "Image files Snapseed keeps in its own storage, shown inline",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Snapseed",
        "sample_data": {
            "emu_a15_oss_v13": "Snapseed 4.1.6.975983225 | 8 rows",
        },
        "notes": "One row per file in com.niksoftware.snapseed/files/imported_images and "
                 "com.niksoftware.snapseed/cache/edits_cache. Stored In says which of the two a "
                 "file came from. The imported_images copy is made when an image is opened in the "
                 "editor and holds the picture as the app received it; the edits_cache files are "
                 "renders the app kept while editing. Both are inside the app's private storage. "
                 "That they outlive the picture they were made from was tested rather than "
                 "assumed: a throwaway photograph was opened in the editor, its source file "
                 "was then deleted from shared storage and dropped from MediaStore, and "
                 "after the app was reopened its copy was still in imported_images. "
                 "The image is shown inline. Format is read from the file's own leading bytes "
                 "rather than from its name, which matters because the edits_cache files carry no "
                 "extension; every file on the tested device was a JPEG, and Width and Height are "
                 "read from that file's own header. "
                 "No link from these files to a row of the Snapseed Images artifact is reported, "
                 "because the store records none. An imported_images file is named after the "
                 "image's display name with a numeric suffix added when that name is already "
                 "taken, and an edits_cache name is a number and a thirty two character "
                 "hexadecimal string that appears nowhere in the database, which was checked "
                 "against every text and blob value the database holds. On the tested device six "
                 "image_metadata rows stood against five imported_images files, so even the "
                 "counts do not line up and matching on a name would be a guess. The dimensions "
                 "and the picture itself are what tie a file to a row, and that is left to the "
                 "examiner. The edit cache is also not a complete history: across two pulls of "
                 "the tested device it went from four files to three, two of the first four "
                 "having gone and a new one appeared, so it holds what the app currently "
                 "needs rather than everything it has rendered. "
                 "As noted on the Snapseed Images artifact, the copy the app holds can carry GPS "
                 "EXIF tags overwritten with zeroes where Android redacted them on handover, so "
                 "the copy is not always byte for byte the source file.",
        "paths": ('*/com.niksoftware.snapseed/files/imported_images/*',
                  '*/com.niksoftware.snapseed/cache/edits_cache/*'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "snapseed_settings": {
        "name": "Snapseed Settings",
        "description": "Snapseed preferences, including when the app was first opened",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Snapseed",
        "sample_data": {
            "emu_a15_oss_v13": "Snapseed 4.1.6.975983225 | 22 rows",
        },
        "notes": "One row per key in the XML preference files under "
                 "com.niksoftware.snapseed/shared_prefs. Value is the string the file holds. "
                 "Time (UTC) is filled only for the keys whose value is Unix milliseconds, which "
                 "are first_app_open_date and lastExitTimestamp, and is blank on every other row. "
                 "first_app_open_date is when the app was first opened and lastExitTimestamp is "
                 "when a Snapseed process last exited, so between them they bound the app's use "
                 "on the device. "
                 "gallery_total_items and gallery_edited_items are counters the app keeps outside "
                 "the database. On the tested device they read 6 and 2, against 6 rows in "
                 "image_metadata and the 2 of those rows carrying a Latest Edited URI, so the two "
                 "stores agree by way of different code paths. "
                 "The keys beginning ui_interaction_ carry a per control tally and tool_edit_count "
                 "a tally of edits. On the tested device, where the Tune Image tool was opened "
                 "three times and the Crop tool and the Looks tab once each, "
                 "ui_interaction_TUNE_BUTTON read 3 and ui_interaction_CROP_BUTTON and "
                 "ui_interaction_LOOKS_BUTTON read 1, and tool_edit_count read 4, matching the "
                 "four adjustments confirmed from the Tools tab and not counting the Look that "
                 "was also applied. Both tallies moved by one when one further Tune Image edit "
                 "was made, which is the second observation each reading rests on. These "
                 "tallies sit "
                 "outside the image database, so they can still show that a tool was used after "
                 "the row for the image it was used on has gone. "
                 "crop_last_aspect_ratio is the aspect ratio last chosen in the Crop tool and is "
                 "reported as stored, no mapping for it being published; on the tested device, "
                 "where the square preset was the one chosen, it read 2. last_save_intent is the "
                 "app's own label for the way the last save was made. "
                 "Keys beginning primes. are written by Google's Primes performance library rather "
                 "than by Snapseed and are not reported, except lastExitProcessName and "
                 "lastExitTimestamp, which that library writes but which time the app's own "
                 "process. The keys excluded on the tested device were primes.battery.snapshot, a "
                 "base64 telemetry payload, and primes.packageMetric.lastSendTime, whose value is "
                 "not a Unix time.",
        "paths": ('*/com.niksoftware.snapseed/shared_prefs/*.xml',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
}

import os
import struct
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, \
    get_sqlite_db_records, logfunc, null_absent_columns
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/image_edit_local_db'
IMPORTED = '/files/imported_images/'
EDIT_CACHE = '/cache/edits_cache/'

# Keys whose value is Unix milliseconds. lastExitTimestamp is written by Google's Primes
# library and times this app's own process exit, so it is kept while the rest of that
# library's keys are not.
MS_KEYS = ('first_app_open_date', 'lastExitTimestamp')
PRIMES_KEPT = ('lastExitTimestamp', 'lastExitProcessName')


def _paths(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)]


def _db_files(context):
    # The pattern also matches the -wal and -shm sidecars, which carry the rows but are
    # not opened directly. Ending exactly at the database name selects the database.
    return [p for p in _paths(context) if p.endswith(DB_SUFFIX)]


def _ms(value):
    """A Unix millisecond value as UTC, blank when absent or zero."""
    if not value:
        return ''
    try:
        value = int(value)
        if value <= 0:
            return ''
        return convert_unix_ts_to_utc(value // 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _yes_no(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _edit_steps(blob):
    """Count the repeated top level entries of an editListData protobuf.

    The stack is a protobuf whose repeated field 4 holds one entry per filter step. The
    field numbers inside each entry identify the tool and carry no names in the store, so
    only the count is reported. Returns '' when the blob cannot be walked.
    """
    if blob is None:
        return ''
    if not isinstance(blob, (bytes, bytearray)):
        return ''
    data = bytes(blob)
    if not data:
        return 0
    steps = 0
    index = 0
    try:
        while index < len(data):
            tag, index = _varint(data, index)
            field, wire = tag >> 3, tag & 7
            if wire == 0:
                _, index = _varint(data, index)
            elif wire == 1:
                index += 8
            elif wire == 2:
                length, index = _varint(data, index)
                if length < 0 or index + length > len(data):
                    raise ValueError('length runs past the end of the blob')
                if field == 4:
                    steps += 1
                index += length
            elif wire == 5:
                index += 4
            else:
                raise ValueError(f'unknown wire type {wire}')
            if index > len(data):
                raise ValueError('field runs past the end of the blob')
    except (IndexError, ValueError) as ex:
        logfunc(f'Snapseed: could not walk an edit list of {len(data)} bytes: {ex}')
        return ''
    return steps


def _varint(data, index):
    result = 0
    shift = 0
    while True:
        byte = data[index]
        index += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, index
        shift += 7
        if shift > 63:
            raise ValueError('varint is too long')


def _jpeg_size(data):
    """(width, height) from a JPEG's own start of frame marker, else ('', '')."""
    index = 2
    while index + 9 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7 or marker == 0xFF:
            index += 2
            continue
        length = struct.unpack('>H', data[index + 2:index + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack('>HH', data[index + 5:index + 9])
            return width, height
        if marker == 0xDA:
            break
        index += 2 + length
    return '', ''


def _describe(path):
    """(format, width, height, size) read from the file's own bytes."""
    try:
        size = os.path.getsize(path)
        with open(path, 'rb') as handle:
            head = handle.read(131072)
    except OSError as ex:
        logfunc(f'Snapseed: could not read {os.path.basename(path)}: {ex}')
        return '', '', '', ''
    if head[:3] == b'\xff\xd8\xff':
        width, height = _jpeg_size(head)
        return 'JPEG', width, height, size
    if head[:8] == b'\x89PNG\r\n\x1a\n' and len(head) >= 24:
        width, height = struct.unpack('>II', head[16:24])
        return 'PNG', width, height, size
    if head[:4] == b'RIFF' and head[8:12] == b'WEBP':
        return 'WebP', '', '', size
    return 'Unrecognised', '', '', size


@artifact_processor
def snapseed_images(context):
    query = '''SELECT m.importTime, m.lastActivityTime, e.timestamp, m.captureTime,
                      m.displayName, m.width, m.height, m.originalUri, m.mediaStoreId,
                      m.latestEditedUri, m.sha1Hash, e.editListData,
                      m.isCameraCapture, m.editedPromotedToOriginal, m.isTrashed,
                      m.isFavorite, m.isRaw, m.unreachableSince, m.id
               FROM image_metadata m
               LEFT JOIN image_edits e ON e.imageId = m.id
               ORDER BY m.importTime DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, null_absent_columns(db_path, query))
        for r in records:
            data_list.append((
                _ms(r[0]), _ms(r[1]), _ms(r[2]), _ms(r[3]),
                r[4] or '', r[5], r[6], r[7] or '', r[8],
                r[9] or '', r[10] or '', _edit_steps(r[11]),
                _yes_no(r[12]), _yes_no(r[13]), _yes_no(r[14]),
                _yes_no(r[15]), _yes_no(r[16]), _ms(r[17]), r[18],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Import Time', 'datetime'), ('Last Activity Time', 'datetime'),
        ('Edit Saved Time', 'datetime'), ('Capture Time', 'datetime'),
        'Display Name', 'Width', 'Height', 'Original URI', 'MediaStore ID',
        'Latest Edited URI', 'SHA-1 Hash', 'Edit Steps',
        'Camera Capture', 'Edited Promoted To Original', 'Trashed', 'Favorite', 'Raw',
        ('Unreachable Since', 'datetime'), 'Image ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def snapseed_cached_images(context):
    data_list = []
    sources = []
    for path in _paths(context):
        if IMPORTED in path:
            stored_in = 'Imported original'
        elif EDIT_CACHE in path:
            stored_in = 'Edit cache'
        else:
            continue
        # A pattern whose last component is a bare * also matches the directory itself.
        if os.path.isdir(path):
            continue
        name = os.path.basename(path)
        image_format, width, height, size = _describe(path)
        media = check_in_media(path, name) if image_format != 'Unrecognised' else None
        data_list.append((name, stored_in, image_format, width, height, size,
                          media or '', context.get_relative_path(path)))
        # One line per file would run to hundreds on a device with a busy cache, so the
        # directories are cited here and the exact file is in each row's Source File.
        parent = os.path.dirname(path)
        if parent not in sources:
            sources.append(parent)

    data_list.sort(key=lambda row: (row[1], row[0]))
    data_headers = ('File Name', 'Stored In', 'Format', 'Width', 'Height',
                    'Size (bytes)', ('Image', 'media'), 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def snapseed_settings(context):
    data_list = []
    sources = []
    for path in _paths(context):
        if '/shared_prefs/' not in path or not path.endswith('.xml'):
            continue
        try:
            root = ET.parse(path).getroot()
        except (ET.ParseError, OSError) as ex:
            logfunc(f'Snapseed: could not read {os.path.basename(path)}: {ex}')
            continue
        found = False
        for entry in root:
            key = entry.get('name')
            if not key:
                continue
            if key.startswith('primes.') and key not in PRIMES_KEPT:
                continue
            value = entry.get('value')
            if value is None:
                value = (entry.text or '').strip()
            timestamp = _ms(value) if key in MS_KEYS else ''
            data_list.append((key, value, timestamp, context.get_relative_path(path)))
            found = True
        if found:
            sources.append(path)

    data_list.sort(key=lambda row: (row[3], row[0]))
    data_headers = ('Setting', 'Value', ('Time (UTC)', 'datetime'), 'Source File')
    return data_headers, data_list, '\n'.join(sources)
