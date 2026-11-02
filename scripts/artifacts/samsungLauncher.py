__artifacts_v2__ = {
    "samsungLauncherItems": {
        "name": "Samsung Launcher Items",
        "description": "Home screen and app screen layout of the Samsung One UI launcher "
                       "(OneUI.db, item table): each item's title, component, position, "
                       "container and hidden flag. Type and container codes are stored as "
                       "raw values and are reported as-is.",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/com.sec.android.app.launcher/databases/OneUI.db*',),
        "output_types": "standard",
        "artifact_icon": "grid",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.launcher | 90 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.launcher | 118 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.launcher | 111 rows",
        },
    },
    "samsungLauncherIcons": {
        "name": "Samsung Launcher Icons",
        "description": "App icon cache of the Samsung One UI launcher (Icon.db, icon "
                       "table): the component name, label, profile_id and last_updated "
                       "values as stored (last_updated is rendered as a UTC time; what it "
                       "marks is not established).",
        "author": "@abrignoni",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/com.sec.android.app.launcher/databases/Icon.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.launcher | 62 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.launcher | 92 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.launcher | 90 rows",
        },
    },
    "samsungLauncherSearchHistory": {
        "name": "Samsung Launcher Search History",
        "description": "Search text entered in the Samsung One UI launcher's search box, newest first, from "
                       "pref_search_history.xml.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Reads pref_search_history.xml from the Samsung One UI launcher's shared_prefs (com.sec.android.app.launcher). No published source exists for the launcher; what is said here comes from its own code, decompiled with jadx from the launcher APKs on two of the tested images (version 15.1.03.75 on samsunga53_a14 and 15.0.09.1 on sharon_a14), class com.honeyspace.search.datamodel.datasources.HistoryDataManager. The file holds one string preference, pref_search_history, a JSON list of strings. In both versions the launcher adds an entry when the keyboard's Enter key is pressed in its search box, taking the text in the box and skipping an empty one, and a second code path adds a value named searchKeyword; a new entry is put first, an entry already in the list moves to the front instead of being added again, and at most 20 are kept. The code also removes a single entry and clears the list on other paths. Position is the entry's place in the list, 1 first, so 1 is the most recently added or repeated search. Search Keyword is the entry as stored. The file stores no times. This was read from the code, not tested on a device: no known-data case was made, because that needs a Samsung phone. Other launcher versions were not read, and anne_a15 holds no launcher bytecode to read. Android User is the Android user whose app data directory holds the file, read from its path; the storage views one extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are read once, and the files read are listed in the report's source paths. On the tested images: 17 rows on 3 of 20 images (anne_a15 9, sharon_a14 6, samsunga53_a14 2), all on Android 14 and 15; every entry was distinct within its list and none was empty. Android User held 0 on every row. The other four Samsung images (Android 10 and 13) had no such file.",
        "paths": ('*/com.sec.android.app.launcher/shared_prefs/pref_search_history.xml',),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "anne_a15": "Android 15 | 9 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hickman_a13": "Android 13 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 2 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 6 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import json
import re
import xml.etree.ElementTree as ET

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc, logfunc


def _unique_db_files(context, name_suffix):
    '''Database files matching the suffix, without -wal/-shm sidecars and without the
    duplicates extractions carry for the same file (data_mirror, and /data/data next
    to /data/user/0).

    The dedupe key is the evidence-relative path, not the extracted path: the report's own
    data folder ends in /data, so a raw-path replace can rewrite the harness boundary
    instead of the evidence path on archives whose members start with data/.'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(name_suffix):
            continue
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if 'data_mirror' in relative:
            continue
        normalized = re.sub(r'(^|/)data/data/', r'\1data/user/0/', relative)
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(file_found)
    return result


@artifact_processor
def samsungLauncherItems(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'OneUI.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT title, component, type, item_position, position_x, position_y, rank,
                   container_type, container_id, hidden, profile_id, restored,
                   reference_package_name
            FROM item
            ORDER BY container_type, container_id, rank, item.rowid
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append(tuple(row))

    data_headers = (
        'Title',
        'Component',
        'Type',
        'Item Position',
        'Position X',
        'Position Y',
        'Rank',
        'Container Type',
        'Container ID',
        'Hidden',
        'Profile ID',
        'Restored',
        'Reference Package',
    )
    return data_headers, data_list, source_path


@artifact_processor
def samsungLauncherIcons(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'Icon.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT last_updated, label, component_name, profile_id, version
            FROM icon
            ORDER BY last_updated DESC, icon.rowid
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                convert_unix_ts_to_utc(row[0]),
                row[1],
                row[2],
                row[3],
                row[4],
            ))

    data_headers = (
        ('Last Updated', 'datetime'),
        'Label',
        'Component Name',
        'Profile ID',
        'Version',
    )
    return data_headers, data_list, source_path


@artifact_processor
def samsungLauncherSearchHistory(context):
    data_headers = ('Position', 'Search Keyword', 'Android User')
    data_list, sources = [], []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.replace('\\', '/').endswith('/pref_search_history.xml'):
            continue
        relative = context.get_relative_path(file_found)
        sources.append(file_found)
        try:
            with open(file_found, 'rb') as handle:
                root = ET.fromstring(handle.read())
        except (OSError, ET.ParseError) as ex:
            logfunc(f'Samsung Launcher Search History: could not read {relative}: {type(ex).__name__}')
            continue
        stored = next((item.text for item in root.iter('string') if item.get('name') == 'pref_search_history'), None)
        if not stored:
            continue
        try:
            keywords = json.loads(stored)
        except ValueError:
            logfunc(f'Samsung Launcher Search History: {relative} holds a value that is not JSON; reported as stored')
            keywords = [stored]
        if not isinstance(keywords, list):
            keywords = [keywords]
        user = android_user(relative)
        for position, keyword in enumerate(keywords, 1):
            data_list.append((position, keyword if isinstance(keyword, str) else json.dumps(keyword), user))
    return data_headers, data_list, '\n'.join(sources)

