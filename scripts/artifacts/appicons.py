__artifacts_v2__ = {
    "appIcons": {
        "name": "App Icon",
        "description": "Extract App icons from Nexus launcher database",
        "author": "@ydkhatri",
        "creation_date": "2020-11-03",
        "last_update_date": "2025-03-08",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Seems to be a google thing, on Nexus/Pixel devices only?",
        "paths": ('*/com.google.android.apps.nexuslauncher/databases/app_icons.db*'),
        "output_types": ["html", "lava"],
        "artifact_icon": "package"
    }
}

import inspect
from html import escape
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_sqlite_db_records, check_in_embedded_media, \
    logfunc, convert_unix_ts_to_utc

class App:
    def __init__(self, package):
        self.name = ''
        self.package = package
        self.main_icon = None
        self.icon = [] # [ Component: ('Label', icon, last_update), .. ]
        self.icons = {} # { Component: ('Label', icon, last_update), .. }

@artifact_processor
def appIcons(files_found, report_folder, seeker, wrap_text):
    artifact_info = inspect.stack()[0]
    source_path = get_file_path(files_found, "app_icons.db", "mirror")
    data_list = []

    app = None
    apps = []
    last_package = None

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

    data_headers = ('App name', 'Package name', ('Main icon', 'media'), ('Icons', 'media'))

    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        icon_last_update = convert_unix_ts_to_utc(record[2])
        componentName = record[0]
        if componentName.find('/') > 0:
            package, component = componentName.split('/', 1)
        else:
            logfunc(f'Warning: Different format detected, no component name found , only package name seen! component = {componentName}')
            package = componentName
            component = ''
        if package != last_package:
            # new package name seen
            last_package = package
            app = App(package)
            apps.append(app)
        app.icons[component] = (record[-1], record[-2], icon_last_update)

    for app in apps:
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
                del app.icons[key]

    for app in apps:
        main_icon = ''
        other_icons = []
        if app.icon:
            # main_icon = check_in_embedded_media(artifact_info, report_folder, seeker, source_path, app.icon[1], app.icon[0], app.icon[2])
            main_icon = check_in_embedded_media(artifact_info, report_folder, seeker, source_path, app.icon[1], app.icon[0])
        for k, v in app.icons.items():
            if v[1]: # sometimes icon is NULL in db
                # other_icon = check_in_embedded_media(artifact_info, report_folder, seeker, source_path, v[1], v[0], v[2])
                other_icon = check_in_embedded_media(artifact_info, report_folder, seeker, source_path, v[1], v[0])
                other_icons.append(other_icon)
        data_list.append((escape(app.name), escape(app.package), main_icon, other_icons ))

    return data_headers, data_list, source_path
