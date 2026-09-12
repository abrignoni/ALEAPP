__artifacts_v2__ = {
    "vivavideo_projects": {
        "name": "VivaVideo Projects",
        "description": "Editing projects VivaVideo saved, with the cover still where one was recorded",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "VivaVideo",
        "sample_data": {
            "emu_a15_oss2_v1": "VivaVideo 9.38.0 | 1 rows",
        },
        "notes": "One row per row of the Project table in "
                 "com.quvideo.xiaoying/databases/ve_sdk.db. Project File is the app's own url "
                 "column, which names the .prj container itself and not its folder; the "
                 "folder is the parent, named Project_<yyyyMMdd>_<HHmmss>. Clips is the "
                 "stored clip_count and Duration (ms) the stored duration; on the tested "
                 "device a project holding one 15 second source clip read 1 and 15000.\n"
                 "Exported Video is the export_url column. It was empty on the tested project, and that "
                 "agrees with what the project folder showed: two export attempts were "
                 "started and both were refused by the paid tier, so nothing was produced. "
                 "An empty value is therefore not evidence that no export was attempted, "
                 "only that none completed. No export completed on the tested device, so "
                 "what the app writes into this column on a successful one was not "
                 "observed.\n"
                 "Created and Modified are NOT UTC. The app writes them as readable local "
                 "wall-clock strings, and they are reported here as plain text so nothing "
                 "downstream applies a zone conversion to a value that never carried a zone. "
                 "That was measured against the device clock rather than assumed: a project made "
                 "at 22:36 in the device's America/New_York zone stored 2026-09-06 22:36:24, "
                 "while file names in the same project directory carry true UTC milliseconds "
                 "(1788748675713 is 02:37:55 UTC, which is 22:37:55 in that zone). The two "
                 "conventions sit side by side, so read each from where it came. On the "
                 "tested extraction the zone needed to read the local columns was itself "
                 "recoverable from the evidence, as persist.sys.timezone in "
                 "data/property/persistent_properties.\n"
                 "Cover is the still the app recorded as the project's cover. It is resolved from the "
                 "coverURL column, falling back to thumbnail, rather than by guessing at file "
                 "names, and it is rendered inline so a project can be recognised without "
                 "opening anything. The sibling Clip and ClipRef tables in the same database "
                 "were empty "
                 "on the tested device, so this store does not record which media a project "
                 "used; that is what the Project Media artifact reads.\n"
                 "Modified is not evidence that anything was changed. Opening a project advances "
                 "it on its own, which was tested rather than assumed: the stored value moved "
                 "from 2026-09-06 22:44:43 to 00:14:06 and again to 00:16:35 across two opens in "
                 "which no edit was made and nothing was exported. Read it as the last time the "
                 "project was opened or later.\n"
                 "The row is not removed when the media it refers to is deleted. Tested by "
                 "removing the one source clip from shared storage, reopening the app and opening "
                 "the project: the row survived with Project Name, Clips, Duration (ms), Width "
                 "and Height unchanged, and only Modified moved. So a project row can outlive the "
                 "media it was built from.\n"
                 "A row is evidence the app "
                 "saved a project, not that anything was exported.",
        "paths": ('*/com.quvideo.xiaoying/databases/ve_sdk.db*',
                  '*/com.quvideo.xiaoying/files/XiaoYing/.public/.projects/*'),
        "output_types": "standard",
        "artifact_icon": "video",
    },
    "vivavideo_project_media": {
        "name": "VivaVideo Project Media",
        "description": "Media paths recorded inside a VivaVideo project container",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "VivaVideo",
        "sample_data": {
            "emu_a15_oss2_v1": "VivaVideo 9.38.0 | 2 rows",
        },
        "notes": "One row per distinct media reference inside a project's .prj file. This is the "
                 "part that names files: a project records the full path of the media placed on "
                 "its timeline. That path survives the file being deleted, which was tested "
                 "rather than assumed: the one source clip was removed from shared storage, the "
                 "app was reopened and the project opened, and the app warned that the original "
                 "was gone and the project could no longer be edited. It rewrote the .prj at "
                 "that point and kept the recorded path under both elements. So a row can tie a "
                 "file to an edit after the file itself is gone, and a path that no longer "
                 "resolves is not evidence the file was never there.\n"
                 "The .prj is NOT XML despite the extension. It opens with the four byte magic "
                 "KPVQ followed by a binary header, and an XML document begins later in the "
                 "file; the reader locates the XML declaration and parses from there, and skips "
                 "a file whose magic does not match. The XML root is xyprj and each reference is "
                 "a file element with a path attribute.\n"
                 "**A path attribute is not always a path.** Its parent carries "
                 "is_template_src, and when that reads 1 the value is a numeric template "
                 "identifier rather than a filesystem path. On the tested project all three "
                 "values marked 1 were numeric and all four marked 0 were real paths, so the "
                 "flag is used to filter rather than guessing from the shape of the value. "
                 "Entries marked 1 are not reported.\n"
                 "Kind is derived from where the path points: a path inside the app's own "
                 "storage under Android/data/com.quvideo.xiaoying is reported as an app asset, "
                 "which on the tested project was the app's own watermark image, and every other "
                 "path is reported as user media. The label describes the path location, not who "
                 "placed the file there. The same path can appear more "
                 "than once in one project, under both a normal_source and a media_source "
                 "element, and is reported once. A row records what the project referred to, not "
                 "that the media was exported or shared.",
        "paths": ('*/com.quvideo.xiaoying/files/XiaoYing/.public/.projects/*',),
        "output_types": "standard",
        "artifact_icon": "photo",
    },
    "vivavideo_export_attempts": {
        "name": "VivaVideo Export Attempts",
        "description": "Cover stills VivaVideo wrote when an export was started, not evidence one finished",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "VivaVideo",
        "sample_data": {
            "emu_a15_oss2_v1": "VivaVideo 9.38.0 | 2 rows",
        },
        "notes": "One row per exportCover file in a project directory. The app names these "
                 "<project>_exportCover_<epoch>.jpg, and that epoch is reported as Unix "
                 "milliseconds in UTC; the comparison against the device clock is the one "
                 "described with its values in the VivaVideo Projects notes.\n"
                 "**An exportCover file is evidence an export was started, not that one "
                 "finished.** That was measured rather than assumed: on the tested device two "
                 "exportCover files were written for one project, and both export attempts were "
                 "refused by the app's paid tier, so no video was produced at all. Do not read a "
                 "row as a completed export, and do not read the count as a number of output "
                 "videos.\n"
                 "The still itself is rendered inline, so the frame the export would have "
                 "started from is visible. A project directory also holds a tempCover file, "
                 "which is not reported here. On the tested project its epoch was 4 seconds "
                 "after the project's recorded create_time and 88 seconds before the first of "
                 "the two export attempts, so it is not written by an export; what does write "
                 "it was not established beyond that timing. The Project table separately records "
                 "export_cover_path, which named the most recent of the two attempts on the "
                 "tested device, so that column alone would under-report how many were made.",
        "paths": ('*/com.quvideo.xiaoying/files/XiaoYing/.public/.projects/*',),
        "output_types": "standard",
        "artifact_icon": "upload",
    },
}

