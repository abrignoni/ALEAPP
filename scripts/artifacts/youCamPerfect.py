__artifacts_v2__ = {
    "youcam_perfect_images": {
        "name": "YouCam Perfect Images",
        "description": "Photos YouCam Perfect recorded, with the copy it cached where one is present",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "YouCam Perfect",
        "sample_data": {
            "emu_a15_oss2_v3": "YouCam Perfect 6.21.1 | 7 rows",
        },
        "notes": "One row per row of the Image table in "
                 "com.cyberlink.youperfect/databases/pht.sqlite. The app writes more than one "
                 "row for the same photo, so Media Store Id repeats and Record Id is the row's "
                 "own identifier.\n"
                 "**Media Store Id is Android's own media identifier**, and Stored Path, Media "
                 "Store Size and Media Store Modified are read from the platform media database "
                 "in the same container, joined on that id. Both package names Android has used for "
                 "that database are read, com.google.android.providers.media.module and "
                 "com.android.providers.media, and only the first exists on this image. The join "
                 "was measured: all five ids held on the tested device matched a row in it, and "
                 "for every row carrying dimensions those dimensions matched the ones the media "
                 "database records for the same file. An extraction without that database leaves those "
                 "three columns blank.\n"
                 "**A row whose Source Modified, File Type, Width and Height are empty is not "
                 "evidence the photo was opened.** The app writes such a row for each photo its "
                 "own picker lists. Measured on the device this image came from, after the image "
                 "was captured, by opening one album of eight photos and selecting none of them: "
                 "the table went from the 7 rows this image holds to 15, and the eight new rows "
                 "were exactly the eight photos in that album.\n"
                 "**Source Modified is the photo file's own modification time, not a time the app "
                 "did anything.** It is the CaptureTime column, Unix seconds reported as UTC. "
                 "Every row of this image that carries a value reads 1788744945, which is exactly "
                 "what the media database records as that file's modification time. The second "
                 "value was produced on the device after this image was captured, by opening a "
                 "screenshot the media database records as modified at 1789173261: the rows "
                 "written for it read 1789173261. The columns are filled in when a photo is "
                 "selected, including on the row the picker had already written.\n"
                 "Cached Copy renders the file the ImageCache table records for this row at the "
                 "highest Level, which on the tested device is the full size copy rather than "
                 "the small one; where that file is not in the extraction, or its name carries "
                 "no image extension, the next Level down is tried. Cached Copies counts every "
                 "file the table records for the row, rendered or not. The app writes two per image on the tested "
                 "device, a full size and a small one, at the moment the editor loads the photo. "
                 "**Leaving the editor without saving deletes them.** Measured on the device "
                 "after this image was captured, by opening one photo, which took ImageCache from "
                 "the 4 rows this image holds to 6, then pressing back without saving, which took "
                 "it to 4 again while the Image row stayed. So a cached copy present is not "
                 "evidence an edit was saved, and a cached copy absent is not evidence a photo was "
                 "never opened.\n"
                 "Edit Steps counts this row's entries in ImageDevelopHistoryStep. Those entries "
                 "survived leaving the editor unsaved in the same test. On this image every one of "
                 "them carried an empty step name and a default settings blob, so no edit "
                 "operation is named and the count is not a count of edits made. One of the three "
                 "entries this image holds carries an image id of -1, which matches no row, so it "
                 "is counted against nothing and is not reported.\n"
                 "Rating, Orientation, PresetCommand, Temperature, RawSDKMode, ShareTo, "
                 "ThumbOrientation, OriginalColorSpace and SourceOrientation are not reported: each "
                 "read a single value across the three rows of this image that carry any metadata, "
                 "so nothing distinguishes them. RefreshModifiedTime is not reported either, "
                 "because it equalled CaptureTime on every row of this image.\n"
                 "The store's Media, Message, Friend, CLGroup, GroupAlbum, Sticker and StickerPack "
                 "tables held no rows and are a checked absence. The app's other databases are not "
                 "user data and are not parsed: pfcommon.sqlite CACHE and interstitial_db.db src "
                 "hold vendor-supplied promotion and pricing catalogues downloaded from the app's "
                 "servers, countly.sqlite holds a queue of analytics the app was sending, "
                 "more.sqlite holds the app's own interface strings, and exoplayer_internal.db "
                 "indexes video the app cached for playback.",
        "paths": ('*/com.cyberlink.youperfect/databases/pht.sqlite*',
                  '*/com.cyberlink.youperfect/cache/imagecache/*',
                  '*/com.google.android.providers.media.module/databases/external.db*',
                  '*/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "youcam_perfect_saved_photos": {
        "name": "YouCam Perfect Saved Photos",
        "description": "Image files sitting in the folder YouCam Perfect writes its output to",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "YouCam Perfect",
        "sample_data": {
            "emu_a15_oss2_v3": "YouCam Perfect 6.21.1 | 0 rows",
        },
        "notes": "One row per file in the device's DCIM/YouCam Perfect folder, and per file in "
                 "any folder below it.\n"
                 "**The app records a saved photo nowhere else.** Its PhotoExport2 table stayed at "
                 "zero rows through a save that really did write a file, so this folder is the "
                 "record. Measured on the device after this image was captured, by opening a photo "
                 "in the editor and pressing Save: a 41,394 byte JPEG appeared in "
                 "DCIM/YouCam Perfect while PhotoExport2 stayed empty. This image was captured "
                 "before that save, holds no such folder, and so reports no rows here.\n"
                 "**The file name is a local wall clock and carries no time zone.** It is written "
                 "as year, month, day, hour, minute, second and milliseconds separated by hyphens. "
                 "On that same save the name read 2026-09-11-23-02-00-451.jpg on a device set to "
                 "America/New_York, and the file's own modification time was 23:02:00 in that same "
                 "zone. The name is reported as stored and no instant is asserted from it, because "
                 "the zone a name was written in is not recorded in the name.\n"
                 "**The folder name and the file name shape both rest on a single observation**, one "
                 "save on one app version, so a different version or a different device may write "
                 "elsewhere or name differently. A row is "
                 "evidence a file is present under the name and folder the app writes, not that "
                 "the app produced this particular file.\n"
                 "Saved renders the file when its name carries an image extension the report can "
                 "display, and is blank otherwise, so a file of another kind saved into this "
                 "folder is still reported by name and size with nothing rendered. Modified is "
                 "the file's own modification time as the extraction carries it.",
        "paths": ('*/DCIM/YouCam Perfect/*',),
        "output_types": "standard",
        "artifact_icon": "device-floppy",
    },
    "youcam_perfect_app_state": {
        "name": "YouCam Perfect App State",
        "description": "Install-level values YouCam Perfect keeps in its own settings file",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "YouCam Perfect",
        "sample_data": {
            "emu_a15_oss2_v3": "YouCam Perfect 6.21.1 | 1 rows",
        },
        "notes": "One row per copy of "
                 "com.cyberlink.youperfect/shared_prefs/YOUPERFECT_ANDROID_SETTING.xml that "
                 "holds at least one of the four keys below. A copy holding none of them, and a "
                 "copy that does not parse as XML, are skipped and produce no row.\n"
                 "**First Launch is APP_FIRST_LAUNCH_TIME, Unix milliseconds reported as UTC, and "
                 "it was corroborated against the platform's own install record**: the value read "
                 "19 seconds after the firstInstallTime that the package manager reports for the "
                 "app on the tested device.\n"
                 "Installation Id is the InstallationId key, an identifier the app generates for "
                 "itself. It is reported as stored; it is not an account, and what the app sends "
                 "it to was not established.\n"
                 "Country is the KEY_PREVIOUS_COUNTRY_CODE key, reported as stored. How the app "
                 "arrives at that value was not established, so it is not evidence of where the "
                 "device was.\n"
                 "Last Photo Picker Check is the LAST_PHOTO_PICKER_CHECK_TIME key, Unix "
                 "milliseconds. What it counts was not established beyond its name, so a reader "
                 "should not treat it as the last time a photo was chosen.\n"
                 "The file's other keys are advertising, subscription and tutorial state and are "
                 "not reported.",
        "paths": ('*/com.cyberlink.youperfect/shared_prefs/YOUPERFECT_ANDROID_SETTING.xml',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
}

import os
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, \
    get_sqlite_db_records, logfunc
from scripts.artifacts.storagePathViews import canonical_path, unique_files

PHT_DB = 'databases/pht.sqlite'
MEDIA_DB = 'databases/external.db'
SETTINGS = 'shared_prefs/YOUPERFECT_ANDROID_SETTING.xml'
CACHE_DIR = '/cache/imagecache/'
SAVED_DIR = '/DCIM/YouCam Perfect/'
# year-month-day-hour-minute-second-milliseconds, observed once on one save.
SAVED_NAME = re.compile(r'^(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{3})\.', re.I)
IMAGE_TYPES = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
               'webp': 'image/webp', 'heic': 'image/heic', 'gif': 'image/gif',
               'bmp': 'image/bmp'}


def _files(context):
    """Matched files with the duplicate storage views of one file collapsed, directories out.

    An Android extraction carries the app's private directory under data/data, data/user/0
    and data_mirror, so reading the seeker's own list would open pht.sqlite three times and
    report every image three times. A pattern ending in * can also match a directory, which
    open() would raise on.
    """
    out = []
    for found in unique_files(context):
        if not os.path.isdir(found):
            out.append(found)
    return out


def _tenant(context, path):
    """The storage class and Android user of the container a file sits in, else ''.

    Used so a value read from one container is only ever joined to files from the same
    container, which keeps a second Android user's data out of the first user's rows.
    """
    key, _ = canonical_path(context.get_relative_path(path))
    parts = str(key).split('\x00')
    return parts[1] if len(parts) == 3 else ''


def _seconds(value):
    """Unix seconds to UTC. Blank for absent, unparsable and non-positive values."""
    if value in (None, ''):
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value)
    except (OverflowError, OSError, ValueError):
        return ''


def _ms(value):
    """Unix milliseconds to UTC. Blank for absent, unparsable and non-positive values."""
    if value in (None, ''):
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value / 1000)
    except (OverflowError, OSError, ValueError):
        return ''


