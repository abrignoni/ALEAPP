__artifacts_v2__ = {
    "externalDB": {
        "name": "External Database",
        "description": "Parses External Database",
        "author": "Heather Charpentier",
        "creation_date": "2025-11-17",
        "last_updated_date": "2025-11-17",
        "requirements": "none",
        "category": "ExternalDB",
        "notes": "",
        "paths": ('*/data/com.android.providers.media/databases/external.db*'),
        "output_types": "standard",
        "artifact_icon": "download",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

@artifact_processor
def externalDB(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    source_path = ''  

    candidate_dbs = []

    for file_found in files_found:
        file_str = str(file_found).lower()

        if file_str.endswith('.db') and (
            'media' in file_str or
            'external' in file_str or
            'internal' in file_str or
            'files' in file_str
        ):
            candidate_dbs.append(str(file_found))

    if not candidate_dbs:
        return (
            ('Path','Size',('Date Taken','datetime'),('Date Added','datetime'),('Date Modified','datetime'),'Album Name','Display Name','Directory','Duration'),
            data_list, 
            source_path
        )

    for db_path in candidate_dbs:

        try:
            db = open_sqlite_db_readonly(db_path)
            source_path = db_path   
            
            cursor = db.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='files';"
            )
            table_check = cursor.fetchone()

            if not table_check:
                db.close()
                continue

            cursor.execute('''
                SELECT 
                    datetime(datetaken/1000, 'unixepoch') AS "Date Taken",
                    datetime(date_added, 'unixepoch') AS "Date Added", 
                    datetime(date_modified, 'unixepoch') AS "Date Modified",
                    album AS "Album Name",
                    _display_name AS "Display Name",
                    _data AS "Path",
                    duration AS "Duration",
                    _size AS "Size"
                FROM files
            ''')

            rows = cursor.fetchall()

            for row in rows:
                data_list.append((
                    row[0], row[1], row[2], row[3], row[4],row[5], row[6], row[7]
                ))

            db.close()

        except Exception as e:
            continue

    data_headers = (('Date Taken','datetime'),('Date Added','datetime'),('Date Modified','datetime'),'Album Name','Display Name','Path','Duration','Size')

    return data_headers, data_list, source_path