import os
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, \
    get_sqlite_db_records, logfunc
from scripts.artifacts.storagePathViews import unique_files

PRJ_MAGIC = b'KPVQ'
XML_START = b'<?xml'
APP_STORAGE = '/Android/data/com.quvideo.xiaoying/'
EXPORT_COVER = re.compile(r'_exportCover_(\d{10,16})\.jpg$', re.IGNORECASE)
DB_SUFFIX = 'databases/ve_sdk.db'


def _paths(context):
    """Every matched file, with the duplicate storage views of one file collapsed.

    An Android extraction carries the app's private directory under data/data,
    data/user/0 and data_mirror, so reading the list the seeker returns would open
    ve_sdk.db three times and report each project three times.
    """
    return [str(f).replace('\\', '/') for f in unique_files(context)]


def _project_dir(path):
    """The Project_<stamp> directory a file sits in, or '' when it is not under one."""
    parts = path.split('/')
    for i, seg in enumerate(parts):
        if seg.startswith('Project_'):
            return '/'.join(parts[:i + 1])
    return ''


def _export_covers(context):
    """project directory -> [(epoch, path)] for every exportCover file in it."""
    out = {}
    for path in _paths(context):
        if os.path.isdir(path):
            continue
        match = EXPORT_COVER.search(os.path.basename(path))
        if not match:
            continue
        prj = _project_dir(path)
        if not prj:
            continue
        out.setdefault(prj, []).append((match.group(1), path))
    return out


