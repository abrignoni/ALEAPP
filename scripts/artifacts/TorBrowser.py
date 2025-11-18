__artifacts_v2__ = {
    "torbrowser_thumbnails": {
        "name": "Tor Browser Tab Thumnails",
        "description": "Parses Tor Browser Tab thumbnail Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2025-11-14",
        "requirements": "none",
        "category": "Tor Browser",
        "notes": "Tested on version 15.0 (140.4.0esr (Oct 28th, 2025)",
        "paths": ('*/org.torproject.torbrowser/cache/mozac_browser_thumbnails/private_thumbnails/*.0'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "image"
    },
    "torbrowser_bookmarks": {
        "name": "Tor Browser - Bookmarks",
        "description": "Parses Tor Browser Bookmarks",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2025-11-14",
        "requirements": "none",
        "category": "Tor Browser",
        "notes": "Tested on version 15.0 (140.4.0esr (Oct 28th, 2025)",
        "paths": ('*/org.torproject.torbrowser/files/places.sqlite'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bookmark"
    },
    "torbrowser_usageinfo": {
        "name": "Tor Browser - Usage Info",
        "description": "Parses Tor Browser Usage Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2025-11-14",
        "requirements": "none",
        "category": "Tor Browser",
        "notes": "Tested on version 15.0 (140.4.0esr (Oct 28th, 2025)",
        "paths": ('*/org.torproject.torbrowser/shared_prefs/fenix_preferences.xml'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "info"
    },
}

import os
import datetime
import inspect
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, is_platform_windows, check_in_media, open_sqlite_db_readonly, get_sqlite_db_records, get_file_path, media_to_html, is_platform_windows, logfunc

@artifact_processor
def torbrowser_thumbnails(files_found, report_folder, seeker, wrap_text):
    artifact_info = inspect.stack()[0]
    data_list = []

    for file_found in files_found:
        media_path = Path(file_found)

        if not media_path.is_file():
            continue
        if media_path.suffix.lower() != '.0':
            continue

        filename = media_path.name
        location = str(media_path.parent)

        modified_ts = os.path.getmtime(file_found)
        modifiedtime = datetime.datetime.utcfromtimestamp(int(modified_ts)).strftime('%Y-%m-%d %H:%M:%S')

        media_item = check_in_media(
            artifact_info,
            report_folder,
            seeker,
            files_found,
            filename
        )

        if media_item:
            data_list.append((modifiedtime, media_item, filename, location))

    data_headers = (('ModifiedTime', 'datetime'),('Thumbnail', 'media'),'File Name','Location')

    return data_headers, data_list, 'See source path(s) below'

@artifact_processor
def torbrowser_bookmarks(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.sqlite'):
            break
                       
    query = '''
        SELECT 
            child.id,
            CASE
                WHEN child.parent = 1 THEN 'PlacesRoot'
                ELSE parent.title
            END AS "Parent Container",
            CASE 
                WHEN child.id = 1 THEN 'PlacesRoot'
                ELSE child.title
            END AS Title,
            moz_places.url AS URL, 
            moz_places.description AS Description, 
            DATETIME((child.dateAdded / 1000), 'unixepoch') AS 'Date Added (UTC)',
            DATETIME((child.lastModified / 1000), 'unixepoch') AS 'Date Last Modified (UTC)'
        FROM moz_bookmarks AS child
        LEFT JOIN moz_places ON child.fk = moz_places.id  
        LEFT JOIN moz_bookmarks AS parent ON child.parent = parent.id
        WHERE child.type = 1;
        '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:
        id              = row[0]
        parent_folder   = row[1]
        title           = row[2]
        url             = row[3]
        description     = row[4]
        added_date      = row[5]
        last_modified   = row[6]

        data_list.append((id,parent_folder,title,url,description,added_date,last_modified))

    data_headers = ('Bookmark ID', 'Parent Folder', 'Title', 'URL', 'Description', ('Date Added','datetime'),('Last Modified','datetime')) 
    data_list = get_sqlite_db_records(source_path, query)        
    
    return data_headers, data_list, source_path
    
@artifact_processor
def torbrowser_usageinfo(files_found, report_folder, seeker, wrap_text):

    usage_keys = {
        "pref_key_last_browse_activity_time",
        "pref_key_times_app_opened",
        "pref_key_open_private_tabs_count"
    }

    data_list = []
    source_path = ""

    for fp in files_found:
        source_path = str(fp)
        if not source_path.lower().endswith(".xml"):
            continue
        if not os.path.isfile(source_path):
            continue

        try:
            tree = ET.parse(source_path)
            root = tree.getroot()
        except Exception:
            continue 

        filename = Path(source_path).name
        path = source_path

        for elem in root.iter():
            key_name = elem.get("name")
            if key_name not in usage_keys:
                continue

            value_raw = elem.text.strip() if elem.text else elem.get("value", "").strip()

            value_out = value_raw
            if key_name == "pref_key_last_browse_activity_time":
                try:
                    ts = int(value_raw)
                    dt = datetime.datetime.utcfromtimestamp(ts / 1000.0)
                    value_out = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass 

            data_list.append((key_name, value_out, filename, path))

    data_headers = ("Key", "Value", "File Name", "Path")

    return data_headers, data_list, source_path