def _positive(value):
    """The store writes -1 where it holds no value. Report those as blank."""
    if value in (None, ''):
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value
    return value if value >= 0 else ''


def _render(path):
    """A media reference for an image file, or blank when the extension is not an image."""
    name = os.path.basename(str(path))
    extension = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
    if extension not in IMAGE_TYPES:
        return ''
    return check_in_media(path, name, force_type=IMAGE_TYPES[extension],
                          force_extension=extension) or ''


def _media_store(context, files):
    """(tenant, media id) -> platform media row, read from any staged external.db."""
    out = {}
    query = '''SELECT _id, _data, _size, date_modified, width, height
               FROM files WHERE _id IS NOT NULL'''
    for found in files:
        path = str(found).replace('\\', '/')
        if not path.endswith(MEDIA_DB):
            continue
        tenant = _tenant(context, found)
        for row in get_sqlite_db_records(found, query):
            out[(tenant, str(row[0]))] = row
    return out


def _cache_files(context, files):
    """(tenant, file name) -> staged path, for the copies the app cached in its own folder."""
    out = {}
    for found in files:
        path = str(found).replace('\\', '/')
        if CACHE_DIR in path:
            out[(_tenant(context, found), os.path.basename(path))] = found
    return out


def _cached_copies(db_path):
    """image id -> [(level, recorded path)] from the store's own cache table."""
    out = {}
    for image_id, level, data_path in get_sqlite_db_records(
            db_path, 'SELECT ImageID, Level, DataPath FROM ImageCache'):
        out.setdefault(image_id, []).append((level or 0, data_path or ''))
    for entries in out.values():
        entries.sort(key=lambda entry: entry[0], reverse=True)
    return out


