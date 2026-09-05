__artifacts_v2__ = {
    "nova_layout": {
        "name": "Nova Launcher Layout",
        "description": "Items Nova Launcher places on the home screen, the dock and drawer folders",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Nova Launcher",
        "sample_data": {
            "emu_a15_oss_v10": "Nova Launcher 8.9.0 | 19 rows",
        },
        "notes": "One row per item in the favorites table of "
                 "com.teslacoilsw.launcher/databases/nova.db, which holds what the launcher draws "
                 "on the home screen and in the dock, and also the items sitting inside its "
                 "drawer folders. Modified is Unix milliseconds and is "
                 "reported as UTC. It is blank on the items Nova copied out of the previous "
                 "launcher when it was first set as the default, and carries a time on items "
                 "written later, so a blank Modified marks an imported item and a filled one marks "
                 "an item Nova itself wrote. That split was produced on the tested device: nine "
                 "rows imported at setup carried 0 and the rest carried the setup time. Location "
                 "resolves the container column, and only the two values seen on the tested device "
                 "are named. Those two are proven by known data rather than by any published "
                 "source: the five items with container -101 were the icons sitting in the dock "
                 "and the items with container -100 were on the home screen itself. Any other "
                 "container is reported as stored, because Nova is closed source and its remaining "
                 "values were not exercised here. The tested image also held items under -202, "
                 "-207 and -208, and those were the members of the Entertainment, Social and "
                 "Travel drawer folders, whose drawer_groups rows are 2, 7 and 8. Read that "
                 "relationship off the Nova Launcher Drawer Groups artifact, which resolves folder "
                 "membership through the join the database records rather than through arithmetic "
                 "on the container number. Item Type is reported as stored for the same "
                 "reason; every item on the tested device was 0. Component is taken out of the "
                 "stored intent and is the package and activity the item launches, which is what "
                 "identifies the app when the title has been renamed by the user. One internal row "
                 "with no container and no title is skipped. Span X and Span Y were 1.0 on every "
                 "row of the tested image because every item there was a single icon; a widget "
                 "occupies more than one cell and is what makes those two columns vary, so they "
                 "are kept rather than dropped. A row is evidence the item was in the launcher's "
                 "layout, not that it was ever tapped.",
        "paths": ('*/com.teslacoilsw.launcher/databases/nova.db*',),
        "output_types": "standard",
        "artifact_icon": "grid",
    },
    "nova_drawer_groups": {
        "name": "Nova Launcher Drawer Groups",
        "description": "Nova Launcher drawer folders and the drawer's whole app list, with the apps in each",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Nova Launcher",
        "sample_data": {
            "emu_a15_oss_v10": "Nova Launcher 8.9.0 | 20 rows",
        },
        "notes": "One row per row of the appgroups table in "
                 "com.teslacoilsw.launcher/databases/nova.db, joined to the drawer_groups row its "
                 "groupId names. The join is the one the database records: appgroups.groupId is "
                 "the _id of a drawer_groups row, which was confirmed on the tested device where "
                 "groups 2, 7 and 8 resolved to the Entertainment, Social and Travel folders that "
                 "held exactly the apps shown. Assigned is Unix milliseconds, reported as UTC, and "
                 "is the appgroups row's own modified column. Every component is written twice, "
                 "once against its group and once against group -100, which is the drawer's whole "
                 "app list rather than a folder; those rows are reported with a blank Group Name "
                 "and are what shows an app was present in the drawer at all. Hides Apps From "
                 "Drawer is the drawer_groups hideApps column and was 1 on every category folder "
                 "of the tested device, which is the app's own default for a category folder and "
                 "not a choice made here. Hiding an individual app is a paid Nova Prime feature "
                 "and was not exercised, so this artifact shows folder membership and the folder's "
                 "hide setting, not a per-app hidden list. Group Type is reported as stored. A row "
                 "is evidence the app was assigned to the group, not that it was launched.",
        "paths": ('*/com.teslacoilsw.launcher/databases/nova.db*',),
        "output_types": "standard",
        "artifact_icon": "folder",
    },
}

import re

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/nova.db'

# Proven from the layout on the tested device: the items Nova drew in the dock carried
# container -101 and the items on the home screen carried -100. Nova is closed source and
# no other container value was produced here, so nothing else is named.
CONTAINERS = {-100: 'Home screen', -101: 'Dock'}

COMPONENT = re.compile(r'component=([^;]+)')


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        value = int(value)
        if value < 0:
            return ''
        return convert_unix_ts_to_utc(value // 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _component(intent):
    if not intent:
        return ''
    match = COMPONENT.search(str(intent))
    return match.group(1) if match else ''


def _location(container):
    if container is None:
        return ''
    if container in CONTAINERS:
        return f'{CONTAINERS[container]} ({container})'
    return f'As stored ({container})'


@artifact_processor
def nova_layout(context):
    query = '''SELECT modified, title, container, screen, cellX, cellY, spanX, spanY,
                      itemType, intent, _id
               FROM favorites
               WHERE container IS NOT NULL
               ORDER BY container, screen, cellY, cellX'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), r[1] or '', _location(r[2]), r[3], r[4], r[5], r[6], r[7],
                r[8], _component(r[9]), r[10], context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Modified', 'datetime'), 'Title', 'Location', 'Screen', 'Cell X', 'Cell Y',
        'Span X', 'Span Y', 'Item Type (as stored)', 'Component', 'Item ID',
        'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def nova_drawer_groups(context):
    query = '''SELECT a.modified, g.title, a.groupId, a.component, g.groupType,
                      g.hideApps, g.tabOrder, a._id
               FROM appgroups a
               LEFT JOIN drawer_groups g ON g._id = a.groupId
               ORDER BY a.groupId, a._id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), r[1] or '', r[2], r[3] or '', r[4] or '',
                'Yes' if r[5] else ('No' if r[5] is not None else ''),
                r[6] if r[6] is not None else '', r[7],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Assigned', 'datetime'), 'Group Name', 'Group ID', 'Component', 'Group Type',
        'Hides Apps From Drawer', 'Tab Order', 'Assignment ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
