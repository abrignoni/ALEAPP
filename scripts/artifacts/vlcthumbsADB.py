__artifacts_v2__ = {
    "get_vlcthumbsADB": {
        "name": "VLC Thumbnails (ADB)",
        "description": "Files under org.videolan.vlc/ef/medialib/thumbnails",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-08-23",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "VLC",
        "notes": "One row per file matched. File Modified is the modification time the tool reads"
                 " from the input for the file as a UTC time, to the whole second, such as from a"
                 " tar header or a zip entry's NTFS or extended timestamp field. When the tool "
                 "reads no UTC time, File Modified is blank and Modified (no zone, as stored) "
                 "shows the date and time the input holds, with no zone conversion. That is the "
                 "case for a FAT directory entry, an exFAT directory entry (its stored UTC offset"
                 " is not applied or shown here) and a zip entry with only its DOS date and time."
                 " Both columns are blank when the input holds neither, and a recorded time of 0 "
                 "is treated as no time. For a folder or single-file input File Modified is the "
                 "time the operating system reports for that file on the examiner's machine, "
                 "including any conversion it applied, and whatever copied the file there may "
                 "have set it. The staged copy's own time is not reported. This artifact lists no"
                 " sample_data, so no test image is recorded as exercising it.",
        "paths": ('*/org.videolan.vlc/ef/medialib/thumbnails/*.*',),
        "output_types": "standard",
        "artifact_icon": "photo",
    },
    "get_vlcthumbsADB_medialib": {
        "name": "VLC Media Lib (ADB)",
        "description": "Files under org.videolan.vlc/ef/medialib, outside its thumbnails folder",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-08-23",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "VLC",
        "notes": "One row per file matched outside the thumbnails folder; the file type is not "
                 "checked. Only paths under the app's medialib/thumbnails directory are left out."
                 " File Modified is the modification time the tool reads from the input for the "
                 "file as a UTC time, to the whole second, such as from a tar header or a zip "
                 "entry's NTFS or extended timestamp field. When the tool reads no UTC time, File"
                 " Modified is blank and Modified (no zone, as stored) shows the date and time "
                 "the input holds, with no zone conversion. That is the case for a FAT directory "
                 "entry, an exFAT directory entry (its stored UTC offset is not applied or shown "
                 "here) and a zip entry with only its DOS date and time. Both columns are blank "
                 "when the input holds neither, and a recorded time of 0 is treated as no time. "
                 "For a folder or single-file input File Modified is the time the operating "
                 "system reports for that file on the examiner's machine, including any "
                 "conversion it applied, and whatever copied the file there may have set it. The "
                 "staged copy's own time is not reported. This artifact lists no sample_data, so "
                 "no test image is recorded as exercising it.",
        "paths": ('*/org.videolan.vlc/ef/medialib/*.*',),
        "output_types": "standard",
        "artifact_icon": "photo",
    }
}

from pathlib import Path

from datetime import datetime, timedelta, timezone
from scripts.ilapfuncs import artifact_processor, check_in_media


def _is_thumbnail(context, path):
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    return '/org.videolan.vlc/ef/medialib/thumbnails/' in '/' + relative.lstrip('/')


def _utc(seconds):
    """Unix seconds as a UTC datetime in whole seconds, '' for none or a value datetime cannot hold."""
    if seconds is None:
        return ''
    try:
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds // 1)
    except OverflowError:
        return ''


def _file_times(seeker, path):
    """(UTC seconds, reading with no zone) the input records for a staged file.

    The staged copy's own time is not used: for a FAT, exFAT or DOS-only zip reading it is
    that reading placed in the examiner's time zone.
    """
    infos = getattr(seeker, 'file_infos', None) or {}
    windows = str(path).replace('/', '\\')
    bare = windows.removeprefix('\\\\?\\')
    info = next((infos[name] for name in (str(path), windows, bare, '\\\\?\\' + bare)
                 if name in infos), None)
    times = getattr(info, 'times', None)
    modified = getattr(times, 'modified', None)
    if isinstance(modified, (int, float)) and modified:
        return modified, ''
    # a reading with no zone comes before the older field, which is never read as its UTC time
    reading = getattr(times, 'modified_no_zone', None)
    if reading:
        return None, reading
    modified = getattr(info, 'modification_date', None)
    if isinstance(modified, (int, float)) and modified:
        return modified, ''
    return None, ''


@artifact_processor
def get_vlcthumbsADB(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not _is_thumbnail(context, file_found):
            continue
        filename = Path(file_found).name
        source_path = str(Path(file_found).parents[1])
        media = check_in_media(file_found, filename)
        modified, no_zone = _file_times(context.get_seeker(), file_found)
        data_list.append((_utc(modified), no_zone, media,
                          filename, context.get_relative_path(file_found)))

    data_headers = (('File Modified', 'datetime'), 'Modified (no zone, as stored)', ('Thumbnail', 'media'), 'Filename',
                    'Location')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_vlcthumbsADB_medialib(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if _is_thumbnail(context, file_found):
            continue
        filename = Path(file_found).name
        source_path = str(Path(file_found).parents[1])
        media = check_in_media(file_found, filename)
        modified, no_zone = _file_times(context.get_seeker(), file_found)
        data_list.append((_utc(modified), no_zone, media,
                          filename, context.get_relative_path(file_found)))

    data_headers = (('File Modified', 'datetime'), 'Modified (no zone, as stored)', ('File', 'media'), 'Filename',
                    'Location')
    return data_headers, data_list, context.get_relative_path(source_path)
