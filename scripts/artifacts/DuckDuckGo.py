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
        "last_update_date": "2025-06-08",
        "requirements": "none",
        "category": "DuckDuckGo",
        "notes": "Tested on version 5.237.0 (June, 3rd 2025)",
        "paths": ('*/com.duckduckgo.mobile.android/databases/app.db*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "book-open"
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
        "paths": ('*/com.duckduckgo.mobile.android/cache/tabPreviews/*/*.jpg'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "image"
    }
}

import inspect   
import sqlite3
import datetime
from pathlib import Path
from scripts.ilapfuncs import artifact_processor, is_platform_windows, check_in_media, open_sqlite_db_readonly, does_column_exist_in_db, get_sqlite_db_records, get_file_path, media_to_html, is_platform_windows, logfunc

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
    data_list = []
    source_path = get_file_path(files_found, 'app.db')

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
        data_list.append((
            row[0],  # Tab ID
            row[1],  # Current Tab
            row[2],  # Title
            row[3],  # URL
            row[6],  # Tab Last Accessed (Local)
            row[4],  # Cached Tab Filename
            row[5],  # Cached Tab Preview Time (Local)
        ))

    data_headers = (
        'Tab ID',
        'Current Tab',
        'Title',
        'URL',
        ('Tab Last Accessed (Local)','datetime'),
        'Cached Tab Filename',
        ('Cached Tab Preview Time (Local)','datetime'),
    )

    return data_headers, data_list, source_path

@artifact_processor
def duckduckgo_thumbnails(files_found, report_folder, seeker, wrap_text):
    artifact_info = inspect.stack()[0]
    data_list = []
    
    for file_found in files_found:
        media_path = Path(file_found)
        
        filename = (media_path.name)
        utctime = int(media_path.stem)
        filepath = str(media_path.parents[1])
        
        timestamp = (datetime.datetime.utcfromtimestamp(utctime/1000).strftime('%Y-%m-%d %H:%M:%S'))
        media_item = check_in_media(artifact_info, report_folder, seeker, files_found, file_found, filename)
        if media_item:
            data_list.append((timestamp, media_item, filename, file_found))
    
    data_headers = (('Timestamp','datetime'),('Thumbnail','media'),'File Name','Location')
    return data_headers, data_list, 'See source path(s) below'