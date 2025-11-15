__artifacts_v2__ = {
    "duckduckgo_bookmarks": {
        "name": "DuckDuckGo - Bookmarks",
        "description": "Parses DuckDuckGo Bookmarks",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-05-21",
        "last_update_date": "2025-06-08",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.237.0 (June, 3rd 2025)",
        "paths": ('*/com.duckduckgo.mobile.android/databases/app.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bookmark"
    },
    "duckduckgo_favorites": {
        "name": "DuckDuckGo - Favorited Sites",
        "description": "Parses DuckDuckGo favorite Sites",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-05-30",
        "last_update_date": "2025-06-08",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.237.0 (June, 3rd 2025)",
        "paths": ('*/com.duckduckgo.mobile.android/databases/app.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "star"
    },
    "duckduckgo_history": {
        "name": "DuckDuckGo - Web Browser History",
        "description": "Parses DuckDuckGo Web Browsing History",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-05-21",
        "last_update_date": "2025-06-08",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.237.0 (June, 3rd 2025)",
        "paths": ('*/com.duckduckgo.mobile.android/databases/history.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe"
    },
    "duckduckgo_opentabs": {
        "name": "DuckDuckGo - Open Tabs",
        "description": "Parses DuckDuckGo Open Tab Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-05-21",
        "last_update_date": "2025-11-13",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.255.0 (Oct, 31st 2025)",
        "paths": ('*/com.duckduckgo.mobile.android/databases/app.db*','*/com.duckduckgo.mobile.android/cache/tabPreviews/*/*.jpg'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "book-open"
    },
        "duckduckgo_fireproof": {
        "name": "DuckDuckGo - FireProof Sites",
        "description": "Parses DuckDuckGo FireProof Sites",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-13",
        "last_update_date": "2025-11-13",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.255.0 (Oct, 31st 2025)",
        "paths": ('*/com.duckduckgo.mobile.android/databases/app.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe"
    },
    
        "duckduckgo_downloads": {
        "name": "DuckDuckGo - Downloads",
        "description": "Parses DuckDuckGo Downloads",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-13",
        "last_update_date": "2025-11-13",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.255.0 (Oct, 31st 2025)",
        "paths": ('*/com.duckduckgo.mobile.android/databases/downloads.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "download"
    },
    "duckduckgo_thumbnails": {
        "name": "DuckDuckGo - Tab Thumbnails",
        "description": "Parses DuckDuckGo Tab thumbnail Information",
        "author": "@abrignoni & @stark4n6",
        "creation_date": "2022-05-28",
        "last_update_date": "2025-06-10",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "",
        "paths": ('*/com.duckduckgo.mobile.android/cache/tabPreviews/*/*.jpg','*/com.duckduckgo.mobile.android/databases/app.db*'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "image"
    },
        "duckduckgo_duckai": {
        "name": "DuckDuckGo - Duck AI",
        "description": "Parses Duck AI Coversations",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-13",
        "last_update_date": "2025-11-13",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.255.0 (Oct, 31st 2025)",
        "paths": ('*com.duckduckgo.mobile.android/app_webview/Default/Local Storage/leveldb/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-square"
    },
        "duckduckgo_cookies": {
        "name": "DuckDuckGo - Cookies",
        "description": "Parses DuckDuckGo Cookies",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2025-11-14",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.255.0 (Oct, 31st 2025)",
        "paths": ('*/com.duckduckgo.mobile.android/app_webview/Default/cookies'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "globe"
    },
}

import inspect   
import sqlite3
import json
import datetime
import pathlib
from pathlib import Path
from scripts.ilapfuncs import artifact_processor, is_platform_windows, check_in_media, open_sqlite_db_readonly, does_column_exist_in_db, get_sqlite_db_records, get_file_path, media_to_html, is_platform_windows, logfunc
from scripts.ccl import ccl_leveldb

@artifact_processor
def duckduckgo_bookmarks(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break
                       
    query = '''
        -- CTE to rebuild bookmark folder path
        WITH RECURSIVE folder_paths AS (
            SELECT 
                entities.entityId AS folderId,
                entities.title AS path
            FROM entities
            WHERE entities.type = 'FOLDER'
              AND entities.entityId NOT IN (SELECT entityId FROM relations)

            UNION ALL
            
            SELECT 
                child.entityId AS folderId,
                folder_paths.path || ' > ' || child.title AS path
            FROM entities AS child
            JOIN relations ON child.entityId = relations.entityId
            JOIN folder_paths ON relations.folderId = folder_paths.folderId
            WHERE child.type = 'FOLDER'
        ),

        -- CTE to store bookmark and folder information
        bookmark_locations AS (
            SELECT
                entities.rowid,
                entities.entityId,
                entities.type,
                entities.title,
                entities.url,
                entities.lastModified,
                entities.deleted,
                relations.folderId
            FROM entities
            LEFT JOIN relations ON entities.entityId = relations.entityId
        )
        -- Main Query
        SELECT 
            bookmark_locations.entityId AS "Entity ID",
            CASE bookmark_locations.deleted
                WHEN 1 THEN 'YES'
                ELSE 'NO'
            END AS Deleted,
            folder_paths.path AS "Folder Path",	
            bookmark_locations.title AS "Title",
            bookmark_locations.url,
            SUBSTR(REPLACE(REPLACE(bookmark_locations.lastModified, 'T', ' '), 'Z', ''), 1, 19) AS "Last Modified"
        FROM bookmark_locations
        LEFT JOIN folder_paths ON bookmark_locations.folderId = folder_paths.folderId
        WHERE bookmark_locations.type LIKE 'BOOKMARK'
        GROUP BY bookmark_locations.entityId
        ORDER BY bookmark_locations.ROWID;
        '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:

        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

    data_headers = ('Entity ID','Deleted','Folder Path','Title','URL', ('Last Modified','datetime')) 
    data_list = get_sqlite_db_records(source_path, query)        
    
    return data_headers, data_list, source_path
    
@artifact_processor
def duckduckgo_favorites(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break
                       
    query = '''
		-- CTE to identify folder name using the folderId

		WITH folder_titles AS (
		   SELECT
				entities.entityId AS folderId,
				entities.title AS folderTitle
			FROM entities
			WHERE entities.type = 'FOLDER'
		),
		-- CTE to identify bookmark favorites
		bookmark_favorites AS (
			SELECT
				relations.entityId
			FROM relations
			WHERE relations.folderId = 'favorites_root'
		)
		-- Main Query
		SELECT
			entities.entityId,
			entities.title,
			entities.url
		FROM entities
		LEFT JOIN relations ON entities.entityId = relations.entityId
		LEFT JOIN folder_titles ON relations.folderId = folder_titles.folderId
		LEFT JOIN bookmark_favorites ON entities.entityId = bookmark_favorites.entityId
		WHERE entities.type LIKE 'BOOKMARK' AND bookmark_favorites.entityId IS NOT NULL
		GROUP BY entities.entityId
	'''
	
    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        data_list.append((row[1],row[2]))

    data_headers = ('Entity ID','Title','URL') 
    data_list = get_sqlite_db_records(source_path, query)        
    
    return data_headers, data_list, source_path
    
@artifact_processor
def duckduckgo_history(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break
            
    query = '''
        SELECT  
            visits_list.rowid,
            history_entries.url,
            history_entries.title, 
            REPLACE(visits_list.timestamp, 'T', ' ') AS 'Visit Date (Local)',
            CASE history_entries.isSerp 
                WHEN 1 THEN 'DuckDuckGo Search'
                WHEN 0 THEN 'Web Page Visit' 
            END AS 'History Type', 
            history_entries.query
        FROM visits_list 
        LEFT JOIN history_entries ON visits_list.historyEntryId = history_entries.id;
        '''

    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

    data_headers = ('Visit ID','URL','Title',('Visit Date (Local)','datetime'),'History Type','Search Query') 
    data_list = get_sqlite_db_records(source_path, query)        
    
    return data_headers, data_list, source_path
    
@artifact_processor
def duckduckgo_opentabs(files_found, report_folder, seeker, wrap_text):
    import inspect
    from pathlib import Path

    artifact_info = inspect.stack()[0]
    data_list = []
    source_path = get_file_path(files_found, 'app.db')  
    thumb_lookup = {}
    for file_found in files_found:
        p = Path(file_found)
        if p.is_file() and p.suffix.lower() in ('.jpg'):
            thumb_lookup[p.name] = file_found

    if does_column_exist_in_db(source_path, 'tabs', 'lastAccessTime'):
        query = '''
            SELECT  
                tabs.tabid,
                CASE 
                    WHEN tab_selection.tabid IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END AS 'Current Tab',
                tabs.title,
                tabs.url,
                tabs.tabPreviewFile,
                DATETIME(RTRIM(tabs.tabPreviewFile, '.jpg') / 1000, 'unixepoch','localtime') AS 'Cached Tab Preview Time (Local)',
                REPLACE(tabs.lastAccessTime, 'T', ' ') AS 'Tab Last Accessed (Local)'
            FROM tabs
            LEFT JOIN tab_selection ON tabs.tabid = tab_selection.tabid;
        '''
    else:
        query = '''
            SELECT  
                tabs.tabid,
                CASE 
                    WHEN tab_selection.tabid IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END AS 'Current Tab',
                tabs.title,
                tabs.url,
                tabs.tabPreviewFile,
                DATETIME(RTRIM(tabs.tabPreviewFile, '.jpg') / 1000, 'unixepoch','localtime') AS 'Cached Tab Preview Time (Local)',
                'Unavailable' AS 'Tab Last Accessed (Local)'
            FROM tabs
            LEFT JOIN tab_selection ON tabs.tabid = tab_selection.tabid;
        '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:
        tab_id          = row[0]  # Tab ID
        current_tab     = row[1]  # Current Tab
        title           = row[2]  # Title
        url             = row[3]  # URL
        cached_filename = row[4]  # Cached Tab Filename
        cached_time     = row[5]  # Cached Tab Preview Time (Local)
        last_accessed   = row[6]  # Tab Last Accessed (Local)

        tab_thumbnail_media = None

        if cached_filename:
            thumb_path = thumb_lookup.get(cached_filename)
            if thumb_path:
                tab_thumbnail_media = check_in_media(
                    artifact_info,
                    report_folder,
                    seeker,
                    files_found,
                    thumb_path,
                    cached_filename
                )

        data_list.append((tab_id, current_tab, title, url, last_accessed, cached_filename, cached_time, tab_thumbnail_media))

    data_headers = (
        'Tab ID',
        'Current Tab',
        'Title',
        'URL',
        ('Tab Last Accessed (Local)','datetime'),
        'Cached Tab Filename',
        ('Cached Tab Preview Time (Local)','datetime'),
        ('Cached Tab Preview','media')
    )

    return data_headers, data_list, source_path

@artifact_processor
def duckduckgo_fireproof(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break
                       
    query = '''
		SELECT
			fireproofWebsites.domain
		FROM fireProofWebsites;
	'''
	
    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        domain = row[0]
        data_list.append((domain,))

    data_headers = ('Fireproof Site',) 
    data_list = get_sqlite_db_records(source_path, query)        
    
    return data_headers, data_list, source_path
    
@artifact_processor
def duckduckgo_downloads(files_found, report_folder, seeker, wrap_text):
    data_list = []

    def is_sqlite_db(path):
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            return header == b"SQLite format 3\x00"
        except Exception:
            return False

    source_path = None
    for f in files_found:
        p = Path(f)
        if p.name.endswith("-wal") or p.name.endswith("-shm"):
            continue
        if is_sqlite_db(f):
            source_path = str(f)
            break

    if not source_path:
         return (), [], "c not found"
            
    query = '''
        SELECT
            downloads.downloadId AS "Download ID",
            CASE downloads.downloadStatus
                WHEN 0 THEN 'Download Started'
                WHEN 1 THEN 'Download Completed'
                ELSE 'Unknown (' || downloads.downloadStatus || ')'
            END AS "Download Status",
            downloads.fileName AS "File Name",
            downloads.contentLength,
            downloads.filePath AS "Download Path",
            DATETIME(downloads.createdat) AS "Download Date (Local)"
        FROM downloads;
        '''

    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        download_id    = row[0]
        download_status = row[1]
        file_name      = row[2]
        size_bytes        = row[3]
        download_path  = row[4]
        download_date  = row[5]

        data_list.append((download_id, download_status, file_name, size_bytes, download_path, download_date))

    data_headers = ('Download ID','Download Status','File Name','Size (Bytes)','Download Path',('Download Date (Local)', 'datetime'))   
    
    return data_headers, data_list, source_path

@artifact_processor
def duckduckgo_thumbnails(files_found, report_folder, seeker, wrap_text):
    artifact_info = inspect.stack()[0]
    data_list = []

    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.db'):
            break
    open_preview_files = set()
    if source_path:
        query = '''
            SELECT
                tabs.tabPreviewFile
            FROM tabs;
        '''
        db_records = get_sqlite_db_records(source_path, query)
        for row in db_records:
            if row[0]:
                open_preview_files.add(Path(str(row[0])).name)

    for file_found in files_found:
        media_path = Path(file_found)
        if media_path.suffix.lower() not in ('.jpg'):
            continue
        filename = (media_path.name)
        utctime = int(media_path.stem)
        filepath = str(media_path.parents[1])
        
        timestamp = (datetime.datetime.utcfromtimestamp(utctime/1000).strftime('%Y-%m-%d %H:%M:%S'))
        media_item = check_in_media(artifact_info, report_folder, seeker, files_found, file_found, filename)

        if media_item:
            tab_status = 'Open' if filename in open_preview_files else 'Closed'

            data_list.append((tab_status, timestamp, media_item, filename, str(file_found)))

    data_headers = ('Tab Status',('Timestamp','datetime'),('Thumbnail','media'),'File Name','Location')

    return data_headers, data_list, 'See source path(s) below'

@artifact_processor
def duckduckgo_duckai(files_found, report_folder, seeker, wrap_text):
    from datetime import datetime
    data_list = []

    duckchats = "_https://duckduckgo.com savedAIChats"
    
    def clean_iso_timestamp(ts):
        if not ts:
            return ts

        ts = ts.rstrip("Z")

        try:
            dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")

        return dt.strftime("%Y-%m-%d %H:%M:%S")


    def clean_key_bytes(value):
        if isinstance(value, (bytes, bytearray)):
            s = value.decode('utf-8', errors='replace')
        else:
            s = str(value)

        if s and ord(s[0]) < 32:
            s = s[1:]

        cleaned = []
        for ch in s:
            if ch.isprintable():
                cleaned.append(ch)
            elif ch in '\t\n\r':
                cleaned.append(ch)
            else:
                cleaned.append(' ')

        s = ''.join(cleaned)

        s = ' '.join(s.split())

        return s

    def decode_json_bytes(value):
        if isinstance(value, (bytes, bytearray)):
            b = bytes(value)
        else:
            b = str(value).encode('utf-8', errors='ignore')

        if b and b[0] < 32:
            b = b[1:]

        return b.decode('utf-8', errors='ignore')


    for source_path in files_found:
        source_path = set(pathlib.Path(x).parent for x in files_found)        
    
    for in_db_dir in source_path:
        try:
            leveldb_records = ccl_leveldb.RawLevelDb(in_db_dir)
        except Exception:
            continue 

        for record in leveldb_records.iterate_records_raw():
            record_sequence = record.seq
            record_key_raw = record.user_key
            record_value_raw = record.value
            origin = str(record.origin_file)

            record_key = clean_key_bytes(record_key_raw)
            if record_key != duckchats:
                continue

            json_text = decode_json_bytes(record_value_raw)
            try:
                parsed = json.loads(json_text)
            except Exception:
                continue

            chats = parsed.get("chats", [])
            parent_folder = pathlib.Path(origin).parent.name
            origin_filename = pathlib.Path(origin).name
            origin_path_short = f"{parent_folder}/{origin_filename}"

            for chat in chats:
                chat_id = chat.get("chatId")
                title = chat.get("title")
                model = chat.get("model")
                messages = chat.get("messages", [])

                for m in messages:
                    role = m.get("role")
                    created_at_raw = m.get("createdAt")
                    created_at = clean_iso_timestamp(created_at_raw)
                    content = m.get("content", "") or ""
                    if not content and isinstance(m.get("parts"), list):
                        text_parts = [
                            p.get("text", "")
                            for p in m["parts"]
                            if isinstance(p, dict) and p.get("type") == "text"
                        ]
                        content = " ".join(tp for tp in text_parts if tp)

                    data_list.append((
                        chat_id,          # Chat ID
                        title,            # Title
                        model,            # LLM Model
                        role,             # Message Role
                        created_at,       # Message Time
                        content,          # Message Content
                        origin_path_short,# Origin File
                        record_sequence   # Sequence Number 
                    ))

    data_headers = (
        "Chat ID",
        "Title",
        "Model",
        "Message Role",
        ("Message Time", "datetime"),
        "Message Content",
        "Origin File",
        "Sequence Number" 
    )

    return data_headers, data_list, 'See source path(s) below'

@artifact_processor
def duckduckgo_cookies(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.sqlite'):
            break
            
    query = '''
        SELECT
            CASE cookies.last_access_utc 
                WHEN "0" THEN "" 
                ELSE datetime(cookies.last_access_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "last_access_utc", 
            cookies.host_key,
            cookies.name,
            cookies.value,
            CASE cookies.creation_utc 
                WHEN "0" THEN "" 
                ELSE datetime(cookies.creation_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "creation_utc", 
            CASE cookies.expires_utc 
                WHEN "0" THEN "" 
                ELSE datetime(cookies.expires_utc / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
            END AS "expires_utc", 
            cookies.path
        FROM cookies
        '''

    db_records = get_sqlite_db_records(source_path, query)
    for row in db_records:
        lastaccessed    = row[0]
        host      = row[1]
        name      = row[2]
        value      = row[3]
        creationtime     = row[4]
        expiry  = row[5]
        path  = row[6]
        
        data_list.append((lastaccessed, host, name, value, creationtime, expiry, path))

    data_headers = (('Last Accessed','datetime'),'Host','Name','Value',('Creation Time','datetime'),('Expiry','datetime'),'Path')   
    
    return data_headers, data_list, source_path

