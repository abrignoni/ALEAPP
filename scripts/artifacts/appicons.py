# Seems to be a google thing, on Nexus/Pixel devices only?
import base64
import os
import sqlite3
from html import escape
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/' 

class App:
    def __init__(self, package):
        self.name = ''
        self.package = package
        self.main_icon = None
        self.icons = {} # { Component: ('Label', icon), .. }

def get_appicons(files_found, report_folder, seeker, wrap_text):
    sessions = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue
        elif os.path.isdir(file_found): # skip folders (there shouldn't be any)
            continue
        elif not os.path.basename(file_found) == 'app_icons.db': # skip -journal and other files
            continue
        
        file_name = os.path.basename(file_found)
        db = open_sqlite_db_readonly(file_found)
        db.row_factory = sqlite3.Row # For fetching columns by name

        cursor = db.cursor()
        cursor.execute('''SELECT componentName, profileid, lastUpdated, version, icon, label FROM icons ORDER BY componentName''')
        # version appears to be the last part of version string for some, ie, if ver=2.3.4.91, then db only stores '91' 
        # On others it changes 1.3.1 to '131'

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('App Icons')
            report.start_artifact_report(report_folder, 'App Icons')
            report.add_script()
            data_headers = ('App name', 'Package name', 'Main icon', 'Icons')
            data_list = []
            app = None
            apps = []
            last_package = None
            for row in all_rows:
                componentName = row['componentName']
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
                app.icons[component] = (row['label'], row['icon'])

            for app in apps:
                if len(app.icons) == 1:
                    app.name, app.main_icon = list(app.icons.items())[0][1]
                    app.icons = {}
                else:
                    desired_key = app.package + '.' # Look for component = 'com.xyz/com.zyz.'
                    if desired_key in app.icons:
                        app.name, app.main_icon= app.icons.get(desired_key)
                        del app.icons[desired_key]
                        continue
                    # If not found yet, look for component = 'com.xyz/com.zyz.*'
                    key_to_delete = None
                    for key in app.icons:
                        if key.startswith(desired_key):
                            app.name, app.main_icon = app.icons.get(key)
                            key_to_delete = key
                            break
                    if key_to_delete:
                        del app.icons[key]

            for app in apps:
                main_icon_html = ''
                other_icons_html = ''
                if app.main_icon:
                    icon_data = base64.b64encode(app.main_icon).decode("utf-8")
                    main_icon_html = f'<img src="data:image/png;base64,{icon_data}">'
                for k, v in app.icons.items():
                    if v[1]: # sometimes icon is NULL in db
                        icon_data = base64.b64encode(v[1]).decode("utf-8")
                        other_icons_html += f'<img title="{v[0]}" src="data:image/png;base64,{icon_data}"> '
                data_list.append(( escape(app.name), escape(app.package), main_icon_html, other_icons_html ))
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            return