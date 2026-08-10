__artifacts_v2__ = {
    "GooglePlaySearches": {
        "name": "Google Play Searches",
        "description": "Search history from the Google Play Store",
        "author": "Alexis Brignoni",
        "creation_date": "2020-04-02",
        "last_update_date": "2025-09-09",
        "requirements": "none",
        "category": "Google Play Store",
        "notes": "",
        "paths": ('*/com.android.vending/databases/suggestions.db*'),
        "output_types": "standard",
        'artifact_icon': 'search',
        "sample_data": {
            "anne_a15": "Android 15 | com.android.vending vc 84801930 | 4 rows",
            "galaxys10_a10": "Android 10 | com.android.vending vc 82481710 | 5 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.vending vc 85180930 | 34 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.vending vc 84812830 | 23 rows",
            "pixel7a_a14": "Android 14 | com.android.vending vc 84191730 | 48 rows",
            "samsunga53_a14": "Android 14 | com.android.vending vc 84913330 | 26 rows",
            "samsungs20_a13": "Android 13 | com.android.vending vc 84962330 | 21 rows",
            "sharon_a14": "Android 14 | com.android.vending vc 84222730 | 25 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.vending vc 83631220 | 12 rows",
            "userb2_a13": "Android 13 | com.android.vending vc 84371930 | 9 rows",
        }
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records

@artifact_processor
def GooglePlaySearches(context):
    files_found = context.get_files_found()
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