def _prj_root(path):
    """Parse the XML embedded in a .prj container. None when it is not one or will not parse."""
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except OSError as error:
        logfunc(f'VivaVideo: could not read {path}: {error}')
        return None
    if not raw.startswith(PRJ_MAGIC):
        logfunc(f'VivaVideo: {os.path.basename(path)} does not carry the KPVQ magic, skipped')
        return None
    start = raw.find(XML_START)
    if start < 0:
        logfunc(f'VivaVideo: {os.path.basename(path)} holds no XML declaration, skipped')
        return None
    try:
        return ET.fromstring(raw[start:].decode('utf-8', 'replace'))
    except ET.ParseError as error:
        logfunc(f'VivaVideo: {os.path.basename(path)} XML did not parse: {error}')
        return None


def _staged_index(context):
    """(project folder, file name) -> staged path, so a recorded device path can be resolved."""
    index = {}
    for path in _paths(context):
        if os.path.isdir(path):
            continue
        prj = _project_dir(path)
        if prj:
            index[(os.path.basename(prj), os.path.basename(path))] = path
    return index


def _resolve(index, recorded):
    """Resolve a path the app recorded to the file as staged, by folder and name."""
    if not recorded:
        return ''
    parts = recorded.replace('\\', '/').split('/')
    if len(parts) < 2:
        return ''
    return index.get((parts[-2], parts[-1]), '')


@artifact_processor
def vivavideo_projects(context):
    index = _staged_index(context)
    query = '''SELECT create_time, modify_time, prj_name, clip_count, duration,
                      streamWidth, streamHeight, url, export_url, coverURL, thumbnail
               FROM Project ORDER BY create_time DESC'''
    data_list = []
    sources = []
    for db_path in [x for x in _paths(context)
                    if x.endswith(DB_SUFFIX) and not os.path.isdir(x)]:
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            still = _resolve(index, r[9]) or _resolve(index, r[10])
            cover = ''
            if still:
                cover = check_in_media(still, os.path.basename(still),
                                       force_type='image/jpeg', force_extension='jpg') or ''
            data_list.append((r[0] or '', r[1] or '', r[2] or '', cover, r[3], r[4],
                              r[5], r[6], r[7] or '', r[8] or '',
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Created (Device Local)', 'Modified (Device Local)', 'Project Name',
        ('Cover', 'media'), 'Clips', 'Duration (ms)', 'Width', 'Height',
        'Project File', 'Exported Video', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def vivavideo_project_media(context):
    data_list = []
    sources = []
    for path in sorted(p for p in _paths(context)
                       if p.lower().endswith('.prj') and not os.path.isdir(p)):
        root = _prj_root(path)
        if root is None:
            continue
        parents = {child: parent for parent in root.iter() for child in parent}
        seen = set()
        for element in root.iter('file'):
            value = element.get('path', '')
            if not value:
                continue
            parent = parents.get(element)
            # The parent's is_template_src flag says whether this is a path at all.
            if parent is not None and parent.get('is_template_src') == '1':
                continue
            if value in seen:
                continue
            seen.add(value)
            kind = 'App asset' if APP_STORAGE in value else 'User media'
            data_list.append((os.path.basename(_project_dir(path)) or '', kind, value,
                              parent.tag if parent is not None else '',
                              context.get_relative_path(path)))
        if seen and path not in sources:
            sources.append(path)

    data_headers = ('Project', 'Kind', 'Media Path', 'Referenced By', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def vivavideo_export_attempts(context):
    data_list = []
    sources = []
    for prj, exports in sorted(_export_covers(context).items()):
        for epoch, path in sorted(exports):
            still = check_in_media(path, os.path.basename(path),
                                   force_type='image/jpeg', force_extension='jpg') or ''
            try:
                when = convert_unix_ts_to_utc(int(epoch) / 1000)
            except (ValueError, OverflowError, OSError):
                when = ''
            data_list.append((when, os.path.basename(prj), still,
                              context.get_relative_path(path)))
            if path not in sources:
                sources.append(path)

    data_headers = (('Export Started', 'datetime'), 'Project', ('Still', 'media'), 'Source File')
    return data_headers, data_list, '\n'.join(sources)
