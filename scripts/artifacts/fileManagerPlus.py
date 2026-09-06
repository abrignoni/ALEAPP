__artifacts_v2__ = {
    "filemanagerplus_thumbnails": {
        "name": "Cx File Explorer and File Manager+ Cached Thumbnails",
        "description": "Thumbnail images these file managers rendered while browsing, recovered from their cache",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "File Manager",
        "sample_data": {
            "emu_a15_oss_v16": "Cx File Explorer 2.7.8 and File Manager+ 3.8.3 | 29 rows",
        },
        "notes": "One row per cached thumbnail under "
                 "Android/data/<package>/cache/thumbnail336x336/ on shared storage. Cx File "
                 "Explorer and File Manager+ are the same developer's apps and use an identical "
                 "layout, so both are read here and the App column is taken from the package "
                 "segment of the path, never from the file name. That matters: the two also ship "
                 "an identically named database, so a glob keyed on a file name rather than the "
                 "package would attribute one app's activity to the other. "
                 "The thumbnail is a JPEG the app rendered while displaying a folder, so its "
                 "presence is evidence the app displayed that item. "
                 "**Whether it outlives the file it was made from is not guaranteed, and both "
                 "outcomes were measured on the tested device.** A thumbnail whose source no "
                 "longer exists anywhere on shared storage was found still cached and still "
                 "rendering, which is the case that makes this cache worth reading. Against "
                 "that, deleting a source image and then running the app removed exactly that "
                 "file's thumbnail, taking the cache from five entries to four, so the app "
                 "does prune. The difference appears to turn on whether the app has since "
                 "revisited the folder, but that mechanism was not established here and is not "
                 "claimed. "
                 "What follows for an examiner is the useful part: a thumbnail present is "
                 "evidence, while an absent thumbnail supports no conclusion either way, since it "
                 "may never have been made or may have been pruned since. "
                 "Kind is taken from the containing directory, which the app splits into "
                 "dir_image, dir_video and dir_audio; on the tested image all rows were "
                 "dir_image, and the video and audio directories existed and were empty, which "
                 "is recorded rather than hidden. "
                 "The cache file name is a set of hashes the app derives from the item, so it "
                 "does not reverse to a path and no path is claimed here. The thumbnail's own "
                 "content is what identifies it. File times are not reported: the framework "
                 "restores only modification time when staging, so a cache file's timestamps "
                 "describe the extraction rather than the browsing. "
                 "The app's bookmarks table is not parsed here because every row on the tested "
                 "image was a shipped default (DCIM, Movies and Music, all written at install "
                 "time), and its last_visited preference held empty lists throughout, so neither "
                 "carried user activity on this image.",
        "paths": ('*/Android/data/com.cxinventor.file.explorer/cache/thumbnail*/*/*',
                  '*/Android/data/com.alphainventor.filemanager/cache/thumbnail*/*/*'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "filemanagerplus_scanned_folders": {
        "name": "Cx File Explorer and File Manager+ Scanned Folders",
        "description": "Folders these file managers recorded scanning, with the time recorded against each",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "File Manager",
        "sample_data": {
            "emu_a15_oss_v16": "Cx File Explorer 2.7.8 and File Manager+ 3.8.3 | 170 rows",
        },
        "notes": "One row per record in Android/data/<package>/files/scanfile.full or "
                 "scanfile.fast on shared storage. The file opens with a short header line, and each line after it is one "
                 "record whose fields are separated by NUL bytes rather than by whitespace: a "
                 "percent-encoded absolute path, a Unix millisecond time, two boolean flags, and "
                 "and optionally a fifth field describing one file in that folder. "
                 "The path is decoded here and the time is reported as UTC; the two flags are "
                 "reported as stored because nothing says what they mean. Flag 2 read false on every "
                 "one of the 170 records on the tested image while Flag 1 varied, so Flag 2 is a "
                 "uniform column here rather than an empty one, and it is kept because a device "
                 "whose scans differ would be the case worth seeing. "
                 "That fifth field is KIND/COUNT/SIZE/MODIFIED/NAME, and the mapping is proven "
                 "rather than assumed: files whose size was known appeared with their exact "
                 "size, a 650 byte document and a 31,204 byte one, and the fourth member "
                 "converts to that file's modification time. It is split into Content Kind, "
                 "Item Count, File Name, File Size and File Modified; a name containing a slash "
                 "is kept whole, and a field not matching the shape is passed through as the "
                 "kind alone rather than being guessed at. "
                 "This is the part worth an examiner's attention: the record names a file that "
                 "was in that folder, with its size and modification time, so it can evidence a "
                 "file that is no longer present. "
                 "The format was read from the file itself, not from any published source, so a "
                 "record that does not match that shape is skipped rather than guessed at, and "
                 "the Records Skipped figure in the log says how many. "
                 "What a row means is bounded: the app wrote the folder into its scan index with "
                 "that time against it. It is not proof a person opened that folder, because the "
                 "app indexes storage on its own. The two scan files differ, but barely: counted "
                 "on the tested image, scanfile.fast held 42 records and scanfile.full 43, in both "
                 "apps, so the fast sweep is not a small subset of the full one. "
                 "Scan File column says which one a row came from. App is taken from the package "
                 "segment of the path for the same reason as the thumbnail artifact.",
        "paths": ('*/Android/data/com.cxinventor.file.explorer/files/scanfile.*',
                  '*/Android/data/com.alphainventor.filemanager/files/scanfile.*'),
        "output_types": "standard",
        "artifact_icon": "folder",
    },
}

import os
import urllib.parse

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, logfunc
from scripts.artifacts.storagePathViews import unique_files

APPS = {
    'com.cxinventor.file.explorer': 'Cx File Explorer',
    'com.alphainventor.filemanager': 'File Manager+',
}
KINDS = {'dir_image': 'Image', 'dir_video': 'Video', 'dir_audio': 'Audio'}


def _app_of(path):
    """The app name from the package segment of the path, blank when no package matches.

    Keyed on a whole path segment so a package name appearing as a substring elsewhere
    cannot claim the row; the two apps share a database file name, so the segment is the
    only safe anchor.
    """
    segments = path.split('/')
    for package, name in APPS.items():
        if package in segments:
            return name
    return ''


def _files(context, test):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if test(str(f).replace('\\', '/'))]



def _summary_row(raw):
    """(kind, count, file name, size, modified ms) from a scan record's fifth field.

    The field is KIND/COUNT/SIZE/MTIME/NAME, mapped from files whose size was known:
    a 650 byte document and a 31,204 byte one each appeared with their exact size, and
    the fourth part converts to that file's modification time. A name may itself contain
    a slash, so the name is everything from the fifth part on. Anything not matching the
    shape is returned as a kind alone, so nothing is invented.
    """
    if not raw:
        return '', '', '', '', ''
    parts = raw.split('/')
    if len(parts) >= 5 and parts[1].isdigit() and parts[2].isdigit() and parts[3].isdigit():
        stamp = int(parts[3])
        modified = ''
        if stamp > 0:
            try:
                modified = convert_unix_ts_to_utc(stamp // 1000)
            except (OverflowError, OSError, ValueError):
                modified = ''
        return parts[0], parts[1], '/'.join(parts[4:]), parts[2], modified
    return raw, '', '', '', ''


@artifact_processor
def filemanagerplus_thumbnails(context):
    data_list = []
    sources = []
    for path in _files(context, lambda p: '/cache/thumbnail' in p and _app_of(p)):
        if os.path.isdir(path):
            continue
        name = os.path.basename(path)
        kind = KINDS.get(os.path.basename(os.path.dirname(path)), '')
        media = check_in_media(path, name)
        data_list.append((
            _app_of(path), kind, name, media or '', context.get_relative_path(path)))
        if path not in sources:
            sources.append(path)

    data_headers = ('App', 'Kind', 'Cache Name', ('Thumbnail', 'media'), 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def filemanagerplus_scanned_folders(context):
    data_list = []
    sources = []
    skipped = 0
    for path in _files(context, lambda p: '/files/scanfile.' in p and _app_of(p)):
        if os.path.isdir(path):
            continue
        try:
            with open(path, 'rb') as handle:
                raw = handle.read()
        except OSError as error:
            logfunc(f'File Manager: could not read {os.path.basename(path)}: {error}')
            continue
        seen = False
        # The first line is a short header; each line after it is one record whose
        # fields are separated by NUL, not by whitespace.
        for record in raw.split(b'\n')[1:]:
            if not record.strip(b'\x00'):
                continue
            parts = record.split(b'\x00')
            if len(parts) < 4 or not parts[1].isdigit():
                skipped += 1
                continue
            seen = True
            stamp = int(parts[1])
            data_list.append((
                convert_unix_ts_to_utc(stamp // 1000) if stamp > 0 else '',
                _app_of(path),
                urllib.parse.unquote(parts[0].decode('utf-8', 'replace')),
                *_summary_row(parts[4].decode('utf-8', 'replace') if len(parts) > 4 else ''),
                parts[2].decode('utf-8', 'replace'),
                parts[3].decode('utf-8', 'replace'),
                os.path.basename(path),
                context.get_relative_path(path)))
        if seen and path not in sources:
            sources.append(path)

    if skipped:
        logfunc(f'File Manager: {skipped} scan record(s) did not match the expected shape')
    data_list.sort(key=lambda row: row[0], reverse=True)
    data_headers = (
        ('Recorded', 'datetime'), 'App', 'Folder', 'Content Kind', 'Item Count',
        'File Name', 'File Size (bytes)', ('File Modified', 'datetime'),
        'Flag 1 (as stored)', 'Flag 2 (as stored)', 'Scan File', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
