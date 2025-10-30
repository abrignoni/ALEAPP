import blackboxprotobuf
import datetime
import json
import os
import shutil
import sqlite3
from html import escape
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/' 

def recursive_convert_bytes_to_str(obj):
    '''Recursively convert bytes to strings if possible'''
    ret = obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = recursive_convert_bytes_to_str(v)
    elif isinstance(obj, list):
        for index, v in enumerate(obj):
            obj[index] = recursive_convert_bytes_to_str(v)
    elif isinstance(obj, bytes):
        # test for string
        try:
            ret = obj.decode('utf8', 'backslashreplace')
        except UnicodeDecodeError:
            ret = str(obj)
    return ret

def get_quicksearch_recent(files_found, report_folder, seeker, wrap_text):
    recents = []
    account_db = ''
    account_name = ''
    screenshot_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('accounts.notifications.db'):
            account_db = str(file_found)
            
            db = open_sqlite_db_readonly(account_db)
            cursor = db.cursor()
            
            cursor.execute('''
            select
            account_name
            from accounts''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
                    account_name = row[0]
            
            db.close()
            
            continue
        
        elif file_found.endswith('.jpg'):
            screenshot_path = file_found
            continue # Skip jpg files, all others should be protobuf
        elif file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue
        elif os.path.isdir(file_found): # skip folders
            continue
        
        with open(file_found, 'rb') as f:
            pb = f.read()
            types = {'1': {'type': 'message', 'message_typedef': 
                {
                    '1': {'type': 'uint', 'name': 'id'},
                    '4': {'type': 'uint', 'name': 'timestamp1'}, 
                    '5': {'type': 'str', 'name': 'search-query'},
                    '7': {'type': 'message', 'message_typedef': 
                        {
                        '1': {'type': 'str', 'name': 'url'}, 
                        '2': {'type': 'str', 'name': 'url-domain'}, 
                        '3': {'type': 'str', 'name': 'title'}
                        }, 'name': 'page'
                    },
                    '8': {'type': 'message', 'message_typedef': 
                        {
                        '1': {'type': 'str', 'name': 'category'}, 
                        '2': {'type': 'str', 'name': 'engine'}
                        }, 'name': 'search'
                    },
                    '9': {'type': 'int', 'name': 'screenshot-id'},
                    '17': {'type': 'uint', 'name': 'timestamp2'},
                }, 'name': ''} }
            values, types = blackboxprotobuf.decode_message(pb, types)
            items = values.get('1', None)
            
            if items:
                if isinstance(items, dict): 
                    # this means only one element was found
                    # No array, just a dict of that single element
                    recents.append( (file_found, [items]) )
                else:
                    # Array of dicts found
                    recents.append( (file_found, items) )

    if report_folder[-1] == slash: 
        folder_name = os.path.basename(report_folder[:-1])
    else:
        folder_name = os.path.basename(report_folder)
    recent_entries = len(recents)
    if recent_entries > 0:
        description = "Recently searched terms from the Google Search widget and webpages read from Google app (previously known as 'Google Now') appear here."
        report = ArtifactHtmlReport('Google Now & Quick Search recent events')
        report.start_artifact_report(report_folder, 'Recent Searches & Google Now', description)
        report.add_script()
        data_headers = ('Timestamp','Screenshot Path','Search Query','Screenshot', 'Protobuf Data')
        data_list = []
        for file_path, items in recents:
            dir_path, base_name = os.path.split(screenshot_path)
            for item in items:
                screenshot_id = str(item.get('screenshot-id', ''))  
                search_timestamp = datetime.datetime.utcfromtimestamp(item.get('timestamp1', '')/1000).strftime('%Y-%m-%d %H:%M:%S')
                search_query = str(item.get('search-query',''))
                screenshot_file_path = os.path.join(dir_path, f'{account_name}-{screenshot_id}.jpg')
                if os.path.exists(screenshot_file_path):
                    shutil.copy2(screenshot_file_path, report_folder)
                img_html = '<a href="{1}/{0}"><img src="{1}/{0}" class="img-fluid" style="max-height:600px; min-width:300px" title="{0}"></a>'.format(f'{account_name}-{screenshot_id}.jpg', folder_name)
                
                platform = is_platform_windows()
                if platform:
                    img_html = img_html.replace('?', '')
                
                recursive_convert_bytes_to_str(item) # convert all 'bytes' to str
                data_list.append((search_timestamp,screenshot_file_path,search_query,img_html, '<pre id="json" style="font-size: 110%">'+ escape(json.dumps(item, indent=4)).replace('\\n', '<br>') +'</pre>'))

        report.write_artifact_data_table(data_headers, data_list, dir_path, html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'google quick search box recent'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No recent quick search or now data available')

__artifacts__ = {
        "Quicksearch_recent": (
                "Google Now & QuickSearch",
                ('*/com.google.android.googlequicksearchbox/files/recently/*','*/com.google.android.googlequicksearchbox/files/accounts/*/RecentsDataStore.pb','*/com.google.android.googlequicksearchbox/databases/accounts.notifications.db'),
                get_quicksearch_recent)
}