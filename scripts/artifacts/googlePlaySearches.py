__artifacts_v2__ = {
    "GooglePlaySearches": {
        "name": "Google Play Searches",
        "description": "Search history from the Google Play Store",
        "author": "Alexis Brignoni",
        "creation_date": "2020-04-02",
        "last_updated_date": "2025-09-09",
        "requirements": "none",
        "category": "Google Play Store",
        "notes": "",
        "paths": ('*/com.android.vending/databases/suggestions.db*'),
        "output_types": "standard",
        'artifact_icon': 'search'
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records

@artifact_processor
def GooglePlaySearches(files_found, report_folder, seeker, wrap_text):
    data_list = []
    
    source_path = get_file_path(files_found, "suggestions.db")
    
    query = '''
    SELECT
    datetime(date / 1000, "unixepoch"),
    display1,
    query
    from suggestions
    '''
    
    db_records = get_sqlite_db_records(source_path, query)

    for record in db_records:
        data_list.append((record[0],record[1],record[2]))

    data_headers = ('Timestamp','Display','Query')
    return data_headers, data_list, source_path