def _edit_steps(db_path):
    """image id -> how many develop-history entries the store holds for it."""
    out = {}
    for (image_id,) in get_sqlite_db_records(
            db_path, 'SELECT ImageID FROM ImageDevelopHistoryStep'):
        out[image_id] = out.get(image_id, 0) + 1
    return out


@artifact_processor
def youcam_perfect_images(context):
    files = _files(context)
    media_store = _media_store(context, files)
    cache_files = _cache_files(context, files)
    data_list = []
    sources = []
    query = '''SELECT _id, CaptureTime, FileID, FileType, FileWidth, FileHeight,
                      HistorySettingsID
               FROM Image ORDER BY _id'''
    for db_path in files:
        if not str(db_path).replace('\\', '/').endswith(PHT_DB):
            continue
        tenant = _tenant(context, db_path)
        cached = _cached_copies(db_path)
        steps = _edit_steps(db_path)
        records = get_sqlite_db_records(db_path, query)
        rows = 0
        for row_id, capture, media_id, file_type, width, height, history_id in records:
            media_key = (tenant, str(media_id) if media_id is not None else '')
            store_row = media_store.get(media_key)
            entries = cached.get(row_id, [])
            rendered = ''
            for _, data_path in entries:
                staged = cache_files.get(
                    (tenant, os.path.basename(str(data_path).replace('\\', '/'))))
                rendered = _render(staged) if staged else ''
                if rendered:
                    break
            data_list.append((
                _seconds(capture), rendered,
                media_id if media_id is not None else '',
                store_row[1] if store_row else '',
                store_row[2] if store_row else '',
                _seconds(store_row[3]) if store_row else '',
                file_type or '', _positive(width), _positive(height),
                len(entries), steps.get(row_id, 0), row_id,
                _positive(history_id), context.get_relative_path(db_path)))
            rows += 1
        if rows and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Source Modified', 'datetime'), ('Cached Copy', 'media'), 'Media Store Id',
        'Stored Path', 'Media Store Size', ('Media Store Modified', 'datetime'),
        'File Type', 'Width', 'Height', 'Cached Copies', 'Edit Steps', 'Record Id',
        'History Settings Id', 'Source File')
    return data_headers, data_list, '\n'.join(str(path) for path in sources)


