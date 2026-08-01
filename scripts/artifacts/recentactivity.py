# pylint: disable=no-member
__artifacts_v2__ = {
    "get_recentactivity": {
        "name": "Recent Activity",
        "description": "Recent task records correlated with task snapshots, low-resolution previews and Android's TaskSnapshot protobuf metadata.",
        "author": "Alexis Brignoni",
        "creation_date": "2020-02-25",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "Recent Activity",
        "notes": (
            "Recent Tasks is a mutable system list, not a complete application-use history. "
            "A task snapshot may be a real screen capture or a theme-generated substitute; "
            "consult Is Real Snapshot before interpreting the image. Snapshot files are "
            "credential-encrypted and may be removed when a task leaves recents. Android sources: "
            "https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/"
            "services/core/java/com/android/server/wm/TaskPersister.java and "
            "https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/"
            "proto/src/windowmanager.proto"
        ),
        "paths": ('*/system_ce/*',
                  '*/system_ce/*/recent_tasks/*',
                  '*/system_ce/*/snapshots/*',
                  '*/system_ce/*/recent_images/*',
                  '*/system_ce/*/recent_images/*/*'),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "anne_a15": "Android 15 | 35 rows",
            "galaxys10_a10": "Android 10 | 38 rows",
            "hc_pixel8pro_a16": "Android 16 | 4 rows",
            "kevin_pocox7_a15": "Android 15 | 21 rows",
            "pixel7a_a14": "Android 14 | 5 rows",
            "samsunga53_a14": "Android 14 | 37 rows",
            "samsungs20_a13": "Android 13 | 36 rows",
            "sharon_a14": "Android 14 | 13 rows",
            "russell_pixel6a_a13": "Android 13 | 15 rows",
            "userb2_a13": "Android 13 | 4 rows",
        },
    }
}

import datetime
import glob
import json
import os
import xml.etree.ElementTree as ET

from google.protobuf.message import DecodeError
from scripts.artifacts.recentactivity_pb import task_snapshot_pb2
from scripts.ilapfuncs import artifact_processor, check_in_media, checkabx, abxread, logfunc


def _ms_to_utc(value):
    if value in (None, '', 0, '0'):
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _parse_tree(filename):
    try:
        if checkabx(filename):
            return abxread(filename, False)
        return ET.parse(filename)
    except (ET.ParseError, OSError, ValueError):
        logfunc('Recent Activity: could not parse ' + filename)
        return None


def _media(folder, *parts):
    path = os.path.join(folder, *parts)
    if os.path.isfile(path):
        return check_in_media(path, os.path.basename(path)) or ''
    return ''


def _snapshot_metadata(folder, task_id):
    """Return TaskSnapshot protobuf details and linked high/low resolution images."""
    empty = ('',) * 15
    if not task_id:
        return empty

    snapshot_folder = os.path.join(folder, 'snapshots')
    high_image = _media(snapshot_folder, f'{task_id}.jpg')
    low_image = _media(snapshot_folder, f'{task_id}_reduced.jpg')
    proto_path = os.path.join(snapshot_folder, f'{task_id}.proto')
    if not os.path.isfile(proto_path):
        return (high_image, low_image) + ('',) * 13

    snapshot = task_snapshot_pb2.TaskSnapshotProto()
    try:
        with open(proto_path, 'rb') as proto_file:
            snapshot.ParseFromString(proto_file.read())
    except (OSError, DecodeError) as error:
        logfunc(f'Recent Activity: could not parse snapshot metadata {proto_path}: {error}')
        return (high_image, low_image) + ('',) * 13

    orientation = {0: 'Undefined', 1: 'Portrait', 2: 'Landscape', 3: 'Square'}.get(
        snapshot.orientation, str(snapshot.orientation))
    rotation = {0: '0°', 1: '90°', 2: '180°', 3: '270°'}.get(
        snapshot.rotation, str(snapshot.rotation))
    return (
        high_image,
        low_image,
        snapshot.id,
        _ms_to_utc(snapshot.id),
        snapshot.top_activity_component,
        'Yes' if snapshot.is_real_snapshot else 'No',
        orientation,
        rotation,
        f'{snapshot.task_width} × {snapshot.task_height}',
        snapshot.windowing_mode,
        'Yes' if snapshot.is_translucent else 'No',
        f'{snapshot.inset_left}, {snapshot.inset_top}, {snapshot.inset_right}, {snapshot.inset_bottom}',
        (f'{snapshot.letterbox_inset_left}, {snapshot.letterbox_inset_top}, '
         f'{snapshot.letterbox_inset_right}, {snapshot.letterbox_inset_bottom}'),
        snapshot.appearance,
        snapshot.ui_mode,
    )


@artifact_processor
def get_recentactivity(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        norm = file_found.replace('\\', '/')
        parts = norm.split('/')
        # only the system_ce/<numeric-uid> profile directories
        if len(parts) < 2 or parts[-2] != 'system_ce' or not parts[-1].isdigit() or '/mirror/' in norm:
            continue
        uid = parts[-1]
        folder = file_found
        source_path = folder
        for filename in glob.iglob(os.path.join(folder, 'recent_tasks', '**'), recursive=True):
            if not os.path.isfile(filename):
                continue
            tree = _parse_tree(filename)
            if tree is None:
                continue
            root = tree.getroot()
            children = list(root) or [None]
            task_id = root.attrib.get('task_id')
            if not task_id:
                task_id = os.path.basename(filename).split('_', 1)[0]
            task_attrs = json.dumps(root.attrib)
            snapshot_details = _snapshot_metadata(folder, task_id)
            icon = root.attrib.get('task_description_icon_filename')
            if icon:
                recent_image = _media(folder, 'recent_images', os.path.basename(icon))
            else:
                recent_image = ''
                if task_id:
                    matches = glob.glob(os.path.join(folder, 'recent_images', task_id, '*.*'))
                    if matches:
                        recent_image = check_in_media(matches[0], os.path.basename(matches[0])) or ''
            for child in children:
                child_attrs = child.attrib if child is not None else {}
                data_list.append((
                    uid, task_id, root.attrib.get('effective_uid'), root.attrib.get('affinity'),
                    root.attrib.get('real_activity'),
                    _ms_to_utc(root.attrib.get('first_active_time')),
                    _ms_to_utc(root.attrib.get('last_active_time')),
                    _ms_to_utc(root.attrib.get('last_time_moved')),
                    root.attrib.get('calling_package'), root.attrib.get('user_id'),
                    child_attrs.get('action'), child_attrs.get('component'),
                    *snapshot_details, recent_image, task_attrs, json.dumps(child_attrs)))

    data_headers = ('CE Profile', 'Task ID', 'Effective UID', 'Affinity', 'Real Activity',
                    ('First Active Time', 'datetime'), ('Last Active Time', 'datetime'),
                    ('Last Time Moved', 'datetime'), 'Calling Package', 'User ID', 'Action',
                    'Component', ('Snapshot Image', 'media'),
                    ('Low Resolution Snapshot', 'media'), 'Snapshot ID',
                    ('Snapshot Capture Time', 'datetime'), 'Snapshot Top Activity',
                    'Is Real Snapshot', 'Snapshot Orientation', 'Snapshot Rotation',
                    'Original Task Size', 'Windowing Mode', 'Is Translucent',
                    'Content Insets (L, T, R, B)', 'Letterbox Insets (L, T, R, B)',
                    'Appearance', 'UI Mode', ('Recent Image', 'media'),
                    'Task Attributes', 'Activity Attributes')
    return data_headers, data_list, source_path
