# pylint: disable=W0613
__artifacts_v2__ = {
    "get_recentactivity": {
        "name": "Recent Activity",
        "description": "Recent tasks, snapshots and images from system_ce/<user>",
        "author": "",
        "creation_date": "2020-02-25",
        "last_update_date": "2020-02-25",
        "requirements": "none",
        "category": "Recent Activity",
        "notes": "",
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
        },
    }
}

import datetime
import glob
import json
import os
import xml.etree.ElementTree as ET

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


@artifact_processor
def get_recentactivity(files_found, report_folder, seeker, wrap_text):
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
            children = list(root)
            if not children:
                continue
            task_id = root.attrib.get('task_id')
            task_attrs = json.dumps(root.attrib)
            snapshot = _media(folder, 'snapshots', f'{task_id}.jpg') if task_id else ''
            icon = root.attrib.get('task_description_icon_filename')
            if icon:
                recent_image = _media(folder, 'recent_images', os.path.basename(icon))
            else:
                recent_image = ''
                if task_id:
                    matches = glob.glob(os.path.join(folder, 'recent_images', task_id, '*.*'))
                    if matches:
                        recent_image = check_in_media(matches[0], os.path.basename(matches[0])) or ''
            for child in root:
                data_list.append((
                    uid, task_id, root.attrib.get('effective_uid'), root.attrib.get('affinity'),
                    root.attrib.get('real_activity'),
                    _ms_to_utc(root.attrib.get('first_active_time')),
                    _ms_to_utc(root.attrib.get('last_active_time')),
                    _ms_to_utc(root.attrib.get('last_time_moved')),
                    root.attrib.get('calling_package'), root.attrib.get('user_id'),
                    child.attrib.get('action'), child.attrib.get('component'),
                    snapshot, recent_image, task_attrs, json.dumps(child.attrib)))

    data_headers = ('CE Profile', 'Task ID', 'Effective UID', 'Affinity', 'Real Activity',
                    ('First Active Time', 'datetime'), ('Last Active Time', 'datetime'),
                    ('Last Time Moved', 'datetime'), 'Calling Package', 'User ID', 'Action',
                    'Component', ('Snapshot Image', 'media'), ('Recent Image', 'media'),
                    'Task Attributes', 'Activity Attributes')
    return data_headers, data_list, source_path