@artifact_processor
def youcam_perfect_saved_photos(context):
    data_list = []
    sources = []
    for found in _files(context):
        path = str(found).replace('\\', '/')
        if SAVED_DIR not in path:
            continue
        name = os.path.basename(path)
        match = SAVED_NAME.match(name)
        stamp = ('{}-{}-{} {}:{}:{}.{}'.format(*match.groups()) if match else '')
        try:
            size = os.path.getsize(found)
            modified = _seconds(int(os.path.getmtime(found)))
        except OSError as error:
            logfunc(f'YouCam Perfect: could not read {name}: {error}')
            size, modified = '', ''
        data_list.append((_render(found), name, stamp, size, modified,
                          context.get_relative_path(found)))
        sources.append(found)

    data_headers = (
        ('Saved', 'media'), 'File Name', 'Name Wall Clock (as stored)', 'Size (bytes)',
        ('Modified', 'datetime'), 'Source File')
    return data_headers, data_list, '\n'.join(str(path) for path in sources)


@artifact_processor
def youcam_perfect_app_state(context):
    wanted = ('APP_FIRST_LAUNCH_TIME', 'InstallationId', 'KEY_PREVIOUS_COUNTRY_CODE',
              'LAST_PHOTO_PICKER_CHECK_TIME')
    data_list = []
    sources = []
    for found in _files(context):
        if not str(found).replace('\\', '/').endswith(SETTINGS):
            continue
        values = {}
        try:
            for element in ET.parse(found).getroot():
                name = element.get('name')
                if name in wanted:
                    values[name] = element.get('value', element.text or '')
        except (ET.ParseError, OSError) as error:
            logfunc(f'YouCam Perfect: could not read the settings file: {error}')
            continue
        if not values:
            continue
        data_list.append((
            _ms(values.get('APP_FIRST_LAUNCH_TIME')),
            values.get('InstallationId', ''),
            values.get('KEY_PREVIOUS_COUNTRY_CODE', ''),
            _ms(values.get('LAST_PHOTO_PICKER_CHECK_TIME')),
            context.get_relative_path(found)))
        sources.append(found)

    data_headers = (
        ('First Launch', 'datetime'), 'Installation Id', 'Country (as stored)',
        ('Last Photo Picker Check', 'datetime'), 'Source File')
    return data_headers, data_list, '\n'.join(str(path) for path in sources)
