__artifacts_v2__ = {
    "inshot_projects": {
        "name": "InShot Projects",
        "description": "Video and photo projects InShot saved, with when each was created and how often it was opened",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "InShot",
        "sample_data": {
            "emu_a15_oss_v17": "InShot 2.222.1548 | 1 row",
        },
        "notes": "One row per .profile file under "
                 "com.camerasideas.instashot/files/inshot/.VideoProfile. Each is a JSON document "
                 "describing one editing project, written when the project is saved. "
                 "Created is the file's own CreateTime, Unix milliseconds, reported as UTC. The "
                 "file name carries a second time, as Video_<yyyyMMdd>_<HHmmssSSS>, and that one "
                 "is **device local**: on the tested device the name read 114256229 for a "
                 "CreateTime of 15:42:44 UTC, four hours ahead, so the two are reported side by "
                 "side rather than one being converted into the other. They also differ by a few "
                 "seconds, the name appearing to mark the save and CreateTime the creation. "
                 "Open Count is the file's openCount. Timeline Duration is MediaClipConfig.MCC_2 "
                 "in microseconds, mapped by loading a clip of known length: a 30 second clip "
                 "gave 30000000. Clips is how many entries its ConfigJson holds. "
                 "Cover is the still InShot renders for the project, kept under .ProfileCover and "
                 "named by a hash; it is surfaced as an image, so the project can be recognised "
                 "without opening anything. Label is the project's name and was empty on the "
                 "tested device, which is the app's default until a project is renamed. "
                 "Watermark is the hasWatermark flag as stored. "
                 "A row is evidence the app saved a project, not that anything was exported. The "
                 "media the project refers to is reported by the Project Clips artifact.",
        "paths": ('*/com.camerasideas.instashot/files/inshot/.VideoProfile/*.profile',
                  '*/com.camerasideas.instashot/files/inshot/.ProfileCover/*'),
        "output_types": "standard",
        "artifact_icon": "film",
    },
    "inshot_project_clips": {
        "name": "InShot Project Clips",
        "description": "Media files referenced by InShot projects, with the identifier the app stored for each",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "InShot",
        "sample_data": {
            "emu_a15_oss_v17": "InShot 2.222.1548 | 1 row",
        },
        "notes": "One row per clip inside a project's MediaClipConfig.ConfigJson, read from the "
                 "same .profile files as the Projects artifact. This is the part that names "
                 "files: a project records the full path of every piece of media placed on its "
                 "timeline, so it can evidence that a file was edited even when that file is no "
                 "longer on the device. "
                 "The keys inside a clip are obfuscated and were mapped by loading media of "
                 "known length and path, not from any published source. Media Path is MCI_1's "
                 "VFI_1 member, which held exactly the file that was loaded. Clip Duration is "
                 "MCI_3 in microseconds, which read 30000000 for a 30 second clip. "
                 "**File Id (as stored) is the clip's fileMd5 member and it is NOT the MD5 of "
                 "the file's bytes.** That was checked rather than assumed: for a file whose "
                 "bytes were under control the app stored 4f012347e900031ca5b19677c82ff8f2 while "
                 "the file's real MD5 was 64b22a793345b56e4f0c135a8a8e29e7. Hashing the path, "
                 "the size, the modification time, several leading and trailing byte ranges and "
                 "combinations of those reproduced none of it, so what the value covers was not "
                 "established and it is reported as stored. Do not try to match it against a "
                 "file hash; it is useful only as the app's own identifier for the clip. "
                 "A row records what the project referred to, not that the media was exported or "
                 "shared.",
        "paths": ('*/com.camerasideas.instashot/files/inshot/.VideoProfile/*.profile',),
        "output_types": "standard",
        "artifact_icon": "video",
    },
}

import json
import os
import re

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, logfunc
from scripts.artifacts.storagePathViews import unique_files

PROFILE_DIR = 'files/inshot/.VideoProfile/'
COVER_DIR = 'files/inshot/.ProfileCover/'
# Mapped from media of known path and length, not from published source.
CLIP_FILE_INFO, CLIP_PATH, CLIP_DURATION, CLIP_ID = 'MCI_1', 'VFI_1', 'MCI_3', 'fileMd5'
NAME_TIME = re.compile(r'_(\d{8})_(\d{6})(\d{3})?\.profile$')


def _files(context, test):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if test(str(f).replace('\\', '/'))]


def _profiles(context):
    return _files(context, lambda p: PROFILE_DIR in p and p.endswith('.profile'))


def _load(path):
    """The parsed project document, or None when it will not read."""
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            return json.loads(handle.read())
    except (OSError, ValueError) as error:
        logfunc(f'InShot: could not read {os.path.basename(path)}: {error}')
        return None


def _clips(document):
    """The clip entries of a project, or [] when the nested document will not read."""
    config = (document.get('MediaClipConfig') or {}).get('ConfigJson')
    if not config:
        return []
    try:
        parsed = json.loads(config)
    except (TypeError, ValueError):
        return []
    return parsed if isinstance(parsed, list) else []


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


def _name_time(path):
    """The local time in the file name, as stored, blank when the name does not carry one."""
    match = NAME_TIME.search(os.path.basename(path))
    if not match:
        return ''
    day, clock = match.group(1), match.group(2)
    return (f'{day[0:4]}-{day[4:6]}-{day[6:8]} {clock[0:2]}:{clock[2:4]}:{clock[4:6]}'
            + (f'.{match.group(3)}' if match.group(3) else ''))


@artifact_processor
def inshot_projects(context):
    covers = {os.path.basename(p): p for p in _files(context, lambda p: COVER_DIR in p)}
    data_list = []
    sources = []
    for path in _profiles(context):
        document = _load(path)
        if not isinstance(document, dict):
            continue
        cover_name = os.path.basename(str(document.get('Cover') or ''))
        cover_path = covers.get(cover_name)
        media = check_in_media(cover_path, cover_name) if cover_path else None
        data_list.append((
            _ms(document.get('CreateTime')),
            _name_time(path),
            os.path.basename(path),
            document.get('Label') or '',
            document.get('openCount'),
            (document.get('MediaClipConfig') or {}).get('MCC_2'),
            len(_clips(document)),
            str(document.get('hasWatermark')),
            media or '',
            context.get_relative_path(path)))
        if path not in sources:
            sources.append(path)

    data_list.sort(key=lambda row: row[0], reverse=True)
    data_headers = (
        ('Created', 'datetime'), 'File Name Time (device local, as stored)', 'Project File',
        'Label', 'Open Count', 'Timeline Duration (microseconds)', 'Clips',
        'Watermark (as stored)', ('Cover', 'media'), 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def inshot_project_clips(context):
    data_list = []
    sources = []
    for path in _profiles(context):
        document = _load(path)
        if not isinstance(document, dict):
            continue
        seen = False
        for position, clip in enumerate(_clips(document)):
            if not isinstance(clip, dict):
                continue
            info = clip.get(CLIP_FILE_INFO)
            if not isinstance(info, dict):
                continue
            seen = True
            data_list.append((
                _ms(document.get('CreateTime')),
                os.path.basename(path),
                position,
                info.get(CLIP_PATH) or '',
                clip.get(CLIP_DURATION),
                info.get(CLIP_ID) or '',
                context.get_relative_path(path)))
        if seen and path not in sources:
            sources.append(path)

    data_list.sort(key=lambda row: (row[0], row[2]), reverse=True)
    data_headers = (
        ('Project Created', 'datetime'), 'Project File', 'Position', 'Media Path',
        'Clip Duration (microseconds)', 'File Id (as stored, not a file hash)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
