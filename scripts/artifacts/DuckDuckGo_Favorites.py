__artifacts_v2__ = {
    
    "duckduckgo_favorites": {
        "name": "DuckDuckGo Favorited Sites",
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
    }
}
   
import sqlite3
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, get_sqlite_db_records

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