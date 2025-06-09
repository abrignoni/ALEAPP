__artifacts_v2__ = {
    
    "duckduckgo_bookmarks": {
        "name": "DuckDuckGo Bookmarks",
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
    }
}
   
import sqlite3
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, get_sqlite_db_records

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

    data_headers = ('Entity ID','Deleted','Folder Path','Title','URL', 'Last Modified') 
    data_list = get_sqlite_db_records(source_path, query)        
    
    return data_headers, data_list, source_path