# pylint: disable=W0612,W0631
__artifacts_v2__ = {
    "appIcons": {
        "name": "App Icon",
        "description": "Extract App icons from Nexus launcher database",
        "author": "@ydkhatri, @AlexisBrignoni, Codex",
        "creation_date": "2020-11-03",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Read every distinct app_icons.db state of the Pixel Launcher. Known canonical "
                 "aliases collapse only when main/WAL/journal bytes agree. Groups remain separate "
                 "by source, package and stored profile ID; profile ID does not establish Android "
                 "user identity or ownership. Combined row origins carry Source File. Icon choice "
                 "is heuristic and does not establish the main app icon or user interaction. "
                 "Other launchers are not covered. Raw component rows, repeated component keys "
                 "within one profile, and version/date fields remain unreported. Shared media items "
                 "retain the first source pointer; row origins and BLOB bytes establish later sources.",
        "paths": ('*/com.google.android.apps.nexuslauncher/databases/app_icons.db*'),
        "output_types": ["html", "lava"],
        "artifact_icon": "package",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.nexuslauncher | 70 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.nexuslauncher | 100 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.nexuslauncher | 359 rows (293 user 0, 66 user 10)",
            "userb2_a13": "Android 13 | com.google.android.apps.nexuslauncher | 88 rows",
        }
    }
}

import hashlib
import sqlite3
from pathlib import Path
from html import escape
from scripts.ilapfuncs import artifact_processor, \
    open_sqlite_db_readonly, check_in_embedded_media, \
    logfunc, convert_unix_ts_to_utc, null_absent_columns
from scripts.artifacts.storagePathViews import canonical_path

class App:
    def __init__(self, package, profileid):
        self.profileid = profileid
        self.name = ''
        self.package = package
        self.main_icon = None
        self.icon = [] # [ Component: ('Label', icon, last_update), .. ]
        self.icons = {} # { Component: ('Label', icon, last_update), .. }


def _app_icon_sources(context):
    """Keep independent complete states; collapse proven canonical aliases only."""
    paths = []
    seen = set()
    for candidate in context.get_files_found():
        path = str(candidate)
        if Path(path).name != 'app_icons.db':
            continue
        relative = context.get_relative_path(path)
        if Path(path).is_symlink():
            logfunc(f'App Icons: symlink main in {relative}; skipping source')
            continue
        if not Path(path).is_file():
            continue
        try:
            with open(path, 'rb') as handle:
                if handle.read(16) != b'SQLite format 3\x00':
                    logfunc(f'App Icons: unsupported SQLite header in {relative}; skipping source')
                    continue
            state = []
            for suffix in ('', '-wal', '-journal'):
                if Path(path + suffix).is_symlink():
                    raise OSError('symlink in database state')
                try:
                    with open(path + suffix, 'rb') as handle:
                        digest = hashlib.sha256()
                        for chunk in iter(lambda handle=handle: handle.read(1024 * 1024), b''):
                            digest.update(chunk)
                    state.append(digest.hexdigest())
                except FileNotFoundError:
                    if not suffix:
                        raise
                    state.append(None)
            identity = (canonical_path(relative)[0], tuple(state))
        except OSError as error:
            logfunc(f'App Icons: unreadable database state {relative}: {error}; skipping source')
            continue
        if identity not in seen:
            seen.add(identity)
            paths.append(path)
    return paths

@artifact_processor
def appIcons(context):
    data_list = []
    sources = {}

    query = '''
    SELECT 
        componentName, 
        profileid, 
        lastUpdated, 
        version, 
        icon, 
        label 
    FROM icons 
    ORDER BY componentName
    '''
    
    # version appears to be the last part of version string for some, ie, if ver=2.3.4.91, then db only stores '91' 
    # On others it changes 1.3.1 to '131'

    data_headers = ('App name', 'Package name', ('Main icon', 'media'), ('Icons', 'media'), 'Profile ID (as stored)')

    for source_path in _app_icon_sources(context):
        relative = context.get_relative_path(source_path)
        db = open_sqlite_db_readonly(source_path)
        if db is None:
            logfunc(f'App Icons: unavailable database {relative}; skipping source')
            continue
        try:
            db_records = db.execute(null_absent_columns(source_path, query)).fetchall()
        except sqlite3.Error as error:
            logfunc(f'App Icons: unsupported icons schema in {relative}: {error}; skipping source')
            continue
        finally:
            db.close()
        apps = {}

        for record in db_records:
            icon_last_update = convert_unix_ts_to_utc(record[2])
            componentName = record[0]
            if componentName.find('/') > 0:
                package, component = componentName.split('/', 1)
            else:
                logfunc(f'Warning: Different format detected, no component name found , only package name seen! component = {componentName}')
                package = componentName
                component = ''
            group = (package, type(record[1]).__name__, record[1])
            if group not in apps:
                apps[group] = App(package, record[1])
            app = apps[group]
            app.icons[component] = (record[-1], record[-2], icon_last_update)

        for app in apps.values():
            if len(app.icons) == 1:
                app.name, app.main_icon, icon_last_update = list(app.icons.items())[0][1]
                app.icon = (app.name, app.main_icon, icon_last_update)
                app.icons = {}
            else:
                desired_key = app.package + '.' # Look for component = 'com.xyz/com.zyz.'
                if desired_key in app.icons:
                    app.name, app.main_icon, icon_last_update = app.icons.get(desired_key)
                    app.icon = (app.name, app.main_icon, icon_last_update)
                    del app.icons[desired_key]
                    continue
                # If not found yet, look for component = 'com.xyz/com.zyz.*'
                key_to_delete = None
                for key in app.icons:
                    if key.startswith(desired_key):
                        app.name, app.main_icon, icon_last_update = app.icons.get(key)
                        key_to_delete = key
                        break
                if key_to_delete:
                    app.icon = (app.name, app.main_icon, icon_last_update)
                    del app.icons[key_to_delete]

        for app in apps.values():
            main_icon = ''
            other_icons = []
            if app.icon:
                # main_icon = check_in_embedded_media(artifact_info, report_folder, seeker, source_path, app.icon[1], app.icon[0], app.icon[2])
                main_icon = check_in_embedded_media(source_path, app.icon[1], app.icon[0])
            for k, v in app.icons.items():
                if v[1]: # sometimes icon is NULL in db
                    # other_icon = check_in_embedded_media(artifact_info, report_folder, seeker, source_path, v[1], v[0], v[2])
                    other_icon = check_in_embedded_media(source_path, v[1], v[0])
                    other_icons.append(other_icon)
            data_list.append((escape(app.name), escape(app.package), main_icon, other_icons, app.profileid, relative))
            sources[source_path] = None

    if len(sources) > 1:
        data_headers += ('Source File',)
    else:
        data_list = [row[:-1] for row in data_list]
    return data_headers, data_list, '\n'.join(sources)